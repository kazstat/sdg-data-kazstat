from collections import defaultdict
import yaml
import os

def parse_preserving_duplicates(src):
    # We deliberately define a fresh class inside the function,
    # because add_constructor is a class method and we don't want to
    # mutate pyyaml classes.
    class PreserveDuplicatesLoader(yaml.loader.Loader):
        pass

    def map_constructor(loader, node, deep=False):
        """Walk the mapping, recording any duplicate keys.

        """
        mapping = defaultdict(list)
        for key_node, value_node in node.value:
            key = loader.construct_object(key_node, deep=deep)
            value = loader.construct_object(value_node, deep=deep)

            mapping[key].append(value)

        return mapping

    PreserveDuplicatesLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, map_constructor)
    return yaml.load(src, PreserveDuplicatesLoader)

# Walk through the translation folder.
for root, dirs, files in os.walk('translations'):
    # Each subfolder is a language code.
    language = os.path.basename(root)
    # For this script we only care about the source translations: Russian
    if language != 'ru':
        continue


    # Loop through the YAML files.
    for file in files:
        # Each YAML filename is a group.
        file_parts = os.path.splitext(file)
        group = file_parts[0]
        extension = file_parts[1]
        if extension != '.yml':
            continue
        with open(os.path.join(root, file), 'r') as stream:
            try:
                print('Scanning ' + file + ' for duplicates...')
                yamldata = parse_preserving_duplicates(stream)
                # Loop through the YAML data to add the translations.
                for key in yamldata:
                    value = yamldata[key]
                    if len(value) > 1:
                        print('-- duplicates found for: ' + key)
            except Exception as exc:
                print(exc)