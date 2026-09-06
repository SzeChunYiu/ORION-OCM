"""Frozen Anthropic FLT dependency extraction and theorem-statement isolation.

The solution files are evaluator-side only.  A theorem wrapper is accepted only when the matching
wrapper imports its exact P2M solution module; dependencies come from active `Theorems.Thm_*`
imports in that solution file.  Statement extraction uses a lexical scanner and a repository-wide
coverage check rather than a one-line regex.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Iterator

from flt_contract import sha256_file


class ExtractionError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class Node:
    theorem_id: str
    wrapper_path: str
    solution_path: str
    dependencies: tuple[str, ...]
    statement_source: str
    wrapper_sha256: str
    solution_sha256: str


def _mask_comments_and_strings(text: str) -> str:
    """Replace comments/string bodies with spaces while preserving newlines and token positions."""
    out = list(text)
    i = 0
    block_depth = 0
    in_string = False
    escaped = False
    while i < len(text):
        if block_depth:
            if text.startswith("/-", i):
                out[i:i+2] = "  "; block_depth += 1; i += 2; continue
            if text.startswith("-/", i):
                out[i:i+2] = "  "; block_depth -= 1; i += 2; continue
            if text[i] != "\n": out[i] = " "
            i += 1; continue
        if in_string:
            ch = text[i]
            if ch != "\n": out[i] = " "
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
            i += 1; continue
        if text.startswith("/-", i):
            out[i:i+2] = "  "; block_depth = 1; i += 2; continue
        if text.startswith("--", i):
            j = text.find("\n", i)
            if j < 0: j = len(text)
            for k in range(i, j): out[k] = " "
            i = j; continue
        if text[i] == '"':
            out[i] = " "; in_string = True; i += 1; continue
        i += 1
    if block_depth or in_string:
        raise ExtractionError("unterminated comment/string")
    return "".join(out)


def active_imports(text: str) -> tuple[str, ...]:
    masked = _mask_comments_and_strings(text)
    modules: list[str] = []
    for line in masked.splitlines():
        stripped = line.strip()
        if not stripped.startswith("import"):
            continue
        m = re.match(r"^\s*import\s+(.+?)\s*$", line)
        if not m:
            raise ExtractionError(f"unsupported import layout: {stripped!r}")
        for token in m.group(1).split():
            if not re.fullmatch(r"[A-Za-z0-9_'.]+", token):
                raise ExtractionError(f"unexpected import token: {token!r}")
            modules.append(token)
    return tuple(modules)


def theorem_imports(solution_text: str) -> tuple[str, ...]:
    return tuple(m for m in active_imports(solution_text) if m.startswith("Theorems.Thm_"))


_DECLARATION = re.compile(r"(?m)^\s*(?:theorem|lemma)\s+[A-Za-z0-9_'.]+\b")
_BRIDGE = re.compile(r":=\s*by\s+p2m_exact_reverting\b")


def extract_statement_source(wrapper_text: str) -> str:
    """Return the exact target declaration prefix, excluding the generated bridge proof.

    Anthropic wrappers are not uniformly one-declaration files: some contain helper lemmas before
    the generated target theorem.  The stable answer-bearing feature is the unique generated
    `:= by p2m_exact_reverting` bridge.  We therefore require exactly one bridge outside
    comments/strings and select the nearest theorem/lemma declaration that begins before it.  This
    remains fail-closed: no bridge, multiple bridges, or no preceding declaration is rejected.
    """
    masked = _mask_comments_and_strings(wrapper_text)
    markers = list(_BRIDGE.finditer(masked))
    if len(markers) != 1:
        raise ExtractionError(f"expected one p2m bridge marker, found {len(markers)}")
    marker = markers[0]
    declarations = [m for m in _DECLARATION.finditer(masked, 0, marker.start())]
    if not declarations:
        raise ExtractionError("no theorem/lemma declaration precedes p2m bridge")
    start = declarations[-1].start()
    end = marker.start()
    statement = wrapper_text[start:end].strip()
    if not statement or "P2M.Sol." in statement or "p2m_exact_reverting" in statement:
        raise ExtractionError("statement slice is empty or leaks solution/bridge text")
    return statement


def _module_for_solution(stem: str) -> str:
    return f"P2M.Sol.S_{stem}"


def extract_node(root: Path, stem: str) -> Node:
    wrapper = root / "Theorems" / f"Thm_{stem}.lean"
    solution = root / "P2M" / "Sol" / f"S_{stem}.lean"
    if not wrapper.is_file() or not solution.is_file():
        raise ExtractionError(f"missing wrapper/solution pair for {stem}")
    wrapper_text = wrapper.read_text(encoding="utf-8")
    solution_text = solution.read_text(encoding="utf-8")
    expected = _module_for_solution(stem)
    if expected not in active_imports(wrapper_text):
        raise ExtractionError(f"wrapper {stem} does not import matching {expected}")
    deps = theorem_imports(solution_text)
    return Node(
        theorem_id=f"Theorems.Thm_{stem}",
        wrapper_path=wrapper.relative_to(root).as_posix(),
        solution_path=solution.relative_to(root).as_posix(),
        dependencies=tuple(sorted(set(deps))),
        statement_source=extract_statement_source(wrapper_text),
        wrapper_sha256=sha256_file(wrapper),
        solution_sha256=sha256_file(solution),
    )


def iter_solution_stems(root: Path) -> Iterator[str]:
    for path in sorted((root / "P2M" / "Sol").glob("S_*.lean")):
        yield path.stem.removeprefix("S_")


def extract_graph(root: Path, *, require_count: int | None = 29511) -> dict[str, Node]:
    stems = tuple(iter_solution_stems(root))
    if require_count is not None and len(stems) != require_count:
        raise ExtractionError(f"solution module count mismatch: {len(stems)} != {require_count}")
    graph: dict[str, Node] = {}
    for stem in stems:
        node = extract_node(root, stem)
        if node.theorem_id in graph:
            raise ExtractionError(f"duplicate theorem identity {node.theorem_id}")
        graph[node.theorem_id] = node
    return graph


def validate_dependency_targets(graph: dict[str, Node]) -> tuple[str, ...]:
    known = set(graph)
    missing = sorted({dep for node in graph.values() for dep in node.dependencies if dep not in known})
    return tuple(missing)
