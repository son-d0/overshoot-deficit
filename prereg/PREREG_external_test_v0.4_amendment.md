# PREREG External Test — Amendment v0.4

**Purpose** To disclose an interim inspection of part of the Hong Kong sample, and to protect the
remainder by registering a two-layer report before any of it is examined.

**Amends** `PREREG_external_test_v0.1.md` (`2b7760fe…c397347`),
`v0.2_amendment` (`88d851ae…2b8ebbab`) and `v0.3_amendment` (`e03a2407…d44a1eb89`), all of which remain
in force and unmodified.

**Date** 2026-08-31
**Author** Son Do, Noralabs, Thai Nguyen University of Information and Communication Technology

---

## 1. Interim inspection, disclosed

On 2026-08-31, with acquisition roughly 60% complete, the frozen pipeline was executed on the portion
then available: **2021-02-25 to 2024-06-26**, 12,120 hourly files. Full output is recorded in
`PEEK_2026-08-31.md` (`40b40b72…`), timestamped.

The run served two purposes: to exercise the pipeline before its single real execution, which found and
fixed one display-only fault; and to establish whether acquisition was worth continuing. It also
produced H1, H2, H3 and β_C values, and those have been seen by the author.

Neither the specification nor the analysis code was altered in consequence. Both were hashed and
anchored before any Hong Kong result existed, so the absence of change is verifiable rather than
asserted. **Nevertheless the full-sample result can no longer be described as blinded.** It will be
reported as:

> a pre-registered analysis with an interim inspection of approximately 60% of the sample.

## 2. The held-back window

Everything after **2024-06-26** is unexamined at the time of this amendment and will remain so until
acquisition completes. No further partial execution of any kind will be run on it.

The boundary is not a design choice: it is wherever the download had reached, which is unrelated to
anything the hypotheses concern.

## 3. Two-layer report, registered now

When acquisition completes, the frozen pipeline is executed once and reports both layers:

**Layer 1 — full sample.** The original protocol of v0.3 §8 on the whole window, carrying the §1
disclosure.

**Layer 2 — held-back period.** The identical protocol on sessions after 2024-06-26 alone, as a
temporal confirmation of direction, of the unity crossing, and of the §4 ordering.

**No criterion is altered for Layer 2 because 60% has been seen.** The six thresholds, the bin edges,
the 60-leg floor, the ANOVA specification, the H2 magnitude criteria, the H3 window [0.15, 0.30] and
the §4 ordering prediction all stand exactly as registered. Layer 2 will have fewer legs and cells
falling below the 60-leg floor are reported as unsupported, not merged.

## 4. Correction to the reading of H2

v0.1 §5.1 requires the significance condition and both magnitude conditions together. Where the
significance condition fails while the magnitude conditions hold, the result will be described as

> conditioning on δ/R absorbs most, but not all, of the threshold dependence

and not as a full replication of the collapse. Overstating θ-irrelevance would be less accurate than
this, not more.

## 5. Consequence for the mechanism claim, registered before the data decides it

If the §4 ordering fails on the full window and again on the held-back window, the manuscript's
mechanism sentence is rewritten. The claim becomes:

> a cross-market conditional scaling relation indexed by δ/R; finite-session spatial compression is a
> natural explanation on VN30F1M, but a pre-registered Hong Kong window experiment does not support
> that causal interpretation.

This wording is fixed here so that it cannot be softened later by degrees. The empirical relation and
the causal explanation are separate claims and will be reported separately whatever happens to either.

## 6. Unchanged

Hypotheses, thresholds, bin edges, directional-change construction, ANOVA specification, H2 magnitude
criteria, GDO crossing criterion, β_C definition, VN30F1M benchmarks, the rule that HKG.IDX/HKD is not
exchange-level replication evidence, and the §7 limitation that narrowing the window also changes
boundary censoring and reset frequency.
