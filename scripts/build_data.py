from sdg.open_sdg import open_sdg_build
from alterations import alter_meta
import sdg
import os

open_sdg_build(config='config_data.yml', alter_meta=alter_meta)

# Also produce a filtered SDMX output for use by UNSD.
# Use a cache-buster at the end of this URL, because our cached version of
# the global DSD has already been changed by the "extend_dsd" option.
# This shouldn't be needed and needs to be fixed in SDG Build!
global_dsd = 'https://registry.sdmx.org/ws/public/sdmxapi/rest/datastructure/IAEG-SDGs/SDG/latest/?format=sdmx-2.1&detail=full&references=children&sdgbuild=true'
def alter_data_for_unsd(data, context):
    indicator_id = context['indicator_id']
    series_code = sdg.helpers.sdmx.get_series_code_from_indicator_id(indicator_id, dsd_path=global_dsd)
    # If the series code could not be found, we will insert
    # a non-existent code to ensure that it will not be in
    # the output.
    if series_code is None:
        series_code = 'do_not_output_this_row'
    if 'SERIES' not in data:
        # This there is no SERIES column, set this value.
        data = data.assign(SERIES=series_code)
    # Also fill any empty SERIES with this value.
    values = {'SERIES': series_code}
    data.fillna(value=values, inplace=True)

    return data

data_input = sdg.inputs.InputCsvData(path_pattern='data/*.csv')
data_input.add_data_alteration(alter_data_for_unsd)
inputs = [
    data_input,
    sdg.inputs.InputYamlMeta(path_pattern='meta/*.yml'),
    sdg.inputs.InputYamlMeta(path_pattern='indicator-config/*.yml'),
]
schema = sdg.schemas.SchemaInputOpenSdg(schema_path='_prose.yml')
output = sdg.outputs.OutputSdmxMl(inputs, schema,
    output_folder=os.path.join('_site', 'unsd'),
    default_values = {
        'REF_AREA': '398',
        'OBS_STATUS': 'A',
        'UNIT_MULT': '0',
        'UNIT_MEASURE': 'NUMBER',
    },
    sender_id='Kazstat',
    structure_specific=True,
    constrain_data=True,
    dsd=global_dsd,
)
output.execute()
