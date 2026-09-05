"""Custody-bound Universal Dependencies induction utilities for N1.

The UD annotations are treated as a DEMONSTRATION/teacher-annotation channel for
form, lemma, morphology and dependency structure.  They are *not* world-truth
semantic warrants.  Train/dev may be inspected by development code.  The EWT
``test`` annotations are protected: this module refuses to read them unless a
caller explicitly sets ``protected_evaluator=True`` and the file bytes match the
frozen custody manifest.

No network access occurs here.  Files must already have been acquired by
``scripts/acquire_ud_ewt.sh`` on an authorized compute host.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Iterable, Iterator, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[2]
CUSTODY = ROOT / "docs" / "provenance" / "UD_EWT_CUSTODY_MANIFEST_V1.json"


class UDCannotCheck(ValueError):
    """The input cannot be used under the frozen UD custody contract."""


@dataclass(frozen=True)
class UDToken:
    token_id: int
    form: str
    lemma: str
    upos: str
    xpos: str | None
    feats: tuple[tuple[str, str], ...]
    head: int
    deprel: str
    misc: tuple[tuple[str, str], ...] = ()

    @property
    def lower_form(self) -> str:
        return self.form.lower()

    @property
    def lower_lemma(self) -> str:
        return self.lemma.lower()


@dataclass(frozen=True)
class UDSentence:
    sent_id: str
    text: str | None
    tokens: tuple[UDToken, ...]

    def token(self, token_id: int) -> UDToken:
        for token in self.tokens:
            if token.token_id == token_id:
                return token
        raise KeyError(token_id)

    @property
    def roots(self) -> tuple[UDToken, ...]:
        return tuple(t for t in self.tokens if t.head == 0)


@dataclass(frozen=True)
class LexicalAttestation:
    form: str
    lemma: str
    upos: str
    feats: tuple[tuple[str, str], ...]
    evidence_id: str


@dataclass(frozen=True)
class UDLexiconInventory:
    attestations: tuple[LexicalAttestation, ...]
    lemma_upos_counts: Mapping[tuple[str, str], int]
    form_readings: Mapping[str, tuple[tuple[str, str, tuple[tuple[str, str], ...]], ...]]
    upos_counts: Mapping[str, int]
    tokens: int

    @property
    def lexeme_types(self) -> int:
        return len(self.lemma_upos_counts)

    @property
    def form_types(self) -> int:
        return len(self.form_readings)


@dataclass(frozen=True)
class MorphologyInventory:
    past_pairs: tuple[tuple[str, str, str], ...]
    regular_ed: tuple[tuple[str, str, str], ...]
    irregular_or_non_ed: tuple[tuple[str, str, str], ...]


@dataclass(frozen=True)
class ClauseSkeleton:
    root_upos: str
    ordered_dependents: tuple[tuple[str, str, str], ...]

    def key(self) -> str:
        body = [self.root_upos]
        body.extend(f"{side}:{rel}:{upos}" for side, rel, upos in self.ordered_dependents)
        return "|".join(body)


def _kv(field: str) -> tuple[tuple[str, str], ...]:
    if not field or field == "_":
        return ()
    out = []
    for part in field.split("|"):
        if "=" not in part:
            out.append((part, ""))
        else:
            k, v = part.split("=", 1)
            out.append((k, v))
    return tuple(sorted(out))


def _comment_value(line: str, key: str) -> str | None:
    prefix = f"# {key} = "
    return line[len(prefix):] if line.startswith(prefix) else None


def parse_conllu(text: str, *, source_label: str = "conllu") -> tuple[UDSentence, ...]:
    """Parse basic integer-token CoNLL-U trees.

    Multiword-token rows (``1-2``) and empty nodes (``3.1``) are representation
    metadata and are skipped.  Their component integer-token rows remain.
    """
    sentences: list[UDSentence] = []
    comments: list[str] = []
    rows: list[str] = []

    def flush() -> None:
        nonlocal comments, rows
        if not rows and not comments:
            return
        sent_id = next((v for line in comments if (v := _comment_value(line, "sent_id")) is not None), None)
        sentence_text = next((v for line in comments if (v := _comment_value(line, "text")) is not None), None)
        parsed: list[UDToken] = []
        for row in rows:
            fields = row.split("\t")
            if len(fields) != 10:
                raise UDCannotCheck(f"{source_label}: malformed CoNLL-U row with {len(fields)} fields")
            raw_id = fields[0]
            if "-" in raw_id or "." in raw_id:
                continue
            try:
                token_id = int(raw_id)
                head = int(fields[6])
            except ValueError as exc:
                raise UDCannotCheck(f"{source_label}: non-integer basic token/head id") from exc
            if token_id < 1 or head < 0:
                raise UDCannotCheck(f"{source_label}: invalid token/head id")
            lemma = fields[2] if fields[2] != "_" else fields[1]
            upos = fields[3]
            if upos == "_":
                raise UDCannotCheck(f"{source_label}: missing UPOS on token {token_id}")
            parsed.append(
                UDToken(
                    token_id,
                    fields[1],
                    lemma,
                    upos,
                    None if fields[4] == "_" else fields[4],
                    _kv(fields[5]),
                    head,
                    fields[7],
                    _kv(fields[9]),
                )
            )
        if parsed:
            ids = {t.token_id for t in parsed}
            if len(ids) != len(parsed):
                raise UDCannotCheck(f"{source_label}: duplicate integer token id")
            if any(t.head != 0 and t.head not in ids for t in parsed):
                raise UDCannotCheck(f"{source_label}: head points outside basic integer tokens")
            roots = [t for t in parsed if t.head == 0]
            if len(roots) != 1:
                raise UDCannotCheck(f"{source_label}: expected exactly one basic root, got {len(roots)}")
            sid = sent_id or f"{source_label}:sentence:{len(sentences) + 1}"
            sentences.append(UDSentence(sid, sentence_text, tuple(sorted(parsed, key=lambda t: t.token_id))))
        comments, rows = [], []

    for raw in text.splitlines():
        line = raw.rstrip("\n")
        if not line.strip():
            flush()
        elif line.startswith("#"):
            comments.append(line)
        else:
            rows.append(line)
    flush()
    return tuple(sentences)


def custody_manifest() -> dict:
    data = json.loads(CUSTODY.read_text(encoding="utf-8"))
    if data.get("dataset") != "UD_English-EWT" or data.get("release") != "r2.14":
        raise UDCannotCheck("unexpected UD EWT custody manifest identity")
    return data


def verify_custody_file(path: Path, split: str, *, protected_evaluator: bool = False) -> None:
    if split not in {"train", "dev", "test"}:
        raise ValueError("split must be train/dev/test")
    if split == "test" and not protected_evaluator:
        raise UDCannotCheck("EWT test annotations are protected; frozen evaluator authorization required")
    manifest = custody_manifest()
    name = f"en_ewt-ud-{split}.conllu"
    spec = manifest["files"].get(name)
    if spec is None:
        raise UDCannotCheck(f"custody manifest does not bind {name}")
    if path.name != name:
        raise UDCannotCheck(f"expected custody filename {name}, got {path.name}")
    data = path.read_bytes()
    if len(data) != spec["bytes"] or hashlib.sha256(data).hexdigest() != spec["sha256"]:
        raise UDCannotCheck(f"custody mismatch for {name}")


def load_split(path: Path, split: str, *, protected_evaluator: bool = False) -> tuple[UDSentence, ...]:
    verify_custody_file(path, split, protected_evaluator=protected_evaluator)
    return parse_conllu(path.read_text(encoding="utf-8"), source_label=f"UD-EWT-r2.14:{split}")


def evidence_id(sentence: UDSentence, token: UDToken) -> str:
    safe_sid = sentence.sent_id.replace(" ", "_")
    return f"ud-ewt:r2.14:{safe_sid}:{token.token_id}"


def induce_lexicon(sentences: Sequence[UDSentence]) -> UDLexiconInventory:
    lemma_counts: Counter[tuple[str, str]] = Counter()
    upos_counts: Counter[str] = Counter()
    form_readings: dict[str, set[tuple[str, str, tuple[tuple[str, str], ...]]]] = defaultdict(set)
    attestations: list[LexicalAttestation] = []
    total = 0
    for sentence in sentences:
        for token in sentence.tokens:
            # Punctuation is structural annotation rather than a lexical concept;
            # keep it in POS totals/grammar, but not in the lexical-learning count.
            upos_counts[token.upos] += 1
            if token.upos == "PUNCT":
                continue
            total += 1
            key = (token.lower_lemma, token.upos)
            lemma_counts[key] += 1
            form_readings[token.lower_form].add((token.lower_lemma, token.upos, token.feats))
            attestations.append(
                LexicalAttestation(
                    token.lower_form,
                    token.lower_lemma,
                    token.upos,
                    token.feats,
                    evidence_id(sentence, token),
                )
            )
    frozen_readings = {form: tuple(sorted(values)) for form, values in sorted(form_readings.items())}
    return UDLexiconInventory(
        tuple(attestations),
        dict(lemma_counts),
        frozen_readings,
        dict(upos_counts),
        total,
    )


def past_morphology(sentences: Sequence[UDSentence]) -> MorphologyInventory:
    pairs: dict[tuple[str, str], str] = {}
    for sentence in sentences:
        for token in sentence.tokens:
            feats = dict(token.feats)
            if token.upos not in {"VERB", "AUX"}:
                continue
            if feats.get("Tense") != "Past":
                continue
            key = (token.lower_lemma, token.lower_form)
            pairs.setdefault(key, evidence_id(sentence, token))
    ordered = tuple((lemma, form, ev) for (lemma, form), ev in sorted(pairs.items()))
    regular = tuple(row for row in ordered if row[1] == row[0] + "ed")
    irregular = tuple(row for row in ordered if row not in regular)
    return MorphologyInventory(ordered, regular, irregular)


def clause_skeleton(sentence: UDSentence) -> ClauseSkeleton:
    root = sentence.roots[0]
    deps = []
    for token in sentence.tokens:
        if token.head != root.token_id or token.upos == "PUNCT":
            continue
        side = "L" if token.token_id < root.token_id else "R"
        deps.append((token.token_id, side, token.deprel, token.upos))
    deps.sort()
    return ClauseSkeleton(root.upos, tuple((side, rel, upos) for _, side, rel, upos in deps))


def skeleton_counts(sentences: Sequence[UDSentence]) -> Mapping[str, int]:
    counts: Counter[str] = Counter()
    for sentence in sentences:
        counts[clause_skeleton(sentence).key()] += 1
    return dict(counts)


def split_summary(sentences: Sequence[UDSentence]) -> dict:
    lex = induce_lexicon(sentences)
    morph = past_morphology(sentences)
    skeletons = skeleton_counts(sentences)
    return {
        "sentences": len(sentences),
        "lexical_tokens_nonpunct": lex.tokens,
        "lexeme_types_lemma_upos": lex.lexeme_types,
        "surface_form_types": lex.form_types,
        "upos_counts": dict(sorted(lex.upos_counts.items())),
        "past_paradigm_pairs": len(morph.past_pairs),
        "past_exact_plus_ed": len(morph.regular_ed),
        "past_irregular_or_non_ed": len(morph.irregular_or_non_ed),
        "clause_skeleton_families": len(skeletons),
    }
