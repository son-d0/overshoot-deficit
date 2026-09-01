"""Walk-forward harness, reimplemented and then re-run on the corrected candidate grid.

Step 1 must reproduce the stored output exactly. If it does not, the reimplementation is not
faithful and any difference in step 2 cannot be attributed to the correction rather than to the
rewrite. The correction itself is a key collision: formatting thresholds with %.0e maps both
1e-2 and 1.2e-2 to the same string, and building a dictionary from those keys silently dropped
six cells."""

import os as _os, sys as _sys
if not _os.path.exists('grid_raw.npz'):
    _sys.exit(
        "This script needs grid_raw.npz, the pre-computed strategy grid, which is not distributed.\n"
        "It is a licensed series and no derivative permitting price reconstruction is\n"
        "redistributable. The script ships so the method can be read and checked line by\n"
        "line; what it produced is recorded under records/. See README, 'What each script\n"
        "needs'. Installing further packages will not change this.")
import numpy as np, json, warnings; warnings.filterwarnings('ignore')
C=0.175
z=np.load('grid_raw.npz',allow_pickle=True); days=z['days']
KA=[str(x) for x in z['ka']]; KF=[str(x) for x in z['kf']]
GA={k:(z[f'ag_{i}'],z[f'at_{i}']) for i,k in enumerate(KA)}
THS=(3e-3,5e-3,7e-3,1e-2,1.2e-2); WIN=('full session','after 09:45'); CAP=('to confirmation','<=60 min','<=120 min')
ORDER=[(t,w,c) for t in THS for w in WIN for c in CAP]          # the loop order of the grid builder
assert len(ORDER)==len(KF)==30
for (t,w,c),k in zip(ORDER,KF): assert k==f'{t:.0e}|{w}|{c}', (t,w,c,k)

GF_BUG={k:(z[f'fg_{i}'],z[f'ft_{i}']) for i,k in enumerate(KF)}                  # with the overwriting fault
GF_FIX={f'{t:g}|{w}|{c}':(z[f'fg_{i}'],z[f'ft_{i}'])                             # unambiguous keys
        for i,(t,w,c) in enumerate(ORDER)}
print(f'fade grid: {len(GF_BUG)} cells with the fault, {len(GF_FIX)} corrected')

WTS=(0.0,0.25,0.5,0.75,1.0,1.5); MINTRAIN=200
FOLDS=[('2023',(days>=20230101)&(days<20240101)),('2024',(days>=20240101)&(days<20250101)),
       ('2025',(days>=20250101)&(days<20260101)),('2026H1',(days>=20260101)&(days<=20260424)),
       ('2026H2',days>20260424)]
def metr(dg,dt,m,mintrade=20):
    x=(dg-dt*C)[m]
    if x.size==0: return None
    if dt[m].sum()<mintrade:
        return dict(net=float(x.sum()),sr=0.0,mdd=0.0,cal=0.0,
                    gpt=float(dg[m].sum()/max(dt[m].sum(),1e-9)),
                    tpd=float(dt[m].sum()/max(m.sum(),1)/2),nd=int(m.sum()),thin=True)
    eq=np.cumsum(x); mdd=float(np.max(np.maximum.accumulate(eq)-eq))
    return dict(net=float(x.sum()),sr=float(x.mean()/x.std()*np.sqrt(252)) if x.std()>0 else 0.0,
                mdd=mdd,cal=float(x.sum()/mdd) if mdd>1e-9 else 0.0,
                gpt=float(dg[m].sum()/max(dt[m].sum(),1e-9)),
                tpd=float(dt[m].sum()/max(m.sum(),1)/2),nd=int(m.sum()),thin=False)
def run(GFx,crit,blend=False,G=None):
    rows=[]; st=np.zeros(len(days)); used=np.zeros(len(days),bool); picks=[]
    for lbl,tm in FOLDS:
        trm=days<days[tm][0]
        if trm.sum()<MINTRAIN: continue
        best=None
        if not blend:
            for k,(dg,dt) in G.items():
                r=metr(dg,dt,trm)
                if r is None or r['thin']: continue
                if best is None or r[crit]>best[0]: best=(r[crit],k,r,(dg,dt))
        else:
            for ka,(ag,at) in GA.items():
                ra=metr(ag,at,trm)
                if ra is None or ra['thin']: continue
                for kf,(fg,ft) in GFx.items():
                    rf=metr(fg,ft,trm)
                    if rf is None or rf['thin']: continue
                    for w in WTS:
                        dg=ag+w*fg; dt=at+w*ft
                        r=metr(dg,dt,trm)
                        if r is None or r['thin']: continue
                        if best is None or r[crit]>best[0]: best=(r[crit],f'{ka} ⊕ {w:g}×{kf}',r,(dg,dt))
        if best is None: continue
        dg,dt=best[3]; ro=metr(dg,dt,tm)
        st[tm]=(dg-dt*C)[tm]; used|=tm; picks.append(best[1])
        rows.append(dict(fold=lbl,pick=best[1],ntrain=int(trm.sum()),
                         IS_sr=best[2]['sr'],IS_net=best[2]['net'],OOS_sr=ro['sr'],OOS_net=ro['net'],
                         nd=ro['nd'],mdd=ro['mdd'],thin=ro['thin'],
                         wfe=(ro['net']/max(tm.sum(),1))/((best[2]['net']/max(trm.sum(),1)) or np.nan)))
    x=st[used]; eq=np.cumsum(x); mdd=float(np.max(np.maximum.accumulate(eq)-eq)) if x.size else 0
    return rows,dict(net=float(x.sum()),sr=float(x.mean()/x.std()*np.sqrt(252)) if x.size and x.std()>0 else 0,
                     mdd=mdd,cal=float(x.sum()/mdd) if mdd>1e-9 else 0,nd=int(used.sum()),nuniq=len(set(picks)))

