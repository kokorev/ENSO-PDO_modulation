#!/usr/bin/env python
# coding=utf-8
"""

"""
from mpl_toolkits.basemap import Basemap
import matplotlib as mpl
from matplotlib.patches import Polygon
import matplotlib.pyplot as plt
import seaborn
import numpy as np
from matplotlib.colors import ListedColormap
import common
import warnings
import pickle

warnings.filterwarnings("ignore")


class MapParameters:
    """
    Contains parameters related to plotting the maps, grid parameters, palette parameters etc
    """
    var_lats = np.linspace(-89.75, 89.75, 360)
    var_lons = np.linspace(-179.75, 179.75, 720)
    var_lons = np.array([lon if lon >= 0 else 360 + lon for lon in var_lons])
    sst_lats = np.linspace(-88, 88, 89)
    sst_lons = np.linspace(0, 358, 180)
    ymin = 1901
    ymax = 2018

    def __init__(self, sst_vmin, sst_vmax, var_vmin, var_vmax, var_n_colors, var_colors=None, sst_colors=None):
        self.sst_vmin = sst_vmin
        self.sst_vmax = sst_vmax
        self.var_vmin = var_vmin
        self.var_vmax = var_vmax
        self.var_n_colors = var_n_colors
        self.sst_cmap = self.get_sst_cmap(colors=sst_colors)
        self.var_cmap = self.get_var_cmap(colors=var_colors, n_colors=var_n_colors)
        self.sst_norm = seaborn.mpl.colors.Normalize(vmin=self.sst_vmin, vmax=self.sst_vmax)
        self.var_norm = seaborn.mpl.colors.Normalize(vmin=self.var_vmin, vmax=self.var_vmax, clip=True)

    def get_sst_cmap(self, colors=None):
        if colors is None:
            colors = ['#2166ac', '#4393c3', '#92c5de', '#d1e5f0', '#fddbc7', '#f4a582', '#d6604d', '#b2182b']
        return ListedColormap(seaborn.color_palette(colors).as_hex())

    def get_var_cmap(self, colors=None, n_colors=None):
        if n_colors is None:
            n_colors = 10
        if colors is None:
            colors = ['#8c510a', '#bf812d', '#dfc27d', '#f6e8c3', '#d9f0d3', '#a6dba0', '#5aae61', '#1b7837']
        var_pal = seaborn.color_palette(colors)
        return mpl.colors.LinearSegmentedColormap.from_list('my_tmp', var_pal, N=n_colors)


def ws_dif_map(var_ip, var_nt):
    dif = var_ip - var_nt
    is_same_sign = (var_ip * var_nt) > 0
    dif[np.logical_not(is_same_sign) & (dif > 0)] *= -1
    dif[(var_ip < 0) & (var_nt < 0)] *= -1
    return dif


def load_pickle(fn):
    with open(fn, 'rb') as f:
        return pickle.load(f)


def load_var_data(var, season_name, fig_num_1, fig_num_2, ymin, ymax, var_percent=True):
    if var is not None:
        var_data_1 = load_pickle(common.get_cache_mean_fn(var, season_name, fig_num_1, ymin=ymin, ymax=ymax, percents=var_percent))
        var_data_2 = load_pickle(common.get_cache_mean_fn(var, season_name, fig_num_2, ymin=ymin, ymax=ymax, percents=var_percent))
    else:
        var_data_1, var_data_2 = None, None
    return var_data_1, var_data_2


def add_grided_data_to_map(m, ax, data, lats, lons, ms, vmin, vmax, cmap):
    sst_norm = seaborn.mpl.colors.Normalize(vmin=vmin, vmax=vmax)
    for ilat, lat in enumerate(lats):
        for ilon, lon in enumerate(lons):
            if not (common.lat_bounds[0] < lat < common.lat_bounds[1] and common.lon_bounds[0] < lon < common.lon_bounds[1]):
                continue
            val = data[ilat, ilon]
            if np.ma.is_masked(val) or np.isnan(val):
                continue
            cors = list(zip(*m([lon - ms, lon - ms, lon + ms, lon + ms],
                               [lat - ms, lat + ms, lat + ms, lat - ms])))
            n_val = val if val <= vmax else vmax
            n_val = n_val if n_val >= vmin else vmin
            point_color = cmap(sst_norm(n_val))
            poly = Polygon(cors, facecolor=point_color, edgecolor=point_color)
            ax.add_patch(poly)
    return ax


