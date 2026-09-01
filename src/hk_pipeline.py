"""PIPELINE ĐÃ KHOÁ  [sửa 2026-08-31: R["df"] → R["df_band"], lỗi CHỈ ở dòng in,
không đại lượng nào bị ảnh hưởng; phát hiện khi chạy thử --partial trước lượt chạy thật]
[2026-08-31: v0.5 §2 — Level A nhóm theo CỬA SỔ GIAO DỊCH (09:00→01:00), không theo ngày lịch.
 Sửa lỗi hiện thực, theo đúng câu chữ đặc tả v0.3 §3. Đóng dấu SAU amendment 8805f895...]
[2026-08-31: thêm báo cáo HAI LỚP theo v0.4 §3 — Lớp 2 = phần sau 2024-06-26 chưa từng nhìn.
 Tiêu chí KHÔNG đổi.] — PREREG_external_test_v0.3_amendment.md §8, hash e03a2407...
Thứ tự bắt buộc: kiểm toàn vẹn → dựng phiên → H1/H2 → β_C(24h), β_C(ngày), β_C(sáng/chiều).
Một lượt. Không cửa sổ, ngưỡng, biên băng hay bộ lọc nào được sửa sau khi thấy kết quả.
Chạy: python3 hk_pipeline.py            (đòi tải xong 100%)
      python3 hk_pipeline.py --partial  (chạy trên phần đã có, KẾT QUẢ KHÔNG ĐƯỢC BÁO CÁO)
"""
import lzma,glob,os,sys,json,numpy as np,pandas as pd,datetime as dt,warnings
warnings.filterwarnings('ignore'); sys.path.insert(0,'../results_v7')
from scipy import stats
import dc_pipeline as Q                      # sáu θ, biên băng, sàn 60 nhịp, ANOVA, β_C — dùng chung với VN30F

PARTIAL='--partial' in sys.argv
SEEN_ONLY='--seen-only' in sys.argv     # v0.5 §5: chốt chặn, chỉ lấy phần ĐÃ công bố là đã xem
HELD_ONLY='--held-back-only' in sys.argv  # v0.5 §5.2: chạy RIÊNG phần giữ lại, TRƯỚC toàn mẫu
SEEN_UPTO=20240626                      # ranh giới nhìn giữa chừng, v0.4 §2
HK=8*3600                                    # HK = UTC+8, không có giờ mùa hè
AM=(9*3600+15*60, 12*3600)                   # 09:15–12:00 HKT   (prereg §2.2)
PM=(13*3600,      16*3600+30*60)             # 13:00–16:30 HKT

# ---------- 1. ĐỌC + KIỂM TOÀN VẸN ----------
def load():
    fs=sorted(f for f in glob.glob('raw/**/*.bi5',recursive=True) if os.path.getsize(f)>0)
    if SEEN_ONLY:
        n0=len(fs)
        fs=[f for f in fs if int(''.join(f.split('/')[1:4]))<=SEEN_UPTO]
        print(f'    [chốt chặn --seen-only] giữ {len(fs):,}/{n0:,} tệp, bỏ mọi thứ sau {SEEN_UPTO}')
    print(f'[1] {len(fs):,} tệp giờ có dữ liệu')
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
    print(f'    {len(T):,} báo giá, loại {int((~ok).sum())} bản ghi không hợp lệ')
    T,M,S=T[ok],M[ok],S[ok]
    print(f'    spread trung vị {np.median(S):.3f} điểm; nhiễu spread trong mid '
          f'{np.abs(np.diff(S)/2).mean()/np.abs(np.diff(M)).mean()*100:.2f}%')
    print(f'    giá {M.min():.1f}–{M.max():.1f}; khoảng thời gian '
          f'{dt.datetime.utcfromtimestamp(T[0]).date()} → {dt.datetime.utcfromtimestamp(T[-1]).date()}')
    return T,M

