"""RV-377-202 — the kind-agnostic mutation grammar is inert on the full alphabet and survives every
single-kind deletion (the 13 kinds that were STRUCTURAL_TO_GENERATOR in RV-377-118 Lane C included)."""
import hashlib
import importlib
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

# digest of 200 random genotypes produced by the generator on main@fa5a754f BEFORE the RV-377-202 edit
# (computed on billy-old from the unmodified clone; pinned so the edit is provably inert on the full alphabet)
PIN_BEFORE_EDIT = "7698605a62b4764addd72c9c3a445f0352b64de619df6889b866789cb450c1e1"
STRUCTURAL_KINDS_RV118C = ["ABSTAIN", "DENSE", "KVSTORE", "LINEAR", "LOOKUP", "MATERIALIZE", "NEAREST", "PROGEXEC",
                           "PROGRAM", "SCORESELECT", "TABLE", "VERIFY", "VERSIONED"]


def _fresh(drop=None):
    for m in ("gmi_microscope.morphgen", "gmi_microscope.morph"):
        sys.modules.pop(m, None)
    morph = importlib.import_module("gmi_microscope.morph")
    if drop is not None:
        del morph.KINDS[drop]
        morph.CLASS_OF.pop(drop, None)
    morphgen = importlib.import_module("gmi_microscope.morphgen")
    return morph, morphgen


def _digest(morph, morphgen):
    h = hashlib.sha256()
    for s in range(200):
        rng = random.Random(s)
        g = morphgen.random_genotype(rng, steps=3 + (s % 9))
        c = morph.canonical(g)
        h.update(c.encode() if isinstance(c, str) else json.dumps(c, sort_keys=True).encode())
    return h.hexdigest()


def test_full_alphabet_is_byte_identical_to_pre_edit_generator():
    morph, morphgen = _fresh(None)
    assert len(morph.KINDS) == 36
    assert _digest(morph, morphgen) == PIN_BEFORE_EDIT


def test_every_single_kind_deletion_generates_without_crashing():
    for drop in STRUCTURAL_KINDS_RV118C:
        morph, morphgen = _fresh(drop)
        assert drop not in morph.KINDS
        rng = random.Random(1)
        for _ in range(60):
            g = morphgen.random_genotype(rng, steps=rng.randrange(3, 12))
            assert all(k != drop for k, _ in g["nodes"].values()), f"{drop} node generated after deletion"
    _fresh(None)  # restore the full alphabet for other tests
