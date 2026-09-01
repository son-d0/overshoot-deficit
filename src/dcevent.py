"""Chen & Tsang (2020) event-level DC decomposition, causal.

For each confirmed trend n we record, using ONLY information available at the
confirmation tick i_conf(n):
    i_ext_prev, i_dcc, i_ext, i_conf   (tick indices)
    TMV_n = (P_ext_n - P_ext_{n-1}) / (P_ext_{n-1} * theta)      >= 1 in abs
    T_n   = i_ext_n - i_ext_{n-1}          ticks to complete the trend
    R_n   = TMV_n / T_n                    time-adjusted return of the trend
    OSV_n = |TMV_n| - 1                    overshoot in theta units
NOTE: TMV_n / T_n / OSV_n describe a trend that is only KNOWN at i_conf(n+1)...
      no: trend n ends at the extreme P_ext_n, which is confirmed at i_conf where
      the OPPOSITE direction is triggered. So (TMV_n,T_n,R_n) is known at i_conf.
      We store i_conf as the 'available_from' index -- any use of these features
      at a tick < i_conf is LOOK-AHEAD.
"""
import numpy as np
from numba import njit

@njit(cache=True)
def _ev(prices, theta, out_i, out_v, cap):
    n = prices.shape[0]; k = 0
    ext_p = prices[0]; ext_i = 0
    curr_max = prices[0]; curr_min = prices[0]
    tp_max = 0; tp_min = 0; up = True
    for i in range(n):
        if up:
            if prices[i] < (1.0 - theta) * curr_max:
                # trend that ENDED at tp_max (an up trend) is now confirmed
                if k < cap:
                    out_i[k,0]=ext_i; out_i[k,1]=tp_max; out_i[k,2]=i; out_i[k,3]=1
                    out_v[k,0]=(curr_max-ext_p)/(ext_p*theta)
                    out_v[k,1]=tp_max-ext_i
                    k+=1
                ext_p=curr_max; ext_i=tp_max
                up=False; curr_min=prices[i]; tp_min=i
            elif prices[i] > curr_max:
                curr_max=prices[i]; tp_max=i
        else:
            if prices[i] > (1.0 + theta) * curr_min:
                if k < cap:
                    out_i[k,0]=ext_i; out_i[k,1]=tp_min; out_i[k,2]=i; out_i[k,3]=-1
                    out_v[k,0]=(curr_min-ext_p)/(ext_p*theta)
                    out_v[k,1]=tp_min-ext_i
                    k+=1
                ext_p=curr_min; ext_i=tp_min
                up=True; curr_max=prices[i]; tp_max=i
            elif prices[i] < curr_min:
                curr_min=prices[i]; tp_min=i
    return k

def events(prices, theta, offset=0):
    p=np.ascontiguousarray(np.asarray(prices,np.float64)); n=p.shape[0]
    cap=max(16,n)
    oi=np.zeros((cap,4),np.int64); ov=np.zeros((cap,2),np.float64)
    k=_ev(p,float(theta),oi,ov,cap)
    oi=oi[:k].copy(); ov=ov[:k].copy()
    oi[:,:3]+=offset
    return dict(i_ext_prev=oi[:,0], i_ext=oi[:,1], i_conf=oi[:,2], dirn=oi[:,3],
                TMV=ov[:,0], T=ov[:,1])

def events_by_group(prices, group, theta):
    p=np.asarray(prices,np.float64); g=np.asarray(group); n=p.shape[0]
    bnd=np.flatnonzero(np.concatenate(([True],g[1:]!=g[:-1]))); bnd=np.concatenate((bnd,[n]))
    parts=[]
    for k in range(len(bnd)-1):
        a,b=int(bnd[k]),int(bnd[k+1])
        if b-a<3: continue
        parts.append(events(p[a:b],theta,offset=a))
    return {k:np.concatenate([q[k] for q in parts]) for k in parts[0]}
