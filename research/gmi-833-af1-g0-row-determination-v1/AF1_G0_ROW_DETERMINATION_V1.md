# AF1 `G0` microscope row — determination

**Verdict: the check survives on the comment and is not supported by anything on `main`.**

No comment is edited here, and no row is un-checked. This file records the determination and
its evidence so the orchestrator can act on it.

## The row

Comment `5693269426`, anchor `### AF1 — Developmental capability response object`:

```
- [x] Construct exact finite `G0` microscopes where two machines have the same current capability but different `Gamma`, and conversely.
```

It is the only checked row in that block with no ` — ✅ …` evidence suffix; its six siblings all
carry one naming `gmi-833-af-barrier-context-v1` and quoting exact numbers.

## What is on `main` at `5e57d429`

1. The row is in the package's **auto-reconciled** list. `ISSUE_833_AF_RECONCILIATION_V1.json`
   carries 23 entries in `tasks`, this row among them, and `deferred_tasks` holds exactly one
   entry — `#833-L`'s developmental-potential row upgrade — not this one.
2. `OPEN_GAPS_V1.json` lists "AF1 two exact crossed developmental microscopes" under
   `locally_closed`.
3. **The package contains no `G0` machinery at all.** Searched with two controls that had to
   match and did (`Gamma` in 8 files, `def ` in 6): the strings `G0-reg-v1`, `G0_RESULT` and
   `check_g0_micro` appear nowhere, and a case-insensitive search for `g0` over the whole
   package returns exactly one line — the row text itself, inside the reconciliation JSON.
4. The committed `af1` receipt has one direction only. `RESULT_V1.json` `af1` records
   `f1_same_current_score: 1/2` with `f1_system_a_capability_set: [1, 1/2]` against
   `f1_system_b_capability_set: [1/2]` — same current capability, different `Gamma`. The machines
   are the Boolean functions `C0`, `C1`, `ID`, `NOT`, not `G0` programs.
5. **There is no converse witness anywhere.** A case-insensitive search for `convers` over the
   package returns one line: the row text.

So the row asserts a conjunction, and `main` carries evidence for the first conjunct only, at
Boolean level rather than through the registered `G0` interpreter.

## The repair PR is open, not merged

PR #969, "research(#833): repair AF1 exact `G0` microscope and `Gamma` converse boundary", says
in its own body that the finite AF witness "was Boolean-level rather than executed through the
registered `G0-reg-v1` interpreter", and that it "removes the original conjunctive row from
automatic issue-comment reconciliation and moves it to `deferred_tasks`".

Checked two ways at `5e57d429`: `gh pr view 969 --json state,mergedAt,mergeCommit` returns
`state: OPEN`, `mergedAt: null`, `mergeCommit: null`; `gh api repos/.../pulls/969` returns
`state: open`, `merged: false`, `merged_at: null`, head `f225c703…`, base `ed736cd3…`,
`mergeable_state: unstable`. **It has not landed.** Any brief describing #969 as merged is
working from a false premise: nothing on `main` has retracted the evidence that produced this
check, which is why the check is still standing.

## The literal converse is unsatisfiable under the merged definition

This is derivable from `main`'s own text and does not need #969. `FORMALIZATION_V1.md` defines

```
Current(M0, Q, V) = { c(g) : g in Gamma and development_steps(g) = 0 }
```

`Current` is therefore a function of `Gamma`. Hence `Gamma_A = Gamma_B` implies
`Current_A = Current_B`, so "different current capability with identical `Gamma`" cannot occur
for any pair of machines whatsoever. The conjunctive row as worded is unsatisfiable, not merely
unevidenced, and no amount of further microscope construction can close it.

`independent_check_v1.py` in this directory re-derives that implication from the registered
definition over an enumerated finite profile universe, and shows the weaker post-development
projection does admit a converse witness — which is the form a repaired row could ask for.

## What the orchestrator should do

1. Treat this row as `checked_but_unsupported`, not as closed and not as open.
2. Merge PR #969, which repairs the evidence and moves the row where it belongs. That is the
   registered fix and it already exists; duplicating it here would be waste.
3. Only after the authoritative wording is repaired should any row of this shape be checked.

Nothing in this tranche edits comment `5693269426`.
