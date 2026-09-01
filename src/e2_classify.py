"""E2: predicting the range accurately is not the requirement. Landing on the correct side
of the unity crossing is, and that is an easier problem.

Everything is causal: the range estimate is formed at the cutoff, and only legs entered after
that time are counted."""

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
from dcevent import events_by_group

z=np.load('panel2.npz')
P=z['last'].astype(np.float64); DAY=z['day']; HMS=(z['time_int']%1000000).astype(np.int64); n=len(P)
d0=pd.DataFrame(dict(p=P,day=DAY,hms=HMS)); g=d0.groupby('day')['p']
D=pd.DataFrame(dict(R=g.max()-g.min())).reset_index()
D['med20']=D.R.shift(1).rolling(20).median()

CUT=[94500,100000,103000]; BURN=120
for c in CUT:
    q=d0[d0.hms<=c].groupby('day')['p']
    D=D.merge((q.max()-q.min()).clip(lower=0.05).rename(f'OR{c}').reset_index(),on='day',how='left')
D=D.dropna().reset_index(drop=True)
for c in CUT:                                    # causal log regression, as in E1
    x,z2,y=np.log(D[f'OR{c}']),np.log(D.med20),np.log(D.R); rh=np.full(len(D),np.nan)
    fin=np.isfinite(x)&np.isfinite(z2)&np.isfinite(y)
    for t in range(BURN,len(D)):
        k=fin[:t]; A=np.column_stack([np.ones(k.sum()),x[:t][k],z2[:t][k]])
        b,*_=np.linalg.lstsq(A,y[:t][k],rcond=None)
        rh[t]=np.exp(b[0]+b[1]*x.iloc[t]+b[2]*z2.iloc[t])
    D[f'Rhat{c}']=rh
D=D.dropna().reset_index(drop=True)
print(f'{len(D)} usable sessions ({D.day.min()} to {D.day.max()})\n')

ED=[0.05,0.10,0.15,0.22,0.32,0.45,0.65]; C=0.20
ud,dayid=np.unique(DAY,return_inverse=True)
legs=[]
for TH in (5e-4,1e-3,2e-3,5e-3,7e-3,1e-2):
    E=events_by_group(P,DAY,TH); ie,ip,ic,dr=E['i_ext'],E['i_ext_prev'],E['i_conf'],E['dirn']
    ok=(ie>ip)&(ic<n-1)&(DAY[ip]==DAY[ic]); ie,ip,ic,dr=[x[ok] for x in (ie,ip,ic,dr)]
    dcc=np.concatenate(([-1],ic[:-1])); v=(dcc>ip)&(dcc<ie); v[0]=False
    ie,ip,ic,dcc=[x[v] for x in (ie,ip,ic,dcc)]
    legs.append(pd.DataFrame(dict(theta=TH,day=DAY[ie],hms_in=HMS[dcc],
        delta=TH*np.abs(P[ie]), omega=np.abs(P[ie]-P[dcc]))))
L=pd.concat(legs,ignore_index=True); L['wd']=L.omega/L.delta
L=L.merge(D,on='day',how='inner')
print(f'{len(L):,} legs across {L.day.nunique():,} sessions\n')

print('ENTRY TIME - how many legs remain if the threshold is fixed in the morning?')
for c in CUT:
    f=(L.hms_in>c).mean()
    print(f'  entered after {c//10000:02d}:{c//100%100:02d} : {f*100:5.1f}% of legs')

def curve(x,y):
    o=[]
    for a,b in zip(ED,ED[1:]):
        m=(x>=a)&(x<b)
        o.append((f'{a:.2f}-{b:.2f}', y[m].mean() if m.sum()>=60 else np.nan, int(m.sum())))
    return o

for c in CUT:
    S=L[L.hms_in>c].copy()
    S['rt']=S.delta/S.R; S['rh']=S.delta/S[f'Rhat{c}']
    print(f'\n{"="*66}\nCUTOFF {c//10000:02d}:{c//100%100:02d}   ({len(S):,} legs)')
    ct,ch=curve(S.rt,S.wd),curve(S.rh,S.wd)
    print(f'{"delta/R band":>12} | {"TRUE, known at the close":>24} | {"ESTIMATED, known in the morning":>26}')
    for (b1,v1,n1),(b2,v2,n2) in zip(ct,ch):
        f1='' if not np.isfinite(v1) else f'{v1:.3f}  (n={n1:,})'
        f2='' if not np.isfinite(v2) else f'{v2:.3f}  (n={n2:,})'
        print(f'{b1:>12} | {f1:>24} | {f2:>26}')
    yt,yh=(S.rt>=C),(S.rh>=C)
    tp,fp=int((yt&yh).sum()),int((~yt&yh).sum()); fn,tn=int((yt&~yh).sum()),int((~yt&~yh).sum())
    acc=(tp+tn)/len(S); bal=.5*(tp/max(tp+fn,1)+tn/max(tn+fp,1))
    print(f'\n  side-of-the-line classification at {C}: accuracy {acc*100:.1f}%  balanced {bal*100:.1f}%')
    print(f'    predicted fade (est >= {C}) : n={tp+fp:,}  realised omega/delta = {S.wd[yh].mean():.3f}'
          f'   [{tp:,} right / {fp:,} wrong]')
    print(f'    predicted not          : n={tn+fn:,}  realised omega/delta = {S.wd[~yh].mean():.3f}')
    print(f'    (ceiling under ex-post labels: {S.wd[yt].mean():.3f} against {S.wd[~yt].mean():.3f})')
    print(f'    (no conditioning at all : {S.wd.mean():.3f})')
L.to_pickle('e2_legs.pkl')
