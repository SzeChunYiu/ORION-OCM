"""RV-377-070 — the `F` axis of GMI-DA7: a hostile refinement of the ecology family, aimed at breaking every
reduction certified by EXACT DEVELOPMENTAL EQUALITY.

WHY THIS MODULE EXISTS. `GMI_DOMAIN_ALGEBRA_EXECUTED_V1.md` section 10 (`GMI-DA7`) part 3 proves that the class set
`K(A, d, p, F)` is MONOTONE in the ecology family `F`: refining `F` — adding an ecology or an intervention — can only
SPLIT classes, never merge them, because response equality over a larger index set is a strictly stronger condition.
It follows that an exact-equality certificate is not evidence that a candidate carrier and its parent are the same
machine. It is evidence that `F` NEVER ASKED THEM TO DIFFER. The registered family (5 ecologies x 6 interventions,
`gmi_microscope/ecology.py`) was designed to test capability, not to separate carriers. This module poses demands the
registered family never posed and re-runs every certified pair under them.

A SPLIT IS THE INTERESTING OUTCOME; A SURVIVAL IS A STRICTLY STRONGER REDUCTION THAN THE ONE ON RECORD. Both are real
results and both are recorded.

-------------------------------------------------------------------------------------------------------------------
PARENT-MAXIMALITY (protocol rule 19, gap DG-5)

A separation verdict is only valid against a PARENT-MAXIMAL opponent. Every parent row here is therefore given, before
any verdict is taken:

  * its best EVICTION policy   — when a demand runs it past its declared capacity, the parent is run under EVERY
                                 declared eviction policy (`EVICTIONS`) and the policy that MINIMISES disagreement
                                 with the candidate is the one that decides the verdict. A split is declared only if
                                 EVERY policy disagrees.
  * its best CUE-MATCHING rule — a parent that stores keys is given exact-key lookup AND the nearest-key fallback in
                                 its own metric (Hamming for bit carriers, |.| for index carriers); the better of the
                                 two decides.
  * its best ABSTENTION rule   — the strongest confidence measure computable from the parent's OWN retained state
                                 under its OWN law. Parents are DENIED the candidate's native operator (the
                                 convention the executed receipts already use: `TABLE_MAT` is "DENIED the gluing
                                 operator", `PAIRTABLE` is "DENIED the join operator"); granting a parent the
                                 candidate's operator would make it the candidate, not a parent.

-------------------------------------------------------------------------------------------------------------------
THE REFINED DEMANDS, AND WHICH PAIR EACH IS DESIGNED TO SEPARATE

`OVERFLOW` — teach strictly more bindings / patterns / entries than the parent's DECLARED CAPACITY, so the bounded
compilation must operate PAST the capacity edge.
    designed to separate  every eager/materializing parent from its lazy/algebraic candidate:
                          (VSA, STORE_MAT), (PHASE, PHASE_STORE_MAT), (SHEAF, TABLE_MAT), (POSET, PAIRTABLE),
                          (AUTOCAT_EAGER, TABLE_FULL), (OBSTRUCT, DENSE_RREF), (QPROJ, TABLE), (SCDI, UNIVERSAL).
    why                   the candidate's sufficient state is a GENERATOR (a codebook, a local section, an invariant
                          basis, an authority state) whose size is independent of the number of answers; the parent's
                          is the ANSWER SET. Past the declared capacity the parent must evict and the generator need
                          not. THIS IS WHERE `GMI-DA4`'s CAPACITY GATE LIVES, so a split found only here is reported
                          as a CAPACITY REFINEMENT OF THE REDUCTION BOUND, NOT AS A KINGDOM.

`NOISY_CUE` — query with `k` bit flips in the cue, `k = 1, 2, 3`.
    designed to separate  exact-key retrieval from similarity-based retrieval:
                          (QPROJ, TABLE), (OBSTRUCT, DENSE_RREF), (AUTOCAT_EAGER, TABLE_FULL), (SHEAF, TABLE_MAT).
    why                   a carrier that retrieves by an exact key degrades discontinuously at the first flipped bit;
                          a carrier that retrieves by a graded match over a metric degrades continuously. For the
                          algebraic pairs (VSA, STORE_MAT) and (PHASE, PHASE_STORE_MAT) this demand is the sharpest
                          possible test of the lazy/eager identity, because the identity
                          `Hamming(cue XOR role, f) = Hamming(cue, role XOR f)` is claimed to hold for EVERY cue,
                          corrupted or not — a claim the registered family only ever tested on one noise setting.

`COMPOSITIONAL_UNSEEN` — query a role/filler or feature combination NEVER taught but IMPLIED by the taught set.
    designed to separate  (QPROJ, TABLE) and (QPROJ, BAYES_ORDERED) above all: the projective carrier holds ONE
                          shared state and one projector per QUESTION, so a cross-pair joint is composed for free,
                          while the table holds 8Q registered numbers and the ordered-Bayes row holds six parameters
                          PER REGISTERED PAIR — neither has a cross-pair entry, and materialising one costs Q^2.
    also                  (SHEAF, TABLE_MAT) via interior pins, (SCDI, UNIVERSAL) via an unlabelled fifth serving
                          regime, (VSA/PHASE, *_STORE_MAT) via untaught (path, filler) combinations.

`ABSTAIN_OBLIGATION` — an obligation that scores ABSTENTION explicitly, priced by the already-registered lifecycle
terms (wrong-answers-served, abstentions, collateral regression, `lambda`; gap G4, records RV-377-032/036/037/038,
`vm.lifecycle_vector`: `B_risk = lambda * wrong_served + (lambda / 16) * abstentions`).
    designed to separate  every pair in which one row can compute a GRADED match score and the other can only detect
                          an EXACT KEY MISS: (OBSTRUCT, DENSE_RREF), (QPROJ, TABLE), (AUTOCAT_EAGER, TABLE_FULL),
                          (SHEAF, TABLE_MAT), (POSET, PAIRTABLE).
    why                   "a carrier that can compute a graded match score can abstain informatively; one that can
                          only detect an exact key miss cannot." The served answer here is the PAIR
                          (answer, abstain-flag), so an abstention difference is a response difference.

`REVOKE_THEN_REQUERY` at multiplicity `m = 3, 4, 5` — strictly higher than the registered `double_revoke` (`m = 2`).
    designed to separate  every pair in which one row's state is a MODEL that folded the revoked item in and the
                          other's is the DATA: (SCDI, UNIVERSAL), (VSA, STORE_MAT), (PHASE, PHASE_STORE_MAT),
                          (POSET, PAIRTABLE), (AUTOCAT_EAGER, TABLE_FULL).
    why                   revocation is the one registered intervention that asks a machine to UN-serve something.
                          At m = 2 both members of a certified pair simply deleted a row. At m >= 3 the revoked set
                          starts to interact: the obligation is that every revoked item serves the declared REVOKED
                          sentinel AND that nothing outside the revoked item's semantic dependency closure changes
                          (collateral regression, `GMI_CP_E1_PARENT_FRONTIER_PROTOCOL_V1.md` L_collateral).

Two further demands are justified directly from the carriers' DECLARED NATIVE OPERATORS:

`INTERIOR_PIN` — pin an interior variable and requery.
    designed to separate  (SHEAF, TABLE_MAT) and (SHEAF, PROG_SEARCH). `SHEAF`'s declared native operators are
                          RESTRICT / GLUE / CHECK / PROJECT; RESTRICT at an interior patch is a native step. The
                          table parent's materialised key is the boundary pair alone and the program parent must
                          add a constraint to its declared search program.

`LATE_EXTEND` — append new events (N10) / new moves (N11) AFTER development closes, then requery.
    designed to separate  (POSET, PAIRTABLE) and (OBSTRUCT, DENSE_RREF). `POSET`'s declared native operator EXTEND
                          absorbs one event in `w` JOIN steps; `PAIRTABLE` has no join and must re-materialise the
                          transitive closure. `OBSTRUCT` re-derives the annihilator; `DENSE_RREF` re-echelons.

-------------------------------------------------------------------------------------------------------------------
SCOPE AND ARITHMETIC

Exact arithmetic throughout; the registered 8-bit fixed-point universe unless a DECLARED WIDE INSTRUMENT is named
(`wide` for the DC7, N10 pairs, exactly as the receipts that certified those pairs declared it). No randomness:
every ecology, perturbation and eviction order is a declared deterministic construction. A configuration count is
never called a species count.
"""
from __future__ import annotations

