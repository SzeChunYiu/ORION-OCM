"""R0A non-test checker population census, by AST, over the source-tracked tree.

The handoff for this tranche asks for a census of checker construction sites and
warns that code search returned empty and that a zero must not be inferred from
it.  This module is written so that a zero is auditable rather than inferred:

* the population is ``git ls-files``, so it is what the repository tracks and not
  whatever happens to be in a working tree;
* sites are found on the parsed syntax tree, in three shapes -- a ``checker=``
  keyword, an assignment to a name or attribute called ``checker``, and a
  ``"checker"`` key in a dict literal -- because a construction spread over
  several lines, or built as a mapping, is invisible to a line-oriented search;
* every file that could not be parsed is counted and named, so a site missed
  through a syntax error cannot be silently absent;
* the classifier is CONSERVATIVE: anything it does not positively recognise as
  belonging to the restricted language is ``NOT_REPRESENTABLE``.

Classification answers one question and no other: could this checker be written
in the certified pure calculus of ``PURE_CHECKER_EFFECT_CONTRACT_V1.md``, whose
grammar is TRUE/FALSE/HAS/TYPE/EQ/AND/OR/NOT over detached candidate data with
STATUS/IF?  It is not an authorization to migrate anything, and this module
changes no production code.
"""
from __future__ import annotations

import ast
import pathlib
import subprocess
from typing import Any, Iterator, Mapping, Sequence

import pure_checker_contract as PCC

__all__ = ["census", "classify_source", "SITE_SHAPES", "CLASSES", "BUCKETS"]

#: The three syntactic shapes a checker can be supplied in. Anything not in this
#: list is not looked for, and the receipt says so rather than implying coverage.
SITE_SHAPES = ("KEYWORD_ARGUMENT", "ASSIGNED_NAME_OR_ATTRIBUTE", "DICT_LITERAL_KEY")

#: Ordered from most to least migratable. A site gets the first class it earns.
CLASSES = (
    "FIELD_DECLARATION",      # the dataclass field itself, not a construction site
    "NOT_A_CHECKER_CALLABLE", # a string/number naming a checker, not a checker
    "NO_CHECKER",             # literal None: not a member of the population
    "CONSTANT_STATUS",        # returns one registered status unconditionally
    "DSL_REPRESENTABLE",      # a boolean combination of HAS/TYPE/EQ over the argument
    "NEEDS_DSL_EXTENSION",    # pure and bounded, but uses operations the grammar lacks
    "INDIRECT_UNRESOLVED",    # a reference this pass could not resolve to a definition
    "NOT_REPRESENTABLE",      # anything else, including everything unrecognised
)

BUCKETS = ("PRODUCTION", "RESEARCH", "TEST", "ARCHIVED_SNAPSHOT")

#: Directory segments that mark a frozen copy of source rather than live source.
#: These are evidence, not code under maintenance, and are counted separately.
_ARCHIVE_MARKERS = ("/raw/", "/records/", "/results/", "/vendor/", "/source-snapshot/")

_STATUS_NAMES = {"PASS", "FAIL", "CANNOT_CHECK"}


def _bucket(path: str) -> str:
    name = pathlib.PurePosixPath(path).name
    if name.startswith("test_") or name.endswith("_test.py") or "/tests/" in f"/{path}":
        return "TEST"
    if any(marker in f"/{path}" for marker in _ARCHIVE_MARKERS):
        return "ARCHIVED_SNAPSHOT"
    if path.startswith("src/"):
        return "PRODUCTION"
    return "RESEARCH"


def tracked_python_files(root: pathlib.Path) -> list[str]:
    out = subprocess.run(["git", "-C", str(root), "ls-files", "*.py"],
                         capture_output=True, text=True, check=True)
    return sorted(line for line in out.stdout.splitlines() if line.endswith(".py"))


# --- finding the sites -------------------------------------------------------

def _sites_in_module(tree: ast.AST) -> Iterator[tuple[str, ast.AST, int]]:
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            for kw in node.keywords:
                if kw.arg == "checker":
                    yield ("KEYWORD_ARGUMENT", kw.value, getattr(kw.value, "lineno", node.lineno))
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                named = (isinstance(target, ast.Name) and target.id == "checker") or (
                    isinstance(target, ast.Attribute) and target.attr == "checker")
                if named and node.value is not None:
                    yield ("ASSIGNED_NAME_OR_ATTRIBUTE", node.value,
                           getattr(node.value, "lineno", node.lineno))
        elif isinstance(node, ast.Dict):
            for key, value in zip(node.keys, node.values):
                if isinstance(key, ast.Constant) and key.value == "checker":
                    yield ("DICT_LITERAL_KEY", value, getattr(value, "lineno", key.lineno))


