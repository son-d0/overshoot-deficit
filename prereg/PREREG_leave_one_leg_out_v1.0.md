# Pre-registration — Leave-One-Leg-Out Denominator

**Version** v1.0 · **Status** FROZEN before any leave-one-leg-out quantity has been computed
**Date** 2026-08-30 · **Author** Son Do, Noralabs, Thai Nguyen University of Information and
Communication Technology

---

## 0. Position before this test

`PREREG_detached_denominator_v1.0.md` (SHA-256 `4450429f…700e9b7d`) was executed and recorded in
`DETACHED_RESULT.md` (SHA-256 `096f67b7…998c4541d`). Its registered primary outcome was *Survives*:
the compression relation is negative at all six thresholds under a denominator that cannot contain the
measured leg, and retains 84–87% of its rank association when the two subsessions are analysed
separately.

Two statements in that record are **calibrated downward here and in the manuscript**, and this wording
supersedes them:

- "measurement noise accounts for roughly 80% of the flattening" → *the magnitude of the attenuation is
  broadly consistent with an errors-in-variables account*. λ = 0.646 is a classical attenuation factor
  derived in logs and applied to a slope in levels; it is indicative, not an identified decomposition.
- "bounds any mechanical contribution at roughly a fifth of the slope" → *a rough diagnostic
  indication, not an identified bound*.

The detached design has two acknowledged defects: its denominator is a noisy proxy, and it mixes legs
from two subsessions whose ranges differ systematically. This test removes both.

## 1. The instrument

For each leg *i*, spanning from the confirmation that opens it to the confirmation that closes it,
define

    R_s^(−i) = range of the same session computed with the ticks of leg i excluded

Same session, same volatility regime, no morning/afternoon scale mismatch, no proxy from another
window. The only thing removed is the direct mechanical path from ω_i into its own denominator.

The whole leg span is excluded, not only its overshoot segment. This removes more than the objection
strictly requires and therefore gives the mechanical explanation more room to reveal itself.

A property that makes the test surgical: for the majority of legs, which set neither the session high
nor the session low, R_s^(−i) = R_s exactly and nothing changes. Only legs that actually contribute to
the session extrema get a different denominator. The test therefore asks directly how much Figure 3
moves when precisely the mechanically implicated cases are corrected.

## 2. Unchanged

The directional-change implementation, the six thresholds, the definitions of ω and δ, the leg filters,
the bin edges [0.05, 0.10, 0.15, 0.22, 0.32, 0.45, 0.65], the 60-leg cell floor and the leg set are all
as published. Directional-change state is constructed per calendar session. Only the denominator
changes. Legs for which R_s^(−i) = 0 are excluded.

## 3. Direction of the prediction

Removing a leg can only shrink or preserve the range, so x^(−i) ≥ x for every leg. Legs that set the
session extrema are the large-ω legs, which carry high ω/δ. Under the mechanical explanation those legs
are currently displaced to low x by their own contribution; correcting it moves them right, into the
region where the curve is low, and **flattens β_C**. Under the null that the compression is real, few
legs are affected and β_C should barely move.

## 4. Reported quantities

β_C, the six band means, and the four criteria of `PREREG_external_test_v0.1.md` §5.1, all computed
with R_s^(−i); the fraction of legs whose denominator actually changes and the distribution of the
change; and the same quantities under the two denominators already computed. **All three denominators
— published same-session, detached subsession, leave-one-leg-out — are reported side by side whatever
they show.**

## 5. Outcomes, written before the result

Reference: β_C(published, same-session) = −1.768.

- **Unaffected.** β_C(LOO) within 10% of −1.768, and all four collapse criteria still pass.
  Self-inclusion is not what produces Figure 3, and the figure stands as published.
- **Partial.** β_C(LOO) between 10% and 40% shallower, or exactly one collapse criterion fails. Part of
  the relation is mechanical; the manuscript reports the measured split rather than the headline slope.
- **Coupling-driven.** β_C(LOO) more than 40% shallower, or the band means are no longer monotone, or
  two or more collapse criteria fail. The interpretation of Figure 3 is rewritten before submission.

## 6. Standing rules

Run once. Reported whatever it gives, alongside the other two denominators. If a coding fault is found
it is recorded here with its date and reason and the run repeated; no other repetition is permitted. No
window, threshold, bin, filter or leg set is revised on the basis of any result. This is the last
denominator test; a fourth will not be constructed if this one is unfavourable.
