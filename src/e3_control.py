"""E3: causal threshold control. Specification frozen in PREREG_E3_threshold_control_v1.0.md
   (SHA-256 278341d41e647edfcda7dbe3234984c85f6d10088c0ba279102e12c60c374c70).
   Run exactly once."""

import os as _os, sys as _sys
if not _os.path.exists('panel2.npz'):
    _sys.exit(
        "This script needs panel2.npz, the VN30F1M one-second tick panel, which is not distributed.\n"
        "It is a licensed series and no derivative permitting price reconstruction is\n"
        "redistributable. The script ships so the method can be read and checked line by\n"
        "line; what it produced is recorded under records/. See README, 'What each script\n"
        "needs'. Installing further packages will not change this.")
import numpy as np, pandas as pd, sys, warnings; warnings.filterwarnings('ignore')
sys.path.insert(0,'.')
from dcevent import events

COST=0.175; DEC=103000; TARGET=0.32; BURN=120
FIXED=[5e-4,1e-3,2e-3,5e-3,7e-3,1e-2]

z=np.load('panel2.npz')
P=z['last'].astype(np.float64); DAY=z['day']; HMS=(z['time_int']%1000000).astype(np.int64); n=len(P)
PCHG=np.zeros(n); nd=np.flatnonzero(np.concatenate(([True],DAY[1:]!=DAY[:-1])))
bnd=np.concatenate((nd,[n]))
for a,b in zip(bnd[:-1],bnd[1:]): PCHG[a:b-1]=P[a+1:b]-P[a:b-1]

# ---- causal range estimate, the E1 model at the 10:30 cutoff ----------------
d0=pd.DataFrame(dict(p=P,day=DAY,hms=HMS)); g=d0.groupby('day')['p']
D=pd.DataFrame(dict(R=g.max()-g.min())).reset_index()
D['med20']=D.R.shift(1).rolling(20).median()
q=d0[d0.hms<=DEC].groupby('day')['p']
D=D.merge((q.max()-q.min()).clip(lower=0.05).rename('OR').reset_index(),on='day',how='left')
D=D.merge(q.last().rename('Pdec').reset_index(),on='day',how='left')
D=D.dropna().reset_index(drop=True)
x,z2,y=np.log(D.OR),np.log(D.med20),np.log(D.R); rh=np.full(len(D),np.nan)
fin=np.isfinite(x)&np.isfinite(z2)&np.isfinite(y)
for t in range(BURN,len(D)):
    k=fin[:t]; A=np.column_stack([np.ones(k.sum()),x[:t][k],z2[:t][k]])
    b,*_=np.linalg.lstsq(A,y[:t][k],rcond=None)
    rh[t]=np.exp(b[0]+b[1]*x.iloc[t]+b[2]*z2.iloc[t])
D['Rhat']=rh; D=D.dropna().reset_index(drop=True)
D['theta_star']=TARGET*D.Rhat/D.Pdec
USE=set(D.day.tolist()); TH_BY_DAY=dict(zip(D.day,D.theta_star))
print(f'E3 - {len(D)} sessions ({D.day.min()} to {D.day.max()})')
print(f'θ* : p10 {np.percentile(D.theta_star,10):.5f}  p50 {np.percentile(D.theta_star,50):.5f}'
      f'  p90 {np.percentile(D.theta_star,90):.5f}\n')

# ---- one session, one threshold ---------------------------------------------
def run_day(a,b,theta):
    """Returns (position slice, round trips, sum of omega/delta, leg count). State reset at the cutoff."""
    s=a+int(np.searchsorted(HMS[a:b],DEC,'right'))     # first tick after the cutoff
    m=b-s
    p=np.zeros(b-a)
    if m<10 or theta<=0 or not np.isfinite(theta): return p,0,0.0,0
    E=events(P[s:b],theta,offset=s)
    ie,ip,ic,dr=E['i_ext'],E['i_ext_prev'],E['i_conf'],E['dirn']
    ok=(ie>ip)&(ic<b-1); ie,ip,ic,dr=[v[ok] for v in (ie,ip,ic,dr)]
    if len(ie)<2: return p,0,0.0,0
    dcc=np.concatenate(([-1],ic[:-1])); v=(dcc>ip)&(dcc<ie); v[0]=False
    ie,ic,dr,dcc=[q[v] for q in (ie,ic,dr,dcc)]
    if not len(ie): return p,0,0.0,0
    delta=theta*np.abs(P[ie]); om=np.abs(P[ie]-P[dcc])
    for e0,e1,dd in zip(dcc+1,np.minimum(ic+1,b-1),dr):   # one-second delay; fade takes the opposite side
        if e1>e0: p[e0-a:e1-a]=-dd
    return p,len(ie),float((om/delta).sum()),len(ie)

def run_arm(theta_of_day,label):
    pos=np.zeros(n); wd=0.0; nl=0
    for a,b in zip(bnd[:-1],bnd[1:]):
        day=int(DAY[a])
        if day not in USE: continue
        th=theta_of_day(day)
        p,_,w,k=run_day(a,b,th); pos[a:b]=p; wd+=w; nl+=k
    t=np.abs(np.diff(pos,prepend=0.0)); gr=pos*PCHG
    ud,did=np.unique(DAY,return_inverse=True)
    daily=np.bincount(did,gr-t*COST,len(ud)); dg=np.bincount(did,gr,len(ud))
    sel=np.isin(ud,list(USE)); s=daily[sel]; eq=np.cumsum(s)
    G,T=float(dg[sel].sum()),float(t.sum())
    return dict(arm=label,net=float(s.sum()),gross=G,turn=T,
                be=G/max(T,1e-9), sr=float(s.mean()/s.std()*np.sqrt(252)) if s.std()>0 else np.nan,
                mdd=float(np.max(np.maximum.accumulate(eq)-eq)),
                nleg=nl, wd=wd/max(nl,1), expo=float((pos[np.isin(DAY,list(USE))]!=0).mean()),
                daily=s, days=ud[sel])

rows=[run_arm(lambda d:TH_BY_DAY[d],'ADAPTIVE  theta* = 0.32 * Rhat / P')]
for th in FIXED: rows.append(run_arm(lambda d,t=th:t,f'fixed theta = {th:.0e}'))
r=pd.DataFrame([{k:v for k,v in x.items() if k not in('daily','days')} for x in rows])
print('RESULT - cost 0.175 per leg, state reset at 10:30, trading only afterwards')
print(r.to_string(index=False,float_format=lambda v:f'{v:.3f}'))

best=max(rows[1:],key=lambda x:x['net']); ad=rows[0]
print(f"\nstrongest comparator, granted hindsight in choosing its threshold: {best['arm']}")
print(f"  net {best['net']:.1f}   Sharpe {best['sr']:.2f}   MDD {best['mdd']:.1f}   break-even {best['be']:.3f}/leg")
print(f"adaptive, granted none:")
print(f"  net {ad['net']:.1f}   Sharpe {ad['sr']:.2f}   MDD {ad['mdd']:.1f}   break-even {ad['be']:.3f}/leg")
print(f"\ndiagnostic E[omega/delta]: adaptive {ad['wd']:.3f}  against  {best['arm']} {best['wd']:.3f}")
yr=pd.DataFrame({x['arm']:pd.Series(x['daily']).groupby(x['days']//10000).sum() for x in rows})
print('\nnet profit by year'); print(yr.to_string(float_format=lambda v:f'{v:.1f}'))
pd.to_pickle(rows,'e3_result.pkl')
