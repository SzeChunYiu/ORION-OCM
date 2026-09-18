"""HRL-2 - agent-constructed candidate map from the 11 K-families to the 43 named rows.

Every edge here is AGENT_CONSTRUCTED_UNADJUDICATED.  No primary artifact in the corpus
binds any K-family to any named Section H row; that absence is verified two ways by
``verify_k_binding_absence`` below.  These edges therefore licence nothing: every cell they
produce is ``SCREENED_NOT_ADJUDICATED`` and may never be promoted.

Edge strength rule, frozen in FREEZE_V1.md section 5 and applied here:

  STRONG - one of the K-family's declared ``parent_anchors`` names the canonical primary
           literature of the row, or the K-family's ``paper_name`` is a synonym of the
           row's head noun phrase.
  WEAK   - the K-family's ``posthoc_fingerprint.required`` clauses are plausibly asserted
           of the row, but no declared anchor names that row's literature.

Python 3.8 compatible, stdlib only, no floating point.
"""
from __future__ import print_function

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RESEARCH = os.path.dirname(HERE)

# (K family, H row id, strength, the declared anchor or fingerprint clause relied on)
CANDIDATE_EDGES = [
    ("K01", "H20", "STRONG", "parent_anchors: McCulloch-Pitts 1943; Rumelhart-Hinton-Williams 1986; LeCun et al. 1998"),
    ("K01", "H21", "WEAK", "learning_extension: experience updates distributed numeric parameters and alters future mapping"),
    ("K02", "H01", "STRONG", "parent_anchors: 'finite-state/recurrent systems literature'"),
    ("K02", "H23", "STRONG", "parent_anchors: Elman 1990 Finding Structure in Time"),
    ("K02", "H24", "WEAK", "required: persistent internal state survives between external steps"),
    ("K02", "H28", "WEAK", "required: the state is updated and fed into subsequent computation"),
    ("K02", "H30", "WEAK", "required: prior internal state causally changes a later output under matched current input"),
    ("K03", "H22", "STRONG", "parent_anchors: LeCun et al. 1998 convolutional networks"),
    ("K03", "H27", "WEAK", "required: a common transform applied at multiple positions restricted to a registered local neighborhood"),
    ("K03", "H36", "WEAK", "required: each application is restricted to a registered local neighborhood or receptive field"),
    ("K04", "H25", "STRONG", "parent_anchors: Vaswani et al. 2017; earlier neural attention literature"),
    ("K04", "H26", "STRONG", "parent_anchors: Vaswani et al. 2017 Attention Is All You Need"),
    ("K04", "H29", "WEAK", "required: source influence on the aggregate changes when query/content changes"),
    ("K04", "H38", "WEAK", "required: a query-dependent compatibility or routing quantity is computed for multiple candidate sources"),
    ("K05", "H09", "STRONG", "parent_anchors: term-rewriting systems; Knuth-Bendix completion"),
    ("K05", "H12", "STRONG", "parent_anchors: classical AI state-space/symbolic search"),
    ("K05", "H08", "WEAK", "required: legal transformations include rule-based rewrite/inference over discrete structures"),
    ("K05", "H39", "WEAK", "required: machine state contains explicitly compositional discrete expressions"),
    ("K06", "H17", "STRONG", "paper_name 'probabilistic/Bayesian'; equivalence_scope names Bayesian belief update"),
    ("K06", "H18", "WEAK", "equivalence_scope: probabilistic belief-update semantics"),
    ("K06", "H19", "WEAK", "equivalence_scope: probabilistic belief-update semantics"),
    ("K07", "H13", "STRONG", "paper_name 'planning/control'"),
    ("K07", "H14", "STRONG", "equivalence_scope: lookahead/dynamic-programming/control-equivalent mechanism"),
    ("K07", "H16", "WEAK", "equivalence_scope: lookahead mechanism, not one named planning algorithm"),
    ("K08", "H05", "STRONG", "equivalence_scope: selective persistent retrieval; may be associative, keyed or content-addressed"),
    ("K08", "H06", "STRONG", "equivalence_scope: ... may be associative ..."),
    ("K08", "H07", "STRONG", "paper_name 'retrieval/memory'"),
    ("K08", "H11", "WEAK", "required: multiple persistent records; query changes selected record"),
    ("K09", "H35", "STRONG", "paper_name 'evolutionary/population search'"),
    ("K09", "H19", "WEAK", "equivalence_scope: population/heredity/variation/selection search mechanism"),
    ("K10", "H10", "STRONG", "paper_name 'program synthesis'"),
    ("K10", "H11", "WEAK", "equivalence_scope: program/expression synthesis from specification"),
    ("K11", "H42", "STRONG", "paper_name 'self-modifying/developmental'"),
    ("K11", "H40", "WEAK", "equivalence_scope: persistent self/developmental mechanism change"),
    ("K11", "H41", "WEAK", "equivalence_scope: persistent self/developmental mechanism change"),
]

