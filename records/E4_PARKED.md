# E4 — Parked hypothesis: deepest reachable band

**Status** NOT RUN. Deliberately parked on 2026-08-30.

**Origin** Generated *after* seeing the E3 result. It is therefore post-hoc with respect to the
VN30F1M dataset and cannot be tested on that dataset without becoming mining.

## The hypothesis

E3's adaptive rule pins δ*/R̂ at 0.32 by construction, so it occupies one band permanently. The two
fixed thresholds that beat it (0.7%, 1.0%) are large enough to reach the 0.45–0.65 band, where
⟨ω⟩/δ ≈ 0.49, on the narrow-range sessions where the deficit is deepest — and the 1.0% arm reaches a
break-even cost of 2.31 per leg, more than double the next best.

**H-E4.** The correct control objective is not a fixed target band but the deepest band reachable on
the session. A rule targeting δ*/R̂ ≈ 0.50 rather than 0.32, or one that maximises the band subject to
a minimum round-trip count, would beat both the E3 adaptive arm and the best fixed threshold.

## Why it is parked and not run

1. It was formulated by inspecting the outcome of a completed test on the same data. Running it now on
   VN30F1M would be selecting a parameter on the basis of a result already observed.
2. `PREREG_E3_threshold_control_v1.0.md` §7.2 forbids revising the 0.32 target on the basis of any E3
   result.
3. The VN30F1M tick history has now been examined by the discovery study, E1, E2 and E3. Its capacity
   to support a further independent test is close to exhausted.

## Conditions under which it may be run

Either (a) on a market other than VN30F1M, pre-registered before that market's data is examined; or
(b) on VN30F1M after a forward record of sufficient length exists to serve as the test window, with
the rule frozen before that window opens.

Not on the historical VN30F1M sample.
