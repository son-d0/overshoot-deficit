"""Positive control. The shared pipeline must reproduce the published VN30F1M figures
exactly before it is allowed anywhere near a second market."""

import os as _os, sys as _sys
if not _os.path.exists('panel2.npz'):
    _sys.exit(
        "This script needs panel2.npz, the VN30F1M one-second tick panel, which is not distributed.\n"
        "It is a licensed series and no derivative permitting price reconstruction is\n"
        "redistributable. The script ships so the method can be read and checked line by\n"
        "line; what it produced is recorded under records/. See README, 'What each script\n"
        "needs'. Installing further packages will not change this.")
import numpy as np, sys, warnings; warnings.filterwarnings('ignore'); sys.path.insert(0,'.')
import dc_pipeline as Q
z=np.load('panel2.npz'); P=z['last'].astype(np.float64); DAY=z['day']
L=Q.legs(P,DAY); C=Q.cells(L); R=Q.collapse(C)
Q.report('VN30F1M - day sessions (group = DAY)',L,C,R)
# reference: the benchmark table in PREREG_external_test_v0.1.md section 0
EXP=dict(band_means=[1.342,1.243,1.048,0.929,0.740,0.492],F_band=45.13,p_theta=0.118,
         ss_ratio=0.046,within_between=0.219,beta_C=-1.768,se=0.112,r2=0.984,ncell=28)
got=[round(v,3) for v in R['band_means'].m.tolist()]
print('\nAGAINST THE PUBLISHED FIGURES')
ok=True
def chk(lbl,g,e,tol):
    global ok; p=abs(g-e)<=tol; ok&=p
    print(f'  {"match " if p else "DIFFERS"} {lbl:22s} {g:>9.3f}  (published {e})')
print(f'  {"match " if got==EXP["band_means"] else "DIFFERS"} band means           {got}')
ok&= got==EXP['band_means']
chk('cells',R['ncell'],EXP['ncell'],0)
chk('F band',R['F_band'],EXP['F_band'],0.05)
chk('p theta',R['p_theta'],EXP['p_theta'],0.002)
chk('SS_θ/SS_band',R['ss_ratio'],EXP['ss_ratio'],0.002)
chk('within/between',R['within_between'],EXP['within_between'],0.002)
chk('beta_C',R['beta_C'],EXP['beta_C'],0.002)
chk('SE',R['se'],EXP['se'],0.002)
chk('R²',R['r2'],EXP['r2'],0.002)
print('\n'+('PIPELINE CORRECT - reproduces the published result exactly'
      if ok else 'PIPELINE WRONG - must not be used on Hong Kong data'))
