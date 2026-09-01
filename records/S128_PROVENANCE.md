# Provenance of the adaptive-threshold figures in Section 7

Section 7 opens with four numbers from an exploratory comparison: gross per turnover unit of 0.657
for a causally estimated adaptive threshold against 1.242 for a fixed one, Sharpe of 2.00 against
2.59, and a maximum drawdown that roughly doubles. This record exists because those numbers are
**auditable rather than publicly reproducible**, and the distinction should be stated rather than
left for a reader to discover.

## Why they are not publicly reproducible

The comparison consumes the VN30F1M one-second tick panel. That series is licensed and we are not
free to redistribute it or any derivative from which a price level can be recovered, which is the
same restriction that governs the released leg extract. No public input reproduces these figures.

## What is auditable

The transformation is in this repository. `src/adaptive_threshold_probe.py` is a standalone rewrite
of the internal script, depending on nothing outside this repository except the panel itself, and it
reproduces the internal original row for row — all eleven configurations, every column identical. A
reader can therefore check what was computed, and check that the estimate is causal: the trailing
range median is built with `.shift(1)` before `.rolling(20)`, so no session contributes to its own
threshold.

The internal library `dclib.py` is not distributed. The probe does not need it: the original used it
for one function, which loaded three columns from the panel, and the probe does that directly.

## Inputs, by hash

| artifact | SHA-256 |
|---|---|
| `panel.npz  (frozen specification panel, 1,255 sessions, not distributed)` | `0d60c1e41a4b01e29d7a951366d4be83d93a60425acbef6c472e508c1c2faa04` |
| `s128_adaptive.py  (internal original, not distributed)` | `c3d1e695102ee33a98ce0575179ce218f0c7bed320d68f3c5ac90a9183cf4776` |
| `dclib.py  (internal library, used only for its load(), not distributed)` | `1450b8adb37de165716862861c945bc1632700c70a0f46b8ef1b267e2fe243f5` |
| `src/adaptive_threshold_probe.py  (this repository)` | `abe2f7175ef9eaa36d13c4bb3250ac46ee18c4b771c680b35af8e53e1b74a55d` |
| `src/dcevent.py  (this repository)` | `a433cb9debf89809592679eda93fd631c512024f34b85937fbadc1bb4999847a` |
| `src/costs.py  (this repository)` | `f6a548fd196e386dcd9084ff334d970d9c72471c98153246b3108da2946e116e` |

## Command and output, re-run 2026-09-01

```
python3 src/adaptive_threshold_probe.py panel.npz
```

```
cost 0.175/leg | entries after 09:45

                                             legs  legs/day  gross/turn     net     SR    MDD  yrs+
  --- FIXED theta (baseline) ---
  fixed theta = 5e-03                        2749      1.66       0.464     783   1.37    214   4/4
  fixed theta = 7e-03                        1279      0.73       1.242    1283   2.59    154   4/4
  fixed theta = 1e-02                         484      0.23       2.160     762   2.02    100   4/4
  --- ADAPTIVE theta: delta = ratio x trailing 20-session range ---
  delta = 0.25 x Rhat  (causal)              6635      5.45       0.005   -1514  -1.84   1567   0/4
  delta = 0.35 x Rhat  (causal)              3225      2.60       0.276     429   0.64    429   3/4
  delta = 0.45 x Rhat  (causal)              1739      1.40       0.657    1106   2.00    300   4/4
  delta = 0.55 x Rhat  (causal)              1005      0.80       0.868     904   1.76    241   4/4
  --- adaptive theta, no new entries after 14:15 ---
  delta = 0.35 x Rhat, stop 14:15            3027      2.41       0.221     181   0.32    371   3/4
  delta = 0.45 x Rhat, stop 14:15            1646      1.31       0.592     892   1.92    262   4/4
  delta = 0.55 x Rhat, stop 14:15             963      0.75       0.801     773   1.88    199   4/4
```

The manuscript quotes the fixed 7e-03 row against the adaptive 0.45 row: gross per turn 1.242 against
0.657, Sharpe 2.59 against 2.00, drawdown 154 against 300, which is the doubling it describes.
