# GMI #833 checklist custody mirror and safe-write protocol — freeze v1

**Parent:** #833 (GMI Ultimate Theory Review & Architecture-Prior-Free Derivation Programme)
**Frozen from main:** `c70dd24eeade46a3afe8322c1a0e0c16a648311e`
**Claim ceiling:** `GMI_833_CHECKLIST_CUSTODY_MIRROR_AND_SAFE_WRITE_PROTOCOL_AT_OBSERVED_BODY_STATE`

This is the pre-implementation custody record. Every tool, ledger, mirror and receipt in this
package must postdate this freeze in git order.

## Why this package exists — the observed defect

The #833 issue body is the programme's only checklist of record. It has **no server-side edit
history**: a GitHub issue body write replaces the previous body irrecoverably. Two independent
hazards were measured against the live body on 2026-09-18:

### D1 — the body is already truncated mid-token

`GET /repos/SzeChunYiu/ORION-OCM/issues/833` returns a body whose final characters are:

```
- [ ] Re-audit cultural accumulation.
- [
```

followed only by blank lines. `- [` is a cut inside a checkbox token, not a valid list item.
At least one checklist row — and possibly a tail of further rows or whole sections — is absent
from the checklist of record. The lost content could not be recovered from any accessible
source (repository tree, issue comments, local session transcripts); this package therefore
**records the loss and refuses to reconstruct it by inference**. Fabricating the missing rows
would be worse than recording their absence.

### D2 — the body is 1,505 characters from a hard write ceiling

Measured at freeze time:

| quantity | value |
| --- | --- |
| body length | 64,031 characters |
| GitHub issue body limit | 65,536 characters |
| remaining headroom | 1,505 characters |
| checked rows | 167 |
| unchecked rows | 92 |
| characters consumed by evidence annotations on checked rows | 57,550 |

Closed rows in this programme carry long inline evidence annotations (mean ≈ 344 characters,
maximum 1,054). At that rate the remaining headroom admits roughly **three further closures**
before writes begin to fail or silently truncate — against 92 rows still open. The checklist of
record cannot reach closure in its current form. D1 is the most likely already-realised
consequence of D2.

## Exact target rows

**This tranche reconciles no #833 scientific row.** It earns no checkbox in sections A–M. It is
infrastructure custody for the checklist itself. No neighbouring row is earned here.

## What this tranche delivers

1. `ISSUE_833_BODY_MIRROR.md` — a byte-exact custody snapshot of the live body at freeze time,
   committed to git, which *does* have history. This is the recovery source that did not exist.
2. `EVIDENCE_LEDGER_V1.json` — every closed row's full evidence annotation, keyed by an exact
   hash of the row's stated text, so the evidence survives independently of the issue body and
   of any future compaction of it.
3. `issue_body_safe_write_v1.py` — the mandatory write path. It re-fetches the live body
   immediately before writing, applies anchored replacements to *that* fetch, diffs old against
   new, and refuses the write unless every changed line is one the caller declared. It writes
   via `--body-file` and verifies post-write length. It never accepts `--body "$(...)"`.
4. `compact_body_v1.py` — a length-recovering rewrite that moves long evidence annotations into
   the ledger and leaves a short, resolvable pointer in the body, under invariants that forbid
   losing a row.

## Invariants the tools must enforce (falsifiers)

- **I1** No row's stated text may change. The multiset of row texts (the portion of each
  checkbox line before the ` — ✅ ` evidence separator) is invariant under compaction.
- **I2** The checked/unchecked disposition of every row is invariant under compaction.
- **I3** Every evidence annotation removed from the body is present, byte-exact, in the ledger.
- **I4** A safe write is refused if the live body changed in any line the caller did not declare.
- **I5** A safe write is refused if the resulting body would exceed the GitHub character limit.
- **I6** The post-write read-back must equal the intended body exactly; any mismatch is an alarm.

Each invariant ships with a hostile that must be **detected**, not merely absent.

## Explicit non-claims

- This package does not recover the content lost to D1 and does not assert what it was.
- It does not assert that D1 was caused by D2; it records both and their consistency.
- It makes no scientific claim about GMI.
- A passing safe write proves the write matched the caller's declared intent; it does not prove
  the caller's scientific claim.
