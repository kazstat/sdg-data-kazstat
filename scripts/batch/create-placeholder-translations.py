import os
import yaml

keys = [
    'national_indicator_description',
    'computation_definitions',
    'computation_calculations',
    'comments_limitations',
]
translations = {}
for key in keys:
    translations[key] = {}

for filename in os.listdir('meta'):
    metadata_file = os.path.join('meta', filename)
    with open(metadata_file, 'r') as stream:
        meta = yaml.load(stream, Loader=yaml.FullLoader)
    indicator_id = filename.replace('.yml', '')
    for key in keys:
        translation_key = key + '.' + indicator_id
        meta[key] = translation_key
        translations[key][translation_key] = ''

    with open(metadata_file, 'w') as stream:
        yaml.dump(meta, stream, allow_unicode=True)

for key in translations:
    filename = key + '.yml'
    translation_file = os.path.join('translations', 'ru', filename)
    with open(translation_file, 'w') as stream:
        yaml.dump(translations[key], stream, allow_unicode=True)
