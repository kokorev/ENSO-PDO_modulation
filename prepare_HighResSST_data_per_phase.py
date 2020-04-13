#!/usr/bin/env python
# coding=utf-8
"""

"""

def get_year_mean(year, days, path, llbox=[80, 180, -25, 25], var='anom'):
    fn = os.path.join(path, 'sst.day.anom.%i.nc' % year)
    nc = netCDF4.Dataset(fn, 'r')
    lats = np.array(nc.variables['lat'][:])
    lons = np.array(nc.variables['lon'][:])
    dates = netCDF4.num2date(nc.variables['time'][:], nc.variables['time'].units)
    # dates = [datetime.datetime(d.year, d.month, 1) for d in dates]
    dti = pd.DatetimeIndex(dates)
    if llbox is None:
        sst = nc.variables[var][dti.dayofyear.isin(days), :, :].mean(axis=0)
    else:
        try:
            sst = nc.variables[var][dti.dayofyear.isin(days), (lats > llbox[2]) & (lats < llbox[3]), (lons > llbox[0]) & (lons < llbox[1])].mean(axis=0)
        except IndexError:
            pass
    return sst


if __name__ == '__main__':
    import pandas as pd
    import os
    import netCDF4
    import numpy as np
    import pickle
    import common
    from prepare_CRU_data_per_phase import select_seasonal_from_index_data
    import datetime

    data_home = r'D:\data\noaa.oisst.v2.highres'

    common.y_min = 1981
    common.y_max = 2017

    var = 'sstHR'

    # prepare index data
    nino = common.get_nino34_daily()
    pdo = common.get_pdo()
    pdo = pdo.resample('d').bfill()
    index_data = pd.DataFrame({'pdo': pdo, 'nino': nino})
    index_data = index_data.dropna()
    index_data['idx'] = pd.Series(data=range(len(index_data.index)), index=index_data.index)
    index_data = index_data[index_data.index >= datetime.datetime(1981, 9, 1)]
    index_data = index_data[(index_data.index.year >= common.y_min) * (index_data.index.year <= common.y_max)]

    for season_name, smonths, nino_sign, pdo_sign, fig_num in common.ensopdo_combinations_generator():
        index_data_season = select_seasonal_from_index_data(index_data, smonths)

        try:
            with open(common.get_cache_mean_fn('sstHR', season_name, fig_num, ymin=1981, ymax=2017), 'rb') as f:
                res_mean = pickle.load(f)
        except FileNotFoundError:
            mask = common.get_idx_mask(index_data_season, 'nino', nino_sign, common.nino_th) & \
                   common.get_idx_mask(index_data_season, 'pdo', pdo_sign, common.pdo_th)

            seldates = mask.index[mask]
            if len(seldates) == 0:
                continue
            years = seldates.year.unique()
            sst_anom_sum = np.zeros((200, 400))
            for y in years:
                days = seldates[seldates.year == y].dayofyear
                year_mean = get_year_mean(y, days, path=data_home)
                sst_anom_sum += year_mean
            sst_anom_sum[year_mean.mask] = np.nan
            sst_dat = sst_anom_sum / len(years)
            with open(common.get_cache_mean_fn('sstHR', season_name, fig_num, ymin=1981, ymax=2017), 'wb') as f:
                pickle.dump(sst_dat, f)