def _module_constants(tree: ast.AST) -> dict[str, Any]:
    """Module-level names bound once to a string/number literal.

    A ``"checker"`` mapping entry whose value is one of these names is a record
    field naming a checker, not a checker. Resolving them is what separates an
    audited zero from an unresolved reference.
    """
    found: dict[str, list[Any]] = {}
    for node in tree.body if isinstance(tree, ast.Module) else []:
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant) \
                and type(node.value.value) in (str, int, float, bool):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    found.setdefault(target.id, []).append(node.value.value)
    return {name: values[0] for name, values in found.items() if len(values) == 1}


def _methods(tree: ast.AST) -> dict[str, ast.AST]:
    """Method definitions by name, for resolving ``self.<attr>`` checkers.

    A name defined in more than one class is dropped rather than guessed at.
    """
    found: dict[str, list[ast.AST]] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for statement in node.body:
                if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    found.setdefault(statement.name, []).append(statement)
    return {name: nodes[0] for name, nodes in found.items() if len(nodes) == 1}


def _definitions(tree: ast.AST) -> dict[str, ast.AST]:
    """Module- and function-level ``def``/``lambda`` bindings, by name.

    One level of resolution only. A name bound twice is dropped rather than
    guessed at, because resolving it wrongly would be worse than declaring it
    unresolved.
    """
    found: dict[str, list[ast.AST]] = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            found.setdefault(node.name, []).append(node)
        elif isinstance(node, ast.Assign) and isinstance(node.value, ast.Lambda):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    found.setdefault(target.id, []).append(node.value)
    return {name: nodes[0] for name, nodes in found.items() if len(nodes) == 1}


# --- classifying one site ----------------------------------------------------

def _is_status(node: ast.AST) -> str | None:
    """``Status.PASS``/``SV.Status.PASS``/``"PASS"`` -- the registered statuses."""
    if isinstance(node, ast.Constant) and node.value in _STATUS_NAMES:
        return node.value
    if isinstance(node, ast.Attribute) and node.attr in _STATUS_NAMES:
        base = node.value
        if isinstance(base, ast.Name) and base.id == "Status":
            return node.attr
        if isinstance(base, ast.Attribute) and base.attr == "Status":
            return node.attr
    return None


def _param_names(node: ast.AST) -> list[str]:
    args = node.args
    return [a.arg for a in (*args.posonlyargs, *args.args, *args.kwonlyargs)]


def _body_expressions(node: ast.AST) -> list[ast.AST] | None:
    """The single returned expression of a lambda, or of a def whose body is one
    ``return``. Anything else is not recognised, which makes it unrepresentable."""
    if isinstance(node, ast.Lambda):
        return [node.body]
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        statements = [s for s in node.body if not (isinstance(s, ast.Expr)
                                                   and isinstance(s.value, ast.Constant))]
        if len(statements) == 1 and isinstance(statements[0], ast.Return):
            return [statements[0].value] if statements[0].value is not None else None
    return None


def _path_of(node: ast.AST, param: str) -> list[Any] | None:
    """``x["a"][0]`` over the checker's own argument, as a DSL path."""
    path: list[Any] = []
    current = node
    while isinstance(current, ast.Subscript):
        key = current.slice
        if not (isinstance(key, ast.Constant) and type(key.value) in (str, int)):
            return None
        path.insert(0, key.value)
        current = current.value
    if isinstance(current, ast.Name) and current.id == param and path:
        return path
    return None


