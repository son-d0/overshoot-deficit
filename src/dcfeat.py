"""Fast, faithful port of TWWH dc.py + causal/ex-post label split.

Outputs per tick i:
  tmv[i]  = (P_i - ext_n) / (ext_n * theta)      -- CAUSAL (ext_n = last CONFIRMED extreme)
  tt[i]   = ticks since last confirmed extreme    -- CAUSAL
  cau[i]  = real-time trend_status at i (+1 up / -1 down)   -- CAUSAL
  exp_[i] = TWWH's FINAL event label after retroactive rewrite -- NON-CAUSAL (leaks)
            0=Up Overshoot 1=Down DCC 2=Down Overshoot 3=Up DCC
"""
import numpy as np
from numba import njit

@njit(cache=True)
def _dc(prices, theta, tmv, tt, cau, exp_):
    n = prices.shape[0]
    ext_point_n = prices[0]; curr_max = prices[0]; curr_min = prices[0]
    tp_max = 0; tp_min = 0; up = True; T = 0
    for i in range(n):
        tmv[i] = (prices[i] - ext_point_n) / (ext_point_n * theta)
        tt[i]  = T
        T += 1
        if up:
            cau[i] = 1; exp_[i] = 0
            if prices[i] < (1.0 - theta) * curr_max:
                up = False; curr_min = prices[i]
                ext_point_n = curr_max; T = i - tp_max
                for j in range(1, i - tp_max + 1):
                    exp_[i + 1 - j] = 1          # 'Downward DCC'
            else:
                if prices[i] > curr_max:
                    curr_max = prices[i]; tp_max = i
        else:
            cau[i] = -1; exp_[i] = 2
            if prices[i] > (1.0 + theta) * curr_min:
                up = True; curr_max = prices[i]
                ext_point_n = curr_min; T = i - tp_min
                for j in range(1, i - tp_min + 1):
                    exp_[i + 1 - j] = 3          # 'Upward DCC'
            else:
                if prices[i] < curr_min:
                    curr_min = prices[i]; tp_min = i

def dc_variables(prices, theta):
    p = np.ascontiguousarray(np.asarray(prices, np.float64))
    n = p.shape[0]
    tmv = np.empty(n); tt = np.empty(n, np.int64)
    cau = np.empty(n, np.int8); exp_ = np.empty(n, np.int8)
    _dc(p, float(theta), tmv, tt, cau, exp_)
    return tmv, tt, cau, exp_

def dc_variables_by_group(prices, group, theta):
    """Run the DC recursion independently within each contiguous group (= session)."""
    p = np.asarray(prices, np.float64); g = np.asarray(group)
    n = p.shape[0]
    tmv = np.empty(n); tt = np.empty(n, np.int64)
    cau = np.empty(n, np.int8); exp_ = np.empty(n, np.int8)
    bnd = np.flatnonzero(np.concatenate(([True], g[1:] != g[:-1])))
    bnd = np.concatenate((bnd, [n]))
    for k in range(len(bnd) - 1):
        a, b = bnd[k], bnd[k+1]
        a_, b_ = int(a), int(b)
        t_, tt_, c_, e_ = dc_variables(p[a_:b_], theta)
        tmv[a_:b_] = t_; tt[a_:b_] = tt_; cau[a_:b_] = c_; exp_[a_:b_] = e_
    return tmv, tt, cau, exp_
