#!/usr/bin/env python
# coding=utf-8
"""
functions and variables used by multiple scripts in enso_pdo_mapping
"""
import netCDF4
import numpy as np
import os
import pandas as pd

figures_parameters = [['-', '-', 1], ['n', '-', 2], ['+', '-', 3],
                      ['-', 'n', 4], ['n', 'n', 5], ['+', 'n', 6],
                      ['-', '+', 7], ['n', '+', 8], ['+', '+', 9]]

nino_sign_text = {'+': 'Positive (>0.75)', 'n': 'Neutral [-0.75, 0.75]', '-': 'Negative (<-0.75)'}
pdo_sign_text = {'+': 'Positive (>1)', 'n': 'Neutral [-1, 1]', '-': 'Negative (<1)'}

dry_wet_pallete = ['#8c510a', '#bf812d', '#dfc27d', '#f6e8c3', '#c7eae5', '#80cdc1', '#35978f', '#01665e']
hot_cold_pallete = ['#b2182b', '#d6604d', '#f4a582', '#fddbc7', '#d1e5f0', '#92c5de', '#4393c3', '#2166ac']

seasons = (
    ('JJA', [6, 7, 8]),
    ('SON', [9, 10, 11]),
    ('DJF', [12, 1, 2]),
    ('MAM', [3, 4, 5])
)

nino_th = 0.75
pdo_th = 1
y_min = 1901
y_max = 2018

lat_bounds = [-25, 25]
lon_bounds = [80, 180]

data_path = r'./data'
home = os.getcwd()


def get_fn(var, ses, fign, ymin=y_min, ymax=y_max):
    nino_sign, pdo_sign = figures_parameters[fign-1][:2]
    fn = '%s_anoms_norm%i-%i_%s_%i(enso%s_pdo%s)' % (var, ymin, ymax, ses, fign, nino_sign, pdo_sign)
    return fn


def get_cache_mean_fn(var, ses, fign, percents=False, ymin=y_min, ymax=y_max):
    percent_prefix = 'prcnt_' if percents else ''
    fn = os.path.join(home, 'pickle_cache', percent_prefix + get_fn(var, ses, fign, ymin, ymax) + '.pickle')
    return fn

def get_cache_selected_fn(var, ses, fign, percents=False):
    percent_prefix = 'prcnt_' if percents else ''
    fn = os.path.join(home, 'pickle_cache', percent_prefix + 'selected_' + get_fn(var, ses, fign) + '.pickle')
    return fn


def get_norm_from_nc(var, ses):
    nc = netCDF4.Dataset(os.path.join(data_path, '%s_seas_norms.nc' % var), 'r')
    seasons = ['DJF', 'MAM', 'JJA', 'SON']
    ses_n = seasons.index(ses)
    norm = np.array(nc.variables[var][ses_n, :, :])
    nc.close()
    return norm


def get_nino34(fn=os.path.join(data_path, 'iersst_nino3.4a_rel.dat')):
    nino = pd.read_table(fn, comment='#', sep='\s+', header=None)[1]
    nino.index = pd.DatetimeIndex(pd.date_range(start='1854-01-15', end='2020-03-15', freq='M'))
    return nino


def get_pdo(fn=os.path.join(data_path, 'ipdo.dat')):
    pdo = pd.read_table(fn, comment='#', sep='\s+', header=None)[1]
    pdo.index = pd.DatetimeIndex(pd.date_range(start='1900-01-15', end='2020-02-15', freq='M'))
    return pdo


def get_nino34_daily(fn=os.path.join(data_path, 'inino34_daily.dat')):
    nino = pd.read_table(fn, comment='#', sep='\s+', header=None)[1]
    nino.index = pd.DatetimeIndex(pd.date_range(start='1981-09-01', end='2020-04-02', freq='d'))
    return nino


def get_idx_mask(dat, el, sign, thold):
    if sign == 'n':
        mask = (dat[el] >= -thold) & (dat[el] <= thold)
    elif sign == '+':
        mask = dat[el] > thold
    elif sign == '-':
        mask = dat[el] < -thold
    return mask


def ensopdo_combinations_generator():
    for season_name, smonths in seasons:
        for nino_sign, pdo_sign, fig_num in figures_parameters:
            yield season_name, smonths, nino_sign, pdo_sign, fig_num