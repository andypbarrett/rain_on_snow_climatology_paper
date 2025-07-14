"""Generates a daily climatology for each station

Fields
------
average 2m temperature
quantiles for 2m temperature [0.0, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0]
P(liquid)
P(solid)
P(sog)
"""

from ros_database.filepath import SURFOBS_COMBINED_PATH

from src.utils import ROSCombinedDataFrame, to_daily_climatology, event_frequency_climatology


# Station-ids for stations with T2m records that start on or before 1979-01-01
# and have more than 70% valid data
long_term_stations = ['PANC', 'PABR', 'PABE', 'PABT', 'PACV', 'PASC', 'PAEI', 'PAFA',
                      'PFYU', 'PABI', 'PAGA', 'PAGK', 'PAIM', 'PAEN', 'PAKN', 'PADQ',
                      'PAOT', 'PAMC', 'PAMH', 'PANN', 'PAOM', 'PAOR', 'PAAQ', 'PPIZ',
                      'PARY', 'PASV', 'PATK', 'PATA', 'PAVD', 'PAFB', 'PAYA', 'CYBK',
                      'CYCB', 'CYCY', 'CYZS', 'CWEU', 'CYUX', 'CYFB', 'CYUT', 'CYRB',
                      'CYKD', 'CZFM', 'CYFS', 'CYSM', 'CYHY', 'CYEV', 'CYCO', 'CYVQ',
                      'CYSY', 'CYUB', 'CYZF', 'CYDA', 'CYMA', 'CYOC', 'CYZW', 'CYXY',
                      'CYVP', 'CYYR', 'EFHA', 'EFHK', 'EFIV', 'EFJY', 'EFKI', 'EFKE',
                      'EFKU', 'EFKS', 'EFLP', 'EFMA', 'EFMI', 'EFOU', 'EFPO', 'EFRO',
                      'EFTU', 'EFUT', 'EFVA', 'BGBW', 'BGSF', 'BGTL', 'BIAR', 'BIKF',
                      'BIRK', 'ENAL', 'ENAT', 'ENDU', 'ENBR', 'ENBV', 'ENBO', 'ENBN',
                      'ENEV', 'ENKB', 'ENNA', 'ENMH', 'ENML', 'ENOL', 'ENSK', 'ENSB',
                      'ENTC', 'ENVA', 'UHMA', 'ULAA', 'USHH', 'UHMM', 'ULMM', 'USNN',
                      'ULPB', 'UHMD', 'USRR', 'UUYY', 'ESNQ', 'ESNK', 'ESPA', 'ESSA',
                      'ESNN', 'ESNU', 'ESOW', 'ESPE']


def make_climatology(fp):
    """Generates a daily climatology for a station"""
    
    df = ROSCombinedDataFrame.from_file(fp)

    df.set_ptype_liquid(inplace=True)
    df_day = df.to_daily()

    df_clim = to_daily_climatology(df_day)
    
    return df_clim

def run_all_stations():

    for stid in long_term_stations[:5]:

        print(f"Getting climatology for {stid}")
        
        fp = list(SURFOBS_COMBINED_PATH.glob(f"{stid}*.csv"))[0]

        df_clim = make_climatology(fp)
        print(df_clim.head())


if __name__ == "__main__":
    run_all_stations()
