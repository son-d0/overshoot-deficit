#!/usr/bin/env python3
"""
Reproduce the central claim of "The Overshoot Deficit" from the shipped extract.

Runs in seconds, needs no proprietary data, and prints the exact numbers that
appear in the paper. If the collapse is not in the data, this script says so.

    python verify/verify_collapse.py
"""
import numpy as np, pandas as pd
from scipy import stats
from pathlib import Path

CSV = Path(__file__).resolve().parent.parent / "data" / "dc_legs_vn30f1m.csv.gz"
EDGES = [0.05, 0.10, 0.15, 0.22, 0.32, 0.45, 0.65]   # frozen, see PREREG §4
THETAS = ["5e-04", "1e-03", "2e-03", "5e-03", "7e-03", "1e-02"]
MIN_LEGS = 60                                          # frozen, see PREREG §4

d = pd.read_csv(CSV)
d["th"] = d.theta.map(lambda t: f"{t:.0e}")
d = d[d.th.isin(THETAS)]
print(f"legs loaded: {len(d):,}   thresholds: {d.th.nunique()}   "
      f"sessions: {d.day.nunique():,}\n")

# ---------------------------------------------------------------- Figure 3
rows = []
for lo, hi in zip(EDGES, EDGES[1:]):
    for th in THETAS:
        m = (d.ratio >= lo) & (d.ratio < hi) & (d.th == th)
        if m.sum() >= MIN_LEGS:
            rows.append(dict(band=f"{lo:.2f}-{hi:.2f}", mid=(lo + hi) / 2, th=th,
                             mean=d.omega_over_delta[m].mean(), n=int(m.sum())))
c = pd.DataFrame(rows)
print("FIGURE 3 — mean omega/delta by (band, theta)")
print(c.pivot(index="band", columns="th", values="mean").round(3).to_string(), "\n")

bm = c.groupby("band").agg(mid=("mid", "first"), m=("mean", "mean")).sort_values("mid")
print("band means (the collapsed curve):")
for b, r in bm.iterrows():
    flag = "fade profitable" if r.m < 1 else "momentum"
    print(f"  {b}   omega/delta = {r.m:.3f}   {flag}")

# ---------------------------------------------------------------- ANOVA
y = c["mean"].values
X = pd.get_dummies(c[["band", "th"]], drop_first=True).astype(float)
one = np.ones((len(c), 1))
def rss(M):
    b, *_ = np.linalg.lstsq(M, y, rcond=None)
    e = y - M @ b
    return float(e @ e), M.shape[1]
Xb = np.column_stack([one] + [X[k].values for k in X if k.startswith("band")])
Xt = np.column_stack([one] + [X[k].values for k in X if k.startswith("th")])
Xf = np.column_stack([one] + [X[k].values for k in X])
rb, kb = rss(Xb); rt, kt = rss(Xt); rf, kf = rss(Xf)
df2 = len(c) - kf
Fb = ((rt - rf) / (kf - kt)) / (rf / df2)
Ft = ((rb - rf) / (kf - kb)) / (rf / df2)
pb = 1 - stats.f.cdf(Fb, kf - kt, df2)
pt = 1 - stats.f.cdf(Ft, kf - kb, df2)

print(f"\nTWO-WAY ANOVA on {len(c)} cell means")
print(f"  band | theta   F({kf-kt},{df2}) = {Fb:7.2f}   p = {pb:.3g}")
print(f"  theta | band   F({kf-kb},{df2}) = {Ft:7.2f}   p = {pt:.3f}")
print(f"  SS_theta / SS_band = {(rb-rf)/(rt-rf):.3f}")

w = c.groupby("band")["mean"].agg(["min", "max", "count"])
w["spread"] = w["max"] - w["min"]
ratio = w[w["count"] > 1]["spread"].mean() / (bm.m.max() - bm.m.min())
print(f"  within-band spread / between-band range = {ratio:.3f}")

sl, ic, rv, pv, se = stats.linregress(bm["mid"], bm["m"])
print(f"  compression slope beta_C = {sl:.3f}  (SE {se:.3f}, R2 {rv**2:.3f})")

# ---------------------------------------------------------------- verdict
print("\nPRE-REGISTERED CRITERIA (PREREG section 5.1)")
for label, val, ok in [
    ("p_band < 0.01",                        f"{pb:.2g}",              pb < 0.01),
    ("p_theta > 0.05",                       f"{pt:.3f}",              pt > 0.05),
    ("SS_theta / SS_band < 0.35",            f"{(rb-rf)/(rt-rf):.3f}", (rb-rf)/(rt-rf) < 0.35),
    ("within/between spread < 0.40",         f"{ratio:.3f}",           ratio < 0.40),
    ("monotone decreasing band means",       "-",                      bool((np.diff(bm.m) < 0).all())),
]:
    print(f"  {'PASS' if ok else 'FAIL'}  {label:38s} {val}")
