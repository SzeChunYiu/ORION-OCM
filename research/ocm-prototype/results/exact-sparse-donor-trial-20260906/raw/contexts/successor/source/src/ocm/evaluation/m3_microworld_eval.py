"""M3 microworld evaluation receipt (M3 §10 metrics — separate numbers, no aggregate).

Learn construction families on the dev split (aligned demonstrations), then report on the frozen
protected split:
  structural   construction identification rate
  semantic     exact canonical-meaning match; role-edge F1; negation/question accuracy
  ambiguity    candidate-set recall on a planted polysemy suite; false-collapse rate (must be 0)
  acquisition  demonstrations required per family; held-out compositional reuse; revocation
               locality (revoke one demonstration → predicted reopen set only)
  paraphrase   active/passive meaning equivalence
Every number names its denominator.  Exit 0 = ran; the verdict is inside; no claim is made.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from ocm.language import acquisition as AQ
from ocm.language import constructions as C
from ocm.language import interpret as I
from ocm.language import lexicon as L
from ocm.language import meaning as M
from ocm.language import microworld as W
from ocm.kso.warrant import WarrantProfile as WP


def lexicon_for_corpus() -> L.Lexicon:
    from ocm.language.bootstrap import microworld_lexicon

    return microworld_lexicon()


def role_f1(pred: M.MeaningGraph, gold: M.MeaningGraph) -> float:
    def roles(g):
        return {(e.relation, g.node(e.tails[0]).label, g.node(e.heads[0]).label) for e in g.edges if e.relation.startswith("ROLE:")}

    p, q = roles(pred), roles(gold)
    if not p and not q:
        return 1.0
    tp = len(p & q)
    prec = tp / len(p) if p else 0.0
    rec = tp / len(q) if q else 0.0
    return 0.0 if prec + rec == 0 else 2 * prec * rec / (prec + rec)


def run(seed: str = "OCM-M3-MICROWORLD-20260905") -> dict:
    ex = W.generate(seed)
    lx = lexicon_for_corpus()
    dev = [e for e in ex if e.split == "dev"]
    prot = [e for e in ex if e.split == "protected"]
    cons = list(C.seed_constructions())  # seed inventory (marked SEED) for families not learned here
    seed_inv = {c.construction_id: c for c in cons}
    # learn the transitive family from dev demonstrations (the M3 acquisition path); NP is a helper
    N, V = L.Category.NOUN, L.Category.VERB
    hyps = AQ.order_hypotheses([("S", C.Slot("subj", N, phrase="NP")), ("V", C.Slot("verb", V, requires=("tense",))), ("O", C.Slot("obj", N, phrase="NP"))])
    fam = AQ.ConstructionFamily("transitive", hyps, seed_inv["en:transitive"].template, query_family=tuple(e.utterance for e in dev if e.family == "transitive")[:5], helpers=(seed_inv["en:np"],))
    demos_all = [AQ.Demonstration(e.utterance, e.meaning, f"ev:demo:{e.example_id}") for e in dev if e.family == "transitive"]
    lessons_needed = None
    learned = None
    for k in range(1, len(demos_all) + 1):
        p = AQ.acquire(fam, lx, demos_all[:k])
        if p.status.value == "PASS":
            lessons_needed, learned = k, AQ.construction_from_proposal(fam, p, "en:transitive:learned")
            break
    inventory = [c for c in cons if c.construction_id != "en:transitive"] + ([learned] if learned else [])
    # protected evaluation
    per_family: dict[str, dict[str, int]] = {}
    exact = ident = 0
    f1_sum = 0.0
    neg_ok = neg_n = q_ok = q_n = 0
    for e in prot:
        r = I.interpret(e.utterance, lx, inventory)
        fam_hit = r.verdict is I.Verdict.INTERPRETED and (r.candidates[0].construction_id.split(":")[1].startswith(e.family.split("_")[0]) or (e.family == "yes_no" and "yesno" in r.candidates[0].construction_id))
        ok = r.verdict is I.Verdict.INTERPRETED and M.isomorphic(r.meaning, e.meaning)
        d = per_family.setdefault(e.family, {"n": 0, "exact": 0, "identified": 0})
        d["n"] += 1
        d["exact"] += int(ok)
        d["identified"] += int(fam_hit)
        exact += int(ok)
        ident += int(fam_hit)
        f1_sum += role_f1(r.meaning, e.meaning) if r.meaning is not None else 0.0
        if e.family == "negation":
            neg_n += 1
            neg_ok += int(ok)
        if e.family == "yes_no":
            q_n += 1
            q_ok += int(ok)
    # ambiguity suite: polysemous 'bank' planted into the lexicon; false collapse must be 0
    lx2 = lexicon_for_corpus()
    lx2.add(L.Lexeme("bank", L.Category.NOUN, (L.Sense("bank:fin", "financial_institution", "entity", WP.of({"ev:bf"})), L.Sense("bank:river", "river_bank", "entity", WP.of({"ev:br"})))))
    amb = [I.interpret(f"the {a} saw the bank", lx2, inventory) for a in ("robot", "cat", "girl")]
    recall = sum(1 for r in amb if r.verdict is I.Verdict.AMBIGUOUS and len(r.candidates) == 2)
    false_collapse = sum(1 for r in amb if r.verdict is I.Verdict.INTERPRETED)
    # revocation locality: revoke one pinning demonstration → construction dead → every transitive utterance reopens, nothing else
    locality = None
    if learned is not None:
        rev = tuple(learned.warrant.evidence)[:1]
        dead_after = I.interpret(prot[0].utterance if prot[0].family == "transitive" else next(e.utterance for e in prot if e.family == "transitive"), lx, inventory, revoked=rev).verdict is not I.Verdict.INTERPRETED
        passive_ok = next((I.interpret(e.utterance, lx, inventory, revoked=rev).verdict is I.Verdict.INTERPRETED for e in prot if e.family == "passive"), None)
        locality = {"revoked": list(rev), "transitive_reopened": dead_after, "passive_intact": passive_ok}
    pairs = W.paraphrase_pairs(ex)
    para_ok = sum(1 for a, p in pairs if (ra := I.interpret(a.utterance, lx, inventory)).verdict is I.Verdict.INTERPRETED and (rp := I.interpret(p.utterance, lx, inventory)).verdict is I.Verdict.INTERPRETED and M.isomorphic(ra.meaning, rp.meaning))
    return {
        "receipt": "M3_MICROWORLD_EVAL_V1",
        "custody": W.custody_receipt(ex, seed),
        "acquisition": {"transitive_demonstrations_required": lessons_needed, "hypothesis_class_size": len(hyps), "learned": learned is not None},
        "protected": {"n": len(prot), "exact_meaning": exact, "construction_identified": ident, "mean_role_f1": round(f1_sum / len(prot), 4), "negation": f"{neg_ok}/{neg_n}", "yes_no": f"{q_ok}/{q_n}", "per_family": per_family},
        "ambiguity": {"suite_n": len(amb), "candidate_set_recall": recall, "false_collapse": false_collapse},
        "revocation_locality": locality,
        "paraphrase": {"pairs": len(pairs), "meaning_equivalent": para_ok},
        "authority": "synthetic microworld with a given vocabulary; measures construction acquisition/interpretation only; no real-language, no comparator, no novelty claim",
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--out", default=None)
    a = p.parse_args(argv)
    r = run()
    txt = json.dumps(r, indent=2, sort_keys=True)
    if a.out:
        from ocm.evaluation.output import write_result
        write_result(Path(a.out), json.loads(txt))
    print(json.dumps({k: r[k] for k in ("acquisition", "protected", "ambiguity", "revocation_locality", "paraphrase")}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
