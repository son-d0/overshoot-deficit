"""The exploratory adaptive-threshold probe reported in the opening paragraph of Section 7.

Section 4 identifies delta measured against the session's realised range as the indexing variable,
which suggests setting the threshold each day so that delta is a fixed fraction of that range. The
range of the day in progress is not known, but it can be estimated causally from sessions already
finished. This script does that and compares the result against fixed thresholds.

    delta_d = ratio * Rhat_d,   Rhat_d = median realised range of the previous 20 sessions

Rhat is built with .shift(1) before .rolling(20), so no session contributes to its own estimate.

WHAT THIS SCRIPT IS FOR. It is the provenance of four numbers in Section 7: gross per turnover unit
of 0.657 for the adaptive rule against 1.242 for the fixed threshold, Sharpe of 2.00 against 2.59,
and a maximum drawdown that roughly doubles, 300 against 154. Those numbers are auditable rather
than publicly reproducible: the transformation is here to be read, but the tick panel it consumes is
a licensed series we are not free to redistribute. See records/S128_PROVENANCE.md for the hashes of
the exact inputs, the command, and the output as it was produced.

This is a standalone rewrite of the internal script that produced those figures. It computes the
same quantities from the same panel and depends on nothing outside this repository except the panel
itself. It was checked against the original: identical output on every row.

    python3 src/adaptive_threshold_probe.py path/to/panel.npz
"""
import os, sys, warnings
PANEL = sys.argv[1] if len(sys.argv) > 1 else 'panel.npz'
if not os.path.exists(PANEL):
    sys.exit(
        f"This script needs the VN30F1M tick panel ({PANEL}), which is not distributed: it is a\n"
        "licensed series. It ships so the transformation behind the Section 7 figures can be read\n"
        "and checked. The hashes, the command and the exact output are in\n"
        "records/S128_PROVENANCE.md. Installing further packages will not change this.")

import numpy as np, pandas as pd
warnings.filterwarnings('ignore')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import costs
from dcevent import events

SPEC_SESSIONS = 819                      # the specification window, 2 Jan 2023 to 24 Apr 2026
ENTRY_FROM    = 585                      # 09:45, in minutes past midnight
DEFAULT_STOP  = 885                      # 14:45
MIN_TICKS     = 600                      # sessions thinner than this are skipped

d    = np.load(PANEL)
P    = d['last'].astype(np.float64)
DAY  = d['day']
TI   = d['time_int']
n    = len(P)
assert TI.max() > 10_000_000, 'time_int must carry eight digits'

ud, dayid = np.unique(DAY, return_inverse=True)
ND, YR    = len(ud), ud // 10000
mins      = (TI // 10000 % 100) * 60 + (TI // 100 % 100)
C         = costs.leg('live')

hi = np.full(ND, -1e18); lo = np.full(ND, 1e18)
np.maximum.at(hi, dayid, P); np.minimum.at(lo, dayid, P)
RNG  = hi - lo
Rhat = pd.Series(RNG).shift(1).rolling(20, min_periods=10).median().to_numpy()   # causal

start = np.searchsorted(dayid, np.arange(ND))
end   = np.append(start[1:], n)


def run(ratio=None, fixed=None, cutoff=DEFAULT_STOP):
    """Fade the confirmed direction, one session at a time, at a fixed or an adaptive threshold."""
    dg = np.zeros(ND); dt = np.zeros(ND); nl = 0
    for i in range(ND):
        a, b = start[i], end[i]
        if b - a < MIN_TICKS:
            continue
        pr, tm = P[a:b], mins[a:b]
        th = fixed if fixed is not None else (
             ratio * Rhat[i] / pr[0] if np.isfinite(Rhat[i]) else np.nan)
        if not np.isfinite(th) or th <= 0:
            continue

        E = events(pr, float(th))
        ie, ip, ic, dr = E['i_ext'], E['i_ext_prev'], E['i_conf'], E['dirn']
        if len(ie) < 2:
            continue

        ok = (ie > ip) & (ic < len(pr) - 1)
        ie, ip, ic, dr = [x[ok] for x in (ie, ip, ic, dr)]

        # the confirmation that opens the leg is the previous leg's confirmation
        dcc = np.concatenate(([-1], ic[:-1]))
        v = (dcc > ip) & (dcc < ie); v[0] = False
        ie, ip, ic, dr, dcc = [x[v] for x in (ie, ip, ic, dr, dcc)]

        k = (tm[dcc] >= ENTRY_FROM) & (tm[dcc] < cutoff) & (tm[ic] < DEFAULT_STOP)
        if k.sum() == 0:
            continue

        pnl   = (-dr[k]) * (pr[ic[k]] - pr[dcc[k] + 1])       # enter one tick after confirmation
        dg[i] = pnl.sum()
        dt[i] = 2.0 * k.sum()                                  # a round trip is two legs
        nl   += int(k.sum())

    m = YR >= 2023
    s = (dg - dt * C)[m]
    if dt[m].sum() < 100:
        return None
    eq = np.cumsum(s)
    yb = pd.Series(dg - dt * C).groupby(YR).sum(); yb = yb[yb.index >= 2023]
    return dict(nl=nl, tpd=dt[m].sum() / SPEC_SESSIONS / 2,
                gpt=dg[m].sum() / dt[m].sum(), net=s.sum(),
                sr=s.mean() / s.std() * np.sqrt(252) if s.std() > 0 else 0,
                mdd=float(np.max(np.maximum.accumulate(eq) - eq)),
                yrs=int((yb > 0).sum()), yb=yb)


def show(name, r):
    if r is None:
        print(f"  {name:40s} too few trades"); return
    print(f"  {name:40s}{r['nl']:>7d}{r['tpd']:>10.2f}{r['gpt']:>12.3f}{r['net']:>8.0f}"
          f"{r['sr']:>7.2f}{r['mdd']:>7.0f}{r['yrs']:>4}/4  "
          + " ".join(f"{v:+5.0f}" for v in r['yb'].values))


print(f"cost {C}/leg | entries after 09:45\n")
print(f"  {'':40s}{'legs':>7}{'legs/day':>10}{'gross/turn':>12}{'net':>8}{'SR':>7}{'MDD':>7}{'yrs+':>6}  by year")
print("  --- FIXED theta (baseline) ---")
for th in (5e-3, 7e-3, 1e-2):
    show(f"fixed theta = {th:.0e}", run(fixed=th))
print("  --- ADAPTIVE theta: delta = ratio x trailing 20-session range ---")
for ra in (0.25, 0.35, 0.45, 0.55):
    show(f"delta = {ra:.2f} x Rhat  (causal)", run(ratio=ra))
print("  --- adaptive theta, no new entries after 14:15 ---")
for ra in (0.35, 0.45, 0.55):
    show(f"delta = {ra:.2f} x Rhat, stop 14:15", run(ratio=ra, cutoff=855))
