# Correction to the audit of 30 August 2026

**Corrects** `AUDIT_2026-08-30.md`, SHA-256
`d0992ca162ac577373a4f42d6090e415b336eb282f5265d79538662cc9ef5270`, which is retained unchanged.
**Date** 2026-08-31

## What the earlier record got wrong

Finding A described `panel.npz` as a *superseded* panel of 1,255 sessions. That characterisation is
wrong and is withdrawn.

`panel.npz` holds **1,255 sessions, 25 February 2021 to 24 April 2026** — exactly the specification
window, ending on the model cutoff date. `panel2.npz` holds those sessions **plus the 85 withheld
evaluation sessions**, 1,340 in total. The first is not an older version of the second; it is the
deliberately truncated file that keeps the evaluation window out of reach.

A second claim built on the same error is also withdrawn: that `app/app.html` sits on stale data
because its `meta.n` reads 1255. It does not. `webdata.json` separates `strat`, covering the 1,255
specification sessions, from `strat.oos`, covering the 85 withheld ones. That is the design the
manuscript describes, and 1255 is the correct count in that context. No regeneration is required and
none was performed.

## What survives, and why the fix was still right

The inconsistency was real, but between the figures and the text rather than between two panels.

Section 4's hypothesis test — 28 cells, F(5,17) = 45.13, p_θ = 0.118 — and the benchmark table frozen
in `PREREG_external_test_v0.1.md` — β_C = −1.768, range 1.342 → 0.492 — are both computed on the full
1,340 sessions. Figures 1 to 3 were computed on the 1,255-session specification window. The figures
therefore disagreed with the text beside them and with the registered benchmark.

Regenerating them on 1,340 aligns figure, text and pre-registration. That remains correct. The
consequent corrections to the ⟨TMV⟩ crossing (0.7% → 0.50%), the Hurst scalars and the band values all
stand.

## What this adds to the manuscript

The paper nowhere states which sample Figure 3 is measured on. It should, because the reader is
entitled to check that the out-of-sample test in Section 5 is not circular. A clause has been added to
Section 4 recording that the collapse is measured on all 1,340 sessions while the prediction tested in
Section 5 was made from the curve fitted through 24 April 2026 alone.

## Note on the other findings

Findings B, C and D of the 30 August record are unaffected. The label collision in the walk-forward
grid, the Vietnamese labels and footer, and the description of the session as continuous were all
verified independently of the panel question.
