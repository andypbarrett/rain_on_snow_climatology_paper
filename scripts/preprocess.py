"""Generates files for climatology paper"""
import argparse
from pathlib import Path

from ros_climatology import preprocess

DATAPATH = Path(".") / "data"


def preprocess(update_all=False, verbose=True):
    """Preprocesses files"""

    database_created = preprocess.database_ctime()
    
    fp = DATAPATH / "all_ptype_count_month.csv"
    if not fp.exists() | preprocess.is_file_current(fp, database_created):
        if verbose: print(f"Updating {fp}")
        preprocess.make_ptype_count(fp, ptype="any")

    
if __name__ == "__main__":
    update_all = False
    
    preprocess()