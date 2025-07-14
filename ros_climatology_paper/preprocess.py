"""Preprocesses database files 
- make_ptype_count: generates files for ptype counts
"""

from typing import Union, List
from pathlib import Path
import os

import pandas as pd

from config import DATABASE_PATH, STATION_METADATA

HOURLY_DATA_PATH = DATABASE_PATH / "combined"


def database_ctime(database_path: Path):
    """Returns the latest creation time for the database
    as an ordinal"""
    return max([os.path.getctime(p) for p in database_path.glob("*")])


def is_file_current(filepath: Path, db_creation_time) -> bool:
    """Returns True is filepath data is 
    after latest file data in database

    Argument
    --------
    filepath : path to file to be checked
    """
    if filepath.exists():
        return os.path.getctime(filepath) >= db_creation_time
    else:
        return False


def get_stid(fname):
    """Get station-id from filepath"""
    return fname.name.split(".")[0]

def station_files():
    """Returns a dictionary of station files indexed by station-id"""
    return {get_stid(f): f for f in HOURLY_DATA_PATH.glob("*.csv")}


def load_ptype(
    fp: Path, 
    stid: str, 
    ptypes: List=["UP","RA","FZRA","SOLID"]) -> pd.Series:
    """Load precipitation type observations and set to True is any
    precipitation type (UP or RA or FZRA or Solid) is True

    Argument
    --------
    fp : filepath
    stid : station id
    ptypes : list of precipitation type codes to load.  Default is all types
             `[UP, RA, FZRA or SOLID]`.  In this case resulting DataFrame is 
             count of any precipitation type reported in an hour.  Limiting list
             to a subset of precipitation types returns a count of only those types.
    
    Returns
    -------
    pandas.Series of booleans, where True indicates one of UP, RA, FZRA or SOLID recorded
    """
    return pd.read_csv(fp, index_col="datetime", parse_dates=True, low_memory=False, 
                       usecols=["datetime"]+ptypes).any(axis=1).rename(stid)


def ptype_list(ptype: Union[str,List[str]]) -> List[str]:
    """
    Translates a string into a list of ptypes and checks supplied
    list.

    Arguments
    ---------
    ptype : either a string describing set of precipitation types or a 
            list of precipitation types.  A string can one of
            "any", "liquid", "solid", or one of the coded precipitation types.
            "any" returns a list containing all precipitation codes
            ["UP", "RA", "FZRA", "SOLID"], "liquid" returns
            ["RA", "FZRA"], and "solid" returns ["SOLID"].

    Returns
    -------
    List of precipitations types
    """

    combined_ptypes = {
        "any": ["UP", "RA", "FZRA", "SOLID"],
        "liquid": ["RA", "FZRA"],
        "solid": ["SOLID"],
        }

    if isinstance(ptype, str):
        if ptype in combined_ptypes["any"]:
            return [ptype]
        else:
            try:
                return combined_ptypes[ptype]
            except:
                raise ValueError(f"Expected one of {combined_ptypes.keys()}, got {ptype} instead")
    else:
        return ptype


def make_ptype_count(
    outfile: Path, 
    ptype: Union[List[str],str]="any",
    rule: str="MS",
):
    """Counts the number of p-type reports by month for stations and writes to file.

    P-type can be selected.  Default is any.

    Arguments
    ---------
    outfile : output filepath
    ptype : type of precipitation to count.  Can be a ptype code (UP, RA, FZRA, or SOLID),
            or a string: liquid, solid or any.
    rule : resampling frequency.  Default is "MS"; start of month

    ptype string value "liquid" includes RA and FZRA, "solid" is just SOLID.  To include UP
    use a list, e.g `["UP", "RA", "FZRA"]`.
    """
    
    df = pd.concat([load_ptype(fpath, stid, ptypes=ptype_list(ptype)) 
                             for stid, fpath in station_files().items()], axis=1)
    df = df.resample("MS").sum().astype(float)  # count monthly occurrances
    df = df.sort_index(axis=1)  # Sort column index for nice plotting
    df.to_csv(outfile)
    return
