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
translation_columns = {}

data_pattern = os.path.join('data', '*-*.csv')
data_input = sdg.inputs.InputCsvData(path_pattern=data_pattern)
data_input.execute(None)
for indicator in data_input.indicators:
    serieses = data_input.indicators[indicator].get_all_series()
    for series in serieses:
        disaggregations = series.get_disaggregations()
        for column in disaggregations:
            if column not in skip_column_names:
                translations_should_include[column] = True
                translation_columns[column] = column
            if column not in skip_values_in_columns:
                if disaggregations[column] and not pd.isna(disaggregations[column]):
                    translations_should_include[disaggregations[column]] = True
                    translation_columns[disaggregations[column]] = column

data_translation_file = os.path.join('translations', 'ru', 'data.yml')
with open(data_translation_file, 'r', encoding='utf-8') as stream:
    data_translations = yaml.load(stream, Loader=yaml.FullLoader)

needs_update = False
num = 0
for key in translations_should_include:
    if key not in data_translations:
        print('***' + key + '***')
        print(' in column: ' + translation_columns[key])
        num += 1

print(num)

"""
disagg_mappings = pd.read_csv(os.path.join('data-updates', 'disagg-mappings.csv'), names=['foo', 'bar'])
#disagg_mappings = disagg_mappings[disagg_mappings['bar'] != 'NEW DISAGGREGATION']
disagg_mappings = dict(zip(disagg_mappings['foo'], disagg_mappings['bar']))

for key in translations_should_include:
    if key not in data_translations:
        if key in disagg_mappings and disagg_mappings[key] != 'NEW DISAGGREGATION':
            #print(str(key) + ' is mapped to: ' + str(disagg_mappings[key]))
            #if disagg_mappings[key] not in data_translations:
            #    print('-- MAPPED VALUE NOT TRANSLATED --')
            pass
        elif key in disagg_mappings:
            pass
            print(disagg_mappings[key])
            #print(str(key) + ' is not mapped')
        else:
            print('FOOOOOOOO')
            print(key)
        #print('***' + key + '***')
        #print(' in column: ' + translation_columns[key])
"""