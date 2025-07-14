"""Plotting routines"""

import pandas as pd

import matplotlib.pyplot as plt


def plot_climatology(df: pd.DataFrame, title: str=''):
    """Generate a climatology plot"""

    iswinter_color = "0.9"

    quantile_colors = ["0.75", "0.5", "0.25"]
    median_color = "k"
    tavg_color = "tab:blue"

    fig = plt.figure()
    gs = GridSpec(3, 1, height_ratios=[3, 2, 1], hspace=0)

    # Temperature Panel
    ax1 = fig.add_subplot(gs[0])
    ax1.set_xlim(0,365)

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
    ax2.fill_between(df.index, dfp_liquid, color="0.3", alpha=0.5)

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

    # Add shading for winter on panels
    for axis in [ax1, ax2, ax3]:
        axis.axvspan(1, last_day, color=iswinter_color, zorder=0)
        axis.axvspan(first_day, 366, color=iswinter_color, zorder=0)

    if title:
        fig.suptitle(title)  #f"{station.loc[stid].station_name} ({stid})");

