"""Detached-denominator falsification.

Specification frozen in PREREG_detached_denominator_v1.0.md
(SHA-256 4450429f82b6f01497459c5006240d8ee079337d043c05c6616329d1700e9b7d).

The session range contains the leg being measured, so a large overshoot can widen it and
induce the reported association mechanically. Replacing the denominator with the range of
the opposite subsession removes that path by construction. Run once."""

import os as _os, sys as _sys
if not _os.path.exists('panel2.npz'):
    _sys.exit(
        "This script needs panel2.npz, the VN30F1M one-second tick panel, which is not distributed.\n"
        "It is a licensed series and no derivative permitting price reconstruction is\n"
        "redistributable. The script ships so the method can be read and checked line by\n"
        "line; what it produced is recorded under records/. See README, 'What each script\n"
        "needs'. Installing further packages will not change this.")
import numpy as np, pandas as pd, sys, warnings; warnings.filterwarnings('ignore'); sys.path.insert(0,'.')
from scipy import stats
from dcevent import events_by_group
import dc_pipeline as Q

z=np.load('panel2.npz'); P=z['last'].astype(np.float64); DAY=z['day']
HMS=(z['time_int']%1000000).astype(np.int64); n=len(P)
inA=(HMS>=91500)&(HMS<=113000); inB=(HMS>=130000)&(HMS<=144500)
ud,dayid=np.unique(DAY,return_inverse=True); ND=len(ud)
def rng_of(mask):
    hi=np.full(ND,-1e18); lo=np.full(ND,1e18)
    np.maximum.at(hi,dayid[mask],P[mask]); np.minimum.at(lo,dayid[mask],P[mask])
    return hi-lo
RA,RB=rng_of(inA),rng_of(inB)
hi=np.full(ND,-1e18); lo=np.full(ND,1e18)
np.maximum.at(hi,dayid,P); np.minimum.at(lo,dayid,P); RS=hi-lo
good=(RA>0)&(RB>0)&np.isfinite(RA)&np.isfinite(RB)
print(f'{ND} sessions, {int(good.sum())} with a non-zero range in both windows')

rows=[]
for TH in Q.THETAS:
    E=events_by_group(P,DAY,TH); ie,ip,ic,dr=E['i_ext'],E['i_ext_prev'],E['i_conf'],E['dirn']
    ok=(ie>ip)&(ic<n-1)&(DAY[ip]==DAY[ic]); ie,ip,ic,dr=[x[ok] for x in (ie,ip,ic,dr)]
    dcc=np.concatenate(([-1],ic[:-1])); v=(dcc>ip)&(dcc<ie); v[0]=False
    ie,ic,dcc=[x[v] for x in (ie,ic,dcc)]
    wA=inA[dcc]&inA[ic]; wB=inB[dcc]&inB[ic]          # legs lying entirely inside one window
    keep=(wA|wB)&good[dayid[ie]]
    ie,ic,dcc,wA=[x[keep] for x in (ie,ic,dcc,wA)]
    d=TH*np.abs(P[ie]); g=dayid[ie]
    own=np.where(wA,RA[g],RB[g]); oth=np.where(wA,RB[g],RA[g])
    rows.append(pd.DataFrame(dict(theta=TH,win=np.where(wA,'A','B'),
        wd=np.abs(P[ie]-P[dcc])/d, x_full=d/RS[g], x_own=d/own, x_det=d/oth)))
L=pd.concat(rows,ignore_index=True)
print(f'{len(L):,} legs lie entirely inside one window  '
      f'(A {int((L.win=="A").sum()):,} / B {int((L.win=="B").sum()):,})\n')

print('PRIMARY QUESTION: rank correlation within each threshold, no threshold selected')
print(f'{"theta":>8} | {"n":>7} | {"rho attached":>13} | {"rho det":>9} | {"p (det)":>9}')
S=[]
for th in Q.THETAS:
    m=L.theta==th
    if m.sum()<60: continue
    ro=stats.spearmanr(L.x_own[m],L.wd[m]); rd=stats.spearmanr(L.x_det[m],L.wd[m])
    S.append(dict(theta=th,n=int(m.sum()),rho_own=ro.statistic,rho_det=rd.statistic,p_det=rd.pvalue))
    print(f'{th:>8.0e} | {int(m.sum()):>7,} | {ro.statistic:>13.3f} | {rd.statistic:>9.3f} | {rd.pvalue:>9.2e}')
S=pd.DataFrame(S)
neg=int((S.rho_det<0).sum())
print(f'\n  negative in {neg}/{len(S)} thresholds   median rho detached = {S.rho_det.median():.3f}'
      f'   (attached {S.rho_own.median():.3f})')

def curve(col,name):
    T=L.rename(columns={col:'ratio'})[['theta','ratio','wd']].copy(); T['grp']=0
    C=Q.cells(T)
    if len(C)<8: print(f'\n{name}: only {len(C)} cells reach the 60-leg floor - too few to analyse'); return None
    R=Q.collapse(C); Q.report(name,T,C,R); return R
Ro=curve('x_own','2 - ATTACHED to its own window (denominator contains the leg)')
Rd=curve('x_det','3 - DETACHED (denominator cannot contain the leg)')

print('\n'+'='*64)
print('THE COMPARISON OF RECORD (2 against 3, identical leg set)')
print(f'  beta_C attached : {Ro["beta_C"]:+.3f}' if Ro else '  attached: too few cells')
print(f'  beta_C detached : {Rd["beta_C"]:+.3f}' if Rd else '  detached: too few cells')
print(f'  published reference, full-session denominator: -1.768')
if Rd:
    b=Rd['beta_C']
    v=('SURVIVES' if (b<=-1.0 and neg>=5) else
       'PARTIAL'  if (b<0 and (neg>=3)) else 'ABSENT')
    print(f'\nVERDICT UNDER THE FROZEN SECTION 6: {v}')
    print(f'  criteria: beta_C detached = {b:+.3f}   negative in {neg}/6 thresholds')
