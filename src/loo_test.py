"""Leave-one-leg-out denominator.

Specification frozen in PREREG_leave_one_leg_out_v1.0.md
(SHA-256 bac0007b8308dd70968653af64eaf3ad1a520670507081e886ac19567b96d676).

The session range is recomputed with the measured leg's own ticks removed. Same session,
same volatility, no proxy from elsewhere: the only path cut is the direct one from the leg
into its own denominator. Most legs never touch the session extremes, so most denominators
do not change at all, which is what makes the test surgical. Run once."""

import os as _os, sys as _sys
if not _os.path.exists('panel2.npz'):
    _sys.exit(
        "This script needs panel2.npz, the VN30F1M one-second tick panel, which is not distributed.\n"
        "It is a licensed series and no derivative permitting price reconstruction is\n"
        "redistributable. The script ships so the method can be read and checked line by\n"
        "line; what it produced is recorded under records/. See README, 'What each script\n"
        "needs'. Installing further packages will not change this.")
import numpy as np, pandas as pd, sys, warnings; warnings.filterwarnings('ignore'); sys.path.insert(0,'.')
from dcevent import events_by_group
import dc_pipeline as Q

z=np.load('panel2.npz'); P=z['last'].astype(np.float64); DAY=z['day']; n=len(P)
nd=np.flatnonzero(np.concatenate(([True],DAY[1:]!=DAY[:-1]))); bnd=np.concatenate((nd,[n]))
NEG,POS=-1e18,1e18
pmax=np.empty(n); pmin=np.empty(n); smax=np.empty(n); smin=np.empty(n)
for a,b in zip(bnd[:-1],bnd[1:]):                       # prefix and suffix extrema within each session
    pmax[a:b]=np.maximum.accumulate(P[a:b]); pmin[a:b]=np.minimum.accumulate(P[a:b])
    smax[a:b]=np.maximum.accumulate(P[a:b][::-1])[::-1]; smin[a:b]=np.minimum.accumulate(P[a:b][::-1])[::-1]
ds=np.zeros(n,np.int64)
for a,b in zip(bnd[:-1],bnd[1:]): ds[a:b]=a
de=np.zeros(n,np.int64)
for a,b in zip(bnd[:-1],bnd[1:]): de[a:b]=b-1
ud,dayid=np.unique(DAY,return_inverse=True); ND=len(ud)
hi=np.full(ND,NEG); lo=np.full(ND,POS)
np.maximum.at(hi,dayid,P); np.minimum.at(lo,dayid,P); RS=hi-lo

rows=[]
for TH in Q.THETAS:
    E=events_by_group(P,DAY,TH); ie,ip,ic,dr=E['i_ext'],E['i_ext_prev'],E['i_conf'],E['dirn']
    ok=(ie>ip)&(ic<n-1)&(DAY[ip]==DAY[ic]); ie,ip,ic,dr=[x[ok] for x in (ie,ip,ic,dr)]
    dcc=np.concatenate(([-1],ic[:-1])); v=(dcc>ip)&(dcc<ie); v[0]=False
    ie,ic,dcc=[x[v] for x in (ie,ic,dcc)]
    L_,R_=dcc,ic                                        # remove the whole leg, not only its overshoot
    lft=L_>ds[ie]; rgt=R_<de[ie]
    mx=np.where(lft,pmax[np.maximum(L_-1,ds[ie])],NEG)
    mn=np.where(lft,pmin[np.maximum(L_-1,ds[ie])],POS)
    mx=np.maximum(mx,np.where(rgt,smax[np.minimum(R_+1,de[ie])],NEG))
    mn=np.minimum(mn,np.where(rgt,smin[np.minimum(R_+1,de[ie])],POS))
    Rloo=np.where(lft|rgt,mx-mn,0.0)
    d=TH*np.abs(P[ie]); g=dayid[ie]
    rows.append(pd.DataFrame(dict(theta=TH,wd=np.abs(P[ie]-P[dcc])/d,
        R_full=RS[g],R_loo=Rloo,x_full=d/RS[g],delta=d)))
L=pd.concat(rows,ignore_index=True)
keep=L.R_loo>0; drop=int((~keep).sum()); L=L[keep].copy()
L['x_loo']=L.delta/L.R_loo
print(f'{len(L):,} legs ({drop} dropped because the leave-one-out range is zero)')

ch=L.R_loo<L.R_full
print(f'\nlegs whose denominator actually changes: {int(ch.sum()):,} / {len(L):,} = {ch.mean()*100:.1f}%')
if ch.any():
    rr=(L.R_loo[ch]/L.R_full[ch])
    print(f'  among those, ratio to the full range: median {rr.median():.3f}  p10 {rr.quantile(.1):.3f}  min {rr.min():.3f}')
    print(f'  omega/delta of affected legs {L.wd[ch].mean():.3f}  against unaffected {L.wd[~ch].mean():.3f}')

def run(col,name):
    T=L.rename(columns={col:'ratio'})[['theta','ratio','wd']].copy(); T['grp']=0
    C=Q.cells(T); R=Q.collapse(C); Q.report(name,T,C,R); return R
Rf=run('x_full','SAME-SESSION DENOMINATOR, as published')
Rl=run('x_loo','LEAVE-ONE-LEG-OUT')

print('\n'+'='*66); print('THE THREE DENOMINATORS SIDE BY SIDE')
print(f'{"denominator":>34} | {"beta_C":>7} | {"p_theta":>8} | {"SS_t/SS_b":>9} | {"within/btw":>10}')
print(f'{"same-session, published":>34} | {Rf["beta_C"]:>7.3f} | {Rf["p_theta"]:>8.3f} | {Rf["ss_ratio"]:>9.3f} | {Rf["within_between"]:>10.3f}')
print(f'{"opposite subsession":>34} | {-1.028:>7.3f} | {0.000:>8.3f} | {0.889:>9.3f} | {0.501:>10.3f}')
print(f'{"leave-one-leg-out":>34} | {Rl["beta_C"]:>7.3f} | {Rl["p_theta"]:>8.3f} | {Rl["ss_ratio"]:>9.3f} | {Rl["within_between"]:>10.3f}')
sh=(abs(Rf['beta_C'])-abs(Rl['beta_C']))/abs(Rf['beta_C'])
fails=sum([Rl['p_band']>=0.01,Rl['p_theta']<=0.05,Rl['ss_ratio']>=0.35,Rl['within_between']>=0.40])
print(f'\nslope flattens by {sh*100:+.1f}%   collapse criteria failing: {fails}/4')
v=('UNAFFECTED' if (abs(sh)<=0.10 and fails==0) else
   'COUPLING-DRIVEN' if (sh>0.40 or not Rl['monotone'] or fails>=2) else 'PARTIAL')
print(f'VERDICT UNDER THE FROZEN SECTION 5: {v}')
