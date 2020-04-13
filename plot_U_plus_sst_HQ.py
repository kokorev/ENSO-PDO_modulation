#!/usr/bin/env python
# coding=utf-8
"""

"""

if __name__ == '__main__':
    import numpy as np
    import common
    from plot_var_plus_sst import MapParameters, plot_large_fig, plot_ws_map

    var = 'U'
    sst_var = None
    var_vmin = -5
    var_vmax = 5

    mp = MapParameters(-1, 1, var_vmin, var_vmax, var_n_colors=10)
    mp.var_lats = np.linspace(-90, 90, 361)
    mp.var_lons = np.linspace(0, 359, 720)
    mp.sst_lats = np.linspace(-24.875, 24.875, 200)
    mp.sst_lons = np.linspace(80.125, 179.875, 400)
    mp.ymin = 1981
    mp.ymax = 2017

    plot_ws_map(var, sst_var, 9, 6, './figures/%s/ws_9-6.pdf' % var, mp, var_pecent=False)
    plot_ws_map(var, sst_var, 1, 4, './figures/%s/ws_1-4.pdf' % var, mp, var_pecent=False)
    for fig_num_1, fig_num_2 in ((9, 6), (1, 4)):
        for season_name, smonths in common.seasons:
            fn = './figures/%s/%s_%i-%i.pdf' % (var, season_name, fig_num_1, fig_num_2)
            try:
                plot_large_fig(var, sst_var, season_name, fig_num_1, fig_num_2, fn, mp, var_pecent=False, var_units='m/s')
            except FileNotFoundError:
                print('skipped', fn)
                continue
            print('done', fn)

