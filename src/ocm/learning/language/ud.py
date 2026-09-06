"""N1 step 1 — corpus-scale lexicon, morphology and construction-skeleton induction from Universal
Dependencies (UD English EWT, custody manifest `docs/provenance/UD_EWT_CUSTODY_MANIFEST_V1.json`).

Epistemic status of the channel: a UD annotation is a *teacher demonstration* (channel
DEMONSTRATION) — the lemma, part of speech, morphological features and dependency relations are
given by annotators, not inferred from raw text.  Every induced lexeme sense therefore carries the
sentence ids that attest it as its warrant evidence (`ud:<sent_id>`), and the receipt reports the
inventory by attestation count; nothing here is "grounded" in the M5 sense (no aligned world
meaning), so senses are recorded with node types by part of speech and status TEACHER_ANNOTATED.
Frequency never raises warrant (M5 hostile): a lemma seen 1 000 times has one sense with 1 000
attesting evidence ids, ⊕ over which is still one warrant interval.

Constructions: for each sentence the root and its core dependents form a *skeleton* (ordered core
relations nsubj / obj / iobj / obl / xcomp / ccomp / cop / aux with the head's part of speech), which
is the UD-aligned counterpart of the M3 construction families; skeleton families are counted and
the protected split's coverage is measured against the families induced from the training split.
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Iterator

from ocm.kso.warrant import WarrantProfile as WP
from ocm.language import lexicon as L

UPOS_TO_CATEGORY = {"NOUN": L.Category.NOUN, "PROPN": L.Category.NOUN, "VERB": L.Category.VERB, "AUX": L.Category.AUX, "ADJ": L.Category.ADJ, "DET": L.Category.DET,
                    "PRON": L.Category.PRON, "ADP": L.Category.PREP, "CCONJ": L.Category.CONJ, "SCONJ": L.Category.CONJ, "ADV": L.Category.ADV, "PART": L.Category.NEG}
NODE_TYPE = {L.Category.NOUN: "entity", L.Category.VERB: "event", L.Category.ADJ: "property", L.Category.ADV: "property", L.Category.PRON: "entity", L.Category.AUX: "event", L.Category.DET: "quantifier"}
CORE_RELS = ("nsubj", "nsubj:pass", "obj", "iobj", "obl", "xcomp", "ccomp", "cop", "aux", "aux:pass", "expl")


@dataclass(frozen=True)
class Token:
    idx: int
    form: str
    lemma: str
    upos: str
    feats: tuple[tuple[str, str], ...]
    head: int
    deprel: str


@dataclass(frozen=True)
class Sentence:
    sent_id: str
    text: str
    tokens: tuple[Token, ...]

    def root(self) -> Token | None:
        return next((t for t in self.tokens if t.head == 0), None)


def read_conllu(path: Path) -> Iterator[Sentence]:
    sid, text, toks = None, "", []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.startswith("# sent_id"):
            sid = line.split("=", 1)[1].strip()
        elif line.startswith("# text"):
            text = line.split("=", 1)[1].strip()
        elif line.startswith("#"):
            continue
        elif not line.strip():
            if sid and toks:
                yield Sentence(sid, text, tuple(toks))
            sid, text, toks = None, "", []
        else:
            cols = line.split("\t")
            if "-" in cols[0] or "." in cols[0]:
                continue                                  # multiword/empty tokens are not lexical units here
            feats = tuple(tuple(kv.split("=", 1)) for kv in cols[5].split("|")) if cols[5] != "_" else ()
            toks.append(Token(int(cols[0]), cols[1], cols[2], cols[3], feats, int(cols[6]) if cols[6] != "_" else 0, cols[7]))
    if sid and toks:
        yield Sentence(sid, text, tuple(toks))


@dataclass
class Induction:
    lexicon: L.Lexicon
    attestations: dict[str, int] = field(default_factory=dict)          # "lemma|CAT" → attesting sentences
    irregular_past: dict[str, str] = field(default_factory=dict)        # lemma → past form (exceptions)
    irregular_present: dict[str, str] = field(default_factory=dict)     # lemma → 3sg present form (exceptions: is, has, does …)
    skeletons: Counter = field(default_factory=Counter)                 # skeleton signature → count
    sentences: int = 0
    tokens: int = 0
    skipped_upos: Counter = field(default_factory=Counter)
    # N1 phase G (ledger S41 Jump: a new evidence class): lexicalised attachment evidence from the demonstrations.
    # Keys: (head lemma, relation, dependent lemma); backoff classes (head lemma, relation, dependent UPOS) and
    # (head UPOS, relation, dependent lemma).  Counts are attesting sentences; frequency never raises a warrant.
    attachments: Counter = field(default_factory=Counter)
    attach_head_class: Counter = field(default_factory=Counter)
    attach_dep_class: Counter = field(default_factory=Counter)

    def attachment_evidence(self, head_lemma: str, head_upos: str, rel: str, dep_lemma: str, dep_upos: str) -> tuple[str | None, int]:
        """The finest evidence class attesting this attachment: LEXICAL (both lemmas), HEAD_CLASS (head lemma with the
        dependent's category), DEP_CLASS (head category with the dependent lemma), or None (no demonstration attests
        it at any registered class).  Returns (class, attesting count)."""
        rel = rel.split(":")[0]
        n = self.attachments.get((head_lemma, rel, dep_lemma), 0)
        if n:
            return "LEXICAL", n
        n = self.attach_head_class.get((head_lemma, rel, dep_upos), 0)
        if n:
            return "HEAD_CLASS", n
        n = self.attach_dep_class.get((head_upos, rel, dep_lemma), 0)
        if n:
            return "DEP_CLASS", n
        return None, 0

    def receipt(self) -> dict[str, Any]:
        cats = Counter(k.split("|")[1] for k in self.attestations)
        return {"channel": "DEMONSTRATION (UD annotations are teacher labels)", "status": "TEACHER_ANNOTATED (not grounded in the M5 sense)", "sentences": self.sentences, "tokens": self.tokens,
                "lexemes": len(self.attestations), "by_category": dict(sorted(cats.items())), "singletons": sum(1 for v in self.attestations.values() if v == 1), "irregular_past_exceptions": len(self.irregular_past), "irregular_present_exceptions": len(self.irregular_present),
                "skeleton_families": len(self.skeletons), "top_skeletons": self.skeletons.most_common(12), "skipped_upos": dict(self.skipped_upos), "frequency_raises_warrant": False,
                "attachment_evidence": {"class": "ATTACHMENT (new evidence class, ledger S41/S43; parent-owned: lexicalised attachment preferences)", "lexical_triples": len(self.attachments), "head_class_triples": len(self.attach_head_class), "dep_class_triples": len(self.attach_dep_class), "lexical_singletons": sum(1 for v in self.attachments.values() if v == 1)}}


def skeleton_of(s: Sentence) -> str | None:
    r = s.root()
    if r is None:
        return None
    deps = sorted((t for t in s.tokens if t.head == r.idx and t.deprel in CORE_RELS), key=lambda t: t.idx)
    parts = []
    for t in deps:
        parts.append(f"{t.deprel}" if t.idx > r.idx else f"{t.deprel}<")
    return f"{r.upos}({','.join(parts)})"


def induce(sentences: Iterable[Sentence], *, evidence_prefix: str = "ud") -> Induction:
    lx = L.Lexicon()
    ind = Induction(lx)
    senses: dict[str, set[str]] = defaultdict(set)
    cat_of: dict[str, L.Category] = {}
    for s in sentences:
        ind.sentences += 1
        for t in s.tokens:
            ind.tokens += 1
            cat = UPOS_TO_CATEGORY.get(t.upos)
            if cat is None:
                ind.skipped_upos[t.upos] += 1
                continue
            key = f"{t.lemma.lower()}|{cat.value}"
            senses[key].add(f"{evidence_prefix}:{s.sent_id}")
            cat_of[key] = cat
            f = dict(t.feats)
            if cat is L.Category.VERB and f.get("Tense") == "Past" and f.get("VerbForm") == "Fin" and t.form.lower() not in (t.lemma.lower() + "ed", t.lemma.lower() + "d"):
                ind.irregular_past.setdefault(t.lemma.lower(), t.form.lower())
            if cat in (L.Category.VERB, L.Category.AUX) and f.get("Tense") == "Pres" and f.get("Person") == "3" and f.get("Number") == "Sing" and t.form.lower() not in (t.lemma.lower() + "s", t.lemma.lower() + "es"):
                ind.irregular_present.setdefault(t.lemma.lower(), t.form.lower())
        sk = skeleton_of(s)
        if sk:
            ind.skeletons[sk] += 1
        by_idx = {t.idx: t for t in s.tokens}
        seen_triples: set = set()
        for t in s.tokens:
            h = by_idx.get(t.head)
            if h is None or t.upos == "PUNCT" or t.upos not in UPOS_TO_CATEGORY or h.upos not in UPOS_TO_CATEGORY:
                continue
            rel = t.deprel.split(":")[0]
            trip = (h.lemma.lower(), rel, t.lemma.lower())
            if trip in seen_triples:
                continue                                  # one attesting sentence counts once
            seen_triples.add(trip)
            ind.attachments[trip] += 1
            ind.attach_head_class[(h.lemma.lower(), rel, t.upos)] += 1
            ind.attach_dep_class[(h.upos, rel, t.lemma.lower())] += 1
    for key, ev in senses.items():
        lemma, _ = key.split("|")
        cat = cat_of[key]
        node_type = NODE_TYPE.get(cat, "value")
        lx.add(L.Lexeme(lemma, cat, (L.Sense(f"{lemma}:{cat.value}", lemma, node_type, WP.of(set(ev))),)))
        ind.attestations[key] = len(ev)
    for lemma, past in ind.irregular_past.items():
        lx.add_rule(L.MorphRule(f"past-{lemma}", L.RuleKind.EXCEPTION, L.Category.VERB, (("tense", "past"),), lambda l, p=past: p, lambda s_, p=past, v=lemma: v if s_ == p else None, WP.of({f"{evidence_prefix}:past:{lemma}"}), lemmas=frozenset({lemma})))
    for lemma, form in ind.irregular_present.items():
        cat = L.Category.AUX if f"{lemma}|AUX" in ind.attestations and f"{lemma}|V" not in ind.attestations else L.Category.VERB
        lx.add_rule(L.MorphRule(f"pres3-{lemma}", L.RuleKind.EXCEPTION, cat, (("tense", "present"),), lambda l, p=form: p, lambda s_, p=form, v=lemma: v if s_ == p else None, WP.of({f"{evidence_prefix}:pres3:{lemma}"}), lemmas=frozenset({lemma})))
    lx.add_rule(L.MorphRule("past-ed", L.RuleKind.PRODUCTIVE, L.Category.VERB, (("tense", "past"),), lambda l: l + "ed", lambda s_: s_[:-2] if s_.endswith("ed") else None, WP.of({f"{evidence_prefix}:rule-ed"})))
    lx.add_rule(L.MorphRule("past-d", L.RuleKind.PRODUCTIVE, L.Category.VERB, (("tense", "past"),), lambda l: l + "d", lambda s_: s_[:-1] if s_.endswith("ed") else None, WP.of({f"{evidence_prefix}:rule-d"})))
    lx.add_rule(L.MorphRule("pres-s", L.RuleKind.PRODUCTIVE, L.Category.VERB, (("tense", "present"),), lambda l: l + "s", lambda s_: s_[:-1] if s_.endswith("s") and not s_.endswith("ss") else None, WP.of({f"{evidence_prefix}:rule-s"})))
    lx.add_rule(L.MorphRule("plural-s", L.RuleKind.PRODUCTIVE, L.Category.NOUN, (("number", "plural"),), lambda l: l + "s", lambda s_: s_[:-1] if s_.endswith("s") and not s_.endswith("ss") else None, WP.of({f"{evidence_prefix}:rule-pl"})))
    return ind


def coverage(sentences: Iterable[Sentence], ind: Induction) -> dict[str, Any]:
    """Protected-split coverage against the induced inventory: a token is covered if (lemma, category)
    is in the lexicon; a sentence is lexically covered if every content token is covered; a sentence's
    skeleton is covered if its family was seen in training.  CANNOT_CHECK is reported for sentences
    whose root is missing or whose parts of speech are outside the category map."""
    n = tok = tok_cov = sent_lex = sent_sk = cannot = 0
    unseen_lemmas: Counter = Counter()
    unseen_skeletons: Counter = Counter()
    for s in sentences:
        n += 1
        cov_all = True
        any_content = False
        for t in s.tokens:
            cat = UPOS_TO_CATEGORY.get(t.upos)
            if cat is None:
                continue
            any_content = True
            tok += 1
            if f"{t.lemma.lower()}|{cat.value}" in ind.attestations:
                tok_cov += 1
            else:
                cov_all = False
                unseen_lemmas[t.lemma.lower()] += 1
        sk = skeleton_of(s)
        if sk is None or not any_content:
            cannot += 1
            continue
        sent_lex += int(cov_all)
        if sk in ind.skeletons:
            sent_sk += 1
        else:
            unseen_skeletons[sk] += 1
    return {"sentences": n, "cannot_check": cannot, "token_coverage": f"{tok_cov}/{tok}", "sentence_lexical_coverage": f"{sent_lex}/{n - cannot}", "skeleton_coverage": f"{sent_sk}/{n - cannot}",
            "unseen_lemmas_top": unseen_lemmas.most_common(10), "unseen_skeletons_top": unseen_skeletons.most_common(8)}


def digest_of(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def mutant_frequency_promotes(ind: Induction, threshold: int = 100) -> int:
    """Planted (M5 hostile): treat frequently attested lemmas as verified/grounded."""
    return sum(1 for v in ind.attestations.values() if v >= threshold)


# ------------------------------------------------------------------ N1 step 2: gold meanings and interpretation on simple clauses
SIMPLE_DEPS = {"det", "amod", "nsubj", "obj", "punct"}
GOLD_MAX_NODES = 7                                  # the exact canonical-form bound of the meaning graphs (M3)


def is_simple_clause(s: Sentence) -> bool:
    """Root is a finite past- or present-tense VERB; every other token is a det/amod/nsubj/obj/punct
    dependent of the root or of a core argument; at most one nsubj and one obj; no pronouns."""
    r = s.root()
    if r is None or r.upos != "VERB":
        return False
    f = dict(r.feats)
    if f.get("VerbForm") != "Fin" or f.get("Tense") not in ("Past", "Pres"):
        return False
    core = {t.idx: t for t in s.tokens if t.head == r.idx and t.deprel in ("nsubj", "obj")}
    if sum(1 for t in core.values() if t.deprel == "nsubj") > 1 or sum(1 for t in core.values() if t.deprel == "obj") > 1:
        return False
    for t in s.tokens:
        if t.idx == r.idx:
            continue
        if t.deprel not in SIMPLE_DEPS:
            return False
        if t.deprel in ("nsubj", "obj") and t.upos not in ("NOUN", "PROPN"):
            return False
        if t.deprel in ("det", "amod") and (t.head not in core):
            return False
        if t.deprel == "punct" and t.head != r.idx:
            return False
    return "nsubj" in {t.deprel for t in core.values()}


def gold_meaning(s: Sentence):
    """The UD-derived meaning in the seed template shape: entity x1/x2 (definite from a determiner
    'the'; MODIFIES property nodes from amod), event e (lemma), ROLE:agent / ROLE:patient, TENSE."""
    from ocm.language.meaning import MEdge, MNode, MeaningGraph
    r = s.root()
    nodes, edges = [], []
    ids = {}
    for t in s.tokens:
        if t.head == r.idx and t.deprel in ("nsubj", "obj"):
            nid = "x1" if t.deprel == "nsubj" else "x2"
            ids[t.idx] = nid
            mods = [m for m in s.tokens if m.head == t.idx]
            feats = tuple(sorted(({"definite": "yes"} if any(m.deprel == "det" and m.lemma.lower() == "the" for m in mods) else {}).items()))
            nodes.append(MNode(nid, "entity", t.lemma.lower(), feats))
            for k, m in enumerate(m for m in mods if m.deprel == "amod"):
                pid = f"{nid}.p" if k == 0 else f"{nid}.p{k}"
                nodes.append(MNode(pid, "property", m.lemma.lower()))
                edges.append(MEdge("MODIFIES", (pid,), (nid,)))
    nodes.append(MNode("e", "event", r.lemma.lower()))
    for idx, nid in ids.items():
        edges.append(MEdge("ROLE:agent" if nid == "x1" else "ROLE:patient", ("e",), (nid,)))
    tense = {"Past": "past", "Pres": "present"}[dict(r.feats)["Tense"]]
    edges.append(MEdge("TENSE", ("e",), ("e",), tense))
    return MeaningGraph(tuple(nodes), tuple(edges), root="e")


def utterance_of(s: Sentence) -> str:
    return " ".join(t.form.lower() for t in s.tokens if t.upos != "PUNCT")


def interpret_simple_clauses(sentences, ind: Induction, constructions) -> dict[str, Any]:
    """Interpret every simple clause of a split with the induced lexicon and the given constructions;
    grade the single live candidate against the UD-derived gold meaning by exact canonical equality."""
    from collections import Counter
    from ocm.language import interpret as I
    from ocm.language.meaning import canonical
    verdicts: Counter = Counter()
    exact = 0
    n = cannot = 0
    misses = []
    for s in sentences:
        if not is_simple_clause(s):
            continue
        g = gold_meaning(s)
        if len(g.nodes) > GOLD_MAX_NODES:
            cannot += 1
            continue
        n += 1
        r = I.interpret(utterance_of(s), ind.lexicon, constructions)
        verdicts[r.verdict.value] += 1
        if r.verdict is I.Verdict.INTERPRETED and canonical(r.candidates[0].meaning)[1] == canonical(g)[1]:
            exact += 1
        elif len(misses) < 12:
            misses.append((utterance_of(s), r.verdict.value, str(getattr(r, 'reason', getattr(r, 'note', getattr(r, 'detail', ''))))[:80]))
    return {"simple_clauses": n, "cannot_check_over_bound": cannot, "verdicts": dict(verdicts), "exact_gold_match": f"{exact}/{n}", "misses_sample": misses}

