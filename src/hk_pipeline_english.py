"""READING COPY. This is not the timestamped artifact.

`hk_pipeline.py` beside this file is the byte-exact script that was hashed and timestamped before the
Hong Kong test was run, and its comments are in the author's working language. This copy carries the
same code with the comments and printed labels in English, so the method can be read without
translation. Run over the same data, the two produce the same values and the same verdicts; see
`records/REPRODUCTION_2026-09-01.md`. Diff them to see that the difference is only language.

Line 29 inserts '../results_v7' on the import path. That path does not exist in this repository and a
missing entry is simply skipped; dc_pipeline.py sits beside this script and is found there. The line
is left in place because the timestamped original contains it and the two files must not diverge in
anything but language.
"""
"""Locked analysis pipeline for the Hong Kong external test.

Specification: PREREG_external_test_v0.3_amendment.md section 8 (hash e03a2407...), as amended
by v0.4 (interim-inspection disclosure and the two-layer report) and v0.5 (Level A regrouped
onto the tradable window, which crosses midnight).

Execution order is fixed by the specification, not by preference:
    integrity check -> session construction -> H1/H2/H3 -> beta_C at each window level.

Run once. No window, threshold, band edge or filter is revised after a result is seen.

    python3 hk_pipeline.py                     full sample, both layers
    python3 hk_pipeline.py --held-back-only    the never-inspected period alone, first
    python3 hk_pipeline.py --seen-only         the already-disclosed portion only
    python3 hk_pipeline.py --partial           incomplete data; results are not reportable

The --seen-only and --held-back-only guards exist so the held-back window cannot be touched by
accident. They refuse rather than warn.

Correction log
  2026-08-31  R["df"] -> R["df_band"]. The fault was in a print statement and affected no
              computed quantity. Found by the --partial dry run, before the real execution.
  2026-08-31  Level A regrouped onto the trading window rather than the calendar date, per
              v0.5 section 2. Timestamped after that amendment, not before.
  2026-08-31  Two-layer report added per v0.4 section 3. Criteria unchanged.
"""
import lzma,glob,os,sys,json,numpy as np,pandas as pd,datetime as dt,warnings
warnings.filterwarnings('ignore'); sys.path.insert(0,'../results_v7')
from scipy import stats
import dc_pipeline as Q                      # thresholds, bands, 60-leg floor, analysis - shared with VN30F1M

PARTIAL='--partial' in sys.argv
SEEN_ONLY='--seen-only' in sys.argv     # guard: only the portion already disclosed as inspected
HELD_ONLY='--held-back-only' in sys.argv  # run the held-back period alone, before the full sample
SEEN_UPTO=20240626                      # boundary of the interim inspection
HK=8*3600                                    # Hong Kong is UTC+8 and observes no daylight saving
AM=(9*3600+15*60, 12*3600)                   # 09:15–12:00 HKT   (prereg §2.2)
PM=(13*3600,      16*3600+30*60)             # 13:00–16:30 HKT

