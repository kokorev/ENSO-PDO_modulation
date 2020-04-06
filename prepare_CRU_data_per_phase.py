#!/usr/bin/env python
# coding=utf-8
"""

"""


def get_season_mask_from_dti(dti, season_months):
    mask = None
    for m in season_months:
        if mask is None:
            mask = dti.month == m
        else:
            mask = mask | (dti.month == m)
    return mask


def select_seasonal_from_index_data(index_data, season_months):
    mask = get_season_mask_from_dti(index_data.index, season_months)
    return index_data[mask]


def select_seasonal_from_var(ncvar, dti, season_months):
    mask = get_season_mask_from_dti(dti, season_months)
    return ncvar[mask, :, :]


def anoms(dat, dti):
    res = np.empty(dat.shape)
    for month in range(1, 13):
        n = dat[dti.month == month, :, :].mean(axis=0)
        mv = dat[dti.month == month, :, :]
        mr = mv - n
        res[dti.month == month, :, :] = mr
    return np.ma.masked_less(res, -9999)


if __name__ == '__main__':
    import os
    import pickle
    import common
    from common import get_pdo, get_nino34, get_idx_mask
    import numpy as np
    import netCDF4
    import datetime
    import pandas as pd


    # prepare index data
    nino = get_nino34()
    pdo = get_pdo()
    index_data = pd.DataFrame({'pdo': pdo, 'nino': nino})
    index_data = index_data.dropna()
    index_data = index_data[(index_data.index.year >= common.y_min) * (index_data.index.year <= common.y_max)]
    index_data['idx'] = pd.Series(data=range(len(index_data.index)), index=index_data.index)

    for var in ('pre', 'wet', 'tmp', 'dtr'):
        var_fn = 'cru_ts4.03.1901.2018.%s.dat.nc' % var
        # read var data
        fn = os.path.join(common.data_path, var_fn)
        nc = netCDF4.Dataset(fn, 'r')
        lats = np.array(nc.variables['lat'][:])
        lons = np.array(nc.variables['lon'][:])
        dates = netCDF4.num2date(nc.variables['time'][:], nc.variables['time'].units)
        dates = [datetime.datetime(d.year, d.month, 1) for d in dates]
        dti = pd.DatetimeIndex(dates)

        var_arr = np.array(nc.variables[var][:, :, :])
        var_arr[var_arr > 99999] = np.nan

        # for each phase
        for season_name, smonths, nino_sign, pdo_sign, fig_num in common.ensopdo_combinations_generator():
            # use only data for months is this season
            index_data_season = select_seasonal_from_index_data(index_data, smonths)
            try:
                with open(common.get_cache_mean_fn(var, season_name, fig_num), 'rb') as f:
                    res_mean = pickle.load(f)
                with open(common.get_cache_mean_fn(var, season_name, fig_num, percents=True), 'rb') as f:
                    res_prcnt = pickle.load(f)
            except FileNotFoundError:
                # use only data for specific phase
                mask = get_idx_mask(index_data_season, 'nino', nino_sign, common.nino_th) & get_idx_mask(index_data_season, 'pdo', pdo_sign, common.pdo_th)
                idx = index_data_season[mask]['idx'].values
                if len(idx) == 0:
                    print('skipped', season_name, smonths, nino_sign, pdo_sign, fig_num)
                    continue
                selected_values = var_arr[idx, :, :]
                res_mean = selected_values.mean(axis=0)
                norm = select_seasonal_from_var(var_arr, dti, smonths).mean(axis=0)
                res_prcnt = res_mean / (0.01 * norm)
                res_prcnt -= 100
                # selected_prcnt = selected_values / res_prcnt
                with open(common.get_cache_mean_fn(var, season_name, fig_num), 'wb') as f:
                    pickle.dump(res_mean, f)
                with open(common.get_cache_mean_fn(var, season_name, fig_num, percents=True), 'wb') as f:
                    pickle.dump(res_prcnt, f)
