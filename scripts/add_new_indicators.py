import pandas as pd
import yaml
import os

def normalize_indicator_id(inid):
  return inid.strip('.').replace('.', '-')

translation_files = [
  os.path.join('translations', 'en', 'global_indicators.yml'),
  os.path.join('translations', 'en', 'national_indicators.yml'),
  os.path.join('translations', 'ru', 'global_indicators.yml'),
  os.path.join('translations', 'ru', 'national_indicators.yml'),
  os.path.join('translations', 'kk', 'global_indicators.yml'),
  os.path.join('translations', 'kk', 'national_indicators.yml'),
]

source = pd.read_excel(
  'new_indicators.xlsx',
  usecols=[1,2,3,4,5,6,7],
  header=None,
  names=['indicator'] + translation_files,
  skiprows=[0,1,2]
)
for index,row in source.iterrows():
  indicator = normalize_indicator_id(row['indicator'])
  data_path = os.path.join('data', 'indicator_' + indicator + '.csv')
  meta_path = os.path.join('meta', indicator + '.md')
  del row['indicator']

  delete = False
  for prop in row:
    if prop == 'delete':
      delete = True

  if row.isnull().all():
    delete = True

  if delete:
    if os.path.isfile(data_path):
      print('Warning: ' + data_path + ' needs to be deleted.')
    if os.path.isfile(meta_path):
      print('Warning: ' + meta_path + ' needs to be deleted.')

  else:
    # Write the data and metadata.
    parts = indicator.split('-')
    data = 'Year,Units,Value'
    with open(data_path, 'w') as file:
      file.write(data)
    translation_key = indicator + '-title'
    meta = {
      'indicator_number': indicator.replace('-', '.'),
      'goal_number': parts[0],
      'target_number': parts[0] + '.' + parts[1],
      'reporting_status': 'notstarted',
    }
    has_global_name = not pd.isna(row[os.path.join('translations', 'ru', 'global_indicators.yml')])
    has_national_name = not pd.isna(row[os.path.join('translations', 'ru', 'national_indicators.yml')])
    global_only = has_global_name and not has_national_name
    national_only = has_national_name and not has_global_name
    if global_only:
      meta['indicator_name'] = 'global_indicators.' + translation_key
    elif national_only:
      meta['indicator_name'] = 'national_indicators.' + translation_key
    else:
      meta['indicator_name'] = 'global_indicators.' + translation_key
      meta['indicator_available'] = 'national_indicators.' + translation_key

    with open(meta_path, 'w') as file:
      yaml_str = yaml.dump(meta)
      file.write('---' + os.linesep + yaml_str + '---')

    # Write the translations.
    for translation_file in translation_files:
      if not pd.isna(row[translation_file]):
        translation_dict = {}
        with open(translation_file, 'r') as file:
          translation_dict = yaml.safe_load(file)
        translation_dict[translation_key] = row[translation_file]
        with open(translation_file, 'w') as file:
          yaml.dump(translation_dict, file, sort_keys=True, encoding='utf-8', allow_unicode=True)