import itertools
import json
import math
import os
import sys

from . import bases
from .core import Machine, sha256_of

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "microscopes", "results")

B0 = "B0_LOCAL_ADAPTIVE_TRANSDUCERS"
REVOKED = "<REVOKED>"
ABSTAIN = "<ABSTAIN>"
LAMBDA = 16                      # the declared risk price of one wrong answer served (G4; abstention costs lambda/16)
NOISE_K = (1, 2, 3)              # declared bit-flip multiplicities of NOISY_CUE
REVOKE_M = (3, 4, 5)             # declared revocation multiplicities, all strictly above the registered double_revoke
EVICTIONS = ("FIFO", "LRU", "LFU_TAUGHT")   # the declared eviction policy set a parent is maximised over

DEMANDS = ("OVERFLOW", "NOISY_CUE", "COMPOSITIONAL_UNSEEN", "ABSTAIN_OBLIGATION", "REVOKE_THEN_REQUERY",
           "INTERIOR_PIN", "LATE_EXTEND")


# =================================================================================================================
# deliverable 1 — recompute the equality certificates from the COMMITTED receipts (not from the prose)
# =================================================================================================================
RECEIPTS = ("STAGE_DC_V24_DC1_VSA.json", "STAGE_DC_V25_DC3_ENERGY.json", "STAGE_DC_V30_DC2_FIELD.json",
            "STAGE_DC_V31_DC7_QUANTUM.json", "STAGE_DC_V32_DC9_PHASE.json", "STAGE_DN_V26_N3_SHEAF.json",
            "STAGE_DN_V27_N10_PARTIALORDER.json", "STAGE_DN_V28_N10_LAW_LW.json",
            "STAGE_DN_V28_N8_AUTOCATALYTIC.json", "STAGE_DN_V29_N11_OBSTRUCTION.json",
            "STAGE_DN_V30_N11_OBSTRUCTION_R2.json", "STAGE_E1_V35_F4_IQL.json", "STAGE_E1_V36_F6_SCDI.json")