def _predicate(node: ast.AST, param: str) -> Mapping[str, Any] | None:
    """Translate one expression into a DSL predicate, or return None.

    None means "not recognised", never "false". Every caller treats None as a
    reason to give up on the whole site.
    """
    if isinstance(node, ast.Constant) and node.value is True:
        return {"op": "TRUE"}
    if isinstance(node, ast.Constant) and node.value is False:
        return {"op": "FALSE"}
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
        inner = _predicate(node.operand, param)
        return {"op": "NOT", "arg": inner} if inner else None
    if isinstance(node, ast.BoolOp):
        parts = [_predicate(v, param) for v in node.values]
        if any(p is None for p in parts):
            return None
        op = "AND" if isinstance(node.op, ast.And) else "OR"
        folded = parts[0]
        for part in parts[1:]:
            folded = {"op": op, "left": folded, "right": part}
        return folded
    if isinstance(node, ast.Compare) and len(node.ops) == 1:
        left, op, right = node.left, node.ops[0], node.comparators[0]
        if isinstance(op, ast.In):
            # "k" in x[...]  ->  HAS(path + [k])
            if isinstance(left, ast.Constant) and type(left.value) in (str, int):
                if isinstance(right, ast.Name) and right.id == param:
                    return {"op": "HAS", "path": [left.value]}
                path = _path_of(right, param)
                if path is not None:
                    return {"op": "HAS", "path": [*path, left.value]}
            return None
        if isinstance(op, (ast.Eq, ast.Is)):
            path = _path_of(left, param)
            literal = right
            if path is None:
                path, literal = _path_of(right, param), left
            if path is None or not isinstance(literal, ast.Constant):
                return None
            if not PCC._literal_ok(literal.value):
                return None
            return {"op": "EQ", "path": path, "literal": literal.value}
        return None
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
            and node.func.id == "isinstance" and len(node.args) == 2:
        path = _path_of(node.args[0], param)
        kind = node.args[1]
        mapping = {"dict": "dict", "list": "list", "tuple": "tuple", "str": "str",
                   "int": "int", "float": "float", "bool": "bool"}
        if path is not None and isinstance(kind, ast.Name) and kind.id in mapping:
            return {"op": "TYPE", "path": path, "kind": mapping[kind.id]}
        return None
    return None


def _checker_ast(node: ast.AST, param: str) -> Mapping[str, Any] | None:
    """Translate a returned expression into a DSL checker, or return None."""
    status = _is_status(node)
    if status is not None:
        return {"op": "STATUS", "status": status}
    if isinstance(node, ast.IfExp):
        test = _predicate(node.test, param)
        then = _checker_ast(node.body, param)
        other = _checker_ast(node.orelse, param)
        if test and then and other:
            return {"op": "IF", "predicate": test, "then": then, "else": other}
    return None


#: Operations that are pure and bounded but outside the grammar. A site built
#: only from these is a candidate for a LANGUAGE EXTENSION rather than a
#: migration, and separating the two is the point of the census.
_EXTENSION_NODES = (ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.NotEq, ast.Add, ast.Sub,
                    ast.Mult, ast.Mod, ast.FloorDiv)
_EXTENSION_CALLS = {"len", "abs", "min", "max", "sorted", "sum", "all", "any", "type", "str", "int"}


