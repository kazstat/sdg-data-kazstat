from sdg.open_sdg import open_sdg_build
from alterations import alter_meta
from alterations import alter_data
import sdg
import os

def alter_data(df):
  if "REF_AREA" in df:
    df["GeoCode"]=df["REF_AREA"]
  return df

open_sdg_build(config='config_data.yml', alter_meta=alter_meta, alter_data=alter_data)
