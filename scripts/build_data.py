from sdg.open_sdg import open_sdg_build

def alter_meta(metadata):
    indicator_id = metadata['indicator_number']
    id_parts = indicator_id.split('.')
    is_global_indicator = len(id_parts) == 3
    metadata['is_global_indicator'] = is_global_indicator
    return metadata

open_sdg_build(config='config_data.yml', alter_meta=alter_meta)
