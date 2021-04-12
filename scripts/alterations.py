from sdg import helpers

def alter_meta(metadata):

    # Automatically detect global indicators.
    if 'indicator_number' in metadata:
        indicator_id = metadata['indicator_number']
        id_parts = indicator_id.split('.')
        is_global_indicator = len(id_parts) == 3
        metadata['is_global_indicator'] = is_global_indicator

        # Automatically set some predicable properties.
        metadata['goal_number'] = id_parts[0]
        metadata['target_number'] = id_parts[0] + '.' + id_parts[1]
        metadata['target_name'] = 'global_targets.' + id_parts[0] + '-' + id_parts[1] + '-title'

    metadata['national_geographical_coverage'] = 'meta.Казахстан'

    return metadata
