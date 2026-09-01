# Pre-registrations

Nine specifications, each frozen and timestamped before the quantity it specifies was computed.

| file | frozen before |
|---|---|
| `PREREG_external_test_v0.1.md` | any second-market data was examined |
| `PREREG_external_test_v0.2_amendment.md` | any Hong Kong data was downloaded; changes only the screening instrument |
| `PREREG_external_test_v0.3_amendment.md` | the run; elevates the feed to a within-feed mechanism test, with a timing disclosure |
| `PREREG_external_test_v0.4_amendment.md` | the final run; discloses the interim inspection and adds the two-layer report |
| `PREREG_external_test_v0.5_amendment.md` | the Level A implementation was corrected; see `../records/PEEK_2026-08-31.md` |
| `PREREG_E3_threshold_control_v1.0.md` | the causal threshold-control test was computed |
| `PREREG_detached_denominator_v1.0.md` | any detached-denominator quantity was computed |
| `PREREG_leave_one_leg_out_v1.0.md` | any leave-one-leg-out quantity was computed |
| `PREREG_E5_remaining_space_v1.0.md` | registered and deliberately not run |

## One document is split in two

Section 7 of `PREREG_detached_denominator_v1.0.md` requires a coding fault to be recorded with its
date and reason. That record was originally appended to the pre-registration itself, which changed
the file's bytes and broke its timestamp. The frozen document is therefore kept byte-exact here, and
the record it calls for is in `PREREG_detached_denominator_v1.0_correction.md`, which carries no
timestamp of its own. `../records/DETACHED_RESULT.md` refers to "that document's correction record"
and means that file.

Anyone can confirm the split is only a split:

```bash
python3 - <<'PY'
import hashlib
t = open('prereg/PREREG_detached_denominator_v1.0.md').read()
print(hashlib.sha256(t.encode()).hexdigest())
# 4450429f82b6f01497459c5006240d8ee079337d043c05c6616329d1700e9b7d, the timestamped digest
PY
```