# ---------- 2. DỰNG PHIÊN, LƯỚI 1 GIÂY ----------
# v0.5 §2: đơn vị là CỬA SỔ GIAO DỊCH (09:00 HK → 01:00 hôm sau), KHÔNG phải ngày lịch.
# Cửa sổ vắt qua nửa đêm, nên nhóm theo lịch sẽ reset DC giữa phiên — đó là lỗi đã sửa.
WIN0=9*3600                                   # gốc cửa sổ = 09:00 giờ HK

def panel(T,M):
    """Lưới 1 giây theo cửa sổ giao dịch, ffill TRONG cửa sổ, không bfill."""
    tl=T+HK
    win=(tl-WIN0)//86400                       # mã cửa sổ giao dịch
    ws=(tl-WIN0)%86400                         # giây trong cửa sổ, 0 = 09:00 HK
    df=pd.DataFrame(dict(win=win,ws=ws,p=M)).groupby(['win','ws'],as_index=False).last()
    out=[]
    for w,g in df.groupby('win',sort=True):
        a,b=int(g.ws.min()),int(g.ws.max())
        idx=np.arange(a,b+1)
        p=pd.Series(np.nan,index=idx); p.loc[g.ws.values]=g.p.values
        p=p.ffill()                            # CHỈ ffill
        m=p.notna().values
        out.append(pd.DataFrame(dict(win=int(w),ws=idx[m],p=p.values[m])))
    P=pd.concat(out,ignore_index=True)
    P['sec']=(P.ws+WIN0)%86400                 # giây trong ngày HK, dùng cho lọc mức B/C
    print(f'[2] {len(P):,} quan sát lưới-1-giây trên {P.win.nunique():,} cửa sổ giao dịch')
    return P

# ---------- 3. BA MỨC CỬA SỔ ----------
def levels(P):
    inAM=(P.sec>=AM[0])&(P.sec<AM[1]); inPM=(P.sec>=PM[0])&(P.sec<PM[1])
    L={}
    L['A_full']  = (P, P.win.values)                                   # cửa sổ giao dịch đầy đủ
    B=P[inAM|inPM]
    L['B_day']   = (B, B.win.values)                                   # phiên ngày HK gộp
    C=P[inAM|inPM].copy()
    C['half']=np.where((C.sec>=AM[0])&(C.sec<AM[1]),0,1)
    L['C_sub']   = (C, (C.win.values*2+C.half.values))                 # từng nửa phiên
    for k,(d,g) in L.items():
        print(f'    {k}: {len(d):,} quan sát, {len(np.unique(g)):,} nhóm')
    return L

# ---------- 4. H1 / H2 / H3 / β_C ----------
def analyse(name,d,g):
    L=Q.legs(d.p.values,g); C=Q.cells(L); R=Q.collapse(C)
    print(f'\n=== {name} ===  {len(L):,} nhịp, {R["ncell"]} ô ≥{Q.MIN_LEGS}')
    for b,r in R['band_means'].iterrows(): print(f'   {b}  ω/δ = {r.m:.3f}')
    print(f'   H1  band|θ F{R["df_band"]} = {R["F_band"]:.2f}  p = {R["p_band"]:.3g}   '
          f'đơn điệu giảm: {R["monotone"]}')
    print(f'   H2  p_θ = {R["p_theta"]:.3f} (>0.05)   SS_θ/SS_band = {R["ss_ratio"]:.3f} (<0.35)   '
          f'trong/giữa = {R["within_between"]:.3f} (<0.40)')
    h2=(R['p_band']<0.01)and(R['p_theta']>0.05)and(R['ss_ratio']<0.35)and(R['within_between']<0.40)
    bm=R['band_means']
    cross=np.nan
    for i in range(len(bm)-1):
        a,b2=bm.m.iloc[i],bm.m.iloc[i+1]
        if (a-1)*(b2-1)<0:
            f=(a-1)/(a-b2); cross=bm.mid.iloc[i]+f*(bm.mid.iloc[i+1]-bm.mid.iloc[i]); break
    print(f'   H3  cắt ω/δ=1 tại δ/R = {cross:.3f}   (tiêu chí [0.15, 0.30])')
    print(f'   β_C = {R["beta_C"]:.3f}  (SE {R["se"]:.3f})')
    print(f'   → H1 {"ĐẠT" if R["p_band"]<0.01 and R["monotone"] else "TRƯỢT"}'
          f' · H2 {"ĐẠT" if h2 else "TRƯỢT"}'
          f' · H3 {"ĐẠT" if 0.15<=cross<=0.30 else "TRƯỢT"}')
    return R,C

