"""Language KSO L1C preflight — raw text can induce form patterns, not grounded meaning.

This module is deliberately weaker than kso_language_v0.py. It receives raw text only: no POS,
no dependency tree, no semantic frame, no hidden target construction. It discovers repeated surface
schemata by exact anti-unification of same-length sentences. Those schemata are FORM candidates.
They cannot enter the semantic Construction store until an independent aligned lesson identifies
which slots correspond to which semantic roles.

The controlled example demonstrates the distinction:

  raw corpus -> `the <slot> <slot> <slot> the <slot> <slot>`
  aligned meaning/utterance examples -> identify slots as A,N,V,A,N with S/V/O phrase grouping

This is only a preflight for real-corpus ingestion. It is not competitive grammar induction and
claims no novelty over usage-based/construction/grammar-induction parents.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

HERE = Path(__file__).resolve().parent
TOKEN_RE = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")
SENTENCE_SPLIT_RE = re.compile(r"[.!?]+")


def _load(name: str):
    if name in sys.modules:
        return sys.modules[name]
    path = HERE / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


lang = _load("kso_language_v0")


@dataclass(frozen=True)
class RawDocument:
    document_id: str
    evidence_id: int
    text: str

    @property
    def content_sha256(self) -> str:
        return hashlib.sha256(self.text.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class RawSentence:
    document_id: str
    evidence_id: int
    sentence_index: int
    tokens: tuple[str, ...]


@dataclass(frozen=True)
class SurfacePattern:
    pattern_id: str
    length: int
    template: tuple[str, ...]
    support_sentence_ids: tuple[str, ...]
    support_evidence_ids: tuple[int, ...]
    semantic_status: str = "UNGROUNDED_FORM_ONLY"

    @property
    def slot_positions(self) -> tuple[int, ...]:
        return tuple(i for i, token in enumerate(self.template) if token.startswith("<SLOT:"))

    def render(self, fillers: Sequence[str]) -> str:
        if len(fillers) != len(self.slot_positions):
            raise ValueError("wrong number of slot fillers")
        it = iter(fillers)
        out = [next(it) if token.startswith("<SLOT:") else token for token in self.template]
        text = " ".join(out)
        return text[:1].upper() + text[1:] + "."


@dataclass(frozen=True)
class SlotRoleBinding:
    pattern_id: str
    role_by_position: tuple[tuple[int, str], ...]
    evidence_id: int
    status: str

    def roles(self) -> dict[int, str]:
        return dict(self.role_by_position)


def tokenize_sentences(doc: RawDocument) -> tuple[RawSentence, ...]:
    rows: list[RawSentence] = []
    for i, raw in enumerate(SENTENCE_SPLIT_RE.split(doc.text)):
        toks = tuple(x.lower() for x in TOKEN_RE.findall(raw))
        if toks:
            rows.append(RawSentence(doc.document_id, doc.evidence_id, i, toks))
    return tuple(rows)


def anti_unify(sentences: Sequence[RawSentence]) -> SurfacePattern:
    if len(sentences) < 2:
        raise ValueError("anti-unification needs at least two sentences")
    lengths = {len(s.tokens) for s in sentences}
    if len(lengths) != 1:
        raise ValueError("anti-unification requires equal-length sentences in V0")
    n = lengths.pop()
    template: list[str] = []
    slot_n = 0
    for i in range(n):
        vals = {s.tokens[i] for s in sentences}
        if len(vals) == 1:
            template.append(next(iter(vals)))
        else:
            slot_n += 1
            template.append(f"<SLOT:{slot_n}>")
    ids = tuple(f"{s.document_id}:{s.sentence_index}" for s in sentences)
    evid = tuple(sorted({s.evidence_id for s in sentences}))
    payload = json.dumps({"template": template, "sentences": ids}, sort_keys=True, separators=(",", ":"))
    return SurfacePattern(
        "form:" + hashlib.sha256(payload.encode()).hexdigest()[:16],
        n,
        tuple(template),
        ids,
        evid,
    )


def mine_surface_patterns(documents: Sequence[RawDocument], *, min_examples: int = 2) -> tuple[SurfacePattern, ...]:
    if min_examples < 2:
        raise ValueError("min_examples must be >=2")
    sentences = tuple(s for d in documents for s in tokenize_sentences(d))
    by_len: dict[int, list[RawSentence]] = {}
    for s in sentences:
        by_len.setdefault(len(s.tokens), []).append(s)
    out: list[SurfacePattern] = []
    for n, rows in sorted(by_len.items()):
        if len(rows) < min_examples:
            continue
        p = anti_unify(rows)
        if p.slot_positions and any(not token.startswith("<SLOT:") for token in p.template):
            out.append(p)
    return tuple(out)


def bind_roles_from_aligned_examples(
    pattern: SurfacePattern,
    examples: Sequence[tuple[lang.SemanticFrame, str]],
    evidence_id: int,
) -> SlotRoleBinding:
    """Identify simple L0 slot roles using independently supplied semantic frames.

    The binder does NOT parse arbitrary language. It is a finite calibration that asks whether the
    same surface-pattern positions consistently carry roles already supplied by the aligned meaning.
    If a position changes role across aligned examples, binding is refused.
    """
    if not examples:
        return SlotRoleBinding(pattern.pattern_id, (), evidence_id, "GAP_NO_ALIGNED_EVIDENCE")
    candidate_maps: list[dict[int, str]] = []
    for frame, surface in examples:
        toks = tuple(x.lower() for x in TOKEN_RE.findall(surface))
        if len(toks) != pattern.length:
            return SlotRoleBinding(pattern.pattern_id, (), evidence_id, "GAP_PATTERN_MISMATCH")
        for i, fixed in enumerate(pattern.template):
            if not fixed.startswith("<SLOT:") and toks[i] != fixed:
                return SlotRoleBinding(pattern.pattern_id, (), evidence_id, "GAP_PATTERN_MISMATCH")

        # Finite L0 role facts come from aligned meaning, not from raw-text position names.
        expected: dict[str, str] = {
            frame.agent.noun_concept.lower(): "SUBJECT_NOUN",
            frame.predicate_concept.lower(): "VERB",
        }
        if frame.agent.adjective_concepts:
            expected[frame.agent.adjective_concepts[0].lower()] = "SUBJECT_ADJECTIVE"
        if frame.patient is not None:
            if frame.patient.adjective_concepts:
                expected[frame.patient.adjective_concepts[0].lower()] = "OBJECT_ADJECTIVE"
            expected[frame.patient.noun_concept.lower()] = "OBJECT_NOUN"

        # Controlled aligned surfaces use concept labels at the latent slot positions.
        mapping: dict[int, str] = {}
        for i in pattern.slot_positions:
            role = expected.get(toks[i])
            if role is None:
                return SlotRoleBinding(pattern.pattern_id, (), evidence_id, "GAP_UNIDENTIFIED_SLOT")
            mapping[i] = role
        candidate_maps.append(mapping)

    first = candidate_maps[0]
    if any(m != first for m in candidate_maps[1:]):
        return SlotRoleBinding(pattern.pattern_id, (), evidence_id, "GAP_INCONSISTENT_ROLE_BINDING")
    return SlotRoleBinding(pattern.pattern_id, tuple(sorted(first.items())), evidence_id, "ALIGNED_ROLE_BINDING_IDENTIFIED")


def run_corpus_l1c_preflight() -> dict[str, object]:
    docs = (
        RawDocument(
            "book-a",
            9001,
            "The CURIOUS ROBOT OPEN the RED DOOR. The SMALL CHILD ADMIRE the BLUE PAINTING.",
        ),
        RawDocument(
            "book-b",
            9002,
            "The BRAVE PILOT HELP the YOUNG STUDENT. The OLD TEACHER GUIDE the NEW ROBOT.",
        ),
    )
    patterns = mine_surface_patterns(docs, min_examples=4)
    assert len(patterns) == 1
    pattern = patterns[0]
    assert pattern.template == (
        "the",
        "<SLOT:1>",
        "<SLOT:2>",
        "<SLOT:3>",
        "the",
        "<SLOT:4>",
        "<SLOT:5>",
    )
    assert pattern.semantic_status == "UNGROUNDED_FORM_ONLY"
    assert pattern.render(("quiet", "scientist", "study", "new", "problem")) == "The quiet scientist study the new problem."

    # The raw pattern has no S/V/O claim and cannot by itself create a semantic Construction.
    no_semantic_roles = not hasattr(pattern, "semantic_roles")
    assert no_semantic_roles

    frame1 = lang.SemanticFrame(
        "en",
        lang.NPConcept("robot", "the", ("curious",), lang.Number.SINGULAR),
        "open",
        lang.NPConcept("door", "the", ("red",), lang.Number.SINGULAR),
    )
    frame2 = lang.SemanticFrame(
        "en",
        lang.NPConcept("child", "the", ("small",), lang.Number.SINGULAR),
        "admire",
        lang.NPConcept("painting", "the", ("blue",), lang.Number.SINGULAR),
    )
    aligned = (
        (frame1, "the curious robot open the red door"),
        (frame2, "the small child admire the blue painting"),
    )
    binding = bind_roles_from_aligned_examples(pattern, aligned, 9100)
    assert binding.status == "ALIGNED_ROLE_BINDING_IDENTIFIED"
    assert binding.roles() == {
        1: "SUBJECT_ADJECTIVE",
        2: "SUBJECT_NOUN",
        3: "VERB",
        5: "OBJECT_ADJECTIVE",
        6: "OBJECT_NOUN",
    }

    # Same semantic frame with a swapped noun assignment conflicts with the first alignment.
    bad = bind_roles_from_aligned_examples(
        pattern,
        (
            aligned[0],
            (frame1, "the curious door open the red robot"),
        ),
        9101,
    )
    assert bad.status == "GAP_INCONSISTENT_ROLE_BINDING"

    return {
        "terminal": "LANGUAGE_CORPUS_L1C_FORM_PREFLIGHT_GREEN",
        "raw": {
            "documents": len(docs),
            "sentences": sum(len(tokenize_sentences(d)) for d in docs),
            "pattern": list(pattern.template),
            "semantic_status": pattern.semantic_status,
            "raw_pattern_has_semantic_roles": False,
        },
        "aligned": {
            "status": binding.status,
            "role_by_position": {str(k): v for k, v in binding.role_by_position},
            "inconsistent_alignment_refused": bad.status,
        },
        "authority": {
            "real_book_corpus_run": False,
            "grounded_meaning_from_raw_text": False,
            "competitive_grammar_induction": False,
            "human_level_language": False,
            "novelty": False,
        },
    }


def main(argv: Sequence[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--out", type=Path)
    a = p.parse_args(argv)
    try:
        r = run_corpus_l1c_preflight()
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"terminal": "FAIL", "reason": f"{type(exc).__name__}: {exc}"}))
        return 1
    text = json.dumps(r, indent=2, sort_keys=True)
    if a.out:
        a.out.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
