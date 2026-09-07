"""M7 §3.1 / §3.3 external families under the frozen protocols: BLiMP admissibility (pair correct
iff the good sentence is INTERPRETED and the bad one is not; uncovered pairs reported separately)
and UD EWT interpretability coverage + role agreement per genre.  Reads the custody-managed data
from a local data root (billy-old: ~/ocm-data); never bundles data.  Exit 0 = ran; CANNOT_CHECK
per family when the data is absent.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

from ocm.chat.session import _load_lexicon_and_constructions
from ocm.language.interpret import Verdict, interpret


def _inventory():
    lx, cons = _load_lexicon_and_constructions(Path("."))
    return lx, cons


def blimp(root: Path, phenomena: list[str]) -> dict:
    lx, cons = _inventory()
    out = {}
    for ph in phenomena:
        p = root / "blimp" / "data" / f"{ph}.jsonl"
        if not p.exists():
            out[ph] = {"status": "CANNOT_CHECK", "reason": "data absent"}
            continue
        n = covered = correct = 0
        for line in p.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            d = json.loads(line)
            n += 1
            g = interpret(d["sentence_good"].rstrip(".?!"), lx, cons).verdict is Verdict.INTERPRETED
            b = interpret(d["sentence_bad"].rstrip(".?!"), lx, cons).verdict is Verdict.INTERPRETED
            if g or b:
                covered += 1
                correct += int(g and not b)
        out[ph] = {"pairs": n, "covered": covered, "coverage": round(covered / n, 4) if n else None, "correct_over_covered": correct, "accuracy_over_covered": round(correct / covered, 4) if covered else None}
    return out


def _conllu_sentences(path: Path):
    sent, meta = [], {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("#"):
            k, _, v = line[1:].partition("=")
            meta[k.strip()] = v.strip()
            continue
        if not line.strip():
            if sent:
                yield meta, sent
            sent, meta = [], {}
            continue
        cols = line.split("\t")
        if "-" in cols[0] or "." in cols[0]:
            continue
        sent.append(cols)
    if sent:
        yield meta, sent


def ud_ewt(root: Path, split: str = "dev", limit: int | None = None) -> dict:
    lx, cons = _inventory()
    p = root / "ud-ewt" / f"en_ewt-ud-{split}.conllu"
    if not p.exists():
        return {"status": "CANNOT_CHECK", "reason": "data absent"}
    per_genre: dict[str, dict[str, int]] = defaultdict(lambda: {"sentences": 0, "interpreted": 0, "agent_agree": 0, "patient_agree": 0, "with_nsubj": 0, "with_obj": 0})
    k = 0
    for meta, sent in _conllu_sentences(p):
        sid = meta.get("sent_id", "")
        genre = sid.split("-")[0] if "-" in sid else "unknown"
        g = per_genre[genre]
        g["sentences"] += 1
        text = " ".join(c[1] for c in sent)
        r = interpret(text.lower().rstrip(".?!"), lx, cons)
        if r.verdict is Verdict.INTERPRETED:
            g["interpreted"] += 1
            roles = {e.relation: r.meaning.node(e.heads[0]).label for e in r.meaning.edges if e.relation.startswith("ROLE:")}
            nsubj = [c[2].lower() for c in sent if c[7] == "nsubj"]
            obj = [c[2].lower() for c in sent if c[7] == "obj"]
            if nsubj:
                g["with_nsubj"] += 1
                g["agent_agree"] += int(roles.get("ROLE:agent") in nsubj or roles.get("ROLE:patient") in nsubj and "passive" in " ".join(c[7] for c in sent))
            if obj:
                g["with_obj"] += 1
                g["patient_agree"] += int(roles.get("ROLE:patient") in obj)
        k += 1
        if limit and k >= limit:
            break
    return {"split": split, "protocol": "coverage + role agreement per genre; never collapsed", "genres": dict(per_genre)}


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--data-root", default=os.path.expanduser("~/ocm-data"))
    p.add_argument("--out", default=None)
    p.add_argument("--ud-limit", type=int, default=None)
    a = p.parse_args(argv)
    root = Path(a.data_root)
    phen = ["determiner_noun_agreement_1", "regular_plural_subject_verb_agreement_1", "irregular_past_participle_verbs", "passive_1", "wh_questions_object_gap", "anaphor_number_agreement"]
    r = {"receipt": "M7_BLIMP_UD_V1", "blimp": blimp(root, phen), "ud_ewt": ud_ewt(root, "dev", a.ud_limit), "authority": "frozen admissibility/coverage protocols over the Alpha inventory; coverage is expected to be small and is reported, not hidden; no likelihoods, no comparator"}
    if a.out:
        Path(a.out).write_text(json.dumps(r, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(r["blimp"], indent=1))
    print(json.dumps({g: v for g, v in r["ud_ewt"].get("genres", {}).items()}, indent=1)[:1500])
    return 0


if __name__ == "__main__":
    sys.exit(main())
