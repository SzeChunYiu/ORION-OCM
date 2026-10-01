# GMI #833 squash-safe gate repair — pre-implementation freeze

Issue: #1049  
Source main: `50f833cc4bc3cadcefd44eca14fa58f73f815587`

## Frozen scope

This package repairs only repository infrastructure that currently prevents an
otherwise clean successor from being evaluated on its own changes.

1. A freeze-custody check MUST use the strict historical ordering proof when
   the freeze and implementation have distinct first-add commits.
2. When an already-published package reached `main` through a squash commit,
   the fallback MUST require that the first package commit contains the named
   freeze and that the package path is absent from every parent of that commit.
   Merely finding a freeze anywhere at `HEAD` is insufficient.
3. The fallback MUST fail for a planted publishing commit without the freeze,
   and for a planted parent that already contains implementation bytes.
4. The AA ledger gate MUST reject newly introduced identified theorem results
   without the four required ledgers. Corpus growth consisting only of complete
   results MUST NOT be counted as increased debt.
5. The five AG5 named results currently reported by that gate MUST acquire
   explicit assumption, dependency, falsifier, and strongest-parent ledgers;
   no exclusion is permitted.
6. On pull requests the AB terminology ratchet MUST block new debt only in the
   files owned by that pull request. Post-baseline debt in non-owned files is
   reported but cannot make an unrelated PR fail. Push-to-main auditing remains
   repository-wide.

## Verification frozen before implementation

- Reproduce every failure exposed by PR #1009 at head `4aca3ceb`.
- Run every repaired workflow command locally where possible.
- Add executable hostile fixtures for both custody fallback failure modes.
- Run the AA and AB test suites in normal and optimized Python.
- Parse every edited workflow as YAML.
- Re-run the PR #1009 check set after this repair lands and its latest `main`
  is integrated.

## Claim ceiling

`SQUASH_SAFE_CUSTODY_AND_PR_OWNED_RATCHET_REPAIR_FOR_REGISTERED_GMI_833_GATES`

This closes no scientific row and does not certify that a freeze existed
before implementation when the only surviving public history is a squash. It
preserves and verifies the committed registration artifact and prevents future
parent contamination; the stronger historical claim remains supported only by
the original PR/branch custody evidence.

## Forbidden promotions

- `SQUASH_COMMIT_PROVES_PRE_IMPLEMENTATION_REGISTRATION`
- `FREEZE_FILE_PRESENT_IMPLIES_FREEZE_FIRST`
- `RATCHET_BASELINE_MAY_BE_RAISED_TO_HIDE_DEBT`
- `UNOWNED_DEBT_MAY_BLOCK_AN_UNRELATED_PULL_REQUEST`
- `ANY_SCIENTIFIC_ROW_CLOSED`
