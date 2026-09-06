# Integration V1 reopened by runtime change (2026-09-06)

The V1 packet (`MANIFEST_V1.json`, `REPLAY_V1.json`) binds the ORION-OCM runtime at commit `09f8c952` and the exact `src/` inventory of that commit. Its checker returns `REVALIDATION_REQUIRED` when the inventory or the bytes of a bound file change; its own contract (README) states that source or runtime change reopens eligibility.

Branch `m11.4/predecessor-binding` changes bound files (`src/ocm/runtime/solve.py`, `src/ocm/lifetime/machine.py`, `src/ocm/lifetime/phases.py`, `src/ocm/selfmodel/govern.py`, `src/ocm/selfmodel/intake.py`) and adds runtime files (`src/ocm/language/chart.py`, `src/ocm/language/meaning_tree.py`, `src/ocm/learning/language/ud.py`, `src/ocm/learning/language/ud_grammar.py`, `src/ocm/evaluation/n1_ud_induction_eval.py`).

Consequence, recorded here and nowhere regenerated in place:

- The four V1 rows (M1–M4 method-learning integration) are **REOPENED** for the current runtime. Their historical replay against commit `09f8c952` stands unchanged.
- The CI workflow treats `REVALIDATION_REQUIRED` as this recorded reopening (warning, not failure); every other non-zero status still fails the workflow, and a passing replay is still compared field-by-field with `REPLAY_V1.json`.
- Re-registration against the current runtime is a separate packet (`theory-runtime-integration-v2/`) with its own review; it is a named follow-up, not implied by this note.

No scientific authority changes: the packet's authority block (`runtime_adoption: NOT_GRANTED`, `scientific_validation: NOT_ESTABLISHED`) is unchanged, and no claim in the manuscript reads this packet.