def _pure_but_richer(node: ast.AST, param: str) -> bool:
    """Conservative: every name it reads is the parameter or a builtin we listed,
    every call is one of those builtins, and there is no attribute access outside
    the registered statuses."""
    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            if not (isinstance(child.func, ast.Name) and child.func.id in
                    _EXTENSION_CALLS | {"isinstance"}):
                return False
        elif isinstance(child, ast.Attribute):
            if _is_status(child) is None:
                return False
        elif isinstance(child, ast.Name):
            if child.id not in {param, "Status", "SV", "True", "False", "None"} \
                    and child.id not in _EXTENSION_CALLS | {"isinstance", "dict", "list",
                                                            "tuple", "str", "int", "float",
                                                            "bool"}:
                return False
        elif isinstance(child, (ast.Import, ast.ImportFrom, ast.Global, ast.Nonlocal,
                                ast.Await, ast.Yield, ast.YieldFrom, ast.Lambda,
                                ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
            return False
    return True


def classify_source(source: str) -> list[dict[str, Any]]:
    """Classify every checker site in one module's source."""
    tree = ast.parse(source)
    definitions = _definitions(tree)
    constants = _module_constants(tree)
    methods = _methods(tree)
    inside = {id(node) for cls in ast.walk(tree) if isinstance(cls, ast.ClassDef)
              for node in ast.walk(cls)}
    out: list[dict[str, Any]] = []
    for shape, value, line in _sites_in_module(tree):
        out.append(_classify_site(shape, value, line, definitions, constants, methods,
                                  id(value) in inside))
    return out


def _classify_site(shape: str, value: ast.AST, line: int,
                   definitions: Mapping[str, ast.AST],
                   constants: Mapping[str, Any] | None = None,
                   methods: Mapping[str, ast.AST] | None = None,
                   in_class: bool = False) -> dict[str, Any]:
    site: dict[str, Any] = {"shape": shape, "line": line,
                            "expression": ast.dump(value)[:200], "resolved_through": None}
    if isinstance(value, ast.Constant) and value.value is None:
        klass = "FIELD_DECLARATION" if shape == "ASSIGNED_NAME_OR_ATTRIBUTE" and in_class \
            else "NO_CHECKER"
        return {**site, "classification": klass, "dsl": None}
    if isinstance(value, ast.Constant):
        # A string or number under a "checker" key names a checker DOMAIN in a
        # record; it is not a callable and not a member of this population. The
        # distinction matters: counting these would turn an audited zero into a
        # phantom population.
        return {**site, "classification": "NOT_A_CHECKER_CALLABLE", "dsl": None,
                "constant": value.value if type(value.value) in (str, int, float, bool)
                else None}

    constants = constants or {}
    methods = methods or {}
    if isinstance(value, ast.Name) and value.id in constants:
        return {**site, "classification": "NOT_A_CHECKER_CALLABLE", "dsl": None,
                "resolved_through": value.id, "constant": constants[value.id]}

    target = value
    if isinstance(value, ast.Attribute) and isinstance(value.value, ast.Name) \
            and value.value.id == "self" and value.attr in methods:
        target, site["resolved_through"] = methods[value.attr], f"self.{value.attr}"
    elif isinstance(value, ast.Name) and value.id in definitions:
        target, site["resolved_through"] = definitions[value.id], value.id
    elif isinstance(value, ast.Call) and isinstance(value.func, ast.Name) \
            and value.func.id in definitions:
        # A factory: the checker is whatever the factory returns, so classify the
        # factory's own body. Its free variables make it a closure, which the
        # richness test below will catch unless the body is a bare status.
        target, site["resolved_through"] = definitions[value.func.id], value.func.id
    elif isinstance(value, (ast.Name, ast.Attribute)):
        if isinstance(value, ast.Attribute):
            site["attribute"] = value.attr
        return {**site, "classification": "INDIRECT_UNRESOLVED", "dsl": None}

    if not isinstance(target, (ast.Lambda, ast.FunctionDef, ast.AsyncFunctionDef)):
        return {**site, "classification": "NOT_REPRESENTABLE", "dsl": None}

    params = _param_names(target)
    if site["resolved_through"] and str(site["resolved_through"]).startswith("self.") \
            and params and params[0] == "self":
        # A bound method's receiver is not the candidate it verifies.
        params = params[1:]
    body = _body_expressions(target)
    if body is None or len(params) != 1:
        # A factory whose body is a nested def is the common shape; look one level
        # deeper for a single nested function and classify that instead.
        statements = target.body if isinstance(
            target, (ast.FunctionDef, ast.AsyncFunctionDef)) else []
        nested = [s for s in statements if isinstance(s, (ast.FunctionDef, ast.Lambda))]
        if len(nested) == 1:
            inner = nested[0]
            params, body = _param_names(inner), _body_expressions(inner)
            site["resolved_through"] = f"{site['resolved_through']}->nested"
            target = inner
        if body is None or len(params) != 1:
            return {**site, "classification": "NOT_REPRESENTABLE", "dsl": None}

    param = params[0]
    expression = body[0]
    dsl = _checker_ast(expression, param)
    if dsl is not None:
        klass = "CONSTANT_STATUS" if dsl["op"] == "STATUS" else "DSL_REPRESENTABLE"
        # A factory-produced constant status still closes over nothing that can
        # change the verdict, so it stays a constant. Anything else must survive
        # the richness test before it is called representable.
        if klass == "DSL_REPRESENTABLE" and not _pure_but_richer(expression, param):
            return {**site, "classification": "NOT_REPRESENTABLE", "dsl": None}
        return {**site, "classification": klass, "dsl": dsl}
    if _is_status_only_closure(expression, param):
        return {**site, "classification": "CONSTANT_STATUS_OVER_A_CLOSED_VARIABLE",
                "dsl": None}
    if _pure_but_richer(expression, param):
        return {**site, "classification": "NEEDS_DSL_EXTENSION", "dsl": None}
    return {**site, "classification": "NOT_REPRESENTABLE", "dsl": None}


def _is_status_only_closure(node: ast.AST, param: str) -> bool:
    """``lambda data: verdict`` where ``verdict`` is a captured status.

    Representable only once the captured value is known, which a static census
    cannot do, so it is reported as its own class rather than folded into either
    neighbour."""
    return isinstance(node, ast.Name) and node.id != param


def _module_name(relative: str) -> str | None:
    """The dotted name a tracked file is importable as, for ``src/`` layout."""
    if not relative.startswith("src/") or not relative.endswith(".py"):
        return None
    parts = pathlib.PurePosixPath(relative[len("src/"):]).with_suffix("").parts
    if parts and parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts) if parts else None


def _import_aliases(tree: ast.AST) -> dict[str, str]:
    """alias -> dotted module, for ``import a.b as M`` and ``from a import b as M``."""
    aliases: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for entry in node.names:
                aliases[entry.asname or entry.name.split(".")[0]] = entry.name
        elif isinstance(node, ast.ImportFrom) and node.module and not node.level:
            for entry in node.names:
                aliases[entry.asname or entry.name] = f"{node.module}.{entry.name}"
    return aliases


def _resolve_across_modules(sites: list[dict[str, Any]], root: pathlib.Path,
                            files: Sequence[str]) -> int:
    """Upgrade ``M.NAME`` references to a constant defined in another tracked module.

    Only constants are resolved, and only one hop. A checker that is genuinely a
    callable in another module stays INDIRECT_UNRESOLVED, because guessing at it
    would be worse than saying the census could not see it.
    """
    constants_by_module: dict[str, dict[str, Any]] = {}
    aliases_by_path: dict[str, dict[str, str]] = {}
    for relative in files:
        try:
            tree = ast.parse((root / relative).read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:
            continue
        aliases_by_path[relative] = _import_aliases(tree)
        dotted = _module_name(relative)
        if dotted:
            constants_by_module[dotted] = _module_constants(tree)

    upgraded = 0
    for site in sites:
        if site["classification"] != "INDIRECT_UNRESOLVED":
            continue
        expression = site["expression"]
        if not expression.startswith("Attribute(value=Name(id='"):
            continue
        alias = expression.split("id='", 1)[1].split("'", 1)[0]
        attribute = site.get("attribute")
        if attribute is None:
            continue
        dotted = aliases_by_path.get(site["path"], {}).get(alias)
        if dotted is None:
            continue
        constants = constants_by_module.get(dotted, {})
        if attribute in constants:
            site["classification"] = "NOT_A_CHECKER_CALLABLE"
            site["constant"] = constants[attribute]
            site["resolved_through"] = f"{dotted}.{attribute}"
            upgraded += 1
    return upgraded


#: Detached candidates the differential check evaluates both implementations on.
#: Chosen to exercise the places the two semantics could disagree: a missing key,
#: a key present with the wrong type, a nested path, and a non-mapping root.
DIFFERENTIAL_CANDIDATES: tuple[Any, ...] = (
    {}, {"status": "PASS"}, {"status": "FAIL"}, {"status": 1}, {"status": None},
    {"output": {}}, {"output": {"value": 0}}, {"output": {"value": "0"}},
    {"output": [1, 2, 3]}, {"other": {"value": 0}}, [], "", 0, None,
)


def _compilable(node: ast.AST, param: str) -> bool:
    """A lambda body safe to evaluate in a namespace holding only the statuses.

    Nothing here is a security boundary -- the file is already in the repository
    and about to be imported by its own tests. It is a CORRECTNESS boundary: an
    expression that reads a free name would evaluate to something the census
    never saw, so its agreement would not be evidence about the translation.
    """
    for child in ast.walk(node):
        if isinstance(child, ast.Name) and child.id not in (param, "Status", "isinstance",
                                                            "dict", "list", "tuple", "str",
                                                            "int", "float", "bool"):
            return False
        if isinstance(child, ast.Attribute) and _is_status(child) is None:
            return False
        if isinstance(child, ast.Call) and not (
                isinstance(child.func, ast.Name) and child.func.id == "isinstance"):
            return False
    return True


def differential_check(sites: Sequence[Mapping[str, Any]], root: pathlib.Path
                       ) -> dict[str, Any]:
    """Evaluate the original checker and its translation on the same candidates.

    Proposition 1 of R0A_CHECKER_CENSUS_V1.md says the translation preserves the
    verdict wherever the original returns one. This is the mechanical half of
    that claim, and it is run over every site the census translated, not a
    sample.
    """
    from ocm.runtime import solve as SV

    statuses = {"PASS": SV.Status.PASS, "FAIL": SV.Status.FAIL,
                "CANNOT_CHECK": SV.Status.CANNOT_CHECK}
    agreements = disagreements = more_defined = skipped = 0
    failures: list[dict[str, Any]] = []
    for site in sites:
        if site.get("dsl") is None:
            continue
        try:
            tree = ast.parse((root / site["path"]).read_text(encoding="utf-8",
                                                             errors="replace"))
        except SyntaxError:
            skipped += 1
            continue
        lambdas = [n for n in ast.walk(tree) if isinstance(n, ast.Lambda)
                   and getattr(n, "lineno", None) == site["line"]]
        if len(lambdas) != 1:
            skipped += 1
            continue
        node = lambdas[0]
        param = _param_names(node)[0]
        if not _compilable(node.body, param):
            skipped += 1
            continue
        original = eval(compile(ast.Expression(body=node), "<census>", "eval"),  # noqa: S307
                        {"__builtins__": {"isinstance": isinstance, "dict": dict,
                                          "list": list, "tuple": tuple, "str": str,
                                          "int": int, "float": float, "bool": bool},
                         "Status": SV.Status}, {})
        certificate = PCC.issue_certificate(site["dsl"])
        for candidate in DIFFERENTIAL_CANDIDATES:
            translated, _ = PCC.evaluate(certificate, candidate)
            try:
                produced = original(candidate)
            except Exception:                       # noqa: BLE001 - the point of the check
                more_defined += 1
                continue
            if isinstance(produced, str):
                produced = statuses.get(produced)
            if produced == translated:
                agreements += 1
            else:
                disagreements += 1
                failures.append({"path": site["path"], "line": site["line"],
                                 "candidate": repr(candidate)[:80],
                                 "original": str(produced), "translated": str(translated)})
    return {
        "sites_checked": sum(1 for s in sites if s.get("dsl") is not None) - skipped,
        "sites_skipped_not_a_closed_lambda": skipped,
        "candidates_per_site": len(DIFFERENTIAL_CANDIDATES),
        "agreements": agreements,
        "disagreements": disagreements,
        "original_raised_translation_returned_a_status": more_defined,
        "failures": failures,
        "reading": (
            "Agreement is required wherever the original returns a status. Where the "
            "original RAISES and the translation returns one, the calculus is strictly "
            "more defined -- a missing key is False under HAS and a KeyError in Python. "
            "That is a property of the calculus, counted rather than hidden, and it is "
            "why Proposition 1 is stated only over inputs where the original is defined."),
    }


def census(root: pathlib.Path) -> dict[str, Any]:
    files = tracked_python_files(root)
    scanned, unparsed, sites = 0, [], []
    for relative in files:
        text = (root / relative).read_text(encoding="utf-8", errors="replace")
        try:
            found = classify_source(text)
        except SyntaxError as exc:
            unparsed.append({"path": relative, "error": str(exc)})
            continue
        scanned += 1
        for site in found:
            sites.append({**site, "path": relative, "bucket": _bucket(relative)})

    cross_module_upgrades = _resolve_across_modules(sites, root, files)

    admitted, admission_failures = 0, []
    for site in sites:
        if site["dsl"] is None:
            continue
        try:
            certificate = PCC.issue_certificate(site["dsl"])
            PCC.verify_certificate(certificate)
            site["certificate_digest"] = certificate.get("digest")
            admitted += 1
        except Exception as exc:                       # noqa: BLE001 - recorded, not raised
            admission_failures.append({"path": site["path"], "line": site["line"],
                                       "error": f"{type(exc).__name__}: {exc}"})

    def tally(bucket: str) -> dict[str, int]:
        rows = [s for s in sites if s["bucket"] == bucket]
        classes = sorted({s["classification"] for s in rows})
        return {klass: sum(1 for s in rows if s["classification"] == klass)
                for klass in classes}

    return {
        "schema": "ocm.r0a.checker-census.v1",
        "authority": (
            "A census of source-tracked checker construction sites and a static "
            "classification of whether each could be written in the certified pure "
            "calculus. It migrates nothing, authorizes nothing, and touches no "
            "production code."),
        "population": {
            "definition": "git ls-files '*.py' at the tree being scanned",
            "python_files_tracked": len(files),
            "python_files_parsed": scanned,
            "python_files_unparsed": unparsed,
        },
        "site_shapes_searched": list(SITE_SHAPES),
        "what_this_census_cannot_see": [
            "a checker supplied positionally rather than by keyword, which the "
            "current dataclass signatures make unlikely but which is not excluded",
            "a checker produced by a factory imported from another module, which is "
            "reported as INDIRECT_UNRESOLVED rather than guessed at",
            "a checker assembled at runtime from data",
        ],
        "sites_total": len(sites),
        "cross_module_constant_resolutions": cross_module_upgrades,
        "by_bucket": {bucket: tally(bucket) for bucket in BUCKETS},
        "differential_check": differential_check(sites, root),
        "dsl_admission": {"translated": sum(1 for s in sites if s["dsl"] is not None),
                          "admitted_by_the_certified_calculus": admitted,
                          "admission_failures": admission_failures},
        "sites": sites,
    }


#: The census fails the job if any of these stops holding. They are the claims the
#: receipt would otherwise assert without anything enforcing them.
TERMINAL = "PRODUCTION_SUPPLIES_NO_CHECKER_CALLABLE"


def terminal_of(doc: Mapping[str, Any]) -> tuple[str, str]:
    if doc["population"]["python_files_unparsed"]:
        return ("VOID_A_TRACKED_FILE_DID_NOT_PARSE",
                "A tracked Python file failed to parse, so every checker site in it is "
                "missing from the census and the counts below are a floor, not a census.")
    if doc["dsl_admission"]["admission_failures"]:
        return ("TRANSLATION_REJECTED_BY_THE_CERTIFIED_CALCULUS",
                "The census emitted an AST the calculus refuses. Proposition 1(i) fails, "
                "so no classification in this receipt may be relied on.")
    if doc["differential_check"]["disagreements"]:
        return ("TRANSLATION_CHANGES_A_VERDICT",
                "A translated checker returned a different status from the original on a "
                "candidate where the original was defined. Proposition 1(ii) fails.")
    allowed = {"FIELD_DECLARATION", "NOT_A_CHECKER_CALLABLE"}
    production = [s for s in doc["sites"] if s["bucket"] == "PRODUCTION"]
    if any(s["classification"] not in allowed for s in production):
        return ("PRODUCTION_NOW_SUPPLIES_A_CHECKER_CALLABLE",
                "src/ supplies a checker callable, which it did not when this census was "
                "written. The population has changed and R0A_CHECKER_CENSUS_V1.md must be "
                "rewritten before anything is concluded from it.")
    return (TERMINAL,
            f"{len(production)} src/ sites, all of them either the dataclass field itself "
            "or a string naming a checker domain. Every checker reaching the protected "
            "CHECK stage is host-supplied, so the restricted DSL cannot be justified by "
            "the current production population.")


def build_report(root: pathlib.Path | None = None) -> dict[str, Any]:
    root = root or pathlib.Path(__file__).resolve().parent.parent.parent
    doc = census(root)
    terminal, reason = terminal_of(doc)
    return {**doc, "terminal": terminal, "terminal_reason": reason}


def main(argv: list[str] | None = None) -> int:
    import argparse
    import json

    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=pathlib.Path, required=True)
    parser.add_argument("--github-notice", action="store_true")
    args = parser.parse_args(argv)
    report = build_report()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    if args.github_notice:
        production = sum(1 for s in report["sites"] if s["bucket"] == "PRODUCTION")
        print(
            "::notice title=R0A checker census::"
            f"files={report['population']['python_files_tracked']}; "
            f"sites={report['sites_total']}; production={production}; "
            f"admitted={report['dsl_admission']['admitted_by_the_certified_calculus']}"
            f"/{report['dsl_admission']['translated']}; "
            f"disagreements={report['differential_check']['disagreements']}; "
            f"terminal={report['terminal']}"
        )
    if report["terminal"] != TERMINAL:
        raise SystemExit(1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
