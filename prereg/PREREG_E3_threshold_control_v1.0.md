# Pre-registration — E3: Causal Threshold Control from an Intraday Range Estimate

**Version** v1.0
**Status** FROZEN before any E3 result has been computed
**Author** Son Do, Noralabs, Thai Nguyen University of Information and Communication Technology
**Market** VN30F1M index futures
**Relationship to prior work** Section 7 of *The Overshoot Deficit* concludes that the state
variable δ/R_s is **not actionable**, because R_s is the session's realised range and is therefore
unknown during the session. E1 and E2 (below) have since shown that conclusion may hold only up to
about 09:45. E3 is the decisive test of whether it holds for the whole session.

---

## 0. What is already known, and what the data has already seen

**This is not an untouched out-of-sample test and will never be described as one.** The VN30F1M
tick history has been examined by the discovery study, by E1, and by E2. E3 is a **locked historical
evaluation**: the specification is frozen here, executed exactly once, and reported whatever it gives.

Results already observed, which motivate E3:

| result | finding |
|---|---|
| E1 | R_s is causally predictable. Best model: log-regression on the 10:30 opening range and the 20-day median range, expanding window. Spearman 0.733, R²(log) 0.446 at the 10:30 cutoff. |
| E2, 09:45 cutoff | Estimated bands are non-monotone; the predicted-fade bucket realises ⟨ω⟩/δ = 1.059, i.e. the wrong side of unity. |
| E2, 10:30 cutoff | Estimated bands are monotone; predicted-fade bucket realises ⟨ω⟩/δ = 0.937, capturing 80.6% of the distance between no-conditioning (1.492) and the ex-post-label ceiling (0.803). |

E2 measures a **mechanism diagnostic**, ⟨ω⟩/δ. It is not evidence of profit. E3 asks the economic
question.

---

## 1. Hypothesis

**H-E3.** Selecting the directional-change threshold causally, from an intraday estimate of the
session's range, produces higher net profit after costs than the best fixed threshold, on the same
sessions, over the same trading window, under the same cost model.

---

## 2. The rule, frozen

**Decision time** 10:30:00 ICT. No other decision time is evaluated.

**Range estimate.** R̂ = exp( b₀ + b₁·log OR₁₀:₃₀ + b₂·log M₂₀ ), where OR₁₀:₃₀ is the high−low of
the session from 09:15 to 10:30 inclusive, floored at 0.05 index points, and M₂₀ is the median of
the previous 20 sessions' full ranges, lagged one session. The coefficients (b₀,b₁,b₂) are refitted
before every session by ordinary least squares on **all strictly prior sessions only**, with a
burn-in of 120 sessions. This is the E1 model unchanged.

**Target ratio** δ* = 0.32 · R̂. The value 0.32 is the lower edge of the frozen band `0.32-0.45`
and is not tuned.

**Threshold** θ* = δ* / P₁₀:₃₀, where P₁₀:₃₀ is the last traded price at or before 10:30:00.

**State reset.** The directional-change state is initialised at the first tick after 10:30:00 of
each session. No state is carried across the reset or across sessions.

**Trading window.** Positions may be opened only strictly after 10:30:00 and are forced flat at the
session's final tick. No overnight exposure.

**Position rule (the DC fade, unchanged from the manuscript).** At each confirmation point, take the
position opposite to the direction of the leg just confirmed, and hold it until the next confirmation
point. Per round trip the realised move is retrace − ω = (retrace − δ) + (δ − ω).

**Execution delay** one second. Entry is at the tick following the confirmation, for both arms.

---

## 3. Comparator, frozen

Fixed θ ∈ { 5×10⁻⁴, 1×10⁻³, 2×10⁻³, 5×10⁻³, 7×10⁻³, 1×10⁻² }, the manuscript's set.

Each fixed arm is run under **identical** treatment: state reset at 10:30, trading only after 10:30,
same delay, same cost, same sessions.

The headline comparison is against the fixed θ with the **highest net profit over the evaluation
window**, i.e. the comparator is granted full hindsight in choosing its own threshold while the
adaptive arm gets none. This is deliberately the hardest available comparator. All six are reported.

---

## 4. Costs

0.175 index points per unit of position change; a flip therefore costs 0.35. This is the manuscript's
default execution benchmark, applied identically to both arms. Break-even cost is reported so the
result can be re-read at any other cost level.

---

## 5. Metrics

**Primary** net profit after cost; break-even cost per leg; annualised Sharpe on daily net P&L;
maximum drawdown.

**Diagnostic, not decisive** realised E[ω/δ] in each arm.

**Reported alongside** turnover, number of round trips, per-year net P&L, exposure.

---

## 6. Outcomes, written before the result

**A — Control works.** Adaptive net > best fixed net, with positive net after cost.
Interpretation: the mechanism is not merely observable but controllable. Section 7 of the manuscript
is wrong as written and must be rewritten.

**B — Readable, not monetisable.** Adaptive achieves E[ω/δ] < 1 and beats the comparator on the
diagnostic, but net after cost is not better. Interpretation: the state variable becomes observable
intraday, yet the observation does not survive execution cost. Section 7's conclusion stands, with a
sharper reason than the one currently given.

**C — Control fails.** Adaptive does not beat the comparator on either axis. Interpretation: E2
established only that the range regime is identifiable at 10:30; identification does not transfer to
threshold control. Section 7 stands unchanged and gains a stronger supporting test.

All three outcomes are publishable and all three will be reported. No outcome licenses a revision of
this document.

---

## 7. Standing rules

1. E3 is executed **once**. If a coding fault is found, the fault is fixed, the correction is recorded
   here with its date and reason, and the run is repeated — no other repetition is permitted.
2. 10:30 and 0.32 are not revised on the basis of any E3 result, nor on the basis of forward
   performance.
3. Regardless of outcome, the specification above is frozen for forward paper-trading beginning the
   next session. The forward record, not this evaluation, is the confirmatory evidence for any
   trading claim.
4. The external-market replication (HSI/KOSPI, `PREREG_external_test_v0.1.md`) is a separate question
   — external validity of the mechanism — and its evidence is not pooled with E3's.
