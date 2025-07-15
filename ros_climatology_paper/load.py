"""Loads datasets"""
from typing import Tuple

from pathlib import Path

import pandas as pd


DATAPATH = Path.home() / "src" / "rain_on_snow_climatology_paper" / "data"
DATABASE_PATH = Path.home() / "Data/AROSS/database/observations/surface/version_2.0.0"

ptype_count_paths = {
    "all": DATAPATH / "all_ptype_count_month.csv",
    "liquid": DATAPATH / "liquid_ptype_count_month.csv",
    "solid": DATAPATH / "solid_ptype_count_month.csv",
    }

def load_ptype_count(
        ptype: str="all",
        time_range: Tuple[str]=("1979",None)) -> pd.DataFrame:
    """Loads precipitation-type counts

    Arguments
    ---------
    ptype : precipitation type.  Either "all", "liquid", "solid"
    time_range : time slice as tuple

    Returns
    -------
    pandas.DataFrame containing counts
    """

    accepted_ptypes = ["all", "solid", "liquid"]
    
    if not ptype in accepted_ptypes:
        raise ValueError(f"Expects ptype to be one of {', '.join(accepted_ptypes)}, "
                         f"got {ptype} instead")

    df = pd.read_csv(ptype_count_paths[ptype], index_col=0, parse_dates=True)
    return df[slice(*time_range)]


# Temporary - update ros_database
def get_filepath(station_id: str, filetype: str="combined") -> Path:
    """Returns path to file of filetype

    Arguments
    ---------
    station_id : station id code
    filetype : type of file to return "raw", "combined", "events"
    
    Returns
    -------
    Path object
    """
    filetypes = ["raw", "clean", "hourly", "combined", "events"]
    if not filetype in filetypes:
        raise ValueError(f"Invalid filetype. Expected one of {', '.join(filetypes)}, "
                         f"got {filetype} instead")
    
    try:
        return next((DATABASE_PATH / filetype).glob(f"{station_id}.*"))
    except:
        raise FileNotFoundError(f"No {filetype} file found for {station_id}")


def load_combined(station_id: str) -> pd.DataFrame:
    """Load data for a combined file with station-id

    Arguments
    ---------
    station_id : ID for station

    Return
    ------
    pandas.DataFrame
    """
    try:
        fp = get_filepath(station_id, filetype="combined")
    except ValueError as err:
        print(err)
    
    return pd.read_csv(fp, index_col=0, parse_dates=True, low_memory=False)
