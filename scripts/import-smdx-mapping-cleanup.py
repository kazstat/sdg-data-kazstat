import pandas as pd
import numpy as np
import os
import yaml
import sdg

import_filename = 'Kazakhstan SDG SDMX mappings - Cleanup.xls'
disaggregations = {}
codes = None
composite_breakdowns = {}
new_translations = {}
debug = False

languages = ['ru', 'kk', 'en']

def parse_code_sheet(df):
    renamed_columns = []
    columns = df.iloc[1]
    last_column = None
    for column in columns:
        if column == 'Name':
            column = last_column + ' ' + 'Name'
        renamed_columns.append(column)
        last_column = column

    df.columns = renamed_columns
    df = df[2:]
    return df

def stop_at_first_blank_row(df):
    first_empty_row = 0
    for index, row in df.iterrows():
        if pd.isnull(row['Value']):
            first_empty_row = index
            break

    return df.head(first_empty_row)

def get_value_by_label(dimension, label):
    if pd.isnull(dimension):
        raise Exception('Cannot search for null dimension in code list. Label was: ' + str(label))
    if pd.isnull(label):
        raise Exception('Cannot search for null label in code list. Dimension was: ' + str(dimension))
    for _, row in codes.iterrows():
        if pd.isnull(row[dimension]):
            break
        row_value = row[dimension]
        row_label = row[dimension + ' Name']
        if row_label == label:
            return row_value

    raise Exception('Could not find ' + str(dimension) + '/' + str(label) + ' in codes list.')

sheets = pd.read_excel(import_filename,
    sheet_name=None,
    index_col=None,
    header=None,
    keep_default_na=False,
    na_values=['#REF!', '']
)

codes = parse_code_sheet(sheets['CODES'])
del sheets['CODES']

columns_renamed = {}

for sheet_name in sheets:

    df = sheets[sheet_name]
    disaggregation = df.iloc[0][0]
    df = df.rename(columns=df.iloc[1])
    df = stop_at_first_blank_row(df)
    df = df[2:]

    disaggregations[disaggregation] = {
        'rename': {},
        'remove': [],
        'dimensions': {},
        'translation': {},
    }
    composite_breakdowns[disaggregation] = False
    for idx, row in df.iterrows():
        original_value = row['Value']
        dimension = row['Dimension 1']
        value_label = row['Code 1']
        if dimension == 'COMPOSITE_BREAKDOWN':
            composite_breakdowns[disaggregation] = True
        if dimension == '[REMOVE]':
            disaggregations[disaggregation]['remove'].append(original_value)
        else:
            if dimension not in disaggregations[disaggregation]['dimensions']:
                disaggregations[disaggregation]['dimensions'][dimension] = 0
            disaggregations[disaggregation]['dimensions'][dimension] += 1
            try:
                value_code = get_value_by_label(dimension, value_label)
                if dimension not in disaggregations[disaggregation]['translation']:
                    disaggregations[disaggregation]['translation'][dimension] = {}
                disaggregations[disaggregation]['rename'][original_value] = value_code
                disaggregations[disaggregation]['translation'][dimension][original_value] = value_code
            except Exception as e:
                if debug:
                    print('A problem happened while trying to get the code for this row:')
                    print(row)
                    print('The problem was:')
                    print(e)

        if not pd.isnull(row['Dimension 2 (optional)']):
            print('WARNING: NEED TO DEAL WITH DIMENSION 2!!')

    most_common_dimension_name = None
    most_common_dimension_score = 0
    for dimension in disaggregations[disaggregation]['dimensions']:
        if most_common_dimension_name is None:
            most_common_dimension_name = dimension
            most_common_dimension_score = disaggregations[disaggregation]['dimensions'][dimension]
        else:
            this_score = disaggregations[disaggregation]['dimensions'][dimension]
            if this_score > most_common_dimension_score:
                most_common_dimension_name = dimension
                most_common_dimension_score = this_score
    if most_common_dimension_name is None:
        print('Probable dimension appeared to be None: ' + disaggregation)
    if pd.isna(most_common_dimension_name):
        print('Probable dimension appeared to be NaN: ' + disaggregation)
    else:
        columns_renamed[disaggregation] = most_common_dimension_name

