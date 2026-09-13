"""Execute the frozen deferred predictions.

The prediction table is PARSED from DEFERRED_PREDICTIONS_V1.md, never hardcoded,
so this executes the registration rather than the author's memory.  The frozen
digest is bound and reported.
"""
import hashlib
import re
from fractions import Fraction
from pathlib import Path

import learning_law_selection_v1 as M

HERE = Path(__file__).resolve().parent
FROZEN = HERE / "DEFERRED_PREDICTIONS_V1.md"

CAPABILITY_WORDS = {
    "differentiable": "DIFFERENTIABLE_OBJECTIVE",
    "euclidean": "EUCLIDEAN_GEOMETRY",
    "simplex": "SIMPLEX_GEOMETRY",
    "likelihood": "LIKELIHOOD_MODEL",
    "finite hypotheses": "FINITE_HYPOTHESES",
    "discrete programs": "DISCRETE_PROGRAM_SPACE",
    "ordinal comparison": "ORDINAL_COMPARISON",
}
OPERATION_WORDS = {
    "normalization": "NORMALIZATION", "projection": "PROJECTION",
    "likelihood eval": "LIKELIHOOD_EVAL", "gradient eval": "GRADIENT_EVAL",
    "enumeration": "ENUMERATION", "comparison": "COMPARISON",
}


def frozen_text():
    return FROZEN.read_text(encoding="utf-8")


def frozen_digest():
    return hashlib.sha256(FROZEN.read_bytes()).hexdigest()


def _price(token):
    token = token.strip()
    if "/" in token:
        a, b = token.split("/")
        return Fraction(int(a), int(b))
    return Fraction(int(token))


def _section(text, heading):
    """Text between one heading and the next, so a parser cannot roam."""
    m = re.search(r"^##\s+" + re.escape(heading) + r"\s*$", text, re.M)
    if not m:
        raise ValueError("section not found: %r" % heading)
    rest = text[m.end():]
    nxt = re.search(r"^##\s+", rest, re.M)
    return rest[:nxt.start()] if nxt else rest


def parse_ecologies(text):
    """Rows like: | `D1_MEMORY_BOUND` | normalization 2, projection 11 |

    Scoped to the Frozen ecologies section: the prediction table also contains
    a backticked ecology id, and an unscoped pattern reads its law cell as a
    price clause.
    """
    text = _section(text, "Frozen ecologies")
    out = {}
    for m in re.finditer(r"\|\s*`(D\d_[A-Z_]+)`\s*\|([^|]+)\|", text):
        name, spec = m.group(1), m.group(2)
        prices = {}
        for part in spec.split(","):
            part = part.strip()
            mm = re.match(r"([a-z ]+?)\s+(\d+(?:/\d+)?)$", part)
            if not mm:
                raise ValueError("unparsed price clause: %r" % part)
            op = OPERATION_WORDS[mm.group(1).strip()]
            prices[op] = _price(mm.group(2))
        out[name] = prices
    return out


def parse_predictions(text):
    """Rows like: | D-P1 | differentiable, Euclidean, simplex | `D1_...` | `LAW` |"""
    text = _section(text, "Predictions not evaluated here")
    out = []
    for m in re.finditer(r"\|\s*(D-P\d)\s*\|([^|]+)\|\s*`(D\d_[A-Z_]+)`\s*\|\s*`([A-Z_]+)`\s*\|", text):
        tag, caps_text, eco, law = m.groups()
        caps = set()
        for word in caps_text.split(","):
            key = word.strip().lower()
            if key not in CAPABILITY_WORDS:
                raise ValueError("unregistered capability word: %r" % key)
            caps.add(CAPABILITY_WORDS[key])
        out.append({"tag": tag, "capabilities": frozenset(caps),
                    "ecology": eco, "predicted": law})
    return out


def execute():
    text = frozen_text()
    ecologies = parse_ecologies(text)
    predictions = parse_predictions(text)
    rows = []
    for p in predictions:
        prices = M.uniform_prices()
        prices.update(ecologies[p["ecology"]])
        result = M.select(p["capabilities"], prices)
        rows.append({
            "tag": p["tag"], "ecology": p["ecology"], "predicted": p["predicted"],
            "terminal": result["terminal"], "observed": result["law"],
            "held": result["terminal"] == "SELECTED" and result["law"] == p["predicted"],
            "costs": {k: str(v) for k, v in (result.get("costs") or {}).items()},
        })
    held = sum(1 for r in rows if r["held"])
    return {"schema": "GMI_DEFERRED_EXECUTION_V1",
            "frozen_digest": frozen_digest(),
            "predictions": rows,
            "held": held, "total": len(rows),
            "terminal": "ALL_DEFERRED_PREDICTIONS_HELD" if held == len(rows)
                        else "DEFERRED_PREDICTIONS_PARTIALLY_FAILED"}


if __name__ == "__main__":
    import json
    print(json.dumps(execute(), indent=1, sort_keys=True))
