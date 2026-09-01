"""Build the released Hong Kong leg extract from the Dukascopy archive.

The extract exists so that Section 8 can be checked without the 28.6-hour acquisition. It carries
one row per directional-change leg, at each of the three pre-registered window levels, with the two
coordinates the analysis uses and the identifiers needed to reproduce the held-back split.

The session construction is not reimplemented here. This script loads `load()`, `panel()` and
`levels()` out of the timestamped pipeline itself, by reading its source and cutting it before
`main()`, so the grid the extract is built on is the grid the pipeline analysed.

    python3 src/build_hk_extract.py          # expects raw/ beside it, writes dc_legs_hkgidx.csv.gz
"""
import os, sys, re
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
if not os.path.isdir('raw'):
    sys.exit("This script needs the Dukascopy archive in raw/. Fetch it with src/dl_hk.py first;\n"
             "the acquisition takes about 28.6 hours. The extract it produces is already released\n"
             "as data/dc_legs_hkgidx.csv.gz, so running this is only necessary to rebuild it.")

import dc_pipeline as Q

src = open(os.path.join(HERE, 'hk_pipeline.py'), encoding='utf-8').read()
cut = src.index('# ---------- 4.')
ns  = {'__name__': 'hk_loader', '__file__': os.path.join(HERE, 'hk_pipeline.py')}
exec(compile(src[:cut], 'hk_pipeline.py', 'exec'), ns)          # load, panel, levels, constants

T, M = ns['load']()
P    = ns['panel'](T, M)
HK, WIN0 = ns['HK'], ns['WIN0']
HELD_BACK = int(re.search(r'^HELD_BACK\s*=\s*(\d+)', src, re.M).group(1))   # read, not restated

import datetime as dt
CUT = (int(dt.datetime(HELD_BACK // 10000, HELD_BACK // 100 % 100, HELD_BACK % 100,
                       tzinfo=dt.timezone.utc).timestamp()) + HK - WIN0) // 86400

rows = []
for level, (d, g) in ns['levels'](P).items():
    L = Q.legs(d.p.values, g)
    win = L.grp.values // 2 if level == 'C_sub' else L.grp.values     # C_sub packs win*2+half
    rows.append(pd.DataFrame(dict(level=level, theta=L.theta.values, win=win.astype(np.int32),
                                  ratio=L.ratio.values, omega_over_delta=L.wd.values)))
    print(f'  {level}: {len(L):,} legs')

D = pd.concat(rows, ignore_index=True)
assert not {'delta', 'overshoot', 'session_range'} & set(D.columns)
D.to_csv('dc_legs_hkgidx.csv.gz', index=False, compression='gzip', float_format='%.17g')
print(f'\n  dc_legs_hkgidx.csv.gz  {len(D):,} rows  '
      f'{os.path.getsize("dc_legs_hkgidx.csv.gz")/1048576:.1f} MB')
print(f'  held-back split: win > {CUT}')
