"""Plots T2m, precipitation type and snow on ground climatology
for stations"""
from pathlib import Path

import pandas as pd

from ros_database.processing.surface import load_station_metadata

import src.plotting as plotting


CLIMATOLOGY_PATH = Path("data")
OUTPATH = Path("figures/climatology")


def make_climatology_plot():
    """Generates a climatology plot for a single station"""

    station = load_station_metadata()
    
    filelist = CLIMATOLOGY_PATH.glob("*.climatology.csv")

    for fp in filelist:

        outpath = OUTPATH / f"{fp.stem}.png"
        
        stid = fp.name.split(".")[0]
        title = f"{station.loc[stid].station_name} ({stid})"
        
        print(f"Creating plot from {fp} -> {outpath}")

        df = pd.read_csv(fp, index_col=0)
        fig = plotting.plot_climatology(df, title=title)

        fig.savefig(outpath)


if __name__ == "__main__":
    make_climatology_plot()