def plot_map_on_ax(ax, var_data, sst_data, map_parameters):
    mp = map_parameters
    var_ms = abs(mp.var_lats[1] - mp.var_lats[0]) / 2.
    sst_ms = abs(mp.sst_lats[1] - mp.sst_lats[0]) / 2.
    m = Basemap(projection='laea', llcrnrlon=common.lon_bounds[0], llcrnrlat=common.lat_bounds[0], urcrnrlon=common.lon_bounds[1],
                urcrnrlat=common.lat_bounds[1], lat_ts=0, lat_0=0, lon_0=130, resolution='i', ax=ax)
    m.drawmapboundary(fill_color='white', linewidth=.2)
    m.drawcoastlines(linewidth=.2)
    if sst_data is not None:
        ax = add_grided_data_to_map(m, ax, sst_data, mp.sst_lats, mp.sst_lons, sst_ms, mp.sst_vmin, mp.sst_vmax, mp.sst_cmap)
    if var_data is not None:
        ax = add_grided_data_to_map(m, ax, var_data, mp.var_lats, mp.var_lons, var_ms, mp.var_vmin, mp.var_vmax, mp.var_cmap)
    return ax


def plot_large_fig(var, sst_var, season_name, fig_num_1, fig_num_2, fn, map_parameters, font_size=20, var_pecent=True, var_units=None):
    mp = map_parameters
    var_data_1, var_data_2 = load_var_data(var, season_name, fig_num_1, fig_num_2, mp.ymin, mp.ymax, var_percent=var_pecent)
    sst_data_1, sst_data_2 = load_var_data(sst_var, season_name, fig_num_1, fig_num_2, mp.ymin, mp.ymax, var_percent=False)
    fig, (ax0, ax1, ax2, ax3, ax4) = plt.subplots(nrows=5, ncols=1, gridspec_kw={'height_ratios': [8, 8, 8, 1, 1]}, dpi=300, figsize=(10, 20))
    plot_map_on_ax(ax0, var_data_1, sst_data_1, mp)
    ax0.set_ylabel('PDO %s' % common.pdo_sign_text[common.figures_parameters[fig_num_1 - 1][1]], fontsize=font_size)
    ax0.set_title('%s, Nino 3.4 %s' % (season_name, common.nino_sign_text[common.figures_parameters[fig_num_1 - 1][0]]), fontsize=font_size)
    plot_map_on_ax(ax1, var_data_2, sst_data_2, mp)
    ax1.set_ylabel('PDO %s' % common.pdo_sign_text[common.figures_parameters[fig_num_2 - 1][1]], fontsize=font_size)
    var_dif = var_data_1-var_data_2 if var is not None else None
    sst_dif = sst_data_1-sst_data_2 if sst_var is not None else None
    plot_map_on_ax(ax2, var_dif, sst_dif, mp)
    ax2.set_ylabel('Difference', fontsize=font_size)
    mpl.colorbar.ColorbarBase(ax3, cmap=mp.sst_cmap, norm=mp.sst_norm, orientation='horizontal')
    ax3.set_title('SST anomaly, °C', fontsize=font_size)
    mpl.colorbar.ColorbarBase(ax4, cmap=mp.var_cmap, norm=mp.var_norm, orientation='horizontal', ticks=np.linspace(mp.var_vmin, mp.var_vmax, mp.var_n_colors + 1))
    ax4.set_title('{} anomaly, {}'.format(var, '% of norm' if var_pecent else var_units), fontsize=font_size)
    plt.tight_layout()
    plt.savefig(fn)
    plt.close()


def plot_ws_map(var, sst_var, fig_num_1, fig_num_2, fn, mp, var_pecent=True):
    fig, axs = plt.subplots(nrows=2, ncols=2, dpi=300, figsize=(20, 15))
    for seas, ax in zip([v[0] for v in common.seasons], axs.flatten()):
        try:
            var_data_1, var_data_2 = load_var_data(var, seas, fig_num_1, fig_num_2, mp.ymin, mp.ymax, var_percent=var_pecent)
            sst_data_1, sst_data_2 = load_var_data(sst_var, seas, fig_num_1, fig_num_2, mp.ymin, mp.ymax, var_percent=False)
        except FileNotFoundError:
            continue
        wsd_var = ws_dif_map(var_data_1, var_data_2) if var is not None else None
        wsd_sst = ws_dif_map(sst_data_1, sst_data_2) if sst_var is not None else None
        plot_map_on_ax(ax, wsd_var, wsd_sst, mp)
        ax.set_title('%s, Nino 3.4 %s' % (seas, common.nino_sign_text[common.figures_parameters[fig_num_1 - 1][0]]), fontsize=20)
    plt.tight_layout()
    plt.savefig(fn)
    plt.close()


if __name__ == '__main__':
    var = 'tmp'
    sst_var = 'sst'
    var_vmin = -10
    var_vmax = 10

    mp = MapParameters(-1, 1, var_vmin, var_vmax, var_n_colors=20)
    plot_ws_map(var, sst_var, 9, 6, './figures/%s/ws_9-6.pdf' % var, mp)
    plot_ws_map(var, sst_var, 1, 4, './figures/%s/ws_1-4.pdf' % var, mp)
    for fig_num_1, fig_num_2 in ((9, 6), (1, 4)):
        for season_name, smonths in common.seasons:
            fn = './figures/%s/%s_%i-%i.pdf' % (var, season_name, fig_num_1, fig_num_2)
            plot_large_fig(var, sst_var, season_name, fig_num_1, fig_num_2, fn, mp)
            print(fn)
