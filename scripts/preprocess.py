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
    
    fp = DATAPATH / "all_ptype_count_month.csv"
    if not fp.exists() | ros_preprocess.is_file_current(fp, database_created):
        if verbose: print(f"Updating {fp}")
        ros_preprocess.make_ptype_count(fp, ptype="any")

    
if __name__ == "__main__":
    update_all = False
    
    preprocess()
