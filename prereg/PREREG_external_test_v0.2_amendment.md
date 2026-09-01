# PREREG External Test — Amendment v0.2

**Amends** `PREREG_external_test_v0.1.md`, SHA-256
`2b7760fe043a14f2d91caae4b0944d8fd3386c1a61c9ffd5e6caa3533c397347`, which remains in force in every
respect not modified below. v0.1 is **not** replaced and is retained for the audit trail.

**Status** Amendment made **before** inspection or download of any Hong Kong market data.
**Date** 2026-08-30
**Author** Son Do, Noralabs, Thai Nguyen University of Information and Communication Technology

---

## 1. Reason for amendment

Version 0.1 specified the Dukascopy Japanese index CFD as the zero-cost screening instrument. Before
inspecting that dataset, the screening instrument is changed to Dukascopy HKG.IDX/HKD.

The reason is experimental design rather than observed performance. The external test concerns spatial
compression relative to a finite trading-session price range. A Hong Kong index instrument provides a
closer structural match to the intended confirmatory HSI futures experiment, and allows the same
predefined regular-session boundaries to be applied both to the free screening feed and to the
subsequent exchange-traded futures data.

## 2. Scope of change

Only the screening instrument is changed:

    Dukascopy Japan index CFD  →  Dukascopy HKG.IDX/HKD

No result from HKG.IDX/HKD or from HSI futures has been inspected before this amendment.

## 3. Unchanged specifications

- H1–H4 remain unchanged.
- The directional-change construction remains unchanged.
- The six thresholds remain 0.0005, 0.001, 0.002, 0.005, 0.007, 0.010.
- The δ/R bin boundaries remain [0.05, 0.10, 0.15, 0.22, 0.32, 0.45, 0.65].
- The ANOVA specification remains unchanged.
- The H2 magnitude criteria remain SS_θ/SS_band < 0.35 and within-band spread ÷ between-band
  spread < 0.40.
- The GDO crossing criterion remains unchanged.
- The compression slope β_C and the H4 differential prediction remain unchanged.
- The VN30F1M discovery benchmark remains β_C = −1.768.
- No thresholds, bins, session definitions, tests or acceptance criteria may be modified on the basis
  of Hong Kong results.

## 4. Role of the screening dataset

HKG.IDX/HKD is an exploratory screening feed and is not treated as exchange-level replication
evidence. The confirmatory external dataset remains exchange-traded HSI futures tick data.

## 5. Data-resolution requirement

Confirmatory testing requires transaction-level tick data. One-minute bars will **not** be used for
H1–H2, because the smallest pre-registered thresholds are of the same order as plausible intraminute
HSI movement, creating an unresolved sampling and discretisation confound. A negative H2 obtained from
one-minute bars could not be distinguished from a measurement artefact and would therefore not
constitute a falsification.

## 6. Freeze condition

This amendment must be hashed and externally timestamped before any HKG.IDX/HKD observation is
downloaded or inspected.
