import yaml
import os

for language in ['en', 'ru', 'kk']:

    with open(os.path.join('translations', language, 'national_indicators.yml'), 'r', encoding='utf-8') as stream:
        this_repo = yaml.load(stream, Loader=yaml.FullLoader)

    for key in this_repo:
        translation = this_repo[key].replace('\n', ' ')
        translation = ' '.join(translation.split())
        this_repo[key] = translation

    with open(os.path.join('translations', language, 'national_indicators.yml'), 'w', encoding='utf-8') as stream:
        yaml.dump(this_repo, stream, allow_unicode=True)