columns_renamed_translation_keys = {}
for disaggregation in columns_renamed:
    if disaggregation and columns_renamed[disaggregation]:
        translation_key = columns_renamed[disaggregation]
        columns_renamed_translation_keys[disaggregation] = translation_key

def convert_disaggregation(disaggregation, map):
    if disaggregation in map:
        return map[disaggregation]
    return disaggregation

composite_breakdown_collisions = {}
for filename in os.listdir('data'):
    df = pd.read_csv(os.path.join('data', filename), dtype='str')
    if df.empty:
        continue
    composite_breakdowns_used = []
    for column in df.columns:
        if column in disaggregations:
            if disaggregations[column]['remove']:
                search_columns_for_duplicates = list(df.columns)
                search_columns_for_duplicates.remove('Value')
                duplicates = df[df.duplicated(subset=search_columns_for_duplicates)]
                num_duplicates = len(duplicates)
                for removed_value in disaggregations[column]['remove']:
                    df_without_cells = df.copy()
                    df_without_cells[column].mask(df_without_cells[column] == removed_value, np.NaN, inplace=True)
                    duplicates_without_cells = df_without_cells[df_without_cells.duplicated(subset=search_columns_for_duplicates)]
                    num_duplicates_without_cells = len(duplicates_without_cells)
                    if num_duplicates_without_cells > num_duplicates:
                        #print('Removing ' + removed_value + ' from cells was a bad idea. Caused new dupliates:')
                        #print(num_duplicates_without_cells - num_duplicates)
                        df = df[df[column] != removed_value]
                    else:
                        df = df_without_cells
            if disaggregations[column]['rename'] and column in df.columns:
                df[column] = df[column].apply(convert_disaggregation, map=disaggregations[column]['rename'])
                if column in composite_breakdowns and composite_breakdowns[column]:
                    composite_breakdowns_used.append(column)
                # Update translations too.
                #update_translations(disaggregations[column]['translation'], columns_renamed[column])

    # Rename the columns.
    new_column_occurences = {}
    old_columns = list(df.columns)
    for old_column in old_columns:
        if old_column in columns_renamed_translation_keys:
            new_column = columns_renamed_translation_keys[old_column]
            if new_column not in new_column_occurences:
                new_column_occurences[new_column] = [old_column]
            else:
                if old_column not in new_column_occurences[new_column]:
                    new_column_occurences[new_column].append(old_column)
    for new_column in new_column_occurences:
        if len(new_column_occurences[new_column]) > 1:
            merge_to = None
            for column in new_column_occurences[new_column]:
                if merge_to is None:
                    merge_to = column
                    continue
                df[merge_to] = df[merge_to].combine_first(df[column])
                df.drop(column, axis=1, inplace=True)
    df = df.rename(columns=columns_renamed_translation_keys)
    #update_translations(columns_renamed, 'codelist')

    if len(composite_breakdowns_used) > 1:
        for composite_breakdown_used in composite_breakdowns_used:
            if composite_breakdown_used not in composite_breakdown_collisions:
                composite_breakdown_collisions[composite_breakdown_used] = 1
            else:
                composite_breakdown_collisions[composite_breakdown_used] += 1
        print('WARNING: ' + filename + ' uses COMPOSITE_BREAKDOWN in ' + str(len(composite_breakdowns_used)) + ' columns:')
        print(composite_breakdowns_used)

    # Drop empty columns.
    df.dropna(how='all', axis=1, inplace=True)
    # Write to disk.
    df.to_csv(os.path.join('data', filename), index=False)

for disaggregation in disaggregations:
    for dimension in disaggregations[disaggregation]['translation']:
        translation_file = os.path.join('translations', 'ru', dimension + '.yml')
        with open(translation_file, 'r', encoding='utf-8') as stream:
            translations = yaml.load(stream, Loader=yaml.FullLoader)
            for translation in disaggregations[disaggregation]['translation'][dimension]:
                code = disaggregations[disaggregation]['translation'][dimension][translation]
                translations[code] = translation
        with open(translation_file, 'w', encoding='utf-8') as stream:
            yaml.dump(translations, stream, allow_unicode=True)
