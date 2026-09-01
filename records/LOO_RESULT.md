# Leave-One-Leg-Out — Result record

**Specification** `PREREG_leave_one_leg_out_v1.0.md`, SHA-256
`bac0007b8308dd70968653af64eaf3ad1a520670507081e886ac19567b96d676`, frozen and timestamped
2026-08-30 22:21 ICT before any leave-one-leg-out quantity was computed. **Executed** once, no
deviation, no coding fault. 263,372 legs, six thresholds, none dropped.

## How surgical the instrument turned out to be

| quantity | value |
|---|---|
| legs whose denominator actually changes | **7,135 of 263,372 = 2.7%** |
| among those, median R^(−i)/R | 0.956 (p10 0.835, min 0.526) |
| ⟨ω⟩/δ of the affected legs | **2.209** |
| ⟨ω⟩/δ of the unaffected legs | 1.469 |

The legs that set the session extrema are exactly the large-overshoot legs, as §3 predicted. 97.3% of
the sample is untouched because those legs never reach the session high or low.

## The three denominators, side by side

| denominator | β_C | p_θ | SS_θ/SS_band | within ÷ between |
|---|---|---|---|---|
| same-session (published) | −1.768 | 0.118 | 0.046 | 0.219 |
| opposite subsession (detached) | −1.028 | < 0.001 | 0.889 | 0.501 |
| **leave-one-leg-out** | **−1.454** | **0.555** | **0.036** | **0.297** |

Band means under leave-one-leg-out: 1.333, 1.241, 1.038, 0.940, 0.797, 0.633. Monotone decreasing.
The unity crossing stays between the 0.15–0.22 and 0.22–0.32 bands, where it was.

## Registered verdict — PARTIAL

Slope flattens by **17.8%**, inside the 10–40% band that §5 defines as *Partial*. Zero of the four
collapse criteria fail.

The two halves of that verdict point in different directions and both are reported.

**Threshold invariance is unaffected, and measures slightly cleaner.** p_θ rises from 0.118 to 0.555
and SS_θ/SS_band falls from 0.046 to 0.036. Removing self-inclusion does not weaken the collapse; if
anything it sharpens it. This also settles the detached test's secondary result: the collapse criteria
failed there because that denominator is a noisy, mixed proxy, not because the invariance is fragile.

**The steepness is overstated by about a sixth.** Self-inclusion contributes roughly 18% of the slope,
and the contribution is concentrated where §3 predicted: the deepest band moves from 0.492 to 0.633
while the shallowest moves only from 1.342 to 1.333. Corrected, the relation still spans 1.333 to
0.633 and still crosses unity in the same place.

## What this settles and what it does not

It settles that self-inclusion does not produce Figure 3: 2.7% of legs cannot manufacture a relation
that holds across the other 97.3%, and threshold invariance is measured on a denominator those legs
cannot contaminate.

It does not license quoting −1.768 as though the mechanical component were absent. The manuscript
reports the measured slope, states the leave-one-leg-out value, and does not present the difference as
noise.

The benchmark β_C = −1.768 registered in `PREREG_external_test_v0.1.md` is not revised. Cross-market
comparison there applies the same same-session convention to both markets, so the comparison is
unaffected by a bias common to both sides.

Per §6 this is the last denominator test. A fourth will not be constructed.
