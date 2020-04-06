#!/usr/bin/env python
# coding=utf-8
"""

"""

if __name__ == '__main__':
    import numpy as np
    import common
    from plot_var_plus_sst import MapParameters, plot_large_fig, plot_ws_map

    var = 'rr'
    sst_var = 'sstHR'
    var_vmin = -30
    var_vmax = 30

    mp = MapParameters(-1, 1, var_vmin, var_vmax, var_n_colors=20)
    mp.var_lats = np.linspace(-24.875, 25.125, 201)
    mp.var_lons = np.linspace(80.125, 179.875, 400)
    mp.sst_lats = np.linspace(-24.875, 24.875, 200)
    mp.sst_lons = np.linspace(80.125, 179.875, 400)
    mp.ymin = 1981
    mp.ymax = 2017

    plot_ws_map(var, sst_var, 9, 6, './figures/%s/ws_9-6.pdf' % var, mp)
    plot_ws_map(var, sst_var, 1, 4, './figures/%s/ws_1-4.pdf' % var, mp)
    for fig_num_1, fig_num_2 in ((9, 6), (1, 4)):
        for season_name, smonths in common.seasons:
            fn = './figures/%s/%s_%i-%i.pdf' % (var, season_name, fig_num_1, fig_num_2)
            try:
                plot_large_fig(var, sst_var, season_name, fig_num_1, fig_num_2, fn, mp)
            except FileNotFoundError:
                print('skipped', fn)
                continue
            print('done', fn)

