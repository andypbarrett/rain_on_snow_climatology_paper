"""Utilities for climatology paper"""
import pandas as pd
import numpy as np

from ros_database.processing.surface import load_station_metadata, load_station_combined_data

    
def to_daily_boolean(x):
    if x.isnull().all():
        # return pd.NA
        return np.nan
    return x.any()

daily_aggregation_rules = {
    "t2m": lambda x: x.mean(skipna=True),
    "p01i": lambda x: x.sum(min_count=1),  #np.sum(x, where=np.isfinite(x)),
    "sog": to_daily_boolean, #lambda x: x.any(),
    "LIQUID": to_daily_boolean, #lambda x: x.any(),
    "RA": to_daily_boolean, #lambda x: x.any(),
    "FZRA": to_daily_boolean, #lambda x: x.any(),
    "SOLID": to_daily_boolean, #lambda x: x.any(),
    "UP": to_daily_boolean, #lambda x: x.any(),
}

climatology_agg_rules = {
    "t2m": lambda x: x.mean(skipna=True),
    "p01i": lambda x: x.mean(skipna=True),
    "sog": lambda x: x.mean(),
    "RA": lambda x: x.mean(),
    "FZRA": lambda x: x.mean(),
    "LIQUID": lambda x: x.mean(),
    "SOLID": lambda x: x.mean(),
    "UP": lambda x: x.mean(),
}

PTYPES = ["RA", "FZRA", "SOLID", "UP"]
LIQUID_PTYPE = ["RA", "FZRA"]

def event_frequency_climatology(s: pd.Series, period: str='7d'):
    """Calculates climatology of frequency of events

    Events are assumed to be boolean or 1,0.  A mean
    frequency for a window is first calculated, then a 
    climatological mean is calculated.

    Arguments
    ---------
    s : pandas.Series time series containing boolean or 1,0
    period : window size

    Return
    ------
    A pandas.Series containing climatological frequencies
    """
    return pd.to_numeric(s).rolling(period, center=True).mean().groupby(s.index.dayofyear).mean()


class ROSCombinedDataFrame(pd.DataFrame):
    """Class for Rain on Snow pandas.DataFrame"""

    def __new__(cls, *args, **kw):
        return super().__new__(cls)
        
    def __init__(self, *args, **kw):
        super(ROSCombinedDataFrame, self).__init__(*args, **kw)

    def set_ptype_liquid(self, include_up=False, inplace=False):
        """Creates new column for presence of liquid precipitation

        Arguments
        ---------
        include_up : include unknown precipitation type (UP).  Otherwise
                     just assign if either RA or FZRA is True
        drop : drop individual liquid precipitation types
        """
        liquid_ptype = LIQUID_PTYPE
        if include_up:
            liquid_ptype.append("UP")
        isliquid = self[liquid_ptype].any(axis=1)
        isliquid = isliquid.where(self[liquid_ptype].notnull().all(axis=1), pd.NA)
        if inplace:
            self["LIQUID"] = isliquid
        else:
            return isliquid

    def to_daily(self):
        return to_daily(self)

    def to_daily_climatology(self):
        return to_daily_climatology(self)
        
    @classmethod
    def from_file(cls, fname):
        """Wrapper to load combined data"""
        return cls(load_station_combined_data(fname))


def to_daily(df):
    """Returns daily aggregation of hourly time series"""
    daily_aggreggation_rules = {key: value for key, value in daily_aggregation_rules.items() 
                                if key in df}
    return df.resample('D').agg(daily_aggregation_rules)
    
def to_daily_climatology(df: pd.DataFrame):
    """Returns a daily climatology"""

    climatology_agg_rules = {
        "t2m": lambda x: x.mean(skipna=True),
        "p01i": lambda x: x.mean(skipna=True),
        "sog": lambda x: x.mean(),
        "RAIN": lambda x: x.mean(),
        "FZRA": lambda x: x.mean(),
        "LIQUID": lambda x: x.mean(),
        "SOLID": lambda x: x.mean(),
        "UP": lambda x: x.mean(),
        }

    if pd.infer_freq(df.index) != "D":
        df_day = to_daily(df)
    else:
        df_day = df

    percentile = [0.,.1,.25,.5,.75,.9,1.]
    t2m_quantile = df_day.t2m.groupby(df_day.index.dayofyear).quantile(percentile).unstack()
    t2m_quantile.columns = ["t2m_min", "t2m_10", "t2m_25", "t2m_50", "t2m_75", "t2m_90", "t2m_max"]

    climatology_agg_rules = {key: value for key, value in climatology_agg_rules.items() 
                                if key in df_day}
    df_clim = df_day.groupby(df_day.index.dayofyear).agg(climatology_agg_rules)

    return pd.concat([df_clim, t2m_quantile], axis=1)
