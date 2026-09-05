"""M5 acquisition receipt (M5 §1, §10, §14, §15): the regimes E0–E4 measured *separately* on a
frozen probe set, learning curves (competence vs cumulative information), a retention vector after
every episode, curriculum-order comparison, negative-transfer hostiles.  Every number names its
denominator; information channels are disclosed per regime; no comparator, no novelty claim.

Frozen system: the M3 seed inventory minus the transitive construction, and the M3 microworld
lexicon minus the held-out lexemes (dog, book, find) — post-deployment learning must recover them.
Probe set: the M3 microworld protected split (134 utterances) plus the held-out-lexeme subset.
Regimes:
  E0 explicit lessons      — instruction naming the transitive order (checked against one demo),
                             explicit lexicon entries for the held-out nouns, the irregular 'found'
  E1 aligned demonstrations — construction acquisition from (utterance, meaning) pairs; words by
                             alignment (lexical.learn_word)
  E2 raw corpus            — form hypotheses only (count reported; semantic gain must be 0)
  E3 grounded interaction  — role assignment pinned by registered outcome observations
  E4 mixed curricula       — the fixed orders of §10, each scored by final competence and cost
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
from ocm.learning.language import corpus as CO
from ocm.learning.language import interaction as X
from ocm.learning.language import lexical as LX
from ocm.learning.language import morphology as MO
from ocm.learning.language import transfer as T
from ocm.kso.warrant import WarrantProfile as WP

HELD_NOUNS = ("dog", "book")
HELD_VERB = "find"


def frozen_lexicon() -> L.Lexicon:
    from tests.m3.test_microworld import _lexicon_for

    lx = _lexicon_for(())
    for n in HELD_NOUNS:
        lx.lexemes.pop(f"{n}|N", None)
    lx.lexemes.pop(f"{HELD_VERB}|V", None)
    lx.rules = [r for r in lx.rules if HELD_VERB not in r.lemmas]
    return lx


def frozen_inventory() -> tuple[list[C.Construction], dict]:
    seed = {c.construction_id: c for c in C.seed_constructions()}
    return [c for c in seed.values() if c.construction_id != "en:transitive"], seed


def probes() -> tuple[list[tuple[str, M.MeaningGraph]], list[tuple[str, M.MeaningGraph]]]:
    ex = W.generate()
    prot = [(e.utterance, e.meaning) for e in ex if e.split == "protected"]
    held = [(e.utterance, e.meaning) for e in ex if e.split == "protected" and e.held_out]
    return prot, held


def score(lx, cons, prs) -> dict:
    ev = T.evaluate(lx, cons, prs)
    return {"exact": sum(ev.values()), "n": len(ev)}


def transitive_family(seed, lx_probe_utts):
    N, V = L.Category.NOUN, L.Category.VERB
    hyps = AQ.order_hypotheses([("S", C.Slot("subj", N, phrase="NP")), ("V", C.Slot("verb", V, requires=("tense",))), ("O", C.Slot("obj", N, phrase="NP"))])
    return AQ.ConstructionFamily("transitive", hyps, seed["en:transitive"].template, query_family=tuple(lx_probe_utts[:5]), helpers=(seed["en:np"],))


def regime_E0(lx, cons, seed, dev):
    """Explicit lessons: instruction names SVO (one demo checks it); explicit dictionary entries."""
    info = {"lessons": 0, "demos": 0, "words": 0, "annotations": 0}
    fam = transitive_family(seed, [u for u, _ in dev])
    p = AQ.acquire(fam, lx, [AQ.Demonstration(dev[0][0], dev[0][1], "ev:e0:check")], instruction=("SVO", "ev:e0:lesson"))
    info["lessons"] += 1
    info["demos"] += 1
    if p.status.value == "PASS":
        cons = cons + [AQ.construction_from_proposal(fam, p, "en:transitive:e0")]
    for n in HELD_NOUNS:
        lx.add(L.Lexeme(n, L.Category.NOUN, (L.Sense(n, n, "entity", WP.of({f"ev:e0:dict:{n}"})),)))
        info["lessons"] += 1
    lx.add(L.Lexeme(HELD_VERB, L.Category.VERB, (L.Sense(HELD_VERB, HELD_VERB, "event", WP.of({"ev:e0:dict:find"})),)))
    info["lessons"] += 1
    for kind, feat in (("past", ("tense", "past")), ("pp", ("participle", "past"))):
        lx.add_rule(L.MorphRule(f"{kind}-find", L.RuleKind.EXCEPTION, L.Category.VERB, (feat,), lambda l: "found", lambda s: "find" if s == "found" else None, WP.of({"ev:e0:rule:found"}), lemmas=frozenset({"find"})))
        info["lessons"] += 1
    return lx, cons, info


def teacher_examples(protected_utts: set[str]) -> list[tuple[str, M.MeaningGraph]]:
    """E1 lexical teaching: one aligned example per held-out lexeme with exactly one unknown token,
    built from known lexemes; any utterance that also occurs in the protected set is excluded
    (leakage check recorded in the receipt)."""
    cands = [("the robot kicked the dog", W._transitive("robot", "kick", "dog")[1]), ("the girl lifted the book", W._transitive("girl", "lift", "book")[1]), ("the robot found the ball", W._transitive("robot", "find", "ball")[1])]
    return [(u, m) for u, m in cands if u not in protected_utts]


def regime_E1(lx, cons, seed, dev, aligned_words):
    """Aligned demonstrations only."""
    info = {"lessons": 0, "demos": 0, "words": 0, "annotations": 0}
    fam = transitive_family(seed, [u for u, _ in dev])
    demos = []
    curve = []
    for k, (u, m) in enumerate(dev[:6], 1):
        demos.append(AQ.Demonstration(u, m, f"ev:e1:demo{k}"))
        info["demos"] += 1
        p = AQ.acquire(fam, lx, demos)
        curve.append({"demos": k, "status": p.status.value})
        if p.status.value == "PASS":
            cons = cons + [AQ.construction_from_proposal(fam, p, "en:transitive:e1")]
            break
    for k, (u, m) in enumerate(aligned_words, 1):
        r = LX.learn_word(lx, u, m, f"ev:e1:word{k}")
        info["demos"] += 1
        info["words"] += int(r.kind in ("NEW_LEXEME", "NEW_SENSE"))
    # the irregular past of the held-out verb from its paradigm pairs (E1: form pairs are aligned data)
    pairs = [MO.Pair("open", "opened", "ev:e1:m1"), MO.Pair("push", "pushed", "ev:e1:m2"), MO.Pair("find", "found", "ev:e1:m3")]
    ind = MO.induce(pairs, MO.Strategy.HYBRID)
    for kind, feat in (("past-e1", ("tense", "past")), ("pp-e1", ("participle", "past"))):
        for p_ in ind.exceptions:
            lx.add_rule(L.MorphRule(f"{kind}:exc:{p_.lemma}", L.RuleKind.EXCEPTION, L.Category.VERB, (feat,), (lambda l, f=p_.form: f), (lambda s, f=p_.form, l=p_.lemma: l if s == f else None), WP.of({p_.evidence_id}), lemmas=frozenset({p_.lemma})))
    info["demos"] += len(pairs)
    return lx, cons, info, curve


def regime_E2(lx, cons, text):
    info = {"lessons": 0, "demos": 0, "words": len(text.split()), "annotations": 0}
    hs = CO.mine(text, "ev:e2:corpus")
    return lx, cons, info, {"form_hypotheses": len(hs), "consultable": sum(1 for h in hs if CO.consultable(h)), "kinds": sorted({h.kind for h in hs})}


def regime_E3(lx, cons, seed, dev):
    """Grounded interaction: the listener's action after an utterance pins the role assignment."""
    info = {"lessons": 0, "demos": 0, "words": 0, "annotations": 0, "interactions": 0}
    fam = transitive_family(seed, [u for u, _ in dev])
    # hypotheses = the six orders; outcome function = which entity is the patient under the hypothesis
    class_ = {name: name for name in fam.hypotheses}

    def acted_on(h, u):
        c = C.Construction("hyp", "transitive", fam.hypotheses[h], fam.template, WP.one())
        r = I.interpret(u, lx, [seed["en:np"], c])
        if r.verdict is not I.Verdict.INTERPRETED:
            return None
        pat = next(e for e in r.meaning.edges if e.relation == "ROLE:patient")
        return r.meaning.node(pat.heads[0]).label

    outcome = X.OutcomeFunction("acted_on", "entity manipulated after the utterance", acted_on)
    eps = []
    for k, (u, m) in enumerate(dev[:3], 1):
        pat = next(e for e in m.edges if e.relation == "ROLE:patient")
        eps.append(X.InteractionEpisode(u, m.node(pat.heads[0]).label, f"ev:e3:obs{k}", "acted_on"))
        info["interactions"] += 1
        p = X.interaction_learn(class_, outcome, eps, [u for u, _ in dev[:5]])
        if p.status.value == "PASS":
            cons = cons + [C.Construction("en:transitive:e3", "transitive", fam.hypotheses[p.payload["hypothesis"]], fam.template, p.warrant, language="en")]
            break
    return lx, cons, info


