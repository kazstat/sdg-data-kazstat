import pandas as pd
import yaml
import os
import yamlmd

def translation_is_global(translation_key):
    if 'global_indicators.' not in translation_key:
        return False
    indicator_id = translation_key.replace('global_indicators.', '')
    indicator_id = translation_key.replace('-title', '')
    parts = indicator_id.split('-')
    if len(parts) > 3:
        return False
    return True

# Load the Russian translations to decide whether each indicator has global/national names.
with open(os.path.join('translations', 'ru', 'global_indicators.yml'), 'r', encoding='utf-8') as stream:
    global_indicators = yaml.load(stream, Loader=yaml.FullLoader)
with open(os.path.join('translations', 'ru', 'national_indicators.yml'), 'r', encoding='utf-8') as stream:
    national_indicators = yaml.load(stream, Loader=yaml.FullLoader)

for filename in os.listdir('meta'):
    filepath = os.path.join('meta', filename)
    meta = yamlmd.read_yamlmd(filepath)
    indicator_id = os.path.splitext(filename)[0]
    translation_key = indicator_id + '-title'
    translation_key_global = 'global_indicators.' + translation_key
    translation_key_national = 'national_indicators.' + translation_key
    
    has_global_title = translation_key in global_indicators
    has_national_title = translation_key in national_indicators

    if has_national_title and not has_global_title:
        if translation_is_global(meta[0]['indicator_name']):
            # In some cases the national indicators use a global indicator name.
            has_global_title = True

    if not has_global_title:
        indicator_id_parts = indicator_id.split('-')
        if len(indicator_id_parts) == 3:
            has_global_title = True

    if has_global_title and has_national_title:
        meta[0]['indicator_name'] = translation_key_global
        meta[0]['indicator_available'] = translation_key_national
        meta[0]['graph_title'] = translation_key_national
    elif has_global_title:
        meta[0]['indicator_name'] = translation_key_global
        if 'indicator_available' in meta[0]:
            del meta[0]['indicator_available']
        meta[0]['graph_title'] = translation_key_global
    elif has_national_title:
        meta[0]['indicator_name'] = translation_key_national
        if 'indicator_available' in meta[0]:
            del meta[0]['indicator_available']
        meta[0]['graph_title'] = translation_key_national
    else:
        print('WARNING - indicator ' + indicator_id + ' has neither global nor national title.')
    
    yamlmd.write_yamlmd(meta, filepath)
