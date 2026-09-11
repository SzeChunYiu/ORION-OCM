"""R4 — known-parent adapters: the registered rows of the D'/E' microscopes written as morphology-IR genotypes (the
calibration zoo of GMI_MACHINE_INTELLIGENCE_BIOSPHERE_V1 section 15). Every genotype uses only neutral primitives; the
names below are labels for the archive, never kinds. Each adapter is validated against its hand-written row by running the
same ecology protocol (smooth.run) and comparing capability and lifecycle coordinates (zoo receipt)."""
from __future__ import annotations

from . import morph


def gradient_net(h=2, lr=4):
    """S4-like: x -> AFFINE(h) -> THRESH -> LINEAR(v) + c -> out; GRAD on both parameter blocks; EVIDENCE for revocation replay."""
    per = 5  # 4 weights + bias per hidden unit
    return morph.make({0: ("INPUT", {"width": 4}), 1: ("DENSE", {"width": per * h}), 2: ("AFFINE", {"width": h}), 3: ("NONLIN", {"fn": 0}), 4: ("DENSE", {"width": h}), 5: ("LINEAR", {}),
                       6: ("CONST", {"value": 0}), 7: ("SUM", {}), 8: ("OUTPUT", {}), 9: ("TARGET", {}), 10: ("GRAD", {"lr": lr}), 11: ("GRAD", {"lr": lr}), 12: ("EVIDENCE", {"cap": 64})},
                      [(1, 2, 0), (0, 2, 1), (2, 3, 0), (4, 5, 0), (3, 5, 1), (5, 7, 0), (6, 7, 1), (7, 8, 0), (1, 10, 0), (7, 10, 1), (9, 10, 2), (4, 11, 0), (7, 11, 1), (9, 11, 2), (0, 12, 0), (9, 12, 1)],
                      meta={"zoo": "gradient_net"})


def hamming_knn(k=3):
    """S5h-like: exemplar store + k-nearest (Hamming) + insert."""
    return morph.make({0: ("INPUT", {"width": 4}), 1: ("KVSTORE", {"cap": 16}), 2: ("NEAREST", {"k": k, "metric": 0}), 3: ("OUTPUT", {}), 4: ("TARGET", {}), 5: ("INSERT", {})},
                      [(1, 2, 0), (0, 2, 1), (2, 3, 0), (1, 5, 0), (0, 5, 1), (4, 5, 2)], meta={"zoo": "hamming_knn"})


def exemplar_table(keybits=4):
    """S5-like: exact table keyed by the input bits (no generalization to unseen keys)."""
    return morph.make({0: ("INPUT", {"width": 4}), 1: ("TABLE", {"keybits": keybits}), 2: ("LOOKUP", {}), 3: ("OUTPUT", {}), 4: ("TARGET", {}), 5: ("CLOSEDFORM", {})},
                      [(1, 2, 0), (0, 2, 1), (2, 3, 0), (1, 5, 0), (0, 5, 1), (4, 5, 2)], meta={"zoo": "exemplar_table"})


def program_search(budget=2401, grammar=0):
    """S2a-like: program (linear coefficient grammar) executed on the input; evidence buffer; search on every feedback."""
    return morph.make({0: ("INPUT", {"width": 4}), 1: ("PROGRAM", {"grammar": grammar}), 2: ("PROGEXEC", {}), 3: ("OUTPUT", {}), 4: ("TARGET", {}), 5: ("EVIDENCE", {"cap": 64}), 6: ("SEARCH", {"budget": budget})},
                      [(1, 2, 0), (0, 2, 1), (2, 3, 0), (0, 5, 0), (4, 5, 1), (1, 6, 0), (5, 6, 1)], meta={"zoo": "program_search"})


def particles(pop=4, grammar=0):
    """S3-like: program + evidence + population/mutation update (stochastic)."""
    return morph.make({0: ("INPUT", {"width": 4}), 1: ("PROGRAM", {"grammar": grammar}), 2: ("PROGEXEC", {}), 3: ("OUTPUT", {}), 4: ("TARGET", {}), 5: ("EVIDENCE", {"cap": 64}), 6: ("PMUTATE", {"pop": pop})},
                      [(1, 2, 0), (0, 2, 1), (2, 3, 0), (0, 5, 0), (4, 5, 1), (1, 6, 0), (5, 6, 1)], meta={"zoo": "particles"})


def soft_retrieval():
    """S5a-like: exemplar store + score-and-select (normalized similarity weights)."""
    return morph.make({0: ("INPUT", {"width": 4}), 1: ("KVSTORE", {"cap": 16}), 2: ("SCORESELECT", {"temp": 1}), 3: ("OUTPUT", {}), 4: ("TARGET", {}), 5: ("INSERT", {})},
                      [(1, 2, 0), (0, 2, 1), (2, 3, 0), (1, 5, 0), (0, 5, 1), (4, 5, 2)], meta={"zoo": "soft_retrieval"})


def compiled_search(budget=2401, keybits=4):
    """search + materialized table serving (compile-then-serve)."""
    return morph.make({0: ("INPUT", {"width": 4}), 1: ("PROGRAM", {"grammar": 0}), 2: ("MATERIALIZE", {"keybits": keybits}), 3: ("LOOKUP", {}), 4: ("OUTPUT", {}), 5: ("TARGET", {}), 6: ("EVIDENCE", {"cap": 64}), 7: ("SEARCH", {"budget": budget})},
                      [(1, 2, 0), (2, 3, 0), (0, 3, 1), (3, 4, 0), (0, 6, 0), (5, 6, 1), (1, 7, 0), (6, 7, 1)], meta={"zoo": "compiled_search"})


ZOO = {"gradient_net_h2": lambda: gradient_net(2), "gradient_net_h4": lambda: gradient_net(4), "hamming_knn_k3": lambda: hamming_knn(3), "exemplar_table": exemplar_table,
       "program_search": program_search, "particles_p4": lambda: particles(4), "soft_retrieval": soft_retrieval, "compiled_search": compiled_search}
