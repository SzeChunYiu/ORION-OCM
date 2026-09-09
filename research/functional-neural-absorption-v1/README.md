# #214 FNA — functional donor absorption, first decisive tranche

**Base `dff3acadb78dfef161d122d00f20ebb30ab8bb51` (#207). Research-only; production `src/`
unmodified. #71 remains `LEARNED_ROUTER_NOT_YET_AUTHORIZED` — no model, router or bandit
exists in this tranche.**

## Result

```text
FNA-1   NON_NEURAL_RESOURCE_ADVANTAGE_AT_REGISTERED_SCOPE
        unbounded: typed channels add NOTHING (Proposition 3, structural)
        bounded:   a non-oracle, parent-owned ordering policy recovers a decisive
                   item a naive order misses — at budgets 4/8/16/32
hostile DECLARED_POST_FREEZE — the advantage is three-way conditional, measured
```

## Three findings, in order of how much they change the programme

### 1. Phase A — most of FNA-1's parent ladder already exists on main

| rung | status | implementation |
|---|---|---|
| R0 full scan | **EXISTS** | `kso/extraction.py`, incl. `pcst_exact_bounded` |
| R1 exact typed/indexed | **EXISTS** | `runtime/operator_index.py`, posting under the **rarest required input** |
| R2 local frontier traversal | **EXISTS** | `kso/extraction_indexed.py` |
| R3 kNN / kernel | absent | |
| R4 local diffusion | **EXISTS** | `kso/navigation_sparse.py` |
| R5 typed multi-channel | absent | **← this tranche** |
| R6 VSA/HDC · R7 neural ref | absent | |

`IndexedExtractionWork` charges 17 coordinates and `ExtractionIndex` records `build_work`
**separately** from query work, so "no free preprocessing" is enforced in code. Rebuilding
R0/R1/R2/R4 would have compared against a strawman — the hand-authored-prior risk §6 names.

### 2. Phase B — #214 §3 mis-attributes typed channels to multi-head attention

§3 assigns multi-head the obligation *"multiple concurrent relevance relations"* and the OCM
form *"semantic / causal / temporal / failure / provenance / goal heads"*. The literature
does not support that:

- **2605.20271** develops multi-head as an **ensemble of Nadaraya-Watson kernel estimators**
  whose function is **variance reduction through decorrelation**.
- **2504.03889** finds many heads **inactive** — redundant estimators, not missing relations.
- **2602.00861** frames heads as competing estimators, not a relation vocabulary.

**An exact gated closure has no estimator variance.** So multi-head's function is not
unmet here — it is *absent*, `NO_OBLIGATION_IN_AN_EXACT_SYSTEM`. Typed channels are a real
mechanism owned by a **different** parent: heterogeneous information networks and metapath
retrieval (2605.30966, 2510.15552). Attributing them to multi-head credits the neural donor
with something classical graph IR already owns.

Separately, **2502.04645** finds cross-encoders implement a semantic variant of **BM25** —
a neural ranker reconstructing a classical IR parent.

### 3. FNA-1 — reach is structurally unwinnable; order under budget is not

**Proposition 3.** `gated_closure` admits a head only via an edge whose tails are reached
and whose warrant is live, so removing edges only removes admissions. Every channel subset
is a subset of the full closure, **for any channel policy whatever**. Typed channels can win
**work, never reach**. Confirmed in the run and re-derived in tests on fresh spaces.

| arm | reached | found decisive |
|---|---:|:--:|
| `R0_DENSE` / `R1_INDEXED` | 62 | ✓ |
| `R5_CHANNEL_SCALE_CHANGE` | 2 | ✓ |
| `R5_CHANNEL_DEPENDENCE` | 41 | ✗ |
| `R5_COMMON_CHANNELS_ONLY` | 61 | ✗ |
| `R5_UNION_ALL_CHANNELS` | 62 | ✓ (= closure exactly) |

The escape is a **binding budget**, where expansion order decides what fits:

| budget | binds | naive | rarity-first | ORACLE |
|---|:--:|---|---|---|
| 4 / 8 / 16 / 32 | ✓ | ✗ | **✓** | ✓ |
| 64 | ✓ | ✓ | ✓ | ✓ |
| 128 | ✗ | ✓ | ✓ | ✓ |

`BOUNDED_RARITY_FIRST` is **not an oracle**: it reads edge-type counts, a property of the
space, never of the task or its answer — the same selectivity heuristic
`runtime/operator_index.py` already applies. **So the advantage is owned by the classical IR
parent, not by a bespoke OCM mechanism and not by attention.**

## The hostile, and what it cost the headline

Declared post-freeze; `experiment.py` was **not** edited, so `FREEZE_V1.json` stands. It can
only weaken the result, which is why it is admissible.

| world | rarity-first vs naive |
|---|---|
| decisive on the **rare** channel | strictly **better** at budgets 4/8/16/32 |
| decisive on a **common** channel | **neutral** — identical at every budget |
| **+ a 40-edge rare-channel decoy** | strictly **worse** at budget 64 |

**Rarity is a selectivity heuristic, not a relevance signal.** It predicts where *few* edges
are, never where the *answer* is. It pays when scarcity coincides with decisiveness, costs
nothing when it does not, and is actively harmful when bulk sits on a scarce channel.

An earlier draft of that verdict said the common-channel world made the policy "strictly
worse". It does not — it makes it *neutral*. Corrected, with a test pinning the distinction.

## What this does not establish

No neural arm was run; R3/R6/R7 are absent, so `APPROXIMATE_RETRIEVAL_NOT_SAFE` stays
untestable. No lifetime economics — acquisition, maintenance and revocation are not
amortised. One planted world, one author, one population: **E1 / L1**, not E3. Nothing here
licenses `TRANSFORMER_REPLACED`, `LLM_EQUIVALENT` or any general-capability claim, and a
test asserts no receipt contains them.

## Files

`REPO_STATE.json` · `OPEN_PR_COLLISION_MAP.json` · `CURRENT_OCM_MECHANISM_MAP.md` (Phase A) ·
`FUNCTIONAL_DONOR_ATLAS_V1.md` · `SOURCE_LEDGER.json` · `PARENT_OWNERSHIP_CARDS.json` (Phase B) ·
`contract.py` · `CONTRACTS_V1.json` · `CONTRACTS_MALFORMED_V1.json` (Phase C) ·
`PROTOCOL.md` · `FREEZE_V1.json` · `experiment.py` · `hostile.py` · receipts · `test_fna1.py` (21 tests)

```
PYTHONPATH=src python3 research/functional-neural-absorption-v1/experiment.py --out .../FNA1_TYPED_CHANNEL_V1.json
PYTHONPATH=src python3 research/functional-neural-absorption-v1/hostile.py   --out .../FNA1_HOSTILE_RARITY_V1.json
PYTHONPATH=src python3 -m unittest test_fna1
```
