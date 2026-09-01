# PREREG External Test — Amendment v0.3

**Purpose** Elevation of the Dukascopy HKG.IDX/HKD dataset from exploratory screening to a
pre-specified **within-feed mechanism test**.

**Amends** `PREREG_external_test_v0.1.md` (SHA-256 `2b7760fe…c397347`) and
`PREREG_external_test_v0.2_amendment.md` (SHA-256 `88d851ae…2b8ebbab`), both of which remain in force
in every respect not modified below and are retained unchanged for the audit trail.

**Date** 2026-08-30
**Author** Son Do, Noralabs, Thai Nguyen University of Information and Communication Technology

---

## 0. Timing disclosure

Download of the HKG.IDX/HKD raw files began **before** this amendment was written. This amendment
therefore makes no claim to have been registered before data acquisition.

In the course of verifying the file format and the download pipeline, a small number of raw
observations were displayed: the CSV column schema; record counts for two individual hours; and six
quoted prices from 2021-03-01. That is the complete extent of Hong Kong data seen by the author.

Beyond it, at the moment this amendment is frozen: no Hong Kong observation has been summarised,
plotted, aggregated, processed through the directional-change algorithm, or used in any statistical
test; no session has been constructed; no range, ratio, overshoot or ⟨ω⟩/δ has been computed at any
threshold.

Accordingly this amendment is registered **before any inspection, summary statistic, directional-change
computation, visualisation or hypothesis test on the Hong Kong data**, and not before data acquisition
or before incidental format verification. Readers may judge for themselves whether six quoted prices
and two record counts could inform H1–H4; the author's position is that they could not, and states the
facts rather than the conclusion.

## 1. What changes

Amendment v0.2 classified HKG.IDX/HKD solely as a zero-cost screening dataset. Version 0.3
additionally designates it as a within-feed test of the available-price-space mechanism.

It remains explicitly **not** an exchange-level replication dataset. The confirmatory external
replication specified in v0.1 and v0.2 remains exchange-traded HSI futures tick data.

## 2. Motivation

The spatial-compression interpretation predicts that normalised overshoot should become progressively
more compressed as the directional-change threshold consumes a larger fraction of the price space
available within the measurement window.

HKG.IDX/HKD permits this mechanism to be tested on a single price feed under multiple pre-defined
temporal windows, avoiding cross-instrument differences in price scale and feed construction.

## 3. Pre-specified window hierarchy

Three levels will be evaluated.

**Level A — near-24-hour broker feed.** The full tradable Dukascopy window, subject only to
source-defined maintenance and unavailable periods.

**Level B — Hong Kong regular day window.** The morning and afternoon regular Hong Kong trading
windows combined into one session.

**Level C — sub-session windows.** Morning and afternoon treated separately. Directional-change state
is reset at the beginning of each sub-session and R_s is computed within that same sub-session.

No window boundary may be altered after Hong Kong data inspection.

## 4. Predictions

H1–H4 remain unchanged. The additional mechanism prediction is directional:

    |β_C| sub-session  >  |β_C| day  >  |β_C| near-24h

equivalently, since β_C < 0,

    β_C, sub-session  <  β_C, day  <  β_C, near-24h

The comparison will be made only on common δ/R support.

Failure of this ordering weakens the finite-available-price-space interpretation but does not
invalidate the VN30F1M empirical relation.

## 5. Unchanged specifications

No change is made to: the six θ values; the δ/R bin boundaries; the directional-change algorithm;
H1–H4; the ANOVA specification; the H2 magnitude criteria; the GDO crossing criterion; the definition
of β_C; or the VN30F1M benchmark values.

## 6. Interpretation constraint

Results from HKG.IDX/HKD may support or weaken the mechanistic interpretation of spatial compression.
They shall **not** be described as independent exchange replication, as HSI futures replication, or as
evidence of cross-market external validity at the exchange level. That claim remains reserved for the
previously specified exchange-traded HSI futures dataset.

## 7. Known limitation

Changing the analysis window also changes boundary censoring, event truncation and
directional-change reset frequency. The within-feed comparison is therefore **not** interpreted as a
perfectly controlled intervention on available price space alone. Sub-session windows reset the
directional-change state more often and truncate more events at the boundary, and those effects
accompany the change in R_s rather than being separable from it. They will be reported as limitations
and no post-hoc correction will be introduced.

## 8. Execution order, frozen

    raw integrity check  →  session construction  →  H1 / H2  →  β_C(24h), β_C(day), β_C(AM/PM)

One pipeline, run once, in that order. If the predicted ordering does not appear, no window, boundary
or threshold is revised. That constraint is the entire purpose of this document.