# the instrument each receipt's equality certificate is declared at (None = the receipt has a single instrument)
RECEIPT_INSTRUMENT = {"STAGE_DC_V31_DC7_QUANTUM.json": "wide", "STAGE_DN_V27_N10_PARTIALORDER.json": "wide",
                      "STAGE_DN_V28_N10_LAW_LW.json": "wide"}

# candidate row of each receipt (the carrier under test); everything else in `rows` is a parent or a negative twin
RECEIPT_CANDIDATE = {"STAGE_DC_V24_DC1_VSA.json": "VSA", "STAGE_DC_V25_DC3_ENERGY.json": "HOPFIELD",
                     "STAGE_DC_V30_DC2_FIELD.json": "FIELD", "STAGE_DC_V31_DC7_QUANTUM.json": "QPROJ",
                     "STAGE_DC_V32_DC9_PHASE.json": "PHASE", "STAGE_DN_V26_N3_SHEAF.json": "SHEAF",
                     "STAGE_DN_V27_N10_PARTIALORDER.json": "POSET", "STAGE_DN_V28_N10_LAW_LW.json": "POSET",
                     "STAGE_DN_V28_N8_AUTOCATALYTIC.json": "AUTOCAT_EAGER",
                     "STAGE_DN_V29_N11_OBSTRUCTION.json": "OBSTRUCT",
                     "STAGE_DN_V30_N11_OBSTRUCTION_R2.json": "OBSTRUCT", "STAGE_E1_V35_F4_IQL.json": "IQL",
                     "STAGE_E1_V36_F6_SCDI.json": "SCDI"}

# rows that are NEGATIVE TWINS (ablations of the candidate) or other candidates' rows, never parents of the candidate
NOT_A_PARENT = {"VSA_NOBIND", "HOPFIELD_RND", "FIELD_NONLOCAL", "QPROJ_COMMUTING", "PHASE_NOCOUPLE",
                "SHEAF_NOGLUE", "POSET_NOJOIN", "AUTOCAT_NOFEED", "AUTOCAT_LAZY", "OBSTRUCT_NOCERT",
                "IQL_NOAMBIG", "SCDI_NORECOMPILE"}


def _row_and_context(key, rows):
    parts = key.split("|")
    for p in parts:
        if p in rows:
            return p, tuple(x for x in parts if x != p)
    return None, None


def enumerate_certificates(res_dir=RES):
    """recompute, from the committed receipts alone, every (candidate row, parent row) pair whose served answers are
    BIT-IDENTICAL on every registered cell of that receipt (at the receipt's declared instrument)."""
    out = {"per_receipt": {}, "certificates": [], "n_certificate_pairs": 0, "n_certified_candidates": 0}
    for fname in RECEIPTS:
        path = os.path.join(res_dir, fname)
        if not os.path.exists(path):
            continue
        d = json.load(open(path))
        rows = d.get("rows") or []
        cells = d.get("cells") or {}
        if not rows or not cells:
            continue
        cand = RECEIPT_CANDIDATE.get(fname)
        instr = RECEIPT_INSTRUMENT.get(fname)
        idx = {}
        for k, v in cells.items():
            r, ctx = _row_and_context(k, rows)
            if r is None:
                continue
            if instr is not None and instr not in ctx:
                continue
            idx.setdefault(r, {})[ctx] = v.get("answer_signature")
        rec = {"candidate": cand, "instrument": instr or "registered_single_instrument",
               "receipt_sha256": d.get("receipt_sha256"), "revival_record": d.get("revival_record"), "pairs": {}}
        for parent in rows:
            if parent == cand or parent in NOT_A_PARENT:
                continue
            common = sorted(set(idx.get(cand, {})) & set(idx.get(parent, {})))
            if not common:
                continue
            diff = [c for c in common if idx[cand][c] != idx[parent][c]]
            rec["pairs"][parent] = {"n_cells": len(common), "n_differing": len(diff),
                                    "bit_identical_everywhere": not diff}
            if not diff:
                out["certificates"].append({"receipt": fname, "candidate": cand, "parent": parent,
                                            "n_cells": len(common), "instrument": rec["instrument"],
                                            "revival_record": d.get("revival_record"),
                                            "receipt_sha256": d.get("receipt_sha256")})
        out["per_receipt"][fname] = rec
    out["n_certificate_pairs"] = len(out["certificates"])
    out["n_certified_candidates"] = len({c["candidate"] for c in out["certificates"]})
    return out
