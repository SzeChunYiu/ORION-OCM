# MATH-1 / N4 result

**N4 stays open.** Neither `CAUSAL_PROOF_METHOD_REUSE_SUPPORTED` nor a valid
negative is earned. Storage of 4,323 P1 contracts and reconstruction of known
proofs cannot close the lane. MATH-2/N5 and MATH-3/N6 remain LOCKED. FLT PRs
129–132 remain BLOCKED.

A small extraction + ablation already exists on an authored near-transfer
control (`CAUSAL_CHUNK_CONSUMPTION_IN_FIXED_AUTHORED_CONTROL`). Do not treat
that as N4 causal theorem-family reuse, and do not rerun it.

## Boxes that can be checked now

| Box | Status | Bound |
|---|---|---|
| exact kernel/environment identity | CHECK | Metamath prefix + pinned Lean replay/F0; not Lean corpus semantics |
| theorem statement identity | CHECK | Metamath P1 / authored targets |
| dependency closure | CHECK | Metamath prefix replay |
| known reconstruction | CHECK | Known proofs and exposed F0; not F1 |
| proof-method extraction | CHECK | Authored I/U miner; corpus proposals unmatched |
| independent method validation | CHECK | Native admission and wrong-hole rejection |
| persistent method admission | CHECK | Persisted projection / empty typed eligibility |
| restart | CHECK | Fresh processes in learning, serving, F0, typed consumer |
| method ablation | CHECK | Exact I remove/restore; unused U |
| symbolic tactic-search parent | CHECK | Ordinary Metamath finite search |

## Not checkable from existing evidence

OPEN: unseen composition; fresh theorem-family reuse; lemma reuse;
failure-attempt reuse; subgoal discovery; representation/lemma introduction;
exact support revocation; retrieval prover; neural-guided prover; Transformer
proof reference.

CANNOT_CHECK: full search/check/storage/acquisition cost (windows exist;
lifetime economics do not).

The ordinary-cut audit remains unresolved at syntax (76/76 proposal screens
`UNKNOWN`). Another worker owns that revival. The remaining experiment is a
screening-only successor on the retained 76 proposals and full P1, then either
a completed all-alias/no-allocation negative or a P0/P1/P2/removal run on a
held-out family. See [CORE.md](CORE.md) and [CHECKLIST.json](CHECKLIST.json).
