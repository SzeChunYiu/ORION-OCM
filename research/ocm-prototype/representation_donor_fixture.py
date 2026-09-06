"""Use the committed SV fixture verbatim; declared field variants are development controls."""
from dataclasses import replace
import hashlib
import importlib.util
from pathlib import Path
from ocm.kso.space import Atom, Hyperedge
from ocm.kso.warrant import WarrantProfile as WP
from ocm.kso.types import Authority

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests/m2/test_solve_loop.py"
FIXTURE_SHA256 = "1f4c20ec1c682ed62036dc2112bd4dc095f2c2784debd41e3fc6db7e528fdcdb"
BACKGROUND_ADDED = 8


def fixture(variant="base"):
    if hashlib.sha256(FIXTURE.read_bytes()).hexdigest() != FIXTURE_SHA256:
        raise ValueError("CONSUMER_FIXTURE_SOURCE_DRIFT")
    spec = importlib.util.spec_from_file_location("representation_existing_sv_fixture", FIXTURE)
    existing = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(existing)
    ks = existing._space()
    added = tuple(f"background_{i}" for i in range(BACKGROUND_ADDED))
    ks = ks.with_atoms(*(Atom(x, "claim") for x in added))
    if variant == "incoming":
        ks = ks.with_edges(Hyperedge("negative-incoming", ("q",), (added[0],), "SUPPORT"))
    elif variant == "mixed_warrant":
        ks = ks.replace_atom(replace(ks.atom(added[0]), warrant=WP.of({"background_support"})))
    elif variant == "alternative":
        ks = ks.replace_atom(replace(ks.atom("fact"), warrant=WP.of({1}, {"backup"})))
    elif variant != "base":
        raise ValueError("UNREGISTERED_FIXTURE_VARIANT")
    merged = ("island", *added)
    blocks = tuple((x,) for x in ks.ids if x not in merged) + (merged,)
    family = tuple(map(frozenset, ((), (1,), ("backup",), (1,"backup"), (2,), (3,),
                                  ("irrelevant",), ("background_support",))))
    return {"ks": ks, "task": existing._task(), "config": existing._cfg(),
            "operators": [existing._op()], "authority": Authority.of(src=3),
            "background": merged, "blocks": blocks, "revocations": family,
            "variant": variant}
