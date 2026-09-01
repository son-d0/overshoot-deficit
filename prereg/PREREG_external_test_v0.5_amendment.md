# PREREG External Test — Amendment v0.5

**Purpose** To record an implementation defect in Level A, to correct it in line with the original
textual specification, and to fix the order in which the remaining data will be used.

**Amends** v0.1 (`2b7760fe…c397347`), v0.2 (`88d851ae…2b8ebbab`), v0.3 (`e03a2407…d44a1eb89`) and
v0.4 (`3ef0ff45…`), all of which remain in force and unmodified.

**Date** 2026-08-31
**Author** Son Do, Noralabs, Thai Nguyen University of Information and Communication Technology

---

## 1. The defect

An implementation defect was identified after the interim inspection of approximately 60% of the Hong
Kong sample disclosed in v0.4 §1.

v0.3 §3 defines Level A as the **full tradable Dukascopy window**. The implementation grouped
observations by **Hong Kong calendar date**. Measured coverage shows the instrument quotes from 09:00
Hong Kong time to approximately 01:00 the following morning, with a genuine cessation over the
12:00–12:59 lunch hour and none from 01:00 to 08:59.

Because the tradable window crosses midnight, grouping by calendar date reset the directional-change
process **inside** a trading window and combined observations belonging to **two different** trading
windows into one group. Level A as computed is therefore not the quantity the specification defines.

**No corrected Level-A statistic has been computed at the time this amendment is frozen.**

## 2. The correction

Level A is redefined operationally as **one complete Dukascopy tradable window, crossing midnight**:
from 09:00 Hong Kong time on a given date to 01:00 the following morning. Concretely, an observation is
assigned to the window whose date is obtained by shifting local time back nine hours and taking the
date.

The correction follows the original textual specification and is made **irrespective of whether it
strengthens or weakens H4**. Its effect on H4 is unknown to the author at the time of writing.

Levels B and C are unaffected: both lie wholly inside a single calendar date.

## 3. Terminology

Level A is no longer described as **near-24-hour**. The instrument quotes roughly 15 hours of 24. It is
described as the **full Dukascopy tradable window**. The §4 comparison is therefore

    full tradable window  →  Hong Kong day session  →  sub-session

and not 24h → 6.25h → 2.75h. H4 retains its meaning: if available-window compression is the cause, the
slope should steepen as the window narrows. But **Level A is no longer an unbounded control**, and the
manuscript will say so.

## 4. The superseded result is retained, not replaced

The calendar-day computation gave β_C(A) = −1.505 on the interim 60%. It is retained in
`PEEK_2026-08-31.md` and in the audit record, labelled **invalid implementation, not interpretable as
the pre-registered Level A**. It is not used as a scientific result and it is not deleted. A bad result
is not removed and quietly replaced by a better one.

## 5. Order of use of the remaining data, fixed now

Everything after **2024-06-26** remains unexamined and no further partial run of any kind will touch it
before the following sequence.

1. The grouping is corrected and the code re-hashed and timestamped. No Hong Kong outcome is computed.
2. The corrected pipeline is run **first on the held-back period alone**, as a genuinely unseen
   temporal test of the corrected implementation.
3. The full sample is then reported, carrying the chronology disclosure of v0.4 §1 and of this
   amendment.

## 6. How the outcome will be read, written before it exists

If the held-back period gives H1 and H3 alive and H4 still failing, the failure of H4 is persuasive:
it survives a corrected implementation on data never previously examined.

If H4 instead passes on the held-back period, **it will not be described as confirmed**. The first 60%
was inspected under a faulty implementation and that history cannot be made clean retrospectively. The
correct description in that case is **mixed evidence**.

## 7. Unchanged

Hypotheses, the six thresholds, the bin edges, the 60-leg floor, the ANOVA specification, the H2
magnitude criteria and their reading under v0.4 §4, the H3 window [0.15, 0.30], the β_C definition, the
VN30F1M benchmarks, the rule that HKG.IDX/HKD is not exchange-level replication evidence, and the v0.3
§7 limitation that narrowing the window also changes boundary censoring and reset frequency.
