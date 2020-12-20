import pandas as pd
import numpy as np
import os
from urllib.request import urlretrieve
from xml.etree import ElementTree as ET
from io import StringIO

custom_code_regex = '^(_L_|KZ.)'
custom_agency = 'Kazstat'
custom_version = '1.0.0'

def register_all_namespaces(filename):
    namespaces = dict([node for _, node in ET.iterparse(filename, events=['start-ns'])])
    for ns in namespaces:
        ET.register_namespace(ns, namespaces[ns])
    return namespaces

def read_mapping():
    return pd.read_excel('sdmx-mapping-tool.xlsx',
        sheet_name=None,
        index_col=None,
        header=None,
        keep_default_na=False,
        na_values=['#REF!', '']
    )

def parse_code_sheet():
    sheets = read_mapping()
    df = sheets['CODES']
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

def parse_unit_sheet():
    sheets = read_mapping()
    df = sheets['UNITS']
    df = df[[3, 4]]
    df.columns = ['from', 'to']
    df = df.iloc[2:]
    return df.dropna()

url = 'https://registry.sdmx.org/ws/public/sdmxapi/rest/datastructure/IAEG-SDGs/SDG/latest/?format=sdmx-2.1&detail=full&references=all&prettyPrint=true'
filename = 'dsd.xml'

if not os.path.isfile(filename):
    urlretrieve(url, filename)

namespaces = register_all_namespaces(filename)
tree = ET.parse(filename)
root = tree.getroot()

dimensions = [
    'FREQ',
    'REPORTING_TYPE',
    'SERIES',
    'REF_AREA',
    'SEX',
    'AGE',
    'URBANISATION',
    'INCOME_WEALTH_QUANTILE',
    'EDUCATION_LEV',
    'OCCUPATION',
    'CUST_BREAKDOWN',
    'COMPOSITE_BREAKDOWN',
    'DISABILITY_STATUS',
    'ACTIVITY',
    'PRODUCT',
]

codelist_mappings = parse_code_sheet()
made_edits = False

for dimension in dimensions:
    dimension_node = root.find('.//str:Dimension[@id="' + dimension + '"]', namespaces)
    codelist_id = dimension_node.find('./str:LocalRepresentation/str:Enumeration/Ref', namespaces).attrib['id']
    codelist_node = root.find('.//str:Codelist[@id="' + codelist_id + '"]', namespaces)
    codelist_urn = codelist_node.attrib['urn']
    custom_codes = codelist_mappings[[dimension, dimension + ' Name']].dropna()
    custom_codes = custom_codes[custom_codes[dimension].str.match(custom_code_regex)]
    if custom_codes.empty:
        continue
    made_edits = True
    codelist_node.attrib['agencyID'] = custom_agency
    for index, row in custom_codes.iterrows():
        custom_code = row[dimension]
        custom_name = row[dimension + ' Name']
        code_node = ET.SubElement(codelist_node, 'str:Code')
        code_node.attrib['id'] = custom_code
        code_node.attrib['urn'] = codelist_urn + '.' + custom_code
        code_name_node = ET.SubElement(code_node, 'com:Name')
        code_desc_node = ET.SubElement(code_node, 'com:Description')
        code_name_node.text = custom_name
        code_desc_node.text = custom_name
        code_name_node.attrib['xml:lang'] = 'en'
        code_desc_node.attrib['xml:lang'] = 'en'

if made_edits:
    header_node = root.find('.//mes:Header', namespaces)

tree.write(filename)
