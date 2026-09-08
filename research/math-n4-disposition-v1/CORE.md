# MATH-1 / N4 disposition from existing evidence

Issue [#165](https://github.com/SzeChunYiu/ORION-OCM/issues/165) MATH-1, owner [#46](https://github.com/SzeChunYiu/ORION-OCM/issues/46).
Worktree head `b35093a26e51ccf4829aa1218957827d95db8923`. No native export, opportunity
audit, FLT study or syntax revival was rerun.

**N4 cannot close.** Required positive
`CAUSAL_PROOF_METHOD_REUSE_SUPPORTED` is not established. No valid negative
(`PARENT_SUFFICIENT`, `PRIMITIVE_ALIAS`, `NO_NEW_ABSTRACTION`, `NO_CAUSAL_REUSE`)
is available: the registered ordinary-cut audit stopped at syntax before parent
matching. Theorem storage and known reconstruction are insufficient by themselves.

MATH-2 / N5 and MATH-3 / N6 stay **LOCKED**. FLT PRs 129–132 stay **BLOCKED** for
this lane; they do not unlock #46.

[Checklist](CHECKLIST.json) · [result](RESULT.md)

## What already exists (do not re-run)

A small method-extraction + removal/restoration ablation **already exists** on an
authored near-transfer control. Its public terminal is
`CAUSAL_CHUNK_CONSUMPTION_IN_FIXED_AUTHORED_CONTROL`, not
`CAUSAL_PROOF_METHOD_REUSE_SUPPORTED`.

| Arm | Tree cost | Action attempts | Method I used |
|---|---:|---:|---|
| Ordinary | 3 | 141,792 | No |
| Learned I | 2 | 72,579 | Yes |
| Exact I removed | 3 | 141,792 | No |
| Exact I restored | 2 | 72,579 | Yes |
| Replacement U | 3 | 141,804 | No |

Citations: [native learning handoff](../native-learning-evidence-v1/HANDOFF.md),
[SUMMARY.json](../native-learning-evidence-v1/SUMMARY.json) (method ID
`5c8ff07719c450616a56ebe26ab8983473c4ad1d95f208df330d4de3c2270a06`),
[programme status](../programme/NATIVE_LEARNING_STATUS.md).
OCM serving later consumed the same imported I
([serving handoff](../native-serving-evidence-v1/HANDOFF.md)); that is adoption,
not new acquisition.

This is supervised traces, a different wrapper premise, and conventional
chunking. It is not held-out theorem-family transfer, not an OCM residual, and
not N4 completion.

## Why reconstruction and storage do not close N4

| Record | What it establishes | What it does not |
|---|---|---|
| [Native training export](../ordinary-training-native-export-v1/CORE.md) | 4,223 prefix theorems freshly checked; 128 training theorems retained in P1 (4,323 contracts); 71 traces in the bounded interface, 57 unusable | Acquired methods, cut opportunities, causal reuse |
| [Ordinary-cut audit](../ordinary-cut-opportunity-result-v1/CORE.md) | 128 roots retained; 76 proposal occurrences (74 bodies) from 17 enumerated roots; all 76 screens `UNKNOWN` at wff syntax/type (28 operator, 48 type); 0 native calls | Alias/nonalias class, empty-opportunity, learned method |
| [Typed consumer revival](../native-typed-consumer-revival-v1/CORE.md) | Fresh reconstruction of six typed permutations and one class witness | Eligible new method (`jccir` alias only) |
| [Proof-corpus inventory](../proof-corpus-v1/RESULT.md) | `LEXICAL_INVENTORY_VALIDATED` for 29,511 wrapper/solution pairs | Semantic/Lean environment closure |
| [Corpus coverage](../proof-corpus-coverage-v1/RESULT.md) | Four assigned rows; **zero semantic results** | Hidden-region reconstruction |
| [Proof replay](../proof-replay-v1/README.md) | Lean 4.19.0 kernel replay of nine authored fixtures | Unseen composition or method learning |
| [Mechanical F0](../mechanical-proof-v1/RESULT.md) | Exposed symbolic composition; `PARENT_SUFFICIENT` | Learned methods; F1–F4 |
| [Unary assay](../math-language-learning-v1/ASSAY-RESULT.md) | Four episodes `NO_METHOD_ACQUIRED` | Causal language/math method reuse |
| [Ordinary-lemma parent](../native-ordinary-lemma-parent-v1/CORE.md) | Prospective design | No native experiment |
| [Next-parent design](../typed-next-parent-design-v1/CORE.md) | Opportunity-then-P0/P1/P2/removal protocol (unregistered) | No execution |

## MATH-1 boxes that can be checked now

Scoped to the registered Metamath native apparatus and authored controls unless
noted. Lean/Mathlib semantic environment of the 29,511-pair corpus remains
`NOT_ESTABLISHED`.

1. **exact kernel/environment identity** — Metamath 96 trusted assertions /
   100-assertion training prefix; Lean 4.19.0 replay archive; Lean 4.33.1 F0 pin.
2. **theorem statement identity** — P1 contracts and authored native targets.
3. **dependency closure** — native replay of the bound Metamath prefix.
4. **known reconstruction** — prefix checking, Lean fixture replay, F0 exposed
   composition, typed claim reconstruction. Not F1 hidden-region reconstruction.
5. **proof-method extraction** — authored miner admitted I and U as derived `$p`.
   Corpus cuts exist only as unresolved proposals.
6. **independent method validation** — native checker admission of I; wrong-hole
   essential-hypothesis rejection.
7. **persistent method admission** — producer persist then sealed serving projection.
8. **restart** — fresh B processes; F0 restart identity; serving eight fresh processes;
   typed fresh consumer.
9. **method ablation** — exact-ID removal/restoration and unused replacement U.
10. **symbolic tactic-search parent** — ordinary Metamath finite-search parent in
    the authored control (not a Lean tactic-search parent).

Open, blocked or cannot-check items, citations and the remaining experiment are
in [CHECKLIST.json](CHECKLIST.json).

## Exact remaining experiment

Do **not** wait on FLT. Do **not** rerun consumed gates
([export](../ordinary-training-native-export-v1/ROOT-OUTCOME-QUALIFICATION-01.json)
`CONSUMED_ONCE_NO_RETRY`; first cut audit consumed). Another worker owns syntax
revival; this capsule does not repair that boundary.

After a separately reviewed syntax/interface revival that preserves `UNKNOWN`
and the original 76 proposals in order:

1. **Screening-only successor.** Reuse retained proposals and the full P1.
   Classify each body as ordinary-theorem alias, nonalias with independent
   support, or still `UNKNOWN`. Matcher work must be measured, not inferred.
2. **If all-alias or no viable allocation.** Record that completed negative
   (`PRIMITIVE_ALIAS` / `NO_NEW_ABSTRACTION` / `PARENT_SUFFICIENT` /
   `NO_VIABLE_ALLOCATION`). That can be a valid N4 negative for *new-method
   acquisition*. It does not by itself prove learned selection utility.
3. **If a nonalias cut survives.** Admit it as an ordinary `$p`, exit the
   producer, restore in a fresh process, and test a **held-out source family**
   (not another wrapper of the same authored composition). Compare P0, P1
   (whole training theorems), P2 (P1 plus the cut), exact removal, and a
   matched unused candidate when one exists
   ([EXPERIMENT.md](../typed-next-parent-design-v1/EXPERIMENT.md)).
   Require actual selected-proof consumption. Only that comparison may emit
   `CAUSAL_PROOF_METHOD_REUSE_SUPPORTED` or a completed `NO_CAUSAL_REUSE`.

Until step 2 or 3 finishes, N4 stays open. Retrieval, neural-guided and
Transformer proof parents remain later comparators, not this experiment.
