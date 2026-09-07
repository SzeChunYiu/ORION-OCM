"""Existing bounded chat donors, shared with ordinary comparator storage.

No runtime, dialogue workspace or answer oracle is imported here. Seed/morphology
and world-query parsing are adopted mechanisms; they do not establish truth.
"""
from pathlib import Path
import json
from ocm.data import default_manifest_path
from ocm.kso.warrant import WarrantProfile
from ocm.language import constructions as C, lexicon as L
from ocm.language.interpret import tokenize
from ocm.language.meaning import MeaningGraph

DEFAULT_MANIFEST = default_manifest_path()
RELATION_WORDS = {"in": "LOCATED_IN", "a": "IS_A", "an": "IS_A", "orbit": "ORBITS", "orbits": "ORBITS", "part": "PART_OF", "contain": "CONTAINS", "contains": "CONTAINS", "before": "BEFORE", "capital": "CAPITAL_OF"}

CORRECTION_PREFIXES = ("correction,", "correction:", "no,", "actually,", "i was wrong,", "i meant")


def correction_body(utterance: str) -> tuple[str, bool]:
    """Separate a registered correction cue without dropping attributed content."""
    stripped = utterance.strip()
    for prefix in CORRECTION_PREFIXES:
        if stripped.lower().startswith(prefix):
            return stripped[len(prefix):].strip(), True
    return utterance, False


def seed_frontend(manifest: Path = DEFAULT_MANIFEST) -> tuple[L.Lexicon, list[C.Construction]]:
    from ocm.language.bootstrap import microworld_lexicon

    if Path(manifest).resolve() == DEFAULT_MANIFEST.resolve():
        # The process may outlive a package-file change. Recheck the registered
        # default for every session; custom manifests have their own custody.
        manifest = default_manifest_path()
    lx = microworld_lexicon()
    # The historical M3 seed equated simple past and past participle. Keep that
    # frozen fixture intact; the current chat grammar distinguishes see/saw/seen.
    lx.rules = [rule for rule in lx.rules if rule.rule_id != "pp-see"]
    lx.add_rule(L.MorphRule("chat:pp-see-v1", L.RuleKind.EXCEPTION, L.Category.VERB,
                            (("participle", "past"),), lambda lemma: "seen",
                            lambda surface: "see" if surface == "seen" else None,
                            WarrantProfile.of({"ev:chat:see-past-participle-v1"}), lemmas=frozenset({"see"})))
    ev = lambda n: WarrantProfile.of({f"ev:lex:{n}"})  # noqa: E731
    # bounded-world vocabulary (nouns from the manifest labels) + question words
    for w in ("which", "what", "who"):
        lx.add(L.Lexeme(w, L.Category.WH, ()))
    lx.add(L.Lexeme("it", L.Category.PRON, ()))
    lx.add(L.Lexeme("is", L.Category.AUX, (), (("tense", "present"),)))
    lx.add(L.Lexeme("a", L.Category.DET, ()))
    lx.add(L.Lexeme("an", L.Category.DET, ()))
    lx.add(L.Lexeme("in", L.Category.PREP, ()))
    lx.add(L.Lexeme("of", L.Category.PREP, ()))
    # a registered polysemous noun (ambiguity set) for the clarification scenario
    lx.add(L.Lexeme("bank", L.Category.NOUN, (L.Sense("bank:fin", "financial_institution", "entity", ev("bank-fin")), L.Sense("bank:river", "river_bank", "entity", ev("bank-river")))))
    man = json.loads(Path(manifest).read_text(encoding="utf-8"))
    labels = {f["subject"] for f in man["facts"]} | {f["object"] for f in man["facts"]}
    for lab in sorted(labels):
        if "_" in lab or f"{lab}|N" in lx.lexemes:
            continue
        lx.add(L.Lexeme(lab, L.Category.NOUN, (L.Sense(lab, lab, "entity", ev(lab)),)))
    return lx, list(C.seed_constructions())


