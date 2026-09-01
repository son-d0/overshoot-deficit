# Pre-registration — External Test of the Overshoot-Compression Hypothesis

**Version** v0.1
**Status** FROZEN before inspection of any cross-market directional-change results
**Discovery market** VN30F1M index futures, 1,340 tick-level sessions, 2021-02-25 to 2026-08-26
**Author** Son Do, Noralabs, Thai Nguyen University of Information and Communication Technology

---

## 0. Motivating result (discovery market, already observed)

On VN30F1M the mean normalised overshoot ⟨ω⟩/δ varies systematically with δ/R_s, the
directional-change threshold measured against the session's realised range. After conditioning on
that ratio, threshold identity θ carries no detectable effect, while the ratio band does. Measured
values on the discovery market, which serve as the reference for every criterion below:

| quantity | VN30F1M |
|---|---|
| p, band effect (two-way ANOVA on cell means) | 3.19 × 10⁻⁹ |
| p, θ effect | 0.118 |
| SS_θ / SS_band | 0.046 |
| within-band spread ÷ between-band range | 0.219 |
| compression slope β_C | −1.768 (SE 0.112, R² 0.984) |
| ⟨ω⟩/δ crossing unity at δ/R_s ≈ | 0.20 |
| range of ⟨ω⟩/δ observed | 1.342 → 0.492 |

---

## 1. Hypotheses, locked

**H1 — Spatial compression (primary).** As x = δ/R_s increases, y = ⟨ω⟩/δ decreases.
This is the mechanism's core prediction.

**H2 — Conditional collapse.** After conditioning on the δ/R_s band, θ adds negligible explanatory
power. This is direct replication of the discovery finding.

**H3 — Universal crossing (stronger).** The conditional mean curve crosses ⟨ω⟩/δ = 1 in the
neighbourhood of δ/R_s ≈ 0.2. H3 failing while H1 and H2 hold refutes the universality of
c ≈ 0.2 but **does not** refute the mechanism.

**H4 — Differential session prediction (strongest test).** A market or window whose available price
space is more tightly bounded exhibits stronger compression than a near-24-hour comparator, measured
on common support.

---

## 2. Data and session definitions

### 2.1 Screening dataset — Dukascopy Japan index CFD

Used as a **screening dataset only**. It is a broker-synthesised instrument and will not be described
as a futures replication in any write-up.

The broker quotes near-24h. We therefore lock the cash-linked TSE windows in advance:

- **09:00–11:30 JST**
- **12:30–15:30 JST**

Observations outside these windows are discarded **before** any DC state is constructed.

- Primary R_s: high − low across both windows of the same trading day.
- Secondary (pre-registered): morning and afternoon treated as independent sub-sessions, DC state
  reset at the start of each, R_s computed within each.

If normalisation by sub-session range reproduces the collapse, the calendar day is not the primitive;
available price space is.

### 2.2 Primary replication market — HSI futures, day session only

- morning 09:15–12:00, afternoon 13:00–16:30 (HKT)
- after-hours 17:00–03:00 **excluded** from primary replication

Two pre-registered scales: whole day session, and AM / PM sub-sessions separately. The sub-session
comparison is a within-instrument mechanism experiment: exchange, tick size, participant population
held constant, only available price space varied.

### 2.3 Boundary comparator — CME NKD or ES

Near-24h. Used only for H4 and only after H1–H2 have been evaluated on §2.2.

---

## 3. Directional-change specification, frozen

Six thresholds, identical to the discovery market:

    θ ∈ { 5×10⁻⁴, 1×10⁻³, 2×10⁻³, 5×10⁻³, 7×10⁻³, 1×10⁻² }

No threshold may be added because a chart looks sparse, and none removed because a cell is awkward.

Definitions of directional change, confirmation point, extreme, overshoot and the discretisation term
are the implementations already validated on VN30F1M (checks V1–V5 of the manuscript). Irregular-time
trade data is reconstructed onto a 1-second grid and forward-filled **within session only**. No
backward fill at any point.

---

## 4. Range bands, frozen verbatim

    δ/R_s edges = [0.05, 0.10, 0.15, 0.22, 0.32, 0.45, 0.65]

Prohibited after seeing results: merging bins, shifting boundaries, adding bins, dropping bins.
A cell with fewer than 60 legs is marked *insufficient support* and excluded from the test; the
binning is not changed.

---

## 5. Statistical test

Two-way ANOVA on cell means, response ⟨ω⟩/δ, factors {δ/R_s band, θ}, same cell-construction and
weighting rule as the discovery market.

### 5.1 Correction to the originally drafted effect-size criterion

The first draft specified partial η²_θ < 0.02. **That criterion is rejected before freezing** because
the discovery market itself fails it: VN30F1M gives partial η²_θ = 0.380. With 28 cells and 5 degrees
of freedom for θ, the residual term is small and partial η² is inflated; the statistic is unusable at
this cell count.

Substituted criteria, both stable in the number of cells, and both of which the discovery market
passes with margin:

| criterion | threshold | VN30F1M |
|---|---|---|
| p, band | < 0.01 | 3.19 × 10⁻⁹ |
| p, θ | > 0.05 | 0.118 |
| SS_θ / SS_band | < 0.35 | **0.046** |
| within-band spread ÷ between-band range | < 0.40 | **0.219** |

Non-significance of θ alone is not treated as evidence of equivalence. H2 requires the significance
condition **and** both magnitude conditions.

---

## 6. Compression slope, for H4

β_C is the OLS slope of band-mean ⟨ω⟩/δ on fixed band midpoints, computed only on bands lying in the
**common support** of the two markets or windows being compared.

Stronger compression means a more negative β_C. The locked prediction is

    β_C(short or bounded session)  <  β_C(near-24h comparator)

Discovery-market reference: **β_C(VN30F1M) = −1.768**, SE 0.112, R² 0.984.

If the inequality reverses, the finite-space interpretation takes a direct hit and that is reported
as such.

---

## 7. Outcome reporting

No single overall PASS/FAIL. Each hypothesis reported separately.

| hypothesis | criterion |
|---|---|
| H1 compression | band effect significant, and band means monotonically decreasing overall |
| H2 collapse | all four conditions of §5.1 simultaneously |
| H3 crossing | interpolated ⟨ω⟩/δ = 1 falls within **c ∈ [0.15, 0.30]** |
| H4 differential | β_C(bounded) < β_C(near-24h) on common support |

---

## 8. Standing rules

1. Adverse results are retained and reported. The value of the second dataset lies entirely in its
   ability to kill the hypothesis.
2. No parameter, band, session definition or threshold is revised after any cross-market result is
   viewed. Revisions, if any, are made here, dated, and the reason recorded before re-running.
3. The screening dataset (§2.1) does not constitute replication evidence and will not be reported as
   such regardless of outcome.
