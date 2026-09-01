# HKG.IDX/HKD — raw integrity check, partial

**Runs** step 1 of `PREREG_external_test_v0.3_amendment.md` §8
(SHA-256 `e03a2407f90856d2381af91b2e5f8c956e6e47db7e67422bd25fd26d44a1eb89`).
**Date** 2026-08-31. **Coverage** 9,083 of 34,440 hourly files, 26% of the acquisition window.

**Purpose** to decide whether to continue acquiring the remaining 74%, not to look at results.
No directional-change state was constructed, no range, ratio or ⟨ω⟩/δ was computed, and none of
H1–H4 was touched.

## Measured, on 200 randomly sampled hours, 555,562 quotes

| quantity | value |
|---|---|
| spread, p1 through p99 | **11.000 points**, i.e. constant in over 98% of quotes |
| spread ÷ price | 0.045% |
| quotes at which the spread changes | 0.04% |
| share of mid movement attributable to spread changes | **0.04%** |
| median non-zero mid increment | 0.871 points on a price of 24,235 |
| steps where half the spread change exceeds δ | **0.0000%, at every one of the six thresholds** |

## Resolution against the six thresholds

| θ | δ (points) | δ ÷ median mid increment |
|---|---|---|
| 5×10⁻⁴ | 12.1 | 13.9× |
| 1×10⁻³ | 24.2 | 27.8× |
| 2×10⁻³ | 48.5 | 55.6× |
| 5×10⁻³ | 121.2 | 139.1× |
| 7×10⁻³ | 169.6 | 194.8× |
| 1×10⁻² | 242.4 | 278.2× |

For comparison, VN30F1M at its narrowest threshold gives δ = 0.6 points on a 0.1 tick, a ratio of 6×.
The Hong Kong feed is better resolved at the end where resolution matters, by roughly a factor of two.

## Verdict

**Continue acquisition. All six thresholds are usable.** A near-constant spread does not perturb the
mid path, and spread jumps are never large enough to manufacture a directional-change event at any
threshold. The measurement confound that disqualified one-minute bars for the confirmatory dataset
does not arise here.

## Structural difference to record in the write-up

VN30F1M is measured on **transaction prices**. HKG.IDX/HKD is measured on the **mid of a broker's
quotes**. A quote mid is not a traded price. This belongs in the limitations regardless of what the
results show, and is separate from the rule that this feed is not exchange-level replication evidence.
