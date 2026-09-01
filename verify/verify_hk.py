#!/usr/bin/env python3
"""Reproduce Section 8 from the released Hong Kong leg extract.

Tables 6 and 7 of the manuscript, rebuilt without the tick archive. The extract carries one row per
directional-change leg at each of the three pre-registered window levels, so everything downstream of
leg construction — the cells, the two-way analysis, the unity crossing and the compression slope — is
recomputed here from scratch.

    python3 verify/verify_hk.py

What this does not check is leg construction itself. For that, fetch the archive with src/dl_hk.py
and run src/hk_pipeline_english.py, which rebuilds the extract's inputs from the quotes.
"""
import sys, os
import numpy as np, pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))
import dc_pipeline as Q

CUT    = 19899                     # trading-window id of 2024-06-26, the held-back boundary
LEVELS = [('C_sub', 'sub-sessions'), ('B_day', 'regular day session'), ('A_full', 'full tradable window')]
PATH   = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'dc_legs_hkgidx.csv.gz')

D = pd.read_csv(PATH)
print(f"{len(D):,} legs across {D.level.nunique()} window levels, "
      f"{D.win.nunique():,} trading windows\n")


def crossing(bm):
    """Interpolated delta/R at which mean omega/delta passes through one."""
    x, y = bm.mid.values, bm.m.values
    for i in range(len(x) - 1):
        if (y[i] - 1) * (y[i + 1] - 1) < 0:
            return x[i] + (1 - y[i]) * (x[i + 1] - x[i]) / (y[i + 1] - y[i])
    return np.nan


def layer(name, sub):
    print("=" * 78); print(name); print("=" * 78)
    print(f"  {'window':24s}{'legs':>10}{'cells':>7}{'band effect':>16}{'crossing':>11}{'beta_C':>10}")
    out = {}
    for key, label in LEVELS:
        L = sub[sub.level == key].rename(columns={'omega_over_delta': 'wd'})
        C = Q.cells(L); R = Q.collapse(C)
        bm = R['band_means'].reset_index().rename(columns={'index': 'band'})
        bm['mid'] = [(float(b.split('-')[0]) + float(b.split('-')[1])) / 2 for b in bm.band]
        x = crossing(bm)
        print(f"  {label:24s}{len(L):>10,}{R['ncell']:>7}"
              f"{'F(%d,%d) = %.1f' % (R['df_band'][0], R['df_band'][1], R['F_band']):>16}"
              f"{x:>11.3f}{R['beta_C']:>10.3f}")
        out[key] = dict(F=R['F_band'], p=R['p_band'], monotone=R['monotone'], p_theta=R['p_theta'],
                        ss=R['ss_ratio'], wb=R['within_between'], cross=x, beta=R['beta_C'])
    print()
    for key, label in LEVELS:
        r = out[key]
        h1 = r['p'] < 0.01 and r['monotone']
        h2 = h1 and r['p_theta'] > 0.05 and r['ss'] < 0.35 and r['wb'] < 0.40
        h3 = 0.15 <= r['cross'] <= 0.30
        print(f"  {label:24s} H1 {'pass' if h1 else 'fail'} | H2 {'pass' if h2 else 'fail'}"
              f" | H3 {'pass' if h3 else 'fail'}      p_theta = {r['p_theta']:.3f}")
    ok = out['C_sub']['beta'] < out['B_day']['beta'] < out['A_full']['beta']
    print(f"\n  compression ordering, sub-session < day < full window: {'obtained' if ok else 'NOT obtained'}")
    print(f"    beta_C  sub {out['C_sub']['beta']:.3f}   day {out['B_day']['beta']:.3f}"
          f"   full {out['A_full']['beta']:.3f}\n")
    return out


layer("LAYER 2 - NEVER-INSPECTED PERIOD (Table 6)", D[D.win > CUT])
layer("LAYER 1 - FULL SAMPLE", D)
