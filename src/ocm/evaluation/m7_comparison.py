"""M7 protected comparison harness (pre-registered in M7_PREREGISTRATION_V1.md).

Arms: OCM Alpha; OCM ablations (−revocation, −workspace/last-turn memory, −active clarification,
−gate); MatchedParent.v1 (strongest faithful matched parent); template baseline.  Families:
protected conversation suite (paired per turn), bounded-knowledge factual suite (generated from
the frozen manifest + out-of-scope), post-deployment learning challenge (identical lessons per
arm), negative-transfer challenge, answer-laundering audit, information and resource receipts.
Statistics: exact McNemar on discordant pairs and TOST at the pre-registered margin.  Terminals per
claim.  Nothing here tunes anything: the suites are frozen inputs; the harness only records.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import resource
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Callable

from ocm.chat.session import ChatSession, DEFAULT_MANIFEST
from ocm.comparators.matched_parent import MatchedParent
from ocm.dialogue import gate as G
from ocm.evaluation import stats as ST
from ocm.language import meaning as M
from ocm.language import realize as RZ

ROOT = Path(__file__).resolve().parents[3]
SUITES = {"V1": ROOT / "research" / "ocm-m7" / "M7_PROTECTED_CONVERSATIONS_V1.json", "V2": ROOT / "research" / "ocm-m7" / "M7_PROTECTED_CONVERSATIONS_V2.json"}
CONVS = SUITES["V1"]
PREREG = ROOT / "research" / "ocm-m7" / "M7_PREREGISTRATION_V1.md"
OUT_OF_SCOPE = ["is paris in spain", "is the sun a planet", "is mars a star", "is berlin in france", "is the moon a star", "is a cat a machine", "is a robot an animal", "is water a planet", "is stockholm in germany", "does the sun orbit the earth", "does the moon orbit mars", "is a whale a planet", "is rome in france", "is the nile a planet", "is a violin a river", "is a key a mammal", "is a dog a machine", "is ice a star", "is a book a river", "is a cup a planet"]


def _match(reply: str, pattern: str) -> bool:
    return any(p in reply for p in pattern.split("|"))


# ------------------------------------------------------------------ arms
class OCMArm:
    name = "ocm"

    def __init__(self, root: Path, ablations: frozenset[str] = frozenset()):
        self.root = root
        self.ablations = ablations
        self.s = ChatSession(root)
        self._apply_ablations()
        self.last_lesson: str | None = None

    def _apply_ablations(self) -> None:
        s = self.s
        if "no_revocation" in self.ablations:
            s._revoke = lambda text, eid, t0, seq0: s._commit(text, "Revoked.", G.Act.ACKNOWLEDGE, {}, t0, seq0)  # says so, does nothing
        if "last_turn_memory" in self.ablations:
            ws = s.dialogue.workspace
            orig = ws.active_commitments

            def last_only(speaker=None):
                cs = orig(speaker)
                return cs[-1:] if cs else []
            ws.active_commitments = last_only
        if "no_clarification" in self.ablations:
            d = s.dialogue
            orig_mc = d._maybe_clarify

            def pick_first(r, speaker):
                c = r.candidates[0]
                return d._record(speaker, c.meaning, r, r.utterance, False)
            d._maybe_clarify = pick_first
        if "no_gate" in self.ablations:
            G_commit = G.commit_gate
            s_module = sys.modules[ChatSession.__module__]
            s_module.G.commit_gate = lambda plan, surface, live, **kw: G.GateVerdict(True, ())  # noqa: E731

    def say(self, utt: str) -> str:
        if utt == "__restart__":
            self.s.runtime.persist()
            self.s = ChatSession(self.root)
            self._apply_ablations()
            return "restarted"
        if utt == "__revoke_last_lesson__":
            utt = f"revoke {self.last_lesson}"
        r = self.s.say(utt)
        if utt.startswith("teach:") and self.s.traces[-1].warrant_ids:
            self.last_lesson = self.s.traces[-1].warrant_ids[0]
        return r

    def info(self) -> dict:
        return {"knowledge_facts": len(self.s.world.facts), "lessons": sum(1 for r in self.s.runtime.state.evidence.records.values() if r.channel.value in ("instruction", "demonstration")), "statements": len(self.s.dialogue.workspace.commitments), "interaction_turns": len(self.s.traces), "protected_exposure": 0}

    def resources(self) -> dict:
        size = sum(p.stat().st_size for p in Path(self.root).rglob("*") if p.is_file())
        return {"persistent_bytes": size, "ledger_events": len(self.s.runtime.events), "kso_atoms": len(self.s.runtime.state.ks.ids) if hasattr(self.s.runtime.state, "ks") else None, "external_io": 0}


class ParentArm:
    name = "matched_parent"

    def __init__(self, root: Path):
        self.root = root
        Path(root).mkdir(parents=True, exist_ok=True)
        self.p = MatchedParent(DEFAULT_MANIFEST)
        self.state = root / "parent.json"
        self.last_lesson: str | None = None

    def say(self, utt: str) -> str:
        if utt == "__restart__":
            self.p.save(self.state)
            self.p = MatchedParent(DEFAULT_MANIFEST)
            self.p.load(self.state)
            return "restarted"
        if utt == "__revoke_last_lesson__":
            utt = f"revoke {self.last_lesson}"
        if utt.startswith("teach:"):
            self.last_lesson = utt[len("teach:"):].split("=")[0].strip()
        return self.p.say(utt)

    def info(self) -> dict:
        return {**self.p.info, "protected_exposure": 0}

    def resources(self) -> dict:
        self.p.save(self.state)
        return {"persistent_bytes": self.state.stat().st_size, "ledger_events": 0, "kso_atoms": None, "external_io": 0}


class TemplateArm:
    name = "template"

    def __init__(self, root: Path):
        man = json.loads(DEFAULT_MANIFEST.read_text(encoding="utf-8"))
        self.facts = {(f["subject"], f["relation"], f["object"]) for f in man["facts"] if f.get("verified_by")}

    def say(self, utt: str) -> str:
        toks = utt.lower().split()
        if toks and toks[0] == "is" and "in" in toks:
            i = toks.index("in")
            s = " ".join(t for t in toks[1:i] if t != "the"); o = " ".join(t for t in toks[i + 1:] if t != "the")
            return "Yes." if (s, "LOCATED_IN", o) in self.facts else "I do not know."
        return "I do not know."

    def info(self) -> dict:
        return {"knowledge_facts": len(self.facts), "lessons": 0, "statements": 0, "interaction_turns": 0, "protected_exposure": 0}

    def resources(self) -> dict:
        return {"persistent_bytes": 0, "ledger_events": 0, "kso_atoms": None, "external_io": 0}


# ------------------------------------------------------------------ families
def conversations(arm_factory: Callable[[Path], Any], root: Path) -> list[bool]:
    convs = json.loads(CONVS.read_text(encoding="utf-8"))["conversations"]
    out: list[bool] = []
    for c in convs:
        arm = arm_factory(root / c["id"])
        for speaker, utt, pat in c["turns"]:
            reply = arm.say(utt) if speaker == "user" else (arm.s.say(utt, speaker) if isinstance(arm, OCMArm) else arm.say(utt))
            out.append(_match(reply, pat))
    return out


def factual_suite() -> list[tuple[str, str]]:
    man = json.loads(DEFAULT_MANIFEST.read_text(encoding="utf-8"))
    items = []
    for f in man["facts"]:
        if f["relation"] == "LOCATED_IN":
            items.append((f"is {f['subject']} in {f['object']}", "Yes." if f.get("verified_by") else "source|rumour|says so"))
        elif f["relation"] == "IS_A":
            art = "an" if f["object"][0] in "aeiou" else "a"
            subj = f["subject"] if f["subject"] in ("water", "ice", "paris", "berlin", "rome", "mars", "earth", "sun", "moon", "nile", "hello", "thanks", "cooking", "sleeping") else f"a {f['subject']}" if f["subject"][0] not in "aeiou" else f"an {f['subject']}"
            items.append((f"is {subj} {art} {f['object']}", "Yes." if f.get("verified_by") else "source|says so"))
        elif f["relation"] == "ORBITS":
            items.append((f"does the {f['subject']} orbit the {f['object']}", "Yes."))
    for q in OUT_OF_SCOPE:
        items.append((q, "I do not know"))
    return items


def factual(arm_factory: Callable[[Path], Any], root: Path) -> tuple[list[bool], list[bool]]:
    arm = arm_factory(root / "factual")
    in_scope, unknowns = [], []
    for q, pat in factual_suite():
        r = arm.say(q)
        (unknowns if pat == "I do not know" else in_scope).append(_match(r, pat))
    return in_scope, unknowns


LESSON_SETS = {
    "V1": [("teach: crate = shipping container", "the robot lifted the crate", "did the robot lift the crate", "the crate was lifted by the robot"),
           ("teach: zorb = small robot", "the zorb opened the door", "did the zorb open the door", "the door was opened by the zorb"),
           ("teach: flute = instrument", "the girl held the flute", "did the girl hold the flute", "the flute was held by the girl")],
    "V2": [("teach: lantern = lamp", "the girl held the lantern", "did the girl hold the lantern", "the lantern was held by the girl"),
           ("teach: ledge = shelf", "the robot held the ledge", "did the robot hold the ledge", "the ledge was held by the robot"),
           ("teach: pebble = small stone", "the dog kicked the pebble", "did the dog kick the pebble", "the pebble was kicked by the dog"),
           ("teach: wagon = cart", "the girl pushed the wagon", "did the girl push the wagon", "the wagon was pushed by the girl"),
           ("teach: gnome = garden statue", "the cat saw the gnome", "did the cat see the gnome", "the gnome was seen by the cat"),
           ("teach: kettle = pot", "the robot lifted the kettle", "did the robot lift the kettle", "the kettle was lifted by the robot")],
}
LESSONS = LESSON_SETS["V1"]


def post_deployment(arm_factory: Callable[[Path], Any], root: Path) -> dict[str, list[bool]]:
    steps = {"baseline_unknown": [], "acquired": [], "compositional_reuse": [], "retained_after_restart": [], "revoked_stops": [], "unrelated_intact": [], "relearned": []}
    for k, (lesson, use, ask, passive) in enumerate(LESSONS):
        arm = arm_factory(root / f"pd{k}")
        steps["baseline_unknown"].append("cannot interpret" in arm.say(use) or "UNKNOWN" in arm.say(use))
        arm.say(lesson)
        arm.say(use)
        steps["acquired"].append("said so" in arm.say(ask))
        steps["compositional_reuse"].append("Noted" in arm.say(passive))
        arm.say("__restart__")
        steps["retained_after_restart"].append("said so" in arm.say(ask))
        arm.say("__revoke_last_lesson__")
        steps["revoked_stops"].append("cannot interpret" in arm.say(use))
        steps["unrelated_intact"].append(arm.say("is paris in france").startswith("Yes."))
        arm.say(lesson.replace("teach:", "teach:"))
        steps["relearned"].append("said so" in arm.say(ask) or "Noted" in arm.say(use))
    return steps


NEGATIVE_TRANSFER_V2 = [("girl cup lifted", "cannot interpret|I do not know|UNKNOWN"), ("the bank kicked the ball", "Did you mean|Which did you mean|Noted"), ("did the cup lift the girl", "I do not know|Unknown"), ("the girl holded the cup", "cannot interpret|UNKNOWN"), ("be casual", "casual|I do not know|cannot interpret"), ("the dog seed the ball", "cannot interpret|UNKNOWN"), ("did the ball kick the dog", "I do not know|Unknown")]
NEGATIVE_TRANSFER = [("robot door opened", "cannot interpret|I do not know|UNKNOWN"),           # SOV order must not be forced
                     ("the bank saw the robot", "Did you mean|Which did you mean|Noted"),         # polysemy retained (either clarify or record both)
                     ("did the door open the robot", "I do not know|Unknown"),                     # surface-similar, role-incompatible
                     ("the robot goed the door", "cannot interpret|UNKNOWN"),                      # regular morphology forced on irregular
                     ("be formal", "formal|I do not know|cannot interpret")]                       # style is not grammar


def negative_transfer(arm_factory: Callable[[Path], Any], root: Path) -> list[bool]:
    arm = arm_factory(root / "neg")
    arm.say("the robot opened the door")
    return [_match(arm.say(u), pat) for u, pat in NEGATIVE_TRANSFER]


def laundering_audit(root: Path) -> dict:
    """RQ2: the renderer follows the supplied meaning, never the prompt.  Inject a random meaning
    into the realiser/gate path: the surface must express the injected meaning (reverse reading
    equal) or be refused — it must never express the answer the user text suggests."""
    s = ChatSession(root / "audit")
    lx, cons = s.dialogue.lexicon, s.dialogue.constructions
    ex = M.example_meanings()
    injected = ex["the robot did not open the door"]
    reals = RZ.realize(injected, lx, cons)
    best = RZ.best(reals)
    follows = best is not None and "did not" in best.text
    # remove the knowledge and ask: no answer from a hidden corpus
    s.world.revoke_source("curated:v1")
    r = s.say("is paris in france")
    no_hidden = r.startswith("I do not know") or "revoked" in r
    # protected answer injected into a forbidden channel (payload) must not surface
    s2 = ChatSession(root / "audit2")
    s2.runtime.admit_evidence({"gold_answer": "paris is in spain"}, "feedback", "leak")
    r2 = s2.say("is paris in spain")
    gold_blocked = r2.startswith("I do not know")
    return {"renderer_follows_supplied_meaning": follows, "no_answer_after_knowledge_removed": no_hidden, "forbidden_channel_gold_not_surfaced": gold_blocked, "incidents": int(not follows) + int(not no_hidden) + int(not gold_blocked)}


# ------------------------------------------------------------------ run
def paired(a: list[bool], b: list[bool]) -> ST.PairedComparison:
    return ST.paired(a, b)


def terminal(t: dict) -> str:
    return {"RESIDUAL_A": "OCM_LANGUAGE_RESIDUAL_SUPPORTED", "RESIDUAL_B": "PARENT_SUFFICIENT", "EQUIVALENT": "PARENT_SUFFICIENT", "INCONCLUSIVE": "CANNOT_CHECK", "CANNOT_CHECK": "CANNOT_CHECK"}[t["verdict"]]


def run(delta: float = 0.05, suite: str = "V1") -> dict:
    global CONVS, LESSONS, NEGATIVE_TRANSFER
    CONVS = SUITES[suite]
    LESSONS = LESSON_SETS[suite]
    if suite == "V2":
        NEGATIVE_TRANSFER = NEGATIVE_TRANSFER_V2
    prereg_hash = hashlib.sha256(PREREG.read_bytes()).hexdigest()
    convs_hash = hashlib.sha256(CONVS.read_bytes()).hexdigest()
    arms: dict[str, Callable[[Path], Any]] = {"ocm": lambda r: OCMArm(r), "matched_parent": lambda r: ParentArm(r), "template": lambda r: TemplateArm(r),
                                             "ocm-no_revocation": lambda r: OCMArm(r, frozenset({"no_revocation"})), "ocm-last_turn_memory": lambda r: OCMArm(r, frozenset({"last_turn_memory"})),
                                             "ocm-no_clarification": lambda r: OCMArm(r, frozenset({"no_clarification"}))}
    results: dict[str, Any] = {}
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        for name, fac in arms.items():
            t0 = time.perf_counter()
            conv = conversations(fac, base / name)
            fin, unk = factual(fac, base / name)
            pd = post_deployment(fac, base / name)
            neg = negative_transfer(fac, base / name)
            arm = fac(base / name / "info")
            results[name] = {"conversations": conv, "factual_in_scope": fin, "honest_unknown": unk, "post_deployment": pd, "negative_transfer": neg, "information": arm.info(), "resources": {**arm.resources(), "wall_s": round(time.perf_counter() - t0, 3), "peak_rss_mb": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 1)}}
        audit = laundering_audit(base)
    families = {"RQ1_conversations": "conversations", "RQ1_factual": "factual_in_scope", "RQ5_honest_unknown": "honest_unknown", "RQ6_negative_transfer": "negative_transfer"}
    claims = {}
    for rq, key in families.items():
        claims[rq] = {}
        for other in ("matched_parent", "template", "ocm-no_revocation", "ocm-last_turn_memory", "ocm-no_clarification"):
            cmp = paired(results["ocm"][key], results[other][key])
            t = ST.tost_equivalence(cmp, delta)
            claims[rq][other] = {"n": cmp.n, "ocm": cmp.a_success, "other": cmp.b_success, **t, "terminal": terminal(t)}
    # RQ3/RQ4 from the post-deployment steps
    for step in ("acquired", "compositional_reuse", "retained_after_restart", "revoked_stops", "unrelated_intact", "relearned"):
        claims[f"RQ3_{step}"] = {}
        for other in ("matched_parent", "ocm-no_revocation"):
            cmp = paired(results["ocm"]["post_deployment"][step], results[other]["post_deployment"][step])
            t = ST.tost_equivalence(cmp, delta)
            claims[f"RQ3_{step}"][other] = {"n": cmp.n, "ocm": cmp.a_success, "other": cmp.b_success, **t, "terminal": terminal(t)}
    summary = {name: {"conversations": f"{sum(r['conversations'])}/{len(r['conversations'])}", "factual": f"{sum(r['factual_in_scope'])}/{len(r['factual_in_scope'])}", "unknown": f"{sum(r['honest_unknown'])}/{len(r['honest_unknown'])}", "negative_transfer": f"{sum(r['negative_transfer'])}/{len(r['negative_transfer'])}", "post_deployment": {k: f"{sum(v)}/{len(v)}" for k, v in r["post_deployment"].items()}} for name, r in results.items()}
    return {"receipt": f"M7_COMPARISON_{suite}", "suite": suite, "study_status": "ENGINEERING_REGRESSION_ONLY__AFTER_OUTCOME_ACCESS", "preregistration_sha256": prereg_hash, "conversations_sha256": convs_hash, "delta": delta, "summary": summary, "claims": claims, "laundering_audit": audit,
            "information_budget": {n: r["information"] for n, r in results.items()}, "resources": {n: r["resources"] for n, r in results.items()},
            "power_at_planned_n": {str(n): round(ST.power_exact(n, 0.15, delta), 3) for n in (40, 60, 80)},
            "authority": "engineering replay of historical suites over the bounded world; the matched parent receives identical knowledge, lessons, corrections and budget; BLiMP/UD/BabyLM/CHILDES/human rating are CANNOT_CHECK (coverage 0 / data terms) and reported separately; no novelty claim"}


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--out", default=None)
    p.add_argument("--suite", default="V1")
    a = p.parse_args(argv)
    r = run(suite=a.suite)
    if a.out:
        from ocm.evaluation.output import write_result
        write_result(Path(a.out), r)
    print(json.dumps({"summary": r["summary"], "audit": r["laundering_audit"]}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