HELD_BACK=20240626        # v0.4 §2: mọi phiên SAU ngày này chưa từng được nhìn

def report(tag,P):
    LV=levels(P); res={}
    for k,(d,g) in LV.items(): res[k]=analyse(f'{tag} · {k}',d,g)
    print('\n'+'-'*62); print(f'{tag} — §4 THỨ TỰ ĐỘ NÉN (miền chung)')
    common=set.intersection(*[set(C.band) for _,C in res.values()])
    order=[]
    for k in ('C_sub','B_day','A_full'):
        R,C=res[k]; c=C[C.band.isin(common)]
        bm=c.groupby('band').agg(mid=('mid','first'),m=('mean','mean')).sort_values('mid')
        sl=stats.linregress(bm['mid'],bm['m']).slope if len(bm)>=3 else np.nan
        order.append(sl); print(f'   β_C({k}) = {sl:.3f}')
    ok=order[0]<order[1]<order[2]
    print(f'   dự đoán nửa phiên < ngày < 24h: {"ĐẠT" if ok else "TRƯỢT"}')
    return res,order

def main():
    n=len(glob.glob('raw/**/*.bi5',recursive=True))
    if n<34440 and not PARTIAL:
        print(f'CHƯA TẢI XONG: {n:,}/34.440 tệp. Dùng --partial để chạy thử (kết quả KHÔNG báo cáo).')
        return
    if PARTIAL: print('*** CHẠY THỬ TRÊN DỮ LIỆU CHƯA ĐỦ — KẾT QUẢ KHÔNG ĐƯỢC BÁO CÁO ***')
    if SEEN_ONLY: print('*** CHỈ PHẦN ĐÃ XEM (≤2024-06-26) — không phơi thêm dữ liệu nào ***')
    print()
    T,M=load(); P=panel(T,M)
    import datetime as _dt
    if not HELD_ONLY:
        print('\n'+'='*62)
        print('LỚP 1 — TOÀN MẪU  (v0.4 §1: phân tích đã pre-register, CÓ nhìn giữa chừng ~60%)')
        print('='*62)
        r1,o1=report('LỚP 1',P)
    else:
        r1,o1={},[np.nan]*3
        print('\n[--held-back-only] BỎ QUA Lớp 1: v0.5 §5.2 yêu cầu chạy phần giữ lại TRƯỚC.')
    cut=(int(_dt.datetime(HELD_BACK//10000,HELD_BACK//100%100,HELD_BACK%100,
                          tzinfo=_dt.timezone.utc).timestamp())+HK-WIN0)//86400
    hb=P[P.win>cut]
    print('\n'+'='*62)
    print(f'LỚP 2 — PHẦN CHƯA TỪNG NHÌN  (sau {HELD_BACK}, {hb.win.nunique():,} cửa sổ)')
    print('   tiêu chí y hệt Lớp 1; không đổi gì vì đã thấy 60% — v0.4 §3')
    print('='*62)
    if SEEN_ONLY:
        print('   BỎ QUA: chốt chặn --seen-only cấm chạm phần giữ lại.')
        return
    r2,o2=report('LỚP 2',hb) if hb.win.nunique()>=60 else ({},[np.nan]*3)
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
