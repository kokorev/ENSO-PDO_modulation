#!/usr/bin/env python
# coding=utf-8
"""

"""


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    import pandas as pd
    import numpy as np
    import common

    common.y_min = 1981
    common.y_max = 2017
    # prepare index data
    nino = common.get_nino34_daily()
    pdo = common.get_pdo()
    pdo = pdo.resample('d').bfill()
    dat = pd.DataFrame({'pdo': pdo, 'nino': nino})
    nino_th = common.nino_th
    pdo_th = common.pdo_th
    dat = dat[(dat.index.year >= common.y_min) * (dat.index.year <= common.y_max)]
    dat = dat.dropna()
    dat['2pos'] = (dat['pdo'] > pdo_th) & (dat['nino'] > nino_th)
    dat['2neg'] = (dat['pdo'] < -pdo_th) & (dat['nino'] < -nino_th)
    dat['p+e-'] = (dat['pdo'] > pdo_th) & (dat['nino'] < -nino_th)
    dat['p-e+'] = (dat['pdo'] < -pdo_th) & (dat['nino'] > nino_th)
    dat['counter_phase'] = dat['p+e-'] | dat['p-e+']

    nino_count = (nino > 1).groupby(nino.index.year).sum()
    pdo_count = (pdo > 1).groupby(pdo.index.year).sum()
    dat_count = pd.DataFrame({'pdo': pdo_count, 'nino': nino_count})

    font_size = 30

    #plot montly hist for each of the 9 events
    fig, axs = plt.subplots(nrows=3, ncols=3, dpi=300, figsize=(20, 20))
    inds_order = [7, 8, 9, 4, 5, 6, 1, 2, 3]
    x_labels = {1: 'ESNO < -%3.2f' % nino_th, 2: 'ENSO neutral', 3: 'ESNO > %3.2f' % nino_th}
    y_labels = {1: 'PDO < -%2.1f' % pdo_th, 4: 'PDO neutral', 7: 'PDO > %2.1f' % pdo_th}
    flat_axs = axs.flatten()
    for fig_ind, ax in zip(inds_order, flat_axs):
        nino_sign, pdo_sign, fig_num = common.figures_parameters[fig_ind - 1]
        mask = common.get_idx_mask(dat, 'nino', nino_sign, nino_th) & common.get_idx_mask(dat, 'pdo', pdo_sign, pdo_th)
        hist_vals = dat['nino'][mask].groupby(dat['nino'][mask].index.month).count()
        hv = pd.Series(hist_vals, index=np.arange(1, 13)).fillna(0)
        seas_count = {sn: sum([hv[mn] for mn in mns]) for sn, mns in common.seasons}
        ylimmax = 350 if not fig_ind == 5 else 600
        text_pad = 80 if not fig_ind == 5 else 135
        ax.bar(hv.index, hv.values, color='#4286f4')
        ax.set_xlim((0.4, 12.6))
        ax.set_ylim((0, ylimmax))
        ax.tick_params(axis='both', labelsize=16, pad=12)
        ax.tick_params(axis='both', which='major', length=10, width=2)
        ax.grid(axis='y')
        sesons_info = '\n'.join(['%s - %i' % (sn, seas_count[sn]) for sn in seas_count])
        ax.text(1, ylimmax - text_pad, sesons_info, fontsize=20)
        if fig_ind in x_labels:
            ax.set_xlabel(x_labels[fig_ind], fontsize=font_size, labelpad=20)
        if fig_ind in y_labels:
            ax.set_ylabel(y_labels[fig_ind], fontsize=font_size, labelpad=20)
    plt.tight_layout()
    plt.savefig('./figures/phase_histogram_daily.pdf')
