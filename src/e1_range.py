"""E1: how much of the full session range is predictable from the opening window?

Every estimate is causal. The scaling coefficient is taken from the expansion ratio over
strictly prior sessions, so nothing from the session being predicted enters its own forecast."""

import os as _os, sys as _sys
if not _os.path.exists('panel2.npz'):
    _sys.exit(
        "This script needs panel2.npz, the VN30F1M one-second tick panel, which is not distributed.\n"
        "It is a licensed series and no derivative permitting price reconstruction is\n"
        "redistributable. The script ships so the method can be read and checked line by\n"
        "line; what it produced is recorded under records/. See README, 'What each script\n"
        "needs'. Installing further packages will not change this.")
import numpy as np, pandas as pd, warnings; warnings.filterwarnings('ignore')

z=np.load('panel2.npz')
P=z['last'].astype(np.float64); DAY=z['day']; HMS=(z['time_int']%1000000).astype(np.int64)
df=pd.DataFrame(dict(p=P,day=DAY,hms=HMS))
g=df.groupby('day')['p']
D=pd.DataFrame(dict(R=g.max()-g.min(), open=g.first(), close=g.last())).reset_index()
D['R_prev']=D.R.shift(1)
D['med20']=D.R.shift(1).rolling(20).median()
D['med60']=D.R.shift(1).rolling(60).median()
D['gap']=(D.open-D.close.shift(1)).abs()

CUT=[93000,94500,100000,101500,103000]
for c in CUT:
    m=df.hms<=c
    q=df[m].groupby('day')['p']
    o=pd.DataFrame(dict(OR=q.max()-q.min())).reset_index()
    o['OR']=o['OR'].clip(lower=0.05)   # floor at half a tick; one or two sessions never move at all
    D=D.merge(o.rename(columns={'OR':f'OR{c}'}),on='day',how='left')
D=D.dropna().reset_index(drop=True)
print(f'{len(D)} sessions with sufficient history ({D.day.min()} to {D.day.max()})\n')

BURN=120
def causal_scale(x,y,burn=BURN):
    """y_hat = k * x, with k the median of (y/x) over strictly prior sessions. No look-ahead."""
    r=(y/x).to_numpy(); out=np.full(len(x),np.nan)
    for t in range(burn,len(x)): out[t]=np.median(r[:t])*x.iloc[t]
    return out

def score(yh,y,name):
    m=np.isfinite(yh)
    if m.sum()<50: return None
    a,b=np.log(y[m]),np.log(yh[m])
    ss=1-((a-b)**2).sum()/((a-a.mean())**2).sum()
    return dict(dubao=name,n=int(m.sum()),
                spearman=float(pd.Series(yh[m]).corr(pd.Series(y[m].values),method='spearman')),
                R2_log=float(ss), MAPE=float((np.abs(yh[m]-y[m])/y[m]).mean()))

rows=[]
for c in CUT:
    rows.append(score(causal_scale(D[f'OR{c}'],D.R),D.R,f'range to {c//10000:02d}:{c//100%100:02d}, scaled'))
rows.append(score(causal_scale(D.med20,D.R),D.R,'20-day median  <- the estimator that lost before'))
rows.append(score(causal_scale(D.med60,D.R),D.R,'60-day median'))
rows.append(score(causal_scale(D.R_prev,D.R),D.R,'yesterday range'))
# combined: opening range and 20-day median, weights fitted causally in logs
x=np.log(D['OR94500']); z2=np.log(D.med20); y=np.log(D.R)
yh=np.full(len(D),np.nan)
fin=np.isfinite(x)&np.isfinite(z2)&np.isfinite(y)
for t in range(BURN,len(D)):
    k=fin[:t]
    A=np.column_stack([np.ones(k.sum()),x[:t][k],z2[:t][k]]); b,*_=np.linalg.lstsq(A,y[:t][k],rcond=None)
    yh[t]=np.exp(b[0]+b[1]*x.iloc[t]+b[2]*z2.iloc[t])
rows.append(score(yh,D.R,'09:45 + 20-day median (log regression, causal)'))

r=pd.DataFrame([x for x in rows if x]).sort_values('R2_log',ascending=False)
print('E1 - SESSION-RANGE FORECAST, out of sample and causal')
print(r.to_string(index=False,float_format=lambda v:f'{v:.3f}'))
D.to_pickle('e1_days.pkl')
print(f'\nsaved e1_days.pkl ({len(D)} sessions)')
