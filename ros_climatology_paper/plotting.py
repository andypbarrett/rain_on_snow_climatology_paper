"""Plotting routines"""
from typing import Union, Tuple, List, Dict

import calendar
import datetime as dt

import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.colors import Normalize, Colormap
import matplotlib as mpl


def doy_month_ticks_and_labels(month_start=1, which="major", with_labels=True):
    """Returns ticks and labels for months when axis is day-of-year"""
    months = np.roll(np.arange(1,13), -1*(month_start-1))
    ticks = np.cumsum([1]+[calendar.monthrange(2001,m)[1] for m in months])
    minor_ticks = (ticks[:-1] + np.roll(ticks,-1)[:-1])*.5
    labels = [calendar.month_abbr[m] for m in months]
    return ticks, minor_ticks, labels


def plot_climatology(df: pd.DataFrame, title: str=''):
    """Generate a climatology plot"""

    iswinter_color = "0.9"

    quantile_colors = ["0.75", "0.5", "0.25"]
    median_color = "k"
    tavg_color = "tab:blue"

    last_day = df.t2m[df.t2m > 0.].index[0]
    first_day = df.t2m[df.t2m > 0.].index[-1]
    
    fig = plt.figure()
    gs = GridSpec(3, 1, height_ratios=[3, 2, 1], hspace=0)

    # Temperature Panel
    ax1 = fig.add_subplot(gs[0])
    ax1.set_xlim(1,365)

    # - quantiles
    for l, u, color in zip(["t2m_min", "t2m_10", "t2m_25"],
                           ["t2m_max", "t2m_90", "t2m_75"], 
                           quantile_colors):
        ax1.fill_between(df.index, df[l], df[u], color=color)
    ax1.plot(df.index, df["t2m_50"], color=median_color)
    # - average
    ax1.plot(df.index, df.t2m, color="tab:blue")
    ax1.axhline(0., ls="--", c="0.2", alpha=0.5)
    ax1.set_xlabel("Day of Year")
    ax1.set_ylabel(r"$^\circ\! \mathrm{C}$");

    ax1.tick_params(labelbottom = False, bottom=False)

    # Precipitation Panel
    ax2 = fig.add_subplot(gs[1], sharex=ax1)
    ax2.tick_params(labelbottom = False, bottom=False, labelleft=False, left=False)
    ax2.set_ylim(0,1)
    ax2.set_ylabel("$P(Rain)$")
    ax2.fill_between(df.index, df.p_liquid, color="0.3", alpha=0.5)

    ax2b = ax2.twinx()
    ax2b.set_ylim(1,0)
    ax2b.tick_params(labelright=False, right=False)
    ax2b.set_ylabel("$P(Solid)$", color="lightblue")
    ax2b.fill_between(df.index, df.p_solid, color="lightblue", alpha=0.5)

    # Snow on the ground panel
    ax3 = fig.add_subplot(gs[2], sharex=ax1)
    ax3.fill_between(df.sog.index, df.sog, color="0.3")
    ax3.set_ylim(0,1)
    ax3.set_ylabel("SOG (%)")
    ax3.tick_params(labelleft = False, left=False)

    # Add ticks and labels to ax3
    # - Make ticks and labels
    doy = np.cumsum([1]+[calendar.monthrange(2004, m)[1] for m in range(1,13)])
    doy[12] = doy[12]-1  # get last day of year
    doy_label = (doy[:-1] + np.roll(doy, -1)[:-1])*0.5
    # Add ticks and labels
    ax3.set_xticks(ticks=doy, labels=[], )
    ax3.set_xticks(ticks=doy_label, labels=calendar.month_abbr[1:], minor=True)
    ax3.tick_params(which='minor', length=0)
    
    # Add shading for winter on panels
    for axis in [ax1, ax2, ax3]:
        axis.axvspan(1, last_day, color=iswinter_color, zorder=0)
        axis.axvspan(first_day, 366, color=iswinter_color, zorder=0)

    if title:
        fig.suptitle(title)  #f"{station.loc[stid].station_name} ({stid})");

    return fig


def minmax_scaler(x):
    """Minmax scaler for an array or pd.Series

    Arguments
    ---------
    x : ndarray or pandas.Series of numeric type.

    Returns
    -------
    object of same type or dimensions as x but scaled by min and max 
    """
    return (x - x.min()) / (x.max() - x.min())


def heatmap(
    df: pd.DataFrame,
    country_order: bool=True,  # Make this a pd.Series of countries
    ax: plt.Axes=None,
    xlim: Tuple[dt.datetime]=(dt.datetime(1979,1,1), dt.datetime(2023,12,31)),
    norm: bool=True,
    cmap: Union[str,mpl.colormaps]="Greys",
    aspect: Union[float,str]="auto",
    cbar_kwargs: Dict=None,
) -> plt.Axes:
    """Plots a heatmap of stations.  Default is to plot in country order

    Arguments
    ---------
    df : pandas.DataFrame containing a timeseries of counts for each station
         ordered by country.
    countries : pandas.Series of countries to apply order
    ax : matplotlib.Axes instance.  If None, one is created.
    norm : if True (default) then apply minmax scaling
    cmap : colormap

    Returns
    -------
    ?
    """

    # Use this to get y-ticks from pd.Series of countries indexed
    # by station-id
    # np.insert(country.sort_values().groupby(country).count().cumsum().values, 0, 0)
    
    if not cbar_kwargs:
        cbar_kwargs = dict(
            shrink=0.5, 
            label="Observations per Month", 
            # aspect=50,
            pad=0.01,
        )
        
    # y-ticks and -ticklabels for country order plots
    yticks = [0, 53,  76,  90,  94, 120, 146, 169, 244]
    ylabels = ['CA', 'FI', 'GL', 'IS', 'NO', 'RU', 'SE', 'US']

    # Scale dataframe
    df_scl = df.apply(minmax_scaler)

    ntime, nstation = df_scl.shape

    norm = Normalize(vmin=0.001, vmax=1.)
    if not isinstance(cmap, Colormap):
        cmap = mpl.colormaps[cmap]
    cmap.set_under("none")
    
    ax.set_xlim(*xlim)
    img = ax.imshow(df_scl.T.values,
                    extent=[df_scl.index.min(), df_scl.index.max(),
                            0, nstation],
                    interpolation="none",
                    origin="lower", 
                    aspect=aspect,
                    cmap=cmap,
                    norm=norm)

    # ax.set_yticks(np.arange(nstation)+0.5, ptype_count_scl.columns, fontsize=5);
    ax.set_yticks(yticks)
    ax.set_yticklabels([])
    ax.set_yticks([(yticks[i]+yticks[i+1])*0.5 for i in range(len(yticks)-1)], minor=True)
    ax.set_yticklabels(ylabels, fontsize=20, minor=True)
    ax.tick_params('y', which="minor", length=0)
    ax.tick_params('y', which="major", length=30)

    ax.grid(which="major", axis="x")
    ax.grid(which="major", axis="y", color='black')

    ax.get_figure().colorbar(img, **cbar_kwargs);
    ax.get_figure().tight_layout()

    return ax
