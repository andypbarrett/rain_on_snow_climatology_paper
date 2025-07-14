"""Generates files for climatology paper"""
import argparse
from pathlib import Path

from config import DATABASE_PATH
from ros_climatology_paper import preprocess as ros_preprocess

DATAPATH = Path(".") / "data"
DATABASE_PATH = DATABASE_PATH / "combined"

def preprocess(update_all=False, verbose=True):
    """Preprocesses files"""

    database_created = ros_preprocess.database_ctime(DATABASE_PATH)

    # Count of any reported p-type 
    fp = DATAPATH / "all_ptype_count_month.csv"
    if not fp.exists() | ros_preprocess.is_file_current(fp, database_created):
        if verbose: print(f"Updating {fp}")
        ros_preprocess.make_ptype_count(fp, ptype="any")

    # Count of reported liquid p-types (RA and FZRA)
    fp = DATAPATH / "liquid_ptype_count_month.csv"
    if not fp.exists() | ros_preprocess.is_file_current(fp, database_created):
        if verbose: print(f"Updating {fp}")
        ros_preprocess.make_ptype_count(fp, ptype="liquid")

    # Count of reported solid p-type (SOLID)
    fp = DATAPATH / "solid_ptype_count_month.csv"
    if not fp.exists() | ros_preprocess.is_file_current(fp, database_created):
        if verbose: print(f"Updating {fp}")
        ros_preprocess.make_ptype_count(fp, ptype="solid")


    # TBD
    # - Add station climatology
    # - Add duration of winter
    # - Add duration of snow cover
    # - Add fraction of liquid precipitation


if __name__ == "__main__":
    update_all = False
    
    preprocess()
