# L1 continual-adaptation parent v1

Issue [#165](https://github.com/SzeChunYiu/ORION-OCM/issues/165) remaining L1
box: **continual adaptation parent**. Coordinator:
[PR #206](https://github.com/SzeChunYiu/ORION-OCM/pull/206).

L1 v4 (`research/l1-linguistic-g2-v4/`) left
`continual_adaptation_parent: CANNOT_CHECK_NOT_RUN`. That file is **cited, not
overwritten**. v1–v3 same. New salts; not a retune.

## Question

At planted microworld scope, after session 1 has acquired and **persisted** a
transitive construction, does session 2 require an OCM residual beyond:

| Arm | Session 2 |
|---|---|
| reset (P0) | wipe constructions; session-2 information only |
| continued | persist construction identity; incremental lexicon; revoke on drift |
| continual-adaptation parent (P4) | experience replay of **live** demonstrations, same lexicon and update budget |

Allowed terminals:

```text
CONTINUAL_ADAPTATION_SUPPORTED_AT_SCOPE
PARENT_SUFFICIENT
RESET_PARENT_EQUIVALENT
CANNOT_CHECK_<reason>
```

`PARENT_SUFFICIENT` is not programme failure.

## Planted protocol

1. **Session 1.** SVO transitive from two aligned demonstrations. Persist
   hypothesis + evidence (`grammar.json`). Restart rebuilds the construction.
2. **Session 2 additive.** Admit a new lexical filler (`fennec` / `inlay` /
   `pyx`). **No construction re-demonstration.** Continued and replay interpret
   the new filler compositionally. Reset, with empty constructions, yields
   `UNKNOWN_CONSTRUCTION`.
3. **Session 2 drift.** Same family, SOV demonstrations. Naive union replay of
   S1 SVO + S2 SOV is contradictory. Continued and the live-replay parent
   **revoke** session-1 evidence then acquire SOV. Reset learns SOV from
   session-2 only. Naive persist without revoke does not parse SOV.

N-gram identity parent of session-1 train does not contain the session-2
utterance. Nearest-spelling mutant maps `fennec` onto a session-1 noun.

## Frozen predecessors (do not overwrite)

| Capsule | Terminal | Continual parent on disk |
|---|---|---|
| `research/l1-linguistic-g2-v1/` | `COMPOSITIONAL_LANGUAGE_LEARNING_ONLY` | `CANNOT_CHECK_NOT_RUN` |
| `research/l1-linguistic-g2-v2/` | `COMPOSITIONAL_LANGUAGE_LEARNING_ONLY` | `CANNOT_CHECK_NOT_RUN` |
| `research/l1-linguistic-g2-v3/` | `COMPOSITIONAL_LANGUAGE_LEARNING_ONLY` | `CANNOT_CHECK_NOT_RUN` |
| `research/l1-linguistic-g2-v4/` | `COMPOSITIONAL_LANGUAGE_LEARNING_ONLY` | `CANNOT_CHECK_NOT_RUN` |

## Claimed / not claimed

**Claimed at this microscope** (`programme_tick: false`): L1
`continual_adaptation_parent` — the parent comparison was run.

**Not claimed / locked:** corpus-scale N1; L2 entire; L3 entire (this is not L3
multi-session dialogue); N2 morphology/agreement (v4 microworld morphology is
cited, not started as N2). Persistent grammar and held-out fillers are cited
from v1–v4, not reticked.

Production `src/` is imported, not edited. Stdlib only.
