"""Calculates start and end of winter based on temperature and likelihood of snow on the ground"""
from pathlib import Path
import re

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

from ros_database.processing.surface import load_station_metadata, load_station_combined_data
from ros_database.filepath import SURFOBS_COMBINED_PATH

from src.utils import ROSCombinedDataFrame, to_daily_climatology, event_frequency_climatology


def make_combined_filename(stid: str) -> Path:
    """Builds filepath for combined station file"""
    return list(SURFOBS_COMBINED_PATH.glob(f"{stid}.*.hourly.combined.csv"))[0]


def t2m_winter_start_and_end(df):
    """Returns start and end of winter based on when 
    2m temperature is above and below 0 C"""
    last_day = df.t2m[df.t2m > 0.].index[0]
    first_day = df.t2m[df.t2m > 0.].index[-1]
    return (first_day, last_day)


def stid_from_path(fp):
    m = re.search(r"/(\w{4})\.\d{8}to\d{8}\.hourly\.combined\.csv", str(fp))
    if m:
        return m.groups()[0]
    else:
        raise KeyError(f"Could not find station id string in {fp}")


def get_por(df: pd.DataFrame):
    """Returns start and end date of valid record, along with number
    of days and precentage of valid data for period

    Arguments
    ---------
    df : pandas.DataFrame of data-type boolean

    Returns
    -------
    date-por-begins, date-por-ends, number-days, percent-valid-data

    Example
    -------
    [In]: get_por(df.t2m.notnull())
    [Out]: (Timestamp('2025-05-04 00:00:00'),
            Timestamp('2025-05-08 00:00:00'),
            5,
            np.float64(80.0))
    """
    test = df[df]
    
    nvalid = test.sum()

    if nvalid <= 0:
        return np.nan, np.nan, 0, 0.0
    
    begin = test.index[0]
    end = test.index[-1]

    nday = (end - begin).days + 1
    nvalid_pc = nvalid * 100. / nday

    return begin, end, nday, nvalid_pc


def get_winter_one_station(fp, verbose=False):
    """Returns statistics for start and end of winter
    based on climatology of t2m
    
    """

#    fp = make_combined_filename(stid)

    stid = stid_from_path(fp)
    result = {}
    
    if verbose: print(f"Getting winter stats for {stid}")
    
    df = ROSCombinedDataFrame.from_file(fp)
    df.set_ptype_liquid(inplace=True)  # defines liquid as RA and FZRA

    df_day = df.to_daily()

    t2m_begin, t2m_end, t2m_record_days, t2m_nvalid_pc = get_por(df_day.t2m.notnull())
    pt_begin, pt_end, pt_record_days, pt_nvalid_pc = get_por(df_day[["RA","FZRA","SOLID","UP"]].notnull().all(axis=1))
    sog_begin, sog_end, sog_record_days, sog_nvalid_pc = get_por(df_day.sog.notnull())

    # if df_day.index[0] > "1a
    _, _, _, t2m_nvalid_1979_pc = get_por(df_day["1979":"2022"].t2m.notnull())

    result["t2m_begin"] = t2m_begin
    result["t2m_end"] = t2m_end
    result["t2m_nvalid_pc"] = t2m_nvalid_pc
    result["t2m_nvalid_1979_pc"] = t2m_nvalid_1979_pc

    result["ptype_begin"] = pt_begin
    result["ptype_end"] = pt_end
    result["ptype_nvalid_pc"] = pt_nvalid_pc

    result["sog_begin"] = sog_begin
    result["sog_end"] = sog_end
    result["sog_nvalid_pc"] = sog_nvalid_pc

#    print(f"{t2m_begin} {t2m_end} {t2m_record_days} {t2m_nvalid_pc}")
    
    df_clim = to_daily_climatology(df_day)

    first_day, last_day = t2m_winter_start_and_end(df_clim)

    result["first_day"] = first_day
    result["last_day"] = last_day
    
    return stid, result  #winter_dates, t2m_begin, t2m_end, t2m_nvalid_pc


def main(debug=False):
    """Process data"""
    
    files = sorted(SURFOBS_COMBINED_PATH.glob("*.csv"))

    index = []
    stats = []
#    last_day = []
#    first_day = []
    for i, fp in enumerate(files):
        stid, result = get_winter_one_station(fp, verbose=True)
        index.append(stid)
        stats.append(result)
        
        if debug:
            if i > 5:
                break

    result = pd.DataFrame(stats, index=index)
    print(result)
#    result.to_csv(Path("data/climatological_winter_period_by_station.csv"))


if __name__ == "__main__":
    main(debug=True)