# The four requirements a blind recovery would bear on if a binding existed.
K_BEARING_REQUIREMENTS = ("R02", "R03", "R04", "R10")


def load_k_registry():
    path = os.path.join(RESEARCH, "gmi-833-aj9a-known-family-benchmark-v1", "KNOWN_FAMILY_BENCHMARK_V1.json")
    with open(path, "r") as handle:
        return json.load(handle)


def verify_k_binding_absence(row_texts):
    """Two independent absence checks for a primary K-family-to-named-row binding.

    Way 1: scan every file of every aj9*/blind-recovery package for any of the 43 verbatim
    row texts.
    Way 2: scan the same packages for the substring 'Section H'.

    Returns a record; an alarm on either way is a hard failure of the freeze's premise.
    """
    packages = [
        "gmi-833-aj9a-known-family-benchmark-v1",
        "gmi-833-aj9b-k01-blind-recovery-v1",
        "gmi-833-aj9c-k02-blind-recovery-v1",
        "gmi-833-aj9d-k03-blind-recovery-v1",
        "gmi-833-aj9e-k04-blind-recovery-v1",
        "gmi-833-aj9f-k05-blind-recovery-v1",
        "gmi-833-aj9g-k06-blind-recovery-v1",
        "gmi-833-aj9h-k07-k11-blind-recovery-v1",
        "gmi-833-blind-recovery-v2-v1",
    ]
    probes = [text.rstrip(".") for text in row_texts]
    way1_hits = []
    way2_hits = []
    files_scanned = 0
    control_hits = 0
    for package in packages:
        root = os.path.join(RESEARCH, package)
        if not os.path.isdir(root):
            raise RuntimeError("expected package missing: " + package)
        for name in sorted(os.listdir(root)):
            path = os.path.join(root, name)
            if not os.path.isfile(path):
                continue
            files_scanned += 1
            try:
                with open(path, "r") as handle:
                    blob = handle.read()
            except (UnicodeDecodeError, ValueError):
                continue
            for probe in probes:
                if probe in blob:
                    way1_hits.append((package, name, probe))
            if "Section H" in blob:
                way2_hits.append((package, name))
            # control pattern: these packages must all mention a K family id, proving the
            # scan reads their bytes at all (a grep that cannot hit anything is not an
            # absence proof).
            if "K0" in blob or "K1" in blob:
                control_hits += 1
    return {
        "files_scanned": files_scanned,
        "way1_verbatim_row_text_hits": way1_hits,
        "way2_section_h_mention_hits": way2_hits,
        "control_pattern_hits": control_hits,
        "absence_established": not way1_hits and not way2_hits and control_hits > 0,
    }


def build_map(registry, row_index):
    """row_index maps H-id -> row text."""
    k_ids = [f["family_id"] for f in registry["families"]]
    k_names = dict((f["family_id"], f["paper_name"]) for f in registry["families"])
    edges = []
    for k_id, h_id, strength, basis in CANDIDATE_EDGES:
        if k_id not in k_ids:
            raise RuntimeError("unknown K family " + k_id)
        if h_id not in row_index:
            raise RuntimeError("unknown H row " + h_id)
        edges.append({
            "k_family": k_id,
            "k_paper_name": k_names[k_id],
            "h_id": h_id,
            "row": row_index[h_id],
            "strength": strength,
            "basis": basis,
            "provenance": "AGENT_CONSTRUCTED_UNADJUDICATED",
        })
    by_row = {}
    for edge in edges:
        by_row.setdefault(edge["h_id"], []).append(edge["k_family"])
    by_k = {}
    for edge in edges:
        by_k.setdefault(edge["k_family"], []).append(edge["h_id"])
    rows_without_k = sorted(h for h in row_index if h not in by_row)
    return {
        "edges": edges,
        "rows_with_candidate_k": sorted(by_row),
        "rows_without_any_k": rows_without_k,
        "k_to_rows": dict((k, sorted(v)) for k, v in by_k.items()),
        "rows_with_multiple_k": sorted(h for h, v in by_row.items() if len(v) > 1),
    }
