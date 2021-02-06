import yaml
import os
import frontmatter
import requests
import sdg
import sys
import pandas as pd
from pathlib import Path

if len(sys.argv) < 2:
    sys.exit('Provide the path of your data config file (eg, config_data.yml). Optionally also provide your preferred language.')

config_file = sys.argv[1]

if not os.path.isfile(config_file):
    sys.exit('The path "' + config_file + '" is not valid.')

options = {}
with open(config_file) as file:
    options = yaml.load(file, Loader=yaml.FullLoader)

if 'translations' not in options:
    options['translations'] = sdg.open_sdg.open_sdg_translation_defaults()
translations = sdg.open_sdg.open_sdg_translations_from_options(options)
translation_helper = sdg.translations.TranslationHelper(translations)

language = options['languages'][0] if 'languages' in options else None
if len(sys.argv) > 2:
    language = sys.argv[2]
if 'languages' in options and language not in options['languages']:
    sys.exit('The specified language "' + language + '" is not valid.')

# Load the jekyll-open-sdg-plugins indicator config file.
indicator_config_file = requests.get('https://raw.githubusercontent.com/open-sdg/jekyll-open-sdg-plugins/master/lib/jekyll-open-sdg-plugins/schema-indicator-config.json')
indicator_config_schema = indicator_config_file.json()

# Get the yamlmd input from the config.
input_config = options['inputs'] if 'inputs' in options else sdg.open_sdg.open_sdg_input_defaults()
yamlmd_input_matches = [x for x in input_config if x['class'] == 'InputYamlMdMeta']
if len(yamlmd_input_matches) == 0:
    sys.exit('The data config does not have an InputYamlMdMeta input.')
yamlmd_input_config = yamlmd_input_matches[0]

meta_path_pattern = yamlmd_input_config['path_pattern']
meta_path_folder = os.path.split(meta_path_pattern)[0]
meta_path_folder_parent = Path(meta_path_folder).parent

# This metadata mapping will be compiled throughout the functions below.
metadata_mapping = {}


def convert_folder(metadata_folder, metadata_folder_parent):

    # Make a folder for the config if needed.
    config_folder = os.path.join(metadata_folder_parent, 'indicator-config')
    os.mkdir(config_folder)
    # Load each metadata file, and create a CSV version with metadata, and a
    # YAML version with indicator config.
    for filename in os.listdir(metadata_folder):
        metadata_file = os.path.join(metadata_folder, filename)
        config_file = os.path.join(config_folder, filename.replace('.md', '.yml'))
        convert_metadata(metadata_file, config_file)

    # TODO: Recurse here for any subfolders.


def convert_metadata(metadata_file, config_file):
    post = frontmatter.load(metadata_file)
    content = post.content
    meta = post.metadata
    indicator_config = {'page_content': content}
    indicator_metadata = {}
    for key in meta:
        if is_indicator_config(key):
            indicator_config[key] = meta[key]
        else:
            indicator_metadata[key] = meta[key]
            # Translate the key for the metadata mapping.
            if key not in metadata_mapping:
                translated_key = translation_helper.translate(key, language, ['metadata_fields', 'data'])
                metadata_mapping[key] = translated_key
    # Write the metadata.
    df = pd.DataFrame({'field': indicator_metadata.keys(), 'value': indicator_metadata.values()})
    csv_metadata_file = metadata_file.replace('.md', '.csv')
    df.to_csv(csv_metadata_file, index=False, header=False, encoding='utf-8')

    # Write the config.
    with open(config_file, 'w') as stream:
        yaml.dump(indicator_config, stream, allow_unicode=True)

    # Delete the old metadata file.
    os.remove(metadata_file)


def is_indicator_config(key):
    return key in indicator_config_schema['properties']


# Recursively convert all metadata.
convert_folder(meta_path_folder, meta_path_folder_parent)

# Write the metadata mapping.
df = pd.DataFrame({'field': metadata_mapping.values(), 'value': metadata_mapping.keys()})
df.to_csv('metadata-mapping.csv', index=False, header=False, encoding='utf-8')

# Update the data config.
with open(config_file, 'w') as file:
    data_config = yaml.load(file, Loader=yaml.FullLoader)
    input_config = sdg.open_sdg.open_sdg_input_defaults()
    if 'inputs' in data_config:
        input_config = data_config['inputs']
    for input_item in input_config:
        if input_item['class'] != 'InputYamlMdMeta':
            new_input_config.append(input_item)
    new_input_config.append({
        'class': 'InputCsvMeta',
        'path_pattern': os.path.join(meta_path_folder, '*.csv')
    })
    new_input_config.append({
        'class': 'InputYamlMeta',
        'path_pattern': os.path.join(meta_path_folder_parent, 'indicator-config', '*.yml')
    })
    data_config['inputs'] = new_input_config
    yaml.dump(data_config, file, allow_unicode=True)
