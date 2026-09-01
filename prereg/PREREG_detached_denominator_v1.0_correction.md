# Correction record for PREREG_detached_denominator_v1.0

This record was written on 2026-08-30 under section 7 of the pre-registration, which requires a
coding fault to be recorded with its date and reason. It was originally appended to the
pre-registration itself, which changed that file's bytes and so broke its OpenTimestamps proof. It
is kept separate here so that the frozen document verifies against the timestamp it was given.

The frozen pre-registration is SHA-256 4450429f82b6f01497459c5006240d8ee079337d043c05c6616329d1700e9b7d.
`DETACHED_RESULT.md` refers to "that document's correction record" and means this file.

## Correction record

**2026-08-30.** First execution raised `AttributeError: 'DataFrame' object has no attribute 'grp'` in
the reporting helper, after the primary within-threshold association had already been computed and
printed. The fault was in display code only; no specification quantity was affected and no
specification was altered. A `grp` column was added for the helper and the run repeated, as permitted
by §7. The primary result printed before the fault is identical to the one in the repeated run.
