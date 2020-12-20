import pandas as pd
import yaml
import os

df = pd.read_excel('changes_to_platform.xlsx',
    sheet_name='rename global indicators',
    index_col=None,
    header=None,
    skiprows=[0,1,2,3],
    names=['indicator', 'global_en', 'national_en', 'global_ru', 'national_ru', 'global_kk', 'national_kk']
)

def clean_indicator(indicator):
    indicator = indicator.replace('add', '')
    indicator = indicator.replace('(ADD) name national indc', '')
    indicator = indicator.strip()
    indicator = indicator.rstrip('.')
    return indicator

def clean_title(title):
    title = title.replace('(ADD)', '')
    title = title.strip()
    return title

def get_translation_path(language, file):
    return os.path.join('translations', language, file)

columns = {
    'global_en': get_translation_path('en', 'global_indicators.yml'),
    'national_en': get_translation_path('en', 'national_indicators.yml'),
    'global_ru': get_translation_path('ru', 'global_indicators.yml'),
    'national_ru': get_translation_path('ru', 'national_indicators.yml'),
    'global_kk': get_translation_path('kk', 'global_indicators.yml'),
    'national_kk': get_translation_path('kk', 'national_indicators.yml')
}

files = {}

for _,row in df.iterrows():
    indicator = clean_indicator(row['indicator'])
    translation_key = indicator.replace('.', '-') + '-title'
    for column in columns:
        filepath = columns[column]
        if filepath not in files:
            files[filepath] = {}
        if not pd.isnull(row[column]):
            title = clean_title(row[column])
            if title != '' and title != 'unchanged':
                files[filepath][translation_key] = clean_title(row[column])

for filepath in files:
    new_translations = files[filepath]
    if new_translations:
        with open(filepath, 'r', encoding='utf-8') as stream:
            old_translations = yaml.load(stream, Loader=yaml.FullLoader)
        for translation_key in new_translations:
            old_translations[translation_key] = new_translations[translation_key]
        with open(filepath, 'w') as file:
            yaml.dump(old_translations, file, sort_keys=True, encoding='utf-8', allow_unicode=True)
