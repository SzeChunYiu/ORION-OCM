# AA ledger gate — amendment for issue #1049 item 2 (immutable-custody debt)

**Observed defect.** On push to `main` the repo-wide ratchet failed with 44
violations: 43 named results merged after the frozen baseline lacked one or more
of the four theorem ledgers, and the identified debt rose from 1,015 to 1,058
(`CORPUS_DEBT_GREW 1058 > 1015`). The 43 results sit in eight theorem notes.

**Repair, at the actual results.** The frozen `LEDGER_BASELINE_V1.json` is not
touched and the ratchet is not loosened.

1. Seven notes are editable (no record pins their bytes). Their 35 results
   receive the missing ledgers in place, append-only, in separate commits.
2. One note, `research/gmi-833-body-residual-akl-v1/BODY_RESIDUAL_AKL_THEOREMS_V1.md`,
   is sha256-pinned by `research/gmi-833-kl-revival-v1/MANIFEST_V1.json`
   (`parent_pins`), and both that package's workflow ("parent drift") and its
   `test_parent_pins` verify the live bytes. Adding ledgers there would turn
   `gmi-833-kl-revival-v1` red. Its eight results are listed one by one in
   `LEDGER_BASELINE_AMENDMENT_V1.json`.

**How the amendment is enforced (fail closed).** `ledger_gate_v1.load_amendment`
re-verifies every entry on every run: the file's live sha256 equals the entry's
`pin_sha256`; the pin record exists, lies in a different package and carries that
sha256; and the `(path, result)` is a live, identified, non-compliant named
result. An entry that fails any check is dropped and reported under
`immutable_custody_dropped_entries`, and the result is enforced again. The
repo-wide debt allowance rises by exactly the number of verified entries that
are not already in the frozen baseline. Editing the pinned note breaks its pin,
which drops its entries, so the exemption cannot outlive the custody it rests
on.

**Debt ratchet.** It still binds the identified population
(`identified_non_compliant`), so a new heading outside the enforcement scope, or
a new compliant result, never moves it. Only non-compliant identified results do.

**Tests.** `test_immutable_amendment_fails_closed` builds a fixture and shows the
valid pin passing, then five hostiles failing: no amendment; a pin record inside
the pinned file's own package; a forged sha256; an entry naming an
already-complete result, which is dropped and not counted; and an edit to the
pinned note, which drops the entry and re-enforces the result.
`test_real_amendment_entries_all_verify` requires every committed entry to
verify on the live repository. Neither test is part of `gate_demo()`, so the
pinned receipt section `gate_failure_demonstration` is unchanged and
`check_receipt_v1.py` still matches.

**How an entry is retired.** Publish a successor note that restates the result
with all four ledgers and re-pin the dependent package to it, or have the
dependent package re-pin edited bytes. The entry then drops by itself.

**Claim ceiling.** This amendment governs the gate only. It asserts nothing about
the contents of any ledger. `LEDGER_CONTENTS_VERIFIED` and
`ALL_THEOREMS_COMPLIANT` remain forbidden.
