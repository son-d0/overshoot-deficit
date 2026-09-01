#!/usr/bin/env python3
"""Reproduce Figure 1 and the out-of-sample test of Section 5 from the released extract.

Two claims are checked here, both from data/dc_legs_vn30f1m.csv.gz alone.

Figure 1. Mean total movement against threshold. A random walk obeying the GDO relation gives
<TMV> = 2, and TMV per leg is 1 + omega/delta, so the released ratios rebuild the whole curve.

Section 5. The relation was fitted on sessions through 24 April 2026 and then confronted with the 85
that follow, which were withheld from all model development. The manuscript reports a prediction of
0.735 against a realised 0.737, and a second, unfavourable prediction: that the widest threshold
would nearly stop firing.

    python3 verify/verify_oos.py
"""
import os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))
import dc_pipeline as Q

SPLIT = 20260424        # last session of the specification window
D = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             '..', 'data', 'dc_legs_vn30f1m.csv.gz'))

print("FIGURE 1 - mean total movement against threshold")
print("  TMV per leg is 1 + omega/delta; the GDO relation puts a random walk at 2.\n")
tmv = {}
for th, g in D.groupby('theta'):
    tmv[th] = 1 + g.omega_over_delta.mean()
    print(f"    theta = {th:.0e}   <TMV> = {tmv[th]:.3f}")
ths = np.array(sorted(tmv)); vals = np.array([tmv[t] for t in ths])
lo = np.where(vals > 2)[0][-1]
cross = np.exp(np.interp(2.0, [vals[lo + 1], vals[lo]], [np.log(ths[lo + 1]), np.log(ths[lo])]))
print(f"\n    crossing of <TMV> = 2 at theta = {cross*100:.2f}%        (manuscript: 0.50%)")

D6 = D[np.isclose(D.theta.values[:, None], Q.THETAS).any(1)]
spec, ev = D6[D6.day <= SPLIT], D6[D6.day > SPLIT]

print("\n\nSECTION 5 - the withheld window")
print(f"    sessions after {SPLIT}                       {ev.day.nunique():>10}"
      f"        (manuscript: 85)")

band = spec[(spec.ratio >= 0.32) & (spec.ratio < 0.45)]
pred = band.omega_over_delta.mean()
w    = ev[np.isclose(ev.theta, 5e-3)]
real = w.omega_over_delta.mean()
print(f"    predicted <omega>/delta, band 0.32-0.45      {pred:>10.3f}        (manuscript: 0.735)")
print(f"    realised, theta = 0.5% on withheld sessions  {real:>10.3f}        (manuscript: 0.737)")
print(f"      that window's legs sit at median delta/R   {w.ratio.median():>10.3f}"
      f"        (inside 0.32-0.45)")
print(f"      legs behind the realised figure            {len(w):>10}")
print(f"    absolute error                               {abs(real-pred):>10.3f}"
      f"        (manuscript: 0.003)")

n1 = int((np.isclose(ev.theta, 1e-2)).sum())
print(f"\n    the unfavourable prediction: at theta = 1% the rule should almost cease to fire")
print(f"    legs at theta = 1% in 85 sessions            {n1:>10}"
      f"        (manuscript: seven)")

ok = (abs(pred - 0.735) < 0.001 and abs(real - 0.737) < 0.001
      and ev.day.nunique() == 85 and n1 == 7 and abs(cross - 0.005) < 0.0003)
print("\n" + ("  ALL FIVE REPRODUCE" if ok else "  MISMATCH - see the lines above"))
