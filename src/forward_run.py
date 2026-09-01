"""Forward recorder for FORWARD_SPEC.md.

The execution rules are fixed in this file rather than passed in as arguments, so the
frozen specification cannot drift between sessions.

    python3 forward_run.py <panel.npz> [--from YYYYMMDD]   appends to forward_ledger.csv"""
import numpy as np, pandas as pd, sys, os, warnings; warnings.filterwarnings('ignore')
sys.path.insert(0,'.')
from dcevent import events

THETA_FIX=0.007; DEC=103000; TARGET=0.32; BURN=120; COST=0.175; LEDGER='forward_ledger.csv'

def load(path):
    z=np.load(path)
    return (z['last'].astype(np.float64), z['day'].astype(np.int64),
            (z['time_int']%1000000).astype(np.int64))

def rhat_table(P,DAY,HMS):
    d0=pd.DataFrame(dict(p=P,day=DAY,hms=HMS)); g=d0.groupby('day')['p']
    D=pd.DataFrame(dict(R=g.max()-g.min())).reset_index()
    D['med20']=D.R.shift(1).rolling(20).median()
    q=d0[d0.hms<=DEC].groupby('day')['p']
    D=D.merge((q.max()-q.min()).clip(lower=0.05).rename('OR').reset_index(),on='day')
    D=D.merge(q.last().rename('Pdec').reset_index(),on='day').dropna().reset_index(drop=True)
    x,z2,y=np.log(D.OR),np.log(D.med20),np.log(D.R); rh=np.full(len(D),np.nan)
    fin=np.isfinite(x)&np.isfinite(z2)&np.isfinite(y)
    for t in range(BURN,len(D)):
        k=fin[:t]; A=np.column_stack([np.ones(k.sum()),x[:t][k],z2[:t][k]])
        b,*_=np.linalg.lstsq(A,y[:t][k],rcond=None); rh[t]=np.exp(b[0]+b[1]*x.iloc[t]+b[2]*z2.iloc[t])
    D['Rhat']=rh; D['theta_star']=TARGET*D.Rhat/D.Pdec
    return D.dropna().set_index('day')

def session(P,HMS,a,b,theta):
    s=a+int(np.searchsorted(HMS[a:b],DEC,'right'))
    if b-s<10 or not np.isfinite(theta) or theta<=0: return dict(trips=0,gross=0.,cost=0.,wd=np.nan)
    E=events(P[s:b],theta,offset=s)
    ie,ip,ic,dr=E['i_ext'],E['i_ext_prev'],E['i_conf'],E['dirn']
    ok=(ie>ip)&(ic<b-1); ie,ip,ic,dr=[v[ok] for v in (ie,ip,ic,dr)]
    if len(ie)<2: return dict(trips=0,gross=0.,cost=0.,wd=np.nan)
    dcc=np.concatenate(([-1],ic[:-1])); v=(dcc>ip)&(dcc<ie); v[0]=False
    ie,ic,dr,dcc=[q[v] for q in (ie,ic,dr,dcc)]
    if not len(ie): return dict(trips=0,gross=0.,cost=0.,wd=np.nan)
    pos=np.zeros(b-a)
    for e0,e1,dd in zip(dcc+1,np.minimum(ic+1,b-1),dr):
        if e1>e0: pos[e0-a:e1-a]=-dd
    ch=np.zeros(b-a); ch[:-1]=P[a+1:b]-P[a:b-1]
    turn=float(np.abs(np.diff(pos,prepend=0.0)).sum())
    wd=float(np.mean(np.abs(P[ie]-P[dcc])/(theta*np.abs(P[ie]))))
    return dict(trips=len(ie),gross=float((pos*ch).sum()),cost=turn*COST,wd=wd)

def main(path,frm=None):
    P,DAY,HMS=load(path); D=rhat_table(P,DAY,HMS)
    nd=np.flatnonzero(np.concatenate(([True],DAY[1:]!=DAY[:-1]))); bnd=np.concatenate((nd,[len(P)]))
    rows=[]
    for a,b in zip(bnd[:-1],bnd[1:]):
        day=int(DAY[a])
        if frm and day<frm: continue
        if day not in D.index: continue
        for arm,th in (('fixed_0.7pct',THETA_FIX),('e3_adaptive',float(D.loc[day,'theta_star']))):
            r=session(P,HMS,a,b,th)
            rows.append(dict(day=day,arm=arm,theta=round(th,6),**r,net=r['gross']-r['cost']))
    out=pd.DataFrame(rows)
    if os.path.exists(LEDGER):
        old=pd.read_csv(LEDGER)
        out=pd.concat([old,out]).drop_duplicates(['day','arm'],keep='last').sort_values(['day','arm'])
    out.to_csv(LEDGER,index=False)
    print(out.groupby('arm').agg(phien=('day','nunique'),vong=('trips','sum'),
          net=('net','sum'),wd=('wd','mean')).to_string())
    print(f'\n-> {LEDGER}  ({len(out)} rows, through {out.day.max()})')

if __name__=='__main__':
    frm=None
    if '--from' in sys.argv: frm=int(sys.argv[sys.argv.index('--from')+1])
    main(sys.argv[1],frm)