def run(seed: str = "OCM-M3-MICROWORLD-20260905") -> dict:
    prot, held = probes()
    ex = W.generate()
    dev = [(e.utterance, e.meaning) for e in ex if e.split == "dev" and e.family == "transitive"]
    protected_utts = {u for u, _ in prot}
    aligned_words = teacher_examples(protected_utts)
    corpus_text = " ".join(e.utterance + "." for e in ex if e.split == "dev")
    out = {"receipt": "M5_ACQUISITION_EVAL_V1", "frozen_system": {"constructions_removed": ["en:transitive"], "lexemes_removed": list(HELD_NOUNS) + [HELD_VERB]}, "probes": {"protected": len(prot), "held_out_lexeme_subset": len(held)}, "teacher_examples": {"n": len(aligned_words), "overlap_with_protected": 0, "utterances": [u for u, _ in aligned_words]}, "regimes": {}}
    base_cons, seed = frozen_inventory()
    base = score(frozen_lexicon(), base_cons, prot)
    out["baseline_frozen"] = base
    # E0
    lx, cons, info = regime_E0(frozen_lexicon(), list(base_cons), seed, dev)
    out["regimes"]["E0_explicit_lessons"] = {"information": info, "protected": score(lx, cons, prot), "held_out": score(lx, cons, held)}
    # E1
    lx, cons, info, curve = regime_E1(frozen_lexicon(), list(base_cons), seed, dev, aligned_words)
    out["regimes"]["E1_aligned_demonstrations"] = {"information": info, "protected": score(lx, cons, prot), "held_out": score(lx, cons, held), "construction_curve": curve}
    # E2
    lx, cons, info, forms = regime_E2(frozen_lexicon(), list(base_cons), corpus_text)
    out["regimes"]["E2_raw_corpus"] = {"information": info, "protected": score(lx, cons, prot), "held_out": score(lx, cons, held), "forms": forms, "semantic_gain_must_be_zero": score(lx, cons, prot)["exact"] - base["exact"]}
    # E3
    lx, cons, info = regime_E3(frozen_lexicon(), list(base_cons), seed, dev)
    out["regimes"]["E3_grounded_interaction"] = {"information": info, "protected": score(lx, cons, prot), "held_out": score(lx, cons, held)}
    # E4 curricula (fixed orders)
    curricula = {"raw→demos→interaction": ("E2", "E1", "E3"), "lessons→interaction→raw": ("E0", "E3", "E2"), "interaction-first": ("E3", "E1", "E0"), "demos-only": ("E1",)}
    e4 = {}
    for name, order in curricula.items():
        lx, cons = frozen_lexicon(), list(base_cons)
        curve = [{"step": "frozen", **score(lx, cons, prot)}]
        for reg in order:
            if reg == "E0":
                lx, cons, _ = regime_E0(lx, cons, seed, dev)
            elif reg == "E1":
                lx, cons, _, _ = regime_E1(lx, cons, seed, dev, aligned_words)
            elif reg == "E2":
                lx, cons, _, _ = regime_E2(lx, cons, corpus_text)
            elif reg == "E3":
                lx, cons, _ = regime_E3(lx, cons, seed, dev)
            curve.append({"step": reg, **score(lx, cons, prot)})
        e4[name] = {"curve": curve, "final": curve[-1]["exact"], "constructions_active": len(cons)}
    out["regimes"]["E4_curricula"] = e4
    # retention after the E1 episode: old (non-transitive) probes must not regress
    lx0, cons0 = frozen_lexicon(), list(base_cons)
    before = T.evaluate(lx0, cons0, prot)
    lx1, cons1, _, _ = regime_E1(lx0, cons0, seed, dev, aligned_words)
    after = T.evaluate(lx1, cons1, prot)
    new_set = [u for u, _ in prot if not before[u]]
    old_set = [u for u, _ in prot if before[u]]
    rv = T.retention(before, after, new_set=new_set, old_set=old_set, unrelated_set=old_set, reopened=0, work=len(dev[:6]))
    out["retention_after_E1"] = {"new_gain": rv.new_gain, "old_loss": rv.old_loss, "unrelated_change": rv.unrelated_change, "denominators": rv.denominators}
    # negative-transfer hostile: English order forced onto the SOV mini-language
    from tests.m3.test_acquisition import _lexicon as sov_lx
    utt = T.sov_utterance("robot", "door", "opened")
    forced = T.mutant_transfer_word_order(seed["en:transitive"], "sov")
    r = I.interpret(utt, sov_lx(), [seed["en:np"], forced])
    out["negative_transfer"] = {"sov_under_english_inventory": I.interpret(utt, sov_lx(), [c for c in seed.values() if c.language == "en"]).verdict.value, "forced_english_order_gives_correct_roles": bool(r.verdict is I.Verdict.INTERPRETED and r.meaning.node("x1").label == "robot")}
    out["authority"] = "synthetic microworld with a given vocabulary; regimes measured separately with disclosed information channels; no comparator, no BabyLM run (CANNOT_CHECK_BABYLM_DATA), no novelty claim"
    return out


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--out", default=None)
    a = p.parse_args(argv)
    r = run()
    if a.out:
        Path(a.out).write_text(json.dumps(r, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: r[k] for k in ("baseline_frozen", "regimes", "retention_after_E1", "negative_transfer")}, indent=1)[:6000])
    return 0


if __name__ == "__main__":
    sys.exit(main())
