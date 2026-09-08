"""Scan held-out set.mm theorems after pssdif for lemma-statement matches."""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import extract as E  # noqa: E402

SETMM = Path("/tmp/orion-native/set.mm")
ADMIT = HERE / "records" / "admit-01" / "ADMIT.json"


def statements_after(label="pssdif"):
    text = SETMM.read_text(encoding="ascii", errors="replace")
    # label $p STMT $=
    pattern = re.compile(r"(\S+) \$p (.*?)\s\$=", re.S)
    started = False
    rows = []
    for match in pattern.finditer(text):
        name, stmt = match.group(1), " ".join(match.group(2).split())
        if not started:
            if name == label:
                started = True
            continue
        rows.append({"label": name, "statement": stmt})
    return rows


def tokens(stmt):
    return stmt.split()


CLASS_VARS = {"A", "B", "C", "D", "E", "F", "G", "H", "K", "S", "T", "U", "V", "W", "X", "Y", "Z"}


def alpha_key(toks):
    """Collapse class identifiers for exact-shape matching."""
    mapping = {}
    out = []
    for tok in toks:
        if tok in CLASS_VARS or (tok.startswith("V") and tok[1:].isdigit()):
            if tok not in mapping:
                mapping[tok] = "C" + str(len(mapping))
            out.append(mapping[tok])
        else:
            out.append(tok)
    return tuple(out)


def scan():
    lemmas = E.unique_negatives()
    zero = [L for L in lemmas if not L["hypotheses"]]
    lemma_keys = {alpha_key(L["target"]): L for L in zero}
    held = statements_after()
    matches = []
    for row in held[:5000]:
        key = alpha_key(tokens(row["statement"]))
        if key in lemma_keys:
            src = lemma_keys[key]
            matches.append({
                "held_out_label": row["label"],
                "held_out_statement": row["statement"],
                "lemma_source": src["source_label"],
                "lemma_target": " ".join(src["target"]),
                "n_hypotheses": 0,
            })
    admit = json.loads(ADMIT.read_text()) if ADMIT.exists() else {}
    out = {
        "schema": "g2.causal-lemma-reuse.heldout-scan.v1",
        "held_out_after": "pssdif",
        "n_held_out_total": len(held),
        "n_scanned": min(5000, len(held)),
        "n_zero_premise_lemmas": len(zero),
        "n_statement_matches": len(matches),
        "first_held_out": [r["label"] for r in held[:12]],
        "matches": matches[:50],
        "native_verified": admit.get("n_verified"),
        "native_calls": admit.get("native_calls"),
    }
    dest = HERE / "records" / "admit-01" / "HELDOUT.json"
    dest.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({k: out[k] for k in out if k != "matches"}, indent=2))
    print("matches", len(matches))
    for m in matches[:15]:
        print(m["held_out_label"], "<=", m["lemma_source"], row_stmt := m["held_out_statement"][:120])
    return out


if __name__ == "__main__":
    scan()
