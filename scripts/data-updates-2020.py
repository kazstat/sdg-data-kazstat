import os
import glob
import pandas as pd
import numpy as np
import yaml

path_pattern = 'data-updates/*.xlsx'
paths = glob.glob(path_pattern)

def convert_path(path):
    filename = path.split('/')[1]
    filename = filename.replace('.xlsx', '')
    filename = filename.replace('SDG ', '')
    filename = filename.split(' ')[0]
    filename = filename.replace('.', '-')
    filename = filename.replace('new', '')
    filename = os.path.join('data', 'indicator_' + filename + '.csv')
    #if not os.path.isfile(filename):
    #    print(path)
    return filename

def column_is_not_year(column):
    if isinstance(column, int):
        return False
    return not column.isnumeric()

def fix_region_spelling(value):
    value = str(value)
    value = value.replace('п. ', 'п_')
    value = value.replace('п.', 'п_')
    value = value.replace('г. ', 'г_')
    value = value.replace('г.', 'г_')
    return value

disagg_mappings = pd.read_csv(os.path.join('data-updates', 'disagg-mappings.csv'), names=['foo', 'bar'])
disagg_mappings = disagg_mappings[disagg_mappings['bar'] != 'NEW DISAGGREGATION']
disagg_mappings = dict(zip(disagg_mappings['foo'], disagg_mappings['bar']))

def clean_value(value):
    if '\n' in value:
        print('Value had a new line in it: ***' + value + '***')
    return value.replace('\n', ' ')

def map_value(value):
    if value in disagg_mappings:
        return disagg_mappings[value]
    else:
        return value

for path in paths:
    # Read Excel file.
    df = pd.read_excel(path,
        index_col=None,
        na_values=['…', '-', '...', 'х', 'x', '..', '….'],
    )

    # Transform to long format.
    non_year_columns = list(filter(column_is_not_year, list(df.columns)))
    df = pd.melt(
        df,
        id_vars=non_year_columns,
        var_name='Year',
        value_name='Value'
    )
    columns = ['Year'] + non_year_columns + ['Value']
    df = df[columns]

    # Fix remaining issues.
    df = df[df['Value'].notna()]
    df = df[df['Year'].notna()]

    df['Value'] = df['Value'].replace(',', '', regex=True)
    df['Value'] = df['Value'].replace(' ', '', regex=True)
    df['Value'] = df['Value'].replace('\s', '', regex=True)

    # Change remaining "nan" to ''.
    df = df.replace(np.nan, '', regex=True)

    df = df.rename(columns=lambda x: x.strip())
    column_fixes = {
        'Unit': 'Units',
        'Регион': 'Регионы',
        'Region': 'Регионы',
    }
    df = df.rename(columns=column_fixes)

    if 'Регионы' in list(df.columns):
        df['Регионы'] = df['Регионы'].apply(fix_region_spelling)
    if 'Город' in list(df.columns):
        df['Город'] = df['Город'].apply(fix_region_spelling)

    df = df.applymap(lambda x: clean_value(x) if isinstance(x, str) else x)

    df = df.applymap(lambda x: map_value(x) if isinstance(x, str) else x)

    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    df = df.applymap(lambda x: map_value(x) if isinstance(x, str) else x)

    # Write CSV file.
    existing_file = convert_path(path)
    df.to_csv(existing_file, index=False)
