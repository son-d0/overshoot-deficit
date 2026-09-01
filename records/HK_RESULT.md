# Hong Kong external test — result record

**Specification** `PREREG_external_test_v0.1.md` (`2b7760fe…`) as amended by v0.2 (`88d851ae…`),
v0.3 (`e03a2407…`), v0.4 (`3ef0ff45…`) and v0.5 (`8805f895…`). Analysis code `hk_pipeline.py`
(`6f8d8c36…`), hashed and timestamped before this execution.

**Executed** 2026-09-01. **Instrument** Dukascopy HKG.IDX/HKD.
**Window** 2021-02-25 to 2026-08-26, matching the VN30F1M discovery sample exactly.

## Acquisition and integrity — v0.3 §8 step 1

| | |
|---|---|
| hourly files acquired | **34,440 of 34,440 — none missing** |
| files carrying quotes | 20,058; the remaining 14,382 are hours the instrument does not quote |
| quotes | **63,154,002** |
| structurally malformed files | 0 |
| spread | 11.000 points at the 1st, 50th and 99th percentiles |
| quoting hours | 15 of 24 — Hong Kong 09:00–11:59, 13:00–00:59, with a genuine cessation over the 12:00 lunch hour |
| share of mid movement attributable to spread changes | 4.15% across the whole file set |

The last figure is higher than the 0.04% measured on a 200-hour sample of active trading, because the
full set includes the quiet late hours where the mid barely moves and an occasional spread change is a
larger share of a very small denominator. It does not affect the thresholds: a spread jump is never
large enough to manufacture a directional-change event at any of the six.

## Chronology, disclosed

Approximately 60% of the sample was inspected on 2026-08-31 under an implementation later found to be
defective, and again after the correction. Both inspections are recorded in `PEEK_2026-08-31.md`
(`b162d651…`). The full-sample result below is therefore **a pre-registered analysis with an interim
inspection of approximately 60% of the sample** (v0.4 §1), and not a blinded confirmatory result.

Everything after **2024-06-26** was never examined before this execution. It is reported first, as
required by v0.5 §5, and constitutes the only clean read in this study.

---

## Layer 2 — held-back period, never previously examined

2024-06-27 to 2026-08-26.

| level | legs | cells | H1 | H2 | H3 crossing | β_C |
|---|---|---|---|---|---|---|
| A, full tradable window | 291,255 | 24 | **pass**, F(5,13) = 244.8 | fail | **0.218** pass | −1.391 |
| B, HK day session | 195,442 | 20 | **pass**, F(5,10) = 37.7 | fail | **0.226** pass | −1.534 |
| C, sub-sessions | 192,676 | 23 | **pass**, F(5,13) = 82.0 | fail | **0.210** pass | −1.372 |

## Layer 1 — full sample

| level | legs | cells | H1 | H2 | H3 crossing | β_C |
|---|---|---|---|---|---|---|
| A, full tradable window | 792,101 | 26 | **pass**, F(5,15) = 171.6 | fail | **0.223** pass | −1.424 |
| B, HK day session | 543,852 | 25 | **pass**, F(5,14) = 88.8 | fail | **0.260** pass | −1.510 |
| C, sub-sessions | 536,397 | 27 | **pass**, F(5,16) = 50.0 | fail | **0.224** pass | −1.488 |

---

## H1 — compression: passes six times out of six

Band means fall monotonically at every level in both layers, with band effects between F = 37.7 and
F = 244.8 and p between 3.6×10⁻⁶ and 2.2×10⁻¹². The relation δ/R ↑ ⟹ ⟨ω⟩/δ ↓ is not a VN30F1M
phenomenon.

## H3 — the crossing: passes six times out of six, and tightly

| | crossing |
|---|---|
| VN30F1M | ≈ 0.20 |
| Hong Kong, held-back | 0.218, 0.226, 0.210 |
| Hong Kong, full sample | 0.223, 0.260, 0.224 |

Registered window [0.15, 0.30]. Five of the six Hong Kong values fall between 0.21 and 0.23 on a market
whose price level is twenty times VN30F1M's, with a different tick size, currency and participant
population. This is the strongest cross-market result in the study.

## H2 — threshold invariance: partial

The significance condition fails at every level in both layers, p_θ between 0.000 and 0.033. **All
three magnitude criteria pass at every level in both layers**: SS_θ/SS_band between 0.036 and 0.150
against a 0.35 threshold, and within-over-between between 0.194 and 0.298 against 0.40.

Reported under v0.4 §4 as registered: **conditioning on δ/R absorbs most, but not all, of the threshold
dependence.** With between two and three times VN30F1M's leg count, small threshold effects become
detectable; the magnitude criteria exist for that reason and they hold.

## H4 — the compression ordering: fails, and the failure is persuasive

Predicted β_C(sub) < β_C(day) < β_C(full).

    held-back    C −1.372    B −1.534    A −1.391
    full sample  C −1.488    B −1.510    A −1.424

Half the prediction holds and half does not. **The widest window does have the shallowest slope in both
layers**, which is the direction finite-space compression predicts. But narrowing from the day session
to the sub-session does not deepen it further; in the held-back period it reverses.

v0.5 §6 fixed the reading before the data existed: H1 and H3 alive with H4 failing on the held-back
period makes the failure persuasive, because it survives a corrected implementation on data never
previously examined. That condition is met.

v0.3 §7 named a candidate for the reversal in advance, and it was written before any Hong Kong data was
downloaded: narrowing the window also raises the frequency of directional-change resets and truncates
more events at the boundary. Those effects are strongest at level C. The window ladder cannot separate
them from available price space, and this study does not claim to.

## What this establishes, and what it does not

**Established.** A conditional scaling relation indexed by δ/R, replicating across two markets, with a
unity crossing near 0.21–0.23 against 0.20 on the discovery market.

**Not established.** That finite-session spatial compression is the cause. The one direct test of that
interpretation was pre-registered, run once on unseen data, and did not support it.

**Not claimed, by rule.** This is not exchange-level replication. HKG.IDX/HKD is a broker's quote
stream, its mid is not a traded price, and v0.1 §8.3 and v0.2 §4 forbid describing it as replication
evidence. That restriction was written before any result existed and applies to the favourable
findings above as much as to the unfavourable one.

## Consequence for the manuscript, as registered in v0.5 §5

The mechanism sentence is rewritten to the wording fixed in advance:

> a cross-market conditional scaling relation indexed by δ/R; finite-session spatial compression is a
> natural explanation on VN30F1M, but a pre-registered Hong Kong window experiment does not support
> that causal interpretation.
