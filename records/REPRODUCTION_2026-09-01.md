# Reproduction check, 2026-09-01

The repository was checked against itself before being made public: cloned fresh from the remote,
installed into an empty virtual environment, and run. Nothing on the author's machine was used except
the Hong Kong tick archive, which is too large to redownload and is noted as such below.

## What was run

**The central result.** Clone, `pip install -r requirements.txt`, `python verify/verify_collapse.py`.
The fresh environment resolved numpy 2.5.2, pandas 3.0.5 and scipy 1.18.1 — all substantially newer
than the versions the analysis was written against — and every line of the output matched the block
printed in the README, including the compression slope to three decimals. Two seconds warm.

**The timestamps.** All twenty OpenTimestamps proofs were checked from the clean clone: each commits
to the SHA-256 of the file shipped beside it. Eighteen carry Bitcoin block attestations. Two,
`E4_PARKED.md.ots` and `FORWARD_SPEC.md.ots`, were stamped most recently and are still confirming.

**The Hong Kong replication.** `src/hk_pipeline.py` was run from the clean clone over the full
archive. Every quantity in `HK_RESULT.md` reproduced: 63,154,002 quotes, 75,799,140 one-second
observations, 1,350 trading windows, and each layer's band means, F statistics, unity crossings and
compression slopes. Of the forty-one numbers in that record, thirty-six appear verbatim in the new
log and five are arithmetic on numbers that do (34,440 files acquired, of which 20,058 carry quotes
and 14,382 are hours the instrument does not trade) or belong to the discovery market.

The acquisition itself was not repeated. It took 28.6 hours the first time and the cached archive was
reused; `src/dl_hk.py` was exercised over a three-day window to confirm it still resolves the feed.

**The translation.** `src/hk_pipeline_english.py` is a reading copy of the timestamped artifact with
its comments and printed labels in English. Both were run over the same data. They produce the same
multiset of 110 reported values and the same twenty pass/fail verdicts. The translation changes no
computed quantity.

## What was fixed as a result

Sixteen of the twenty timestamp proofs shipped were pre-upgrade files with no Bitcoin attestation.
One pre-registration had been edited after stamping, by writing into it the correction record its own
section 7 demands. `hk_pipeline.py` had been translated after stamping, so the single script the
repository claims was hashed before it ran was the one whose proof did not verify. Seven README paths
pointed nowhere after a reorganisation, the documented `ots verify` command could not work without a
Bitcoin node, and the README called the notebook a reproduction that runs from one shipped file when
it reads a tick panel that is not distributed. `economics.json` still carried two configuration labels
in the author's working language rather than the manuscript's notation.

None of these touched a computed result. All are corrected in the commit that carries this record.

## Addendum, later the same day

The two pending proofs confirmed. `ots upgrade` over the whole set now returns twenty of twenty
committing to the bytes beside them and twenty of twenty carrying Bitcoin block attestations, so the
qualification recorded above no longer applies. The count in the body is left as it was written
rather than corrected in place, because it was accurate when the check was run.
