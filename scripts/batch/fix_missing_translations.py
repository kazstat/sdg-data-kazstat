import os
import sdg
import yaml
import pandas as pd

skip_values_in_columns = [
    'GeoCode',
    'Group',
]

skip_column_names = [
    'GeoCode',
    'Group',
    'Units'
]

translations_should_include = {}

data_pattern = os.path.join('data', '*-*.csv')
data_input = sdg.inputs.InputCsvData(path_pattern=data_pattern)
data_input.execute()
for indicator in data_input.indicators:
    serieses = data_input.indicators[indicator].get_all_series()
    for series in serieses:
        disaggregations = series.get_disaggregations()
        for column in disaggregations:
            if column not in skip_column_names:
                translations_should_include[column] = True
            if column not in skip_values_in_columns:
                if disaggregations[column] and not pd.isna(disaggregations[column]):
                    translations_should_include[disaggregations[column]] = True

data_translation_file = os.path.join('translations', 'ru', 'data.yml')
with open(data_translation_file, 'r', encoding='utf-8') as stream:
    data_translations = yaml.load(stream, Loader=yaml.FullLoader)

needs_update = False
for key in translations_should_include:
    if key not in data_translations:
        needs_update = True
        data_translations[key] = key

with open(data_translation_file, 'w') as file:
    yaml.dump(data_translations, file, sort_keys=True, encoding='utf-8', allow_unicode=True)