# ---------- 1. LOAD AND INTEGRITY CHECK ----------
def load():
    fs=sorted(f for f in glob.glob('raw/**/*.bi5',recursive=True) if os.path.getsize(f)>0)
    if SEEN_ONLY:
        n0=len(fs)
        fs=[f for f in fs if int(''.join(f.split('/')[1:4]))<=SEEN_UPTO]
        print(f'    [--seen-only] keeping {len(fs):,}/{n0:,} files, discarding everything after {SEEN_UPTO}')
    print(f'[1] {len(fs):,} hourly files carrying quotes')
    ts=[];mid=[];sp=[]
    for f in fs:
        p=f.split('/'); y,mo,d,hh=int(p[1]),int(p[2]),int(p[3]),int(p[4][:2])
        base=int(dt.datetime(y,mo,d,hh,tzinfo=dt.timezone.utc).timestamp())
        a=np.frombuffer(lzma.decompress(open(f,'rb').read()),dtype='>u4').reshape(-1,5)
        A=a[:,1].astype(np.float64)/1000; B=a[:,2].astype(np.float64)/1000
        ts.append(base+a[:,0].astype(np.int64)//1000); mid.append((A+B)/2); sp.append(A-B)
    T=np.concatenate(ts); M=np.concatenate(mid); S=np.concatenate(sp)
    o=np.argsort(T,kind='stable'); T,M,S=T[o],M[o],S[o]
    ok=np.isfinite(M)&(M>0)&(S>=0)
    print(f'    {len(T):,} quotes, dropped {int((~ok).sum())} invalid records')
    T,M,S=T[ok],M[ok],S[ok]
    print(f'    median spread {np.median(S):.3f} points; spread noise in the mid '
          f'{np.abs(np.diff(S)/2).mean()/np.abs(np.diff(M)).mean()*100:.2f}%')
    print(f'    price {M.min():.1f}-{M.max():.1f}; date range '
          f'{dt.datetime.utcfromtimestamp(T[0]).date()} → {dt.datetime.utcfromtimestamp(T[-1]).date()}')
    return T,M

# ---------- 2. SESSION CONSTRUCTION, ONE-SECOND GRID ----------
# The unit is the trading window, 09:00 Hong Kong to 01:00 the next day, not the calendar date.
# The window crosses midnight, so grouping by date would reset the state mid-window.
WIN0=9*3600                                   # window origin, 09:00 Hong Kong time

def panel(T,M):
    """One-second grid per trading window. Forward fill within the window only, never backward."""
    tl=T+HK
    win=(tl-WIN0)//86400                       # trading-window id
    ws=(tl-WIN0)%86400                         # second within the window, 0 at 09:00
    df=pd.DataFrame(dict(win=win,ws=ws,p=M)).groupby(['win','ws'],as_index=False).last()
    out=[]
    for w,g in df.groupby('win',sort=True):
        a,b=int(g.ws.min()),int(g.ws.max())
        idx=np.arange(a,b+1)
        p=pd.Series(np.nan,index=idx); p.loc[g.ws.values]=g.p.values
        p=p.ffill()                            # forward fill only
        m=p.notna().values
        out.append(pd.DataFrame(dict(win=int(w),ws=idx[m],p=p.values[m])))
    P=pd.concat(out,ignore_index=True)
    P['sec']=(P.ws+WIN0)%86400                 # second of the Hong Kong day, for the B and C filters
    print(f'[2] {len(P):,} one-second observations across {P.win.nunique():,} trading windows')
    return P

# ---------- 3. THE THREE WINDOW LEVELS ----------
def levels(P):
    inAM=(P.sec>=AM[0])&(P.sec<AM[1]); inPM=(P.sec>=PM[0])&(P.sec<PM[1])
    L={}
    L['A_full']  = (P, P.win.values)                                   # full tradable window
    B=P[inAM|inPM]
    L['B_day']   = (B, B.win.values)                                   # Hong Kong regular day session
    C=P[inAM|inPM].copy()
    C['half']=np.where((C.sec>=AM[0])&(C.sec<AM[1]),0,1)
    L['C_sub']   = (C, (C.win.values*2+C.half.values))                 # morning and afternoon separately
    for k,(d,g) in L.items():
        print(f'    {k}: {len(d):,} observations, {len(np.unique(g)):,} groups')
    return L

# ---------- 4. H1 / H2 / H3 / β_C ----------
def analyse(name,d,g):
    L=Q.legs(d.p.values,g); C=Q.cells(L); R=Q.collapse(C)
    print(f'\n=== {name} ===  {len(L):,} legs, {R["ncell"]} cells at or above {Q.MIN_LEGS}')
    for b,r in R['band_means'].iterrows(): print(f'   {b}  ω/δ = {r.m:.3f}')
    print(f'   H1  band|θ F{R["df_band"]} = {R["F_band"]:.2f}  p = {R["p_band"]:.3g}   '
          f'monotone decreasing: {R["monotone"]}')
    print(f'   H2  p_θ = {R["p_theta"]:.3f} (>0.05)   SS_θ/SS_band = {R["ss_ratio"]:.3f} (<0.35)   '
          f'within/between = {R["within_between"]:.3f} (<0.40)')
    h2=(R['p_band']<0.01)and(R['p_theta']>0.05)and(R['ss_ratio']<0.35)and(R['within_between']<0.40)
    bm=R['band_means']
    cross=np.nan
    for i in range(len(bm)-1):
        a,b2=bm.m.iloc[i],bm.m.iloc[i+1]
        if (a-1)*(b2-1)<0:
            f=(a-1)/(a-b2); cross=bm.mid.iloc[i]+f*(bm.mid.iloc[i+1]-bm.mid.iloc[i]); break
    print(f'   H3  crossing of unity at delta/R = {cross:.3f}   (registered window [0.15, 0.30])')
    print(f'   β_C = {R["beta_C"]:.3f}  (SE {R["se"]:.3f})')
    print(f'   -> H1 {"pass" if R["p_band"]<0.01 and R["monotone"] else "fail"}'
          f' | H2 {"pass" if h2 else "fail"}'
          f' | H3 {"pass" if 0.15<=cross<=0.30 else "fail"}')
    return R,C

HELD_BACK=20240626        # every trading window after this date was never inspected

def report(tag,P):
    LV=levels(P); res={}
    for k,(d,g) in LV.items(): res[k]=analyse(f'{tag} · {k}',d,g)
    print('\n'+'-'*62); print(f'{tag} - COMPRESSION ORDERING, common support')
    common=set.intersection(*[set(C.band) for _,C in res.values()])
    order=[]
    for k in ('C_sub','B_day','A_full'):
        R,C=res[k]; c=C[C.band.isin(common)]
        bm=c.groupby('band').agg(mid=('mid','first'),m=('mean','mean')).sort_values('mid')
        sl=stats.linregress(bm['mid'],bm['m']).slope if len(bm)>=3 else np.nan
        order.append(sl); print(f'   β_C({k}) = {sl:.3f}')
    ok=order[0]<order[1]<order[2]
    print(f'   predicted sub-session < day < full window: {"pass" if ok else "fail"}')
    return res,order

def main():
    n=len(glob.glob('raw/**/*.bi5',recursive=True))
    if n<34440 and not PARTIAL:
        print(f'ACQUISITION INCOMPLETE: {n:,}/34,440 files. Use --partial for a dry run; its results are not reportable.')
        return
    if PARTIAL: print('*** DRY RUN ON INCOMPLETE DATA - RESULTS ARE NOT REPORTABLE ***')
    if SEEN_ONLY: print('*** ALREADY-INSPECTED PORTION ONLY - no additional data is exposed ***')
    print()
    T,M=load(); P=panel(T,M)
    import datetime as _dt
    if not HELD_ONLY:
        print('\n'+'='*62)
        print('LAYER 1 - FULL SAMPLE  (pre-registered analysis, with an interim inspection of ~60%)')
        print('='*62)
        r1,o1=report('LAYER 1',P)
    else:
        r1,o1={},[np.nan]*3
        print('\n[--held-back-only] Layer 1 skipped: the held-back period is required to run first.')
    cut=(int(_dt.datetime(HELD_BACK//10000,HELD_BACK//100%100,HELD_BACK%100,
                          tzinfo=_dt.timezone.utc).timestamp())+HK-WIN0)//86400
    hb=P[P.win>cut]
    print('\n'+'='*62)
    print(f'LAYER 2 - NEVER-INSPECTED PERIOD  (after {HELD_BACK}, {hb.win.nunique():,} windows)')
    print('   criteria identical to Layer 1; nothing was changed because 60% had been seen')
    print('='*62)
    if SEEN_ONLY:
        print('   SKIPPED: the --seen-only guard forbids touching the held-back period.')
        return
    r2,o2=report('LAYER 2',hb) if hb.win.nunique()>=60 else ({},[np.nan]*3)
    if HELD_ONLY:
        json.dump(dict(layer2={k:{kk:(float(vv) if isinstance(vv,(int,float,np.floating)) else str(vv))
                                 for kk,vv in R.items() if kk!='band_means'} for k,(R,_) in r2.items()},
                       beta_layer2=list(map(float,o2))),open('hk_result_heldback.json','w'),indent=1)
        print('\n→ hk_result_heldback.json'); return
    json.dump(dict(layer1={k:{kk:(float(vv) if isinstance(vv,(int,float,np.floating)) else str(vv))
                              for kk,vv in R.items() if kk!='band_means'} for k,(R,_) in r1.items()},
                   layer2={k:{kk:(float(vv) if isinstance(vv,(int,float,np.floating)) else str(vv))
                              for kk,vv in R.items() if kk!='band_means'} for k,(R,_) in r2.items()},
                   beta_layer1=list(map(float,o1)),beta_layer2=list(map(float,o2))),
              open('hk_result.json','w'),indent=1)
main()
