"""Shared collapse pipeline, used unchanged on both markets.

No free parameters: the six thresholds, the band edges, the 60-leg cell floor, the
two-way analysis on cell means and the compression slope are all fixed here.

`group` is the session unit. Directional-change state resets at each group boundary
and the realised range is computed within the same group, so changing the analysis
window is a matter of passing a different group identifier and nothing else.
"""
import numpy as np, pandas as pd
from scipy import stats

THETAS=(5e-4,1e-3,2e-3,5e-3,7e-3,1e-2)
EDGES=(0.05,0.10,0.15,0.22,0.32,0.45,0.65)
MIN_LEGS=60

def legs(P,GRP):
    """Directional-change legs at all six thresholds. P is the price grid; GRP the group
    identifier, in contiguous runs."""
    from dcevent import events_by_group          # imported here: cells() and collapse() work
                                                 # on leg tables alone and need no DC engine
    P=np.ascontiguousarray(np.asarray(P,np.float64)); GRP=np.asarray(GRP); n=len(P)
    ug,gid=np.unique(GRP,return_inverse=True)
    hi=np.full(len(ug),-1e18); lo=np.full(len(ug),1e18)
    np.maximum.at(hi,gid,P); np.minimum.at(lo,gid,P); RNG=hi-lo
    out=[]
    for TH in THETAS:
        E=events_by_group(P,GRP,TH)
        ie,ip,ic,dr=E['i_ext'],E['i_ext_prev'],E['i_conf'],E['dirn']
        ok=(ie>ip)&(ic<n-1)&(GRP[ip]==GRP[ic]); ie,ip,ic,dr=[x[ok] for x in (ie,ip,ic,dr)]
        if len(ie)<2: continue
        dcc=np.concatenate(([-1],ic[:-1])); v=(dcc>ip)&(dcc<ie); v[0]=False
        ie,ip,ic,dr,dcc=[x[v] for x in (ie,ip,ic,dr,dcc)]
        if not len(ie): continue
        d=TH*np.abs(P[ie])
        out.append(pd.DataFrame(dict(theta=TH,grp=GRP[ie],delta=d,
            overshoot=np.abs(P[ie]-P[dcc]),retrace=np.abs(P[ic]-P[ie]),
            session_range=RNG[gid[ie]],dur=(ie-ip).astype(np.int64))))
    L=pd.concat(out,ignore_index=True)
    L['ratio']=L.delta/L.session_range; L['wd']=L.overshoot/L.delta
    return L

def cells(L):
    r=[]
    for a,b in zip(EDGES,EDGES[1:]):
        for th in THETAS:
            m=(L.ratio>=a)&(L.ratio<b)&(L.theta==th)
            if m.sum()>=MIN_LEGS:
                r.append(dict(band=f'{a:.2f}-{b:.2f}',mid=(a+b)/2,theta=th,
                              mean=float(L.wd[m].mean()),n=int(m.sum())))
    return pd.DataFrame(r)

def collapse(C):
    """Two-way analysis on cell means, plus the compression slope. Returns exactly the
    quantities the pre-registration names."""
    y=C['mean'].to_numpy(float); one=np.ones((len(C),1))
    X=pd.get_dummies(C[['band','theta']].astype(str),drop_first=True).astype(float)
    def rss(M):
        b,*_=np.linalg.lstsq(M,y,rcond=None); e=y-M@b; return float(e@e),M.shape[1]
    Xb=np.column_stack([one]+[X[k].to_numpy() for k in X if k.startswith('band')])
    Xt=np.column_stack([one]+[X[k].to_numpy() for k in X if k.startswith('theta')])
    Xf=np.column_stack([one]+[X[k].to_numpy() for k in X])
    rb,kb=rss(Xb); rt,kt=rss(Xt); rf,kf=rss(Xf); df2=len(C)-kf
    Fb=((rt-rf)/(kf-kt))/(rf/df2); Ft=((rb-rf)/(kf-kb))/(rf/df2)
    bm=C.groupby('band').agg(mid=('mid','first'),m=('mean','mean')).sort_values('mid')
    w=C.groupby('band')['mean'].agg(['min','max','count']); w['s']=w['max']-w['min']
    sl,ic_,rv,pv,se=stats.linregress(bm['mid'],bm['m'])
    return dict(ncell=len(C),
        F_band=Fb, p_band=float(1-stats.f.cdf(Fb,kf-kt,df2)), df_band=(kf-kt,df2),
        F_theta=Ft, p_theta=float(1-stats.f.cdf(Ft,kf-kb,df2)), df_theta=(kf-kb,df2),
        ss_ratio=(rb-rf)/(rt-rf),
        within_between=float(w[w['count']>1]['s'].mean()/(bm.m.max()-bm.m.min())),
        beta_C=float(sl), se=float(se), r2=float(rv**2),
        band_means=bm, monotone=bool((np.diff(bm.m)<0).all()))

def report(name,L,C,R):
    print(f'\n=== {name} ===')
    print(f'{len(L):,} legs, {L.grp.nunique():,} groups, {R["ncell"]} cells at or above {MIN_LEGS}')
    for b,r in R['band_means'].iterrows(): print(f'  {b}  ω/δ = {r.m:.3f}')
    print(f'  band|θ  F{R["df_band"]} = {R["F_band"]:.2f}  p = {R["p_band"]:.3g}')
    print(f'  θ|band  F{R["df_theta"]} = {R["F_theta"]:.2f}  p = {R["p_theta"]:.3f}')
    print(f'  SS_theta/SS_band = {R["ss_ratio"]:.3f}   within/between = {R["within_between"]:.3f}')
    print(f'  beta_C = {R["beta_C"]:.3f}  (SE {R["se"]:.3f}, R2 {R["r2"]:.3f})  monotone: {R["monotone"]}')
