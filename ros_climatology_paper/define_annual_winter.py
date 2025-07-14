import pandas as pd


def get_freezing_days(s, nday=5):
    """Returns N-day sum of days below freezing"""
    # Set forward window indexer.  Window is today+nday-1
    indexer = pd.api.indexers.FixedForwardWindowIndexer(window_size=nday)
    return (s.interpolate() < 0.).rolling(window=indexer, min_periods=nday).sum()


def get_warming_days(s, nday=5):
    """Returns N-day sum of days at or above freezing"""
        # Set forward window indexer.  Window is today+nday-1
    indexer = pd.api.indexers.FixedForwardWindowIndexer(window_size=nday)
    return (s.interpolate() >= 0.).rolling(window=indexer, min_periods=nday).sum()

    
def get_annual_winter_period(s: pd.Series,
                             nday: int=5):
    """Find start and end of winter period

    We use the SMHI definition of winter, which defines the start of winter
    as the first day of the first N-day period with temperatures below freezing (0 C).
    The default value for N used by SMHI is 5 but can be changed with the `nday` 
    keyword parameter.

    NB: last_day is last day of winter in year, and first_day is first_day of winter
        in same year.  So first_day and last_day do not define start and end of same winter.
        
    Arguments
    ---------
    s : a `pandas.Series` object containing daily average near-surface temperature
    nday : length of the period to evaluate in days

    Returns
    -------
    """

    # t2m_max_date is rough date of maximum temperature
    year = s.index[0].year
    t2m_max_date = f"{year}-08-01"
    
    # Find first day of winter
    # Freezing days are days below 0C
    # freezing_days = (s.interpolate() < 0.).rolling(window=indexer, min_periods=nday).sum()
    freezing_days = get_freezing_days(s)
    try:
        first_day = freezing_days[freezing_days == nday][t2m_max_date:].index[0]
    except IndexError as err:
        print(f"No valid data for range [{t2m_max_date}:], returning NaN")
        first_day = pd.NaT

    # Find last day of winter
    # warming_days are days greater than equal to 0C
    # warming_days = (s.interpolate() >= 0.).rolling(window=indexer, min_periods=nday).sum()
    warming_days = get_warming_days(s)
    try:
        last_day = warming_days[warming_days == nday].index[0]
    except IndexError as err:
        print(f"No valid data for ['{year}'], returning NaN")
        last_day = pd.NaT

    return last_day, first_day