# ---------- STEP 1: is the reimplementation faithful? ----------
ref=json.load(open('wfa.json'))
print('\n=== STEP 1 - reproduce the stored output using the faulty grid ===')
allok=True
for nm,G,bl in (('A+M',GA,False),('DC-fade',GF_BUG,False),('Blend',None,True)):
    for crit in ('sr','cal'):
        rows,agg=run(GF_BUG,crit,blend=bl,G=G)
        r0=ref[f'{nm}|{crit}']
        ok=True
        for a,b in zip(rows,r0['folds']):
            if a['pick']!=b['pick'] or abs(a['OOS_net']-b['OOS']['net'])>0.02: ok=False
        ok&= abs(agg['net']-r0['agg']['net'])<0.05 and abs(agg['sr']-r0['agg']['sr'])<0.005
        allok&=ok
        print(f"  {nm+'|'+crit:>26}: {'match' if ok else 'DIFFERS'}   net {agg['net']:+.2f} vs {r0['agg']['net']:+.2f}"
              f"   SR {agg['sr']:.3f} vs {r0['agg']['sr']:.3f}")
print('\n  -> reimplementation is faithful' if allok else '\n  -> DOES NOT MATCH - STOP')
if not allok: raise SystemExit(1)
np.save('_ok.npy',np.array([1]))

# ---------- STEP 2: same harness, corrected grid ----------
print('\n=== STEP 2 - same harness, 30-cell fade grid with unambiguous keys ===')
NEW={}
for nm,G,bl in (('A+M',GA,False),('DC-fade',GF_FIX,False),('Blend',None,True)):
    for crit in ('sr','cal'):
        rows,agg=run(GF_FIX,crit,blend=bl,G=G); NEW[f'{nm}|{crit}']=(rows,agg)
        old=ref[f'{nm}|{crit}']['agg']
        d=agg['net']-old['net']
        print(f"  {nm+'|'+crit:>26}: net {agg['net']:+9.2f} (was {old['net']:+9.2f}, {d:+8.2f})"
              f"   SR {agg['sr']:.3f} (was {old['sr']:.3f})   MDD {agg['mdd']:.0f}")
print('\n=== TABLE 3 AFTER THE CORRECTION - Calmar criterion ===')
for nm in ('A+M','DC-fade','Blend'):
    rows,agg=NEW[f'{nm}|cal']
    print(f'\n{nm}')
    print(f"  {'fold':>7} {'train':>6} {'selected cell':<46} {'IS SR':>6} {'OOS SR':>7} {'OOS net':>9} {'MDD':>6} {'WFE':>6}")
    for r in rows:
        th='  thin' if r['thin'] else ''
        print(f"  {r['fold']:>7} {r['ntrain']:>6} {r['pick'][:46]:<46} {r['IS_sr']:>6.2f} {r['OOS_sr']:>7.2f}"
              f" {r['OOS_net']:>9.1f} {r['mdd']:>6.1f} {r['wfe']*100:>5.0f}%{th}")
    print(f"  stitched: net {agg['net']:+.0f}  Sharpe {agg['sr']:.2f}  MDD {agg['mdd']:.0f}  "
          f"distinct cells {agg['nuniq']}  positive folds {sum(1 for r in rows if r['OOS_net']>0)}/{len(rows)}")
json.dump({k:{'folds':v[0],'agg':v[1]} for k,v in NEW.items()},open('wfa_fixed.json','w'),indent=1,default=float)
print('\n→ wfa_fixed.json')

# ---------- STEP 3: corrected blend equity for Figure 4 ----------
rows,agg=run(GF_FIX,'cal',blend=True)
st=np.zeros(len(days)); used=np.zeros(len(days),bool)
for lbl,tm in FOLDS:
    trm=days<days[tm][0]
    if trm.sum()<MINTRAIN: continue
    best=None
    for ka,(ag,at) in GA.items():
        ra=metr(ag,at,trm)
        if ra is None or ra['thin']: continue
        for kf,(fg,ft) in GF_FIX.items():
            rf=metr(fg,ft,trm)
            if rf is None or rf['thin']: continue
            for w in WTS:
                dg=ag+w*fg; dt=at+w*ft
                r=metr(dg,dt,trm)
                if r is None or r['thin']: continue
                if best is None or r['cal']>best[0]: best=(r['cal'],f'{ka} ⊕ {w:g}×{kf}',r,(dg,dt))
    dg,dt=best[3]; st[tm]=(dg-dt*C)[tm]; used|=tm
x=st[used]; eq=np.cumsum(x)
json.dump(dict(eq=[round(float(v),3) for v in eq],days=[int(d) for d in days[used]]),
          open('blend_eq_fixed.json','w'))
print(f'\ncorrected equity: {len(eq)} sessions, final {eq[-1]:+.1f}, MDD {np.max(np.maximum.accumulate(eq)-eq):.1f}')
