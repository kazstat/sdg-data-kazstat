import os
import sdg
import yaml
import pandas as pd

translation_file = os.path.join('translations', 'ru', 'data.yml')

with open(translation_file, 'r', encoding='utf-8') as stream:
    translations = yaml.load(stream, Loader=yaml.FullLoader)

with open(translation_file, 'w') as file:
    yaml.dump(translations, file, sort_keys=True, encoding='utf-8', allow_unicode=True)
