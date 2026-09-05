"""Recursive UD grammar induction and exact packed structural parsing for N1.

The grammar is learned from projective dependency trees.  One production is
created for each dependency head:

    phrase(deprel-to-parent, head-UPOS)
        -> ordered child-phrases + HEAD(head-UPOS)

The order is taken from the annotated surface tree.  Across training examples,
all distinct orders for the same unordered family are retained as a version
space; frequency is evidence metadata, never a hidden probability that collapses
alternatives.

Every production consumes exactly one lexical HEAD token, so the packed parser
has strict input progress and finite derivation multiplicity.  Non-projective
training/evaluation trees are explicitly outside this CFG bridge and are reported
as CANNOT_CHECK_PROJECTIVITY rather than silently approximated.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
import hashlib
from typing import Any, Iterable, Mapping, Sequence

from ud_induction import UDLexiconInventory, UDSentence, UDToken, induce_lexicon


@dataclass(frozen=True, order=True)
class UDPart:
    kind: str  # HEAD | CHILD
    symbol: str

    def __post_init__(self) -> None:
        if self.kind not in {"HEAD", "CHILD"}:
            raise ValueError("UDPart kind must be HEAD or CHILD")


@dataclass(frozen=True)
class UDRule:
    rule_id: str
    lhs: str
    family_id: str
    pattern: tuple[UDPart, ...]
    evidence_count: int

    def __post_init__(self) -> None:
        if sum(part.kind == "HEAD" for part in self.pattern) != 1:
            raise ValueError("every UD rule must consume exactly one lexical head")
        if self.evidence_count < 1:
            raise ValueError("UD rule evidence count must be positive")


@dataclass(frozen=True)
class UDGrammar:
    rules: tuple[UDRule, ...]
    projective_sentences: int
    nonprojective_sentences: int
    family_order_counts: Mapping[str, Mapping[tuple[str, ...], int]]

    @property
    def families(self) -> int:
        return len(self.family_order_counts)

    @property
    def order_hypotheses(self) -> int:
        return sum(len(orders) for orders in self.family_order_counts.values())


@dataclass(frozen=True)
class UDTree:
    symbol: str
    head_upos: str
    head_form: str
    children: tuple["UDTree", ...]
    surface_order: tuple[str, ...] = ()

    def structural_tuple(self, *, include_form: bool = False) -> tuple[Any, ...]:
        head = (self.head_upos, self.head_form.lower()) if include_form else self.head_upos
        return (
            self.symbol,
            head,
            self.surface_order,
            tuple(child.structural_tuple(include_form=include_form) for child in self.children),
        )

    def digest(self, *, include_form: bool = False) -> str:
        return hashlib.sha256(repr(self.structural_tuple(include_form=include_form)).encode()).hexdigest()


@dataclass(frozen=True)
class PackedUDNode:
    tree: UDTree
    span: tuple[int, int]
    head_index: int
    rule_id: str
    derivations: int

    def __post_init__(self) -> None:
        if self.derivations < 1:
            raise ValueError("packed derivation count must be positive")


@dataclass(frozen=True)
class UDParseResult:
    status: str
    tokens: tuple[str, ...]
    roots: tuple[PackedUDNode, ...]
    chart_nodes: int
    derivations: int
    structural_ambiguity: int
    reason: str = ""


@dataclass(frozen=True)
class UDCoverage:
    sentences: int
    projective_sentences: int
    nonprojective_sentences: int
    lexical_tokens: int
    lexical_gold_reading_covered: int
    grammar_gold_rules: int
    grammar_gold_rules_covered: int
    parsed_projective_sentences: int
    exact_gold_structure_sentences: int

    def as_dict(self) -> dict[str, Any]:
        def ratio(a: int, b: int) -> float | None:
            return None if b == 0 else a / b
        return {
            **self.__dict__,
            "lexical_gold_reading_coverage": ratio(self.lexical_gold_reading_covered, self.lexical_tokens),
            "grammar_gold_rule_coverage": ratio(self.grammar_gold_rules_covered, self.grammar_gold_rules),
            "parse_coverage_projective": ratio(self.parsed_projective_sentences, self.projective_sentences),
            "exact_gold_structure_projective": ratio(self.exact_gold_structure_sentences, self.projective_sentences),
        }


def phrase_symbol(token: UDToken) -> str:
    return f"ROOT:{token.upos}" if token.head == 0 else f"{token.deprel}:{token.upos}"


def _arcs(sentence: UDSentence) -> list[tuple[int, int]]:
    arcs = []
    for token in sentence.tokens:
        if token.head == 0 or token.upos == "PUNCT":
            continue
        a, b = sorted((token.token_id, token.head))
        arcs.append((a, b))
    return arcs


def is_projective(sentence: UDSentence) -> bool:
    arcs = _arcs(sentence)
    for i, (a, b) in enumerate(arcs):
        for c, d in arcs[i + 1:]:
            if a < c < b < d or c < a < d < b:
                return False
    return True


def _children(sentence: UDSentence) -> Mapping[int, tuple[UDToken, ...]]:
    by_head: dict[int, list[UDToken]] = defaultdict(list)
    for token in sentence.tokens:
        if token.head and token.upos != "PUNCT":
            by_head[token.head].append(token)
    return {head: tuple(values) for head, values in by_head.items()}


def _descendants(token_id: int, children: Mapping[int, tuple[UDToken, ...]]) -> tuple[int, ...]:
    out = [token_id]
    for child in children.get(token_id, ()):
        out.extend(_descendants(child.token_id, children))
    return tuple(sorted(out))


def _pattern(sentence: UDSentence, token: UDToken) -> tuple[UDPart, ...]:
    children = _children(sentence)
    pieces: list[tuple[int, UDPart]] = [(token.token_id, UDPart("HEAD", token.upos))]
    for child in children.get(token.token_id, ()):
        span = _descendants(child.token_id, children)
        pieces.append((min(span), UDPart("CHILD", phrase_symbol(child))))
    pieces.sort(key=lambda row: (row[0], 0 if row[1].kind == "CHILD" else 1))
    return tuple(part for _, part in pieces)


def _family(lhs: str, pattern: tuple[UDPart, ...]) -> str:
    # A family retains the same head and multiset of child phrase types while
    # allowing surface-order hypotheses to compete.
    head = next(part.symbol for part in pattern if part.kind == "HEAD")
    children = sorted(part.symbol for part in pattern if part.kind == "CHILD")
    return lhs + "<-HEAD:" + head + "+CHILDREN:" + ",".join(children)


def _order_key(pattern: tuple[UDPart, ...]) -> tuple[str, ...]:
    return tuple(f"{part.kind}:{part.symbol}" for part in pattern)


def sentence_rules(sentence: UDSentence) -> tuple[tuple[str, tuple[UDPart, ...], str], ...]:
    if not is_projective(sentence):
        raise ValueError("CANNOT_CHECK_PROJECTIVITY")
    out = []
    for token in sentence.tokens:
        if token.upos == "PUNCT":
            continue
        lhs = phrase_symbol(token)
        pattern = _pattern(sentence, token)
        out.append((lhs, pattern, _family(lhs, pattern)))
    return tuple(out)


def induce_grammar(sentences: Sequence[UDSentence], *, min_attestations: int = 1) -> UDGrammar:
    if min_attestations < 1:
        raise ValueError("min_attestations must be positive")
    production_counts: Counter[tuple[str, tuple[UDPart, ...], str]] = Counter()
    family_orders: dict[str, Counter[tuple[str, ...]]] = defaultdict(Counter)
    projective = nonprojective = 0
    for sentence in sentences:
        if not is_projective(sentence):
            nonprojective += 1
            continue
        projective += 1
        for lhs, pattern, family in sentence_rules(sentence):
            production_counts[(lhs, pattern, family)] += 1
            family_orders[family][_order_key(pattern)] += 1
    rules = []
    for (lhs, pattern, family), count in sorted(
        production_counts.items(),
        key=lambda row: (row[0][0], _order_key(row[0][1]), row[0][2]),
    ):
        if count < min_attestations:
            continue
        raw = repr((lhs, _order_key(pattern), family)).encode()
        rid = "ud:" + hashlib.sha256(raw).hexdigest()[:16]
        rules.append(UDRule(rid, lhs, family, pattern, count))
    frozen_families = {
        family: dict(sorted(counter.items()))
        for family, counter in sorted(family_orders.items())
    }
    return UDGrammar(tuple(rules), projective, nonprojective, frozen_families)


def _node_key(node: PackedUDNode) -> tuple[Any, ...]:
    return (
        node.span,
        node.tree.symbol,
        node.head_index,
        node.rule_id,
        node.tree.digest(include_form=True),
    )


def parse_forms(
    forms: Sequence[str],
    lexicon: UDLexiconInventory,
    grammar: UDGrammar,
    *,
    max_chart_nodes: int = 2_000_000,
) -> UDParseResult:
    tokens = tuple(form.lower() for form in forms)
    if not tokens:
        return UDParseResult("NO_PARSE", tokens, (), 0, 0, 0, "empty input")
    readings = []
    for form in tokens:
        rs = lexicon.form_readings.get(form, ())
        if not rs:
            return UDParseResult("UNKNOWN_LEXEME", tokens, (), 0, 0, 0, form)
        readings.append(tuple(sorted({upos for _, upos, _ in rs})))

    rules = grammar.rules
    table: dict[tuple[int, int], dict[tuple[Any, ...], PackedUDNode]] = {}
    by_start_symbol: dict[tuple[int, str], list[PackedUDNode]] = defaultdict(list)
    n = len(tokens)

    def add_node(cell: dict[tuple[Any, ...], PackedUDNode], node: PackedUDNode) -> None:
        key = _node_key(node)
        if key in cell:
            old = cell[key]
            cell[key] = PackedUDNode(old.tree, old.span, old.head_index, old.rule_id, old.derivations + node.derivations)
        else:
            cell[key] = node

    for length in range(1, n + 1):
        frozen_index = {key: tuple(values) for key, values in by_start_symbol.items()}
        staged: list[PackedUDNode] = []
        for start in range(0, n - length + 1):
            target = start + length
            cell: dict[tuple[Any, ...], PackedUDNode] = {}
            for rule in rules:
                states: list[tuple[int, tuple[UDTree, ...], int | None, str | None, int]] = [(start, (), None, None, 1)]
                for part in rule.pattern:
                    nxt: dict[tuple[Any, ...], tuple[int, tuple[UDTree, ...], int | None, str | None, int]] = {}
                    for pos, children, head_index, head_form, multiplicity in states:
                        if part.kind == "HEAD":
                            if pos >= n or part.symbol not in readings[pos]:
                                continue
                            row = (pos + 1, children, pos, tokens[pos], multiplicity)
                            key = (row[0], tuple(c.digest(include_form=True) for c in children), row[2], row[3])
                            if key in nxt:
                                old = nxt[key]
                                nxt[key] = (*old[:-1], old[-1] + multiplicity)
                            else:
                                nxt[key] = row
                        else:
                            for child in frozen_index.get((pos, part.symbol), ()):
                                row = (
                                    child.span[1],
                                    children + (child.tree,),
                                    head_index,
                                    head_form,
                                    multiplicity * child.derivations,
                                )
                                key = (row[0], tuple(c.digest(include_form=True) for c in row[1]), row[2], row[3])
                                if key in nxt:
                                    old = nxt[key]
                                    nxt[key] = (*old[:-1], old[-1] + row[-1])
                                else:
                                    nxt[key] = row
                    states = list(nxt.values())
                    if not states:
                        break
                for pos, children, head_index, head_form, multiplicity in states:
                    if pos != target or head_index is None or head_form is None:
                        continue
                    tree = UDTree(
                        rule.lhs,
                        next(p.symbol for p in rule.pattern if p.kind == "HEAD"),
                        head_form,
                        children,
                        _order_key(rule.pattern),
                    )
                    add_node(cell, PackedUDNode(tree, (start, target), head_index, rule.rule_id, multiplicity))
            if cell:
                table[(start, target)] = cell
                staged.extend(cell.values())
                if sum(len(values) for values in table.values()) > max_chart_nodes:
                    return UDParseResult(
                        "CANNOT_CHECK_CHART_BUDGET",
                        tokens,
                        (),
                        sum(len(values) for values in table.values()),
                        0,
                        0,
                        f"chart node budget {max_chart_nodes} exceeded",
                    )
        for node in staged:
            by_start_symbol[(node.span[0], node.tree.symbol)].append(node)

    roots = tuple(
        node
        for node in table.get((0, n), {}).values()
        if node.tree.symbol.startswith("ROOT:")
    )
    if not roots:
        return UDParseResult("NO_PARSE", tokens, (), sum(len(v) for v in table.values()), 0, 0, "no full-span root")
    structures = {node.tree.digest() for node in roots}
    return UDParseResult(
        "PARSED" if len(structures) == 1 else "AMBIGUOUS",
        tokens,
        roots,
        sum(len(v) for v in table.values()),
        sum(node.derivations for node in roots),
        len(structures),
        "",
    )


def gold_tree(sentence: UDSentence) -> UDTree:
    if not is_projective(sentence):
        raise ValueError("CANNOT_CHECK_PROJECTIVITY")
    children = _children(sentence)

    def build(token: UDToken) -> UDTree:
        cs = sorted(
            children.get(token.token_id, ()),
            key=lambda child: min(_descendants(child.token_id, children)),
        )
        return UDTree(
            phrase_symbol(token),
            token.upos,
            token.lower_form,
            tuple(build(c) for c in cs),
            _order_key(_pattern(sentence, token)),
        )

    return build(sentence.roots[0])


def coverage(
    train_sentences: Sequence[UDSentence],
    eval_sentences: Sequence[UDSentence],
    *,
    min_attestations: int = 1,
    max_chart_nodes: int = 2_000_000,
) -> UDCoverage:
    lexicon = induce_lexicon(train_sentences)
    grammar = induce_grammar(train_sentences, min_attestations=min_attestations)
    known_rules = {(r.lhs, r.pattern, r.family_id) for r in grammar.rules}
    projective = nonprojective = lexical_tokens = lexical_covered = 0
    gold_rules = gold_rules_covered = parsed = exact = 0
    for sentence in eval_sentences:
        if not is_projective(sentence):
            nonprojective += 1
            continue
        projective += 1
        forms = []
        for token in sentence.tokens:
            if token.upos == "PUNCT":
                continue
            lexical_tokens += 1
            forms.append(token.form)
            readings = lexicon.form_readings.get(token.lower_form, ())
            if any(lemma == token.lower_lemma and upos == token.upos for lemma, upos, _ in readings):
                lexical_covered += 1
        rules = sentence_rules(sentence)
        gold_rules += len(rules)
        gold_rules_covered += sum(rule in known_rules for rule in rules)
        result = parse_forms(forms, lexicon, grammar, max_chart_nodes=max_chart_nodes)
        if result.status in {"PARSED", "AMBIGUOUS"}:
            parsed += 1
            gold = gold_tree(sentence).digest()
            if any(root.tree.digest() == gold for root in result.roots):
                exact += 1
    return UDCoverage(
        len(eval_sentences),
        projective,
        nonprojective,
        lexical_tokens,
        lexical_covered,
        gold_rules,
        gold_rules_covered,
        parsed,
        exact,
    )
