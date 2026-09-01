# Pre-registration — E5: Remaining-Space as the Compression State

**Version** v1.0 · **Status** FROZEN and **NOT RUN**. Registered now precisely so that it cannot be
run retrospectively on the VN30F1M history that has already been examined.
**Date** 2026-08-30 · **Author** Son Do, Noralabs, Thai Nguyen University of Information and
Communication Technology

---

## 0. Why E5 is not E3

E3 asked: *how wide will today finally be?* It answered with a causal estimate of the final session
range, and lost to a fixed threshold on every registered metric.

The spatial-compression mechanism asks a different question: *from this moment on, how much room
remains for an overshoot to complete?* Those are not the same quantity. The first is a forecast of a
day-level total; the second contains a component that is known exactly at decision time.

## 1. The state variable

Let

    q_t = (active trading time remaining at t) / (total active trading time)

Under diffusion the range still attainable scales as R_remaining ∝ σ·√(q_t). A causal compression
coordinate is therefore

    S_t = θ / ( σ_0 · √(q_t) )

where σ_0 is a **fixed scale frozen in advance**, not a forecast of today's range. The essential
property is that q_t is known exactly at t. E5 contains no R² = 0.47 regression and no forecast of
today's range.

## 2. Hypothesis

    S_t increasing  ⟹  E[ ω/δ | S_t ] decreasing

up to the terminal region where event completion, not available space, becomes the binding
constraint. E2 already established that this constraint is real: at θ = 1% the rule nearly stops
firing when there is insufficient room.

## 3. Prohibitions, registered now

1. The functional form of S_t may not be optimised against VN30F1M history.
2. No time of day may be selected after inspecting profit and loss.
3. S_t may not be extrapolated as q_t → 0. A terminal exclusion or saturation rule must be written
   into a subsequent amendment **before** any run, and that rule may not be chosen by comparing
   candidate cut-offs on outcomes.

## 4. Comparators, frozen

    fixed θ    vs    E3 range-adaptive    vs    E5 clock-state

all three under identical treatment: same sessions, same trading window, same execution delay, same
cost accounting, one contract.

## 5. Endpoints, frozen

Net profit after cost; annualised Sharpe; maximum drawdown; break-even cost per leg; realised ⟨ω⟩/δ.
No metric is added after results are seen.

## 6. Evaluation dataset

Forward VN30F1M, or a market other than VN30F1M. **The existing VN30F1M history may not be used to
select the functional form, σ_0, or the terminal rule.** That history has been examined by the
discovery study, E1, E2, E3 and the detached-denominator test; it can no longer support a further
independent selection.

## 7. Relationship to the manuscript

E5 makes no claim about any published result and does not modify any. It is recorded here to fix a
date and a form for a hypothesis generated on 2026-08-30 from mechanism reasoning rather than from
inspecting an outcome, and to remove the option of testing it retrospectively.
