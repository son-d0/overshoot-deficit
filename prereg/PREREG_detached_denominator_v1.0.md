# Pre-registration — Detached-Denominator Falsification of Figure 3

**Version** v1.0 · **Status** FROZEN before any detached-denominator quantity has been computed
**Date** 2026-08-30 · **Author** Son Do, Noralabs, Thai Nguyen University of Information and
Communication Technology

---

## 0. The objection being tested

Figure 3 plots ⟨ω⟩/δ against δ/R_s, where R_s is the session's realised range. The overshoot ω is
itself part of the session's price path and therefore contributes to R_s. A larger ω can raise R_s,
lower δ/R_s, and so induce a negative association **mechanically**, in the same direction as the
reported effect.

The objection is legitimate and a referee is entitled to raise it. This test is run before submission
so that the answer is known to the author first.

Two reasons to expect the coupling to be weak are **not** treated as evidence: R_s is a max−min rather
than a sum, so a leg affects it only by setting the session extreme; and a single ω is a small
fraction of R_s. Neither is a test.

## 1. Design

The session has an exchange-defined lunch break with zero ticks between 11:30:00 and 13:00:00. The two
windows are therefore given by the exchange and not chosen by the author:

    A = 09:15:00 – 11:30:00      B = 13:00:00 – 14:45:00
    R_A = max(P_A) − min(P_A)    R_B = max(P_B) − min(P_B)

A leg is assigned to a window only if its entire span, from the confirmation that opens it to the
confirmation that closes it, lies inside that window. Legs spanning the break are excluded. Sessions
with R_A = 0 or R_B = 0 are excluded.

**Detached coordinate.** Leg in A → x = δ/R_B. Leg in B → x = δ/R_A. The measured leg cannot
contribute to its own denominator, by construction. A morning leg taking an afternoon denominator is
acceptable because this is a diagnostic falsification, not a causal trading rule.

## 2. Unchanged

The directional-change implementation, the six thresholds, the definitions of ω and δ, the leg
filters, the bin edges [0.05, 0.10, 0.15, 0.22, 0.32, 0.45, 0.65], and the 60-leg cell floor are all
unchanged. Directional-change state is constructed per calendar session exactly as published; only
the denominator changes. Nothing above may be altered after results are seen.

## 3. Three coordinates on the identical leg set

To separate a change of denominator from a change of sample, all three are computed on exactly the
same legs:

1. **attached-full** x = δ/R_s, the published convention
2. **attached-window** x = δ/R of the leg's own window
3. **detached** x = δ/R of the other window

Comparing 1 with 3 confounds the sample restriction with the denominator. Comparing **2 with 3**
isolates the denominator, and is the comparison of record.

## 4. Primary question

    H0: ⟨ω⟩/δ no longer decreases in the detached δ/R.

Association is measured **within each threshold** — Spearman ρ between x and ω/δ across legs — and
then aggregated over the six thresholds by counting signs and reporting the median. The best
threshold is not selected. The pooled band-mean curve and its compression slope β_C are reported
against the published reference β_C = −1.768.

## 5. Secondary question

After conditioning on the detached ratio band, does θ still carry explanatory power? Two-way ANOVA on
cell means, and the four criteria of `PREREG_external_test_v0.1.md` §5.1: p_band < 0.01, p_θ > 0.05,
SS_θ/SS_band < 0.35, within/between < 0.40.

## 6. Outcomes, written before the result

- **Survives.** β_C(detached) ≤ −1.0 and at least 5 of 6 thresholds show negative ρ. The mechanical
  coupling is not what produces Figure 3, and the paper says so with this test as the evidence.
- **Partial.** β_C(detached) < 0 but shallower than −1.0, or 3–4 of 6 negative. Part of Figure 3 is
  mechanical and part is structural. The interpretation section is rewritten to say exactly that, with
  the measured split.
- **Absent.** β_C(detached) ≥ 0, or the band means are not decreasing. The interpretation of Figure 3
  must be corrected before submission.

Note that the detached ratio is computed against a half-session range, which is smaller than the
full-session range. Values of x are therefore systematically larger and the occupied bands shift
upward. This is expected, the bin edges are not adjusted for it, and cells that fall below the 60-leg
floor are reported as unsupported rather than merged.

## 7. Standing rules

Run once. Reported whatever it gives. If a coding fault is found, it is recorded here with its date
and reason and the run repeated; no other repetition is permitted. No window, threshold, bin or
filter is revised on the basis of any result.