def world_query(low: str) -> tuple[str, str, str] | None:
    toks = tokenize(low)
    if not toks:
        return None
    if toks[0] == "is" and len(toks) == 3 and all(t not in ("not", "no", "the", "a", "an") for t in toks[1:]):
        # Registered bare nominal copula: "is ice water". This only creates
        # a query; the ordinary world warrant/commit gates decide its answer.
        return (toks[1], "IS_A", toks[2])
    if toks[0] in ("is", "does", "do") and len(toks) >= 4:
        body = [t for t in toks[1:] if t not in ("the", "a", "an")]
        if toks[0] == "is" and "capital" in body:
            i = body.index("capital")
            subj = " ".join(body[:i]); obj = " ".join(body[i + 1:]).replace("of ", "")
            return (subj, "CAPITAL_OF", obj)
        if toks[0] == "is" and "in" in toks:
            i = toks.index("in")
            subj = " ".join(t for t in toks[1:i] if t not in ("the",)); obj = " ".join(t for t in toks[i + 1:] if t not in ("the",))
            return (subj, "LOCATED_IN", obj)
        if toks[0] == "is" and any(t in ("a", "an") for t in toks[2:]):
            start = 2 if toks[1] in ("a", "an", "the") else 1          # "is a whale a mammal" / "is the moon a planet"
            i = next(k for k, t in enumerate(toks) if k >= start + 1 and t in ("a", "an"))
            subj = " ".join(t for t in toks[start:i] if t != "the"); obj = " ".join(toks[i + 1:])
            return (subj, "IS_A", obj)
        if toks[0] == "does" and len(body) >= 3 and body[1] in RELATION_WORDS:
            return (body[0], RELATION_WORDS[body[1]], " ".join(body[2:]))
    return None

def parse_lexical_lesson(body: str):
    """Parse the existing lexical lesson syntax independently of persistence."""
    word, separator, concept = body.partition("=")
    word, concept = word.strip().lower(), concept.strip().lower()
    if not separator or not word or not concept or any(c in body for c in ("\n", "\r")):
        raise ValueError("incomplete lexical lesson")
    category = L.Category.NOUN
    for suffix, candidate in ((" as noun", L.Category.NOUN), (" as verb", L.Category.VERB)):
        if concept.endswith(suffix):
            concept, category = concept[:-len(suffix)].strip(), candidate
            break
    if not concept:
        raise ValueError("empty lexical meaning")
    return word, concept, category


def add_lexical_lesson(lx, word, concept, eid, cat=L.Category.NOUN):
    """The existing chat lesson-to-sense donor; each lesson has separate support."""
    ntype = "event" if cat is L.Category.VERB else "entity"
    key = f"{word}|{cat.value}"
    prior = [s for s in (lx.lexemes[key].senses if key in lx.lexemes else ()) if s.concept == concept]
    sense_id = f"{word}:{concept}" + (f"#{len(prior) + 1}" if prior else "")
    sense = L.Sense(sense_id, concept, ntype, WarrantProfile.of({eid}))
    if key in lx.lexemes:
        old = lx.lexemes[key]
        lx.add(L.Lexeme(old.lemma, old.category, old.senses + (sense,), old.features, old.warrant, old.scope))
    else:
        lx.add(L.Lexeme(word, cat, (sense,)))


def _is_question(m: MeaningGraph) -> bool:
    return any(e.relation == "ASKS" for e in m.edges)


def _strip(m: MeaningGraph, relation: str, node_type: str | None = None) -> MeaningGraph:
    nodes = tuple(n for n in m.nodes if node_type is None or n.node_type != node_type)
    return MeaningGraph(nodes, tuple(e for e in m.edges if e.relation != relation), m.root)


def _is_negated(m: MeaningGraph) -> bool:
    return any(e.relation == "NEGATES" for e in m.edges)


def _describe(m: MeaningGraph) -> str:
    parts = [f"{e.relation[5:]}={m.node(e.heads[0]).label}" for e in m.edges if e.relation.startswith("ROLE:")]
    return f"{m.node(m.root).label if m.root else '?'}({', '.join(parts)})"


def clarification_choice(utterance, candidates, question_id):
    """Recognize the existing dialogue donor's answer; None means the speaker moved on."""
    tok = utterance.strip().lower().strip(".!?")
    if tok.isdigit() and 1 <= int(tok) <= len(candidates):
        return candidates[int(tok) - 1]
    if tok in ("yes", "y") and question_id.startswith("is:"):
        return candidates[int(question_id.split(":")[1])]
    hits = [c for c in candidates if tok and tok in _describe(c.meaning).lower()
            + " " + " ".join(n.label or "" for n in c.meaning.nodes).lower()]
    return hits[0] if len(hits) == 1 else None
