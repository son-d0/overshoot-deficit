# Forward paper-trade — frozen specification

**Opens** the session following 2026-08-26 (the last session in the historical sample).
**Frozen** 2026-08-30. Nothing below may be changed on the basis of forward performance.

## Arm 1 — PRIMARY: fixed threshold

    theta            = 0.007  (0.7%)
    state reset      = 10:30:00 ICT, first tick after
    trading window   = strictly after 10:30:00, forced flat at the session's last tick
    position rule    = DC fade — at each confirmation take the position opposite to the
                       direction of the leg being confirmed, hold to the next confirmation
    execution delay  = 1 second (entry at the tick following the confirmation)
    size             = 1 contract
    cost accounting  = 0.175 index points per unit of position change

Historical reference over 1,200 sessions: net +1,583, Sharpe 2.35, max DD 104, break-even 1.110/leg,
847 round trips, ⟨ω⟩/δ = 0.837.

## Arm 2 — COMPARATOR: E3 adaptive

Identical in every respect except the threshold, which is set each session at 10:30 as

    R_hat      = exp( b0 + b1*log(OR_1030) + b2*log(M20) )
    delta_star = 0.32 * R_hat
    theta_star = delta_star / P_1030

with (b0,b1,b2) refitted by OLS on all strictly prior sessions, burn-in 120 sessions; OR_1030 the
09:15–10:30 high−low floored at 0.05; M20 the median full range of the previous 20 sessions.

Historical reference: net +1,194, Sharpe 1.53, max DD 189, break-even 0.483/leg, 1,940 round trips,
⟨ω⟩/δ = 0.936.

## Rules

1. No parameter changes. Not the threshold, not 10:30, not 0.32, not the range model, not the
   execution rule. A losing month is not grounds for revision; neither is a winning one.
2. Both arms are recorded every session regardless of which is trading capital.
3. Recorded per session: date, arm, round trips, gross, cost, net, realised ⟨ω⟩/δ, θ used.
4. The forward record — not the historical evaluation — is the confirmatory evidence for any trading
   claim made about this rule.
5. A break in the specification (missing data, execution outage) is recorded as such and the session
   excluded, rather than patched.
