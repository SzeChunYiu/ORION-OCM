"""Prospectively frozen future task families (FO-V1).

The T3 key is frozen and held out.  The directive is explicit: do not look at
T3 to design anything and do not re-draw it.  Evolvability nevertheless needs a
FUTURE family, and D27 needs related / unrelated / harmful controls.

So the families here are minted from NEW keys, before any scored run, using the
SAME deterministic generator the frozen stack already owns
(evaluation/t3_ecology.t3_draw / run_t3).  Nothing about T3 is read, re-drawn or
touched; only the generator is reused, which is what "carve a new split and
freeze it first" means in a stack whose families are a pure function of a key.

Keys are derived from a fixed protocol string so they are auditable and
reproducible from the freeze alone -- nobody chooses the instance parameters.

    FOF1   related future family     evolvability target, D27 "related tasks"
    CTRLU  unrelated control         must NOT gain from inheritance
    CTRLH  harmful control           inheritance should hurt (negative transfer)

CORRELATION DISCLOSURE (recorded, not hidden): FOF1 and the held-out T3 share a
generator, so T3-generalization and evolvability are not independent
measurements.  The realised correlation is computed and reported; it is a
property of the design, declared before the run, not a finding.
"""
from __future__ import annotations

import hashlib
from typing import Any, Dict, Tuple

PROTOCOL_SALT = "OCM_FORM_ORACLE_V1|2026-09-10|prospective_future_families"

# The three keys are pure functions of the protocol salt: minted here, recorded
# verbatim in FORM_ORACLE_PROTOCOL_V1.json, never hand-picked.
_KEY_ROLES: Tuple[str, ...] = ("FOF1_RELATED", "CTRLU_UNRELATED",
                               "CTRLH_HARMFUL")


def mint_key(role: str) -> str:
    if role not in _KEY_ROLES:
        raise ValueError("unknown future-family role %r" % role)
    h = hashlib.sha256(("%s|%s" % (PROTOCOL_SALT, role)).encode()).hexdigest()
    return "FOFutureFamilyV1:%s" % h[:16]


FOF1_KEY = mint_key("FOF1_RELATED")
CTRLU_KEY = mint_key("CTRLU_UNRELATED")
CTRLH_KEY = mint_key("CTRLH_HARMFUL")

# The one T3 key this module is allowed to know: its IDENTIFIER, used only to
# PROVE disjointness.  Its draw and its results are never read here.
HELDOUT_T3_KEY_ID = "GSHeldoutT3V1:4d0a1487e4427449"


def keys_record() -> Dict[str, Any]:
    return {
        "protocol_salt": PROTOCOL_SALT,
        "FOF1_RELATED": FOF1_KEY,
        "CTRLU_UNRELATED": CTRLU_KEY,
        "CTRLH_HARMFUL": CTRLH_KEY,
        "heldout_t3_key_id": HELDOUT_T3_KEY_ID,
        "generator": "evaluation.t3_ecology.t3_draw",
        "correlation_disclosure": (
            "FOF1 and the held-out T3 share the t3_draw generator; "
            "t3_gen and evolvability are therefore not independent. "
            "Declared pre-run; realised correlation reported."),
    }


def assert_disjoint_from_t3() -> Dict[str, Any]:
    """Hard check: every minted key differs from the held-out T3 key, and the
    resulting parameter DRAWS differ too.

    Executed, not logged.  Raises on collision.  Returns the pass record with
    the drawn parameters for FOF1/CTRLU/CTRLH so the freeze can carry them
    verbatim -- the T3 draw is NOT computed or returned.
    """
    from evaluation.t3_ecology import t3_draw
    minted = {"FOF1": FOF1_KEY, "CTRLU": CTRLU_KEY, "CTRLH": CTRLH_KEY}
    for name, k in minted.items():
        if k == HELDOUT_T3_KEY_ID:
            raise RuntimeError("FUTURE_FAMILY_KEY_COLLIDES_WITH_T3: %s" % name)
    draws = {name: t3_draw(k) for name, k in minted.items()}
    # pairwise distinctness among the minted families themselves
    seen: Dict[str, str] = {}
    for name, d in draws.items():
        blob = repr(sorted((f, tuple(sorted(v.items()))) for f, v in d.items()))
        if blob in seen:
            raise RuntimeError("FUTURE_FAMILY_DRAW_COLLISION: %s == %s"
                               % (name, seen[blob]))
        seen[blob] = name
    return {"GATE_FUTURE_FAMILIES_DISJOINT": True,
            "keys": minted, "draws": draws}


def evaluate_future(genome: Any, key: str) -> Dict[str, Any]:
    """One future-family evaluation, frozen gates and charging verbatim."""
    from evaluation.t3_ecology import evaluate_t3
    return evaluate_t3(genome, key)


def future_capability(genome: Any, key: str) -> float:
    r = evaluate_future(genome, key)
    return float(r["evaluation"].get("solved_fraction", 0.0))
