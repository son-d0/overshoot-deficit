# Detached-Denominator Test — Result record

**Specification** `PREREG_detached_denominator_v1.0.md`, SHA-256
`4450429f82b6f01497459c5006240d8ee079337d043c05c6616329d1700e9b7d`, frozen and timestamped before any
detached quantity was computed. **Executed** 2026-08-30, once, plus one repetition after a display-code
fault recorded in that document's correction record.

**Sample** 258,489 legs lying entirely within one exchange-defined window, on 1,337 sessions where both
windows have non-zero range. A = 09:15–11:30, B = 13:00–14:45 (effective data to 14:30).

## Registered primary result — SURVIVES

Spearman ρ between x and ω/δ, within each threshold, no threshold selected:

| θ | n | ρ attached-window | ρ **detached** |
|---|---|---|---|
| 0.05% | 171,323 | −0.181 | −0.130 |
| 0.1% | 63,843 | −0.139 | −0.086 |
| 0.2% | 19,348 | −0.149 | −0.097 |
| 0.5% | 2,536 | −0.271 | −0.151 |
| 0.7% | 1,075 | −0.350 | −0.194 |
| 1.0% | 364 | −0.354 | −0.152 |

Negative in **6 of 6** thresholds. β_C(detached) = **−1.028**, band means monotone decreasing
(1.360, 1.216, 1.157, 1.091, 0.940, 0.845). The §6 criteria for *Survives* — β_C ≤ −1.0 and at least
5 of 6 negative — are met. The compression relation is not manufactured by ω contributing to R.

Reference: β_C(attached-window, same legs) = −1.836; β_C(published, full-session denominator) = −1.768.
The sample restriction alone therefore changes almost nothing; only the denominator does.

## Registered secondary result — collapse criteria fail under the detached coordinate

| criterion | threshold | attached | detached |
|---|---|---|---|
| p, θ | > 0.05 | 0.007 | < 0.001 |
| SS_θ / SS_band | < 0.35 | 0.056 | **0.889** |
| within ÷ between | < 0.40 | 0.227 | **0.501** |

Reported as it came out. See the interpretation below: this outcome is what the design predicts even
when the collapse is real, so it is not read as evidence against it.

## Post-hoc analysis

The three checks below were **not** in the frozen specification. They were run after the primary result
to audit the design, and they improve the picture, which is a direction that deserves more scepticism
than the reverse. They are reported as diagnostics, not as registered findings.

**Integrity.** Every leg assigned to a window has its opening confirmation, its extreme and its closing
confirmation inside that window and on the same session: 0 violations in 258,595 legs.

**Scale.** Window ranges differ: median R_A = 10.20, R_B = 12.60 — the shorter afternoon window is the
wider one. Detaching therefore multiplies x by 0.821 for A-legs and by 1.218 for B-legs: **opposite
directions**, geometric median 1.000. There is no common horizontal stretch, so a pure rescaling does
not explain the flattening. It does mean each detached band mixes A-legs and B-legs whose true ratios
differ systematically.

**Errors-in-variables.** log x_detached = log x_true + u, with Var(log x_true) = 0.539 and
Var(u) = 0.296, giving an attenuation factor λ = 0.646 and a predicted slope of −1.186. The observed
slope is −1.028, a realised factor of 0.560. Measurement noise in the denominator therefore accounts
for roughly **80%** of the observed flattening, leaving about a fifth unexplained. λ is a log-linear
approximation applied to a slope in levels and is indicative rather than exact.

**Within-window, no A/B mixing.** Running the same comparison separately inside each window:

| window | n | ρ attached | ρ detached | retained |
|---|---|---|---|---|
| A | 125,629 | −0.180 | −0.150 | 84% |
| B | 132,860 | −0.208 | −0.180 | 87% |

Detaching the denominator costs 13–16% of the rank association once the mixing is removed. The pooled
figure (62% retained) was depressed by the mixing, not by the coupling.

## Interpretation

The compression relation survives a denominator that cannot, by construction, contain the leg being
measured. Most of the attenuation that does occur is accounted for by measurement noise and by the
mixing the design introduces; what remains bounds any mechanical contribution to Figure 3 at roughly a
fifth of its slope, and that bound is an upper one.

The failure of the collapse criteria under the detached coordinate is expected by construction and is
not read as evidence about the market. δ = θ·P exactly, so θ *is* the numerator of x. When the
denominator is replaced by a noisy proxy — λ = 0.646, so 35% of the state's variation is uncontrolled —
θ necessarily regains explanatory power over the residual. A detached coordinate can test the
compression; it cannot test the collapse. That limit belongs to this design and should have been
anticipated when the specification was written.

## What would separate the remaining fifth

A leave-one-leg-out session range — R_s computed over the full session with the ticks of the measured
leg excluded — removes the mechanical contribution without introducing either noise or mixing. It is
the correct instrument for the residual and was not run, because it was conceived after seeing this
result. Testing it requires its own pre-registration.
