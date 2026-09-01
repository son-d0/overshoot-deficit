"""Build the public extract: dimensionless quantities only.

No column permits recovery of a price level. Delta, overshoot, retrace and the session
range are withheld, because delta = theta * price would reconstruct the underlying
series; only the ratios are published. That is enough to rebuild Figure 3, the two-way
analysis, the compression slope and the unity crossing."""

import os as _os, sys as _sys
if not _os.path.exists('panel2.npz'):
    _sys.exit(
        "This script needs panel2.npz, the VN30F1M one-second tick panel, which is not distributed.\n"
        "It is a licensed series and no derivative permitting price reconstruction is\n"
        "redistributable. The script ships so the method can be read and checked line by\n"
        "line; what it produced is recorded under records/. See README, 'What each script\n"
        "needs'. Installing further packages will not change this.")
import numpy as np, pandas as pd, sys, os, warnings; warnings.filterwarnings('ignore')
sys.path.insert(0,'.')
from dcevent import events_by_group
z=np.load('panel2.npz'); P=z['last'].astype(np.float64); DAY=z['day']; n=len(P)
ud,dayid=np.unique(DAY,return_inverse=True); ND=len(ud)
hi=np.full(ND,-1e18); lo=np.full(ND,1e18)
np.maximum.at(hi,dayid,P); np.minimum.at(lo,dayid,P); RNG=hi-lo
out=[]
for TH in (2e-4,5e-4,1e-3,2e-3,5e-3,7e-3,1e-2):
    E=events_by_group(P,DAY,TH)
    ie,ip,ic,dr=E['i_ext'],E['i_ext_prev'],E['i_conf'],E['dirn']
    ok=(ie>ip)&(ic<n-1)&(DAY[ip]==DAY[ic]); ie,ip,ic,dr=[x[ok] for x in (ie,ip,ic,dr)]
    dcc=np.concatenate(([-1],ic[:-1])); v=(dcc>ip)&(dcc<ie); v[0]=False
    ie,ip,ic,dr,dcc=[x[v] for x in (ie,ip,ic,dr,dcc)]
    d=TH*np.abs(P[ie])                                   # delta: used as a divisor, never written out
    out.append(pd.DataFrame(dict(
        theta=TH, day=DAY[ie], dirn=dr,
        ratio=d/RNG[dayid[ie]],                          # delta / session range
        omega_over_delta=np.abs(P[ie]-P[dcc])/d,         # ω / δ
        retrace_over_delta=np.abs(P[ic]-P[ie])/d,        # r / δ
        dur_sec=(ie-ip).astype(np.int32))))
D=pd.concat(out,ignore_index=True)
assert not {'delta','overshoot','retrace','session_range'} & set(D.columns)
D.to_csv('dc_legs_public.csv.gz',index=False,compression='gzip',float_format='%.17g')
print(f'dc_legs_public.csv.gz : {len(D):,} legs, {D.shape[1]} columns, '
      f'{os.path.getsize("dc_legs_public.csv.gz")/1e6:.1f} MB')
print('columns:',list(D.columns))
print('\nPRICE-LEAK CHECK: no column carries units of index points')
for c in D.columns:
    print(f'  {c:<20} {"dimensionless" if c in ("ratio","omega_over_delta","retrace_over_delta") else ("seconds" if c=="dur_sec" else ("date" if c=="day" else "+-1" if c=="dirn" else "threshold"))}')
print('\ncheck: rebuild the Figure 3 curve from this file alone')
ED=[0.05,0.10,0.15,0.22,0.32,0.45,0.65]; TH6=(5e-4,1e-3,2e-3,5e-3,7e-3,1e-2)
S=D[D.theta.isin(TH6)]
for a,b in zip(ED,ED[1:]):
    m=(S.ratio>=a)&(S.ratio<b)
    cells=[S.omega_over_delta[m&(S.theta==t)].mean() for t in TH6
           if (m&(S.theta==t)).sum()>=60]
    if cells: print(f'  {a:.2f}-{b:.2f}  omega/delta = {np.mean(cells):.3f}  ({len(cells)} cells)')
