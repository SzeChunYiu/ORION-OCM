"""Hostile tests for the R0A non-test checker census.

The census exists to answer a question whose wrong answer is silent: how many
source-tracked checker construction sites are there, and could they be written in
the certified pure calculus.  A census that under-counts reports an audited zero
that is really a blind spot, and a census that over-classifies reports that
production checkers are migratable when they are not.  Both failures are tested
for here, and the second is tested harder, because it is the one that would let
an unsafe omission through.
"""

from __future__ import annotations

import ast
import json
import os
import pathlib
import sys

import pytest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import checker_census as C
import pure_checker_contract as PCC
from ocm.runtime import solve as SV


def _one(source: str) -> dict:
    sites = C.classify_source(source)
    assert len(sites) == 1, [s["shape"] for s in sites]
    return sites[0]


# --- a line-oriented search would miss these -------------------------------

def test_a_call_split_over_several_lines_is_found():
    site = _one("""
op = OperatorSpec(
    operator_id="x",
    checker=lambda data:
        Status.PASS,
)
""")
    assert site["shape"] == "KEYWORD_ARGUMENT"
    assert site["classification"] == "CONSTANT_STATUS"


def test_a_checker_supplied_as_a_dict_entry_is_found():
    site = _one('spec = {"operator_id": "x", "checker": lambda d: Status.FAIL}')
    assert site["shape"] == "DICT_LITERAL_KEY"
    assert site["classification"] == "CONSTANT_STATUS"


def test_a_checker_assigned_to_an_attribute_is_found():
    site = _one("self.checker = lambda d: Status.CANNOT_CHECK")
    assert site["shape"] == "ASSIGNED_NAME_OR_ATTRIBUTE"


def test_a_checker_reached_through_a_module_level_name_is_resolved():
    site = _one("""
verify = lambda data: Status.PASS
op = make(checker=verify)
""")
    assert site["resolved_through"] == "verify"
    assert site["classification"] == "CONSTANT_STATUS"


def test_a_bound_method_checker_is_resolved_to_its_definition():
    site = _one("""
class Runner:
    def _check(self, packet):
        return Status.PASS

    def build(self):
        return make(checker=self._check)
""")
    assert site["resolved_through"] == "self._check"
    assert site["classification"] == "CONSTANT_STATUS"


def test_a_name_bound_twice_is_left_unresolved_rather_than_guessed():
    site = _one("""
verify = lambda data: Status.PASS
verify = lambda data: Status.FAIL
op = make(checker=verify)
""")
    assert site["classification"] == "INDIRECT_UNRESOLVED"


# --- a string naming a checker is not a checker -----------------------------

def test_a_string_under_a_checker_key_is_not_counted_as_a_checker():
    """src/ocm/learning/methods.py records ``"checker": CHECKER`` where CHECKER is
    a domain name. Counting that as a checker would invent a population."""
    site = _one('record = {"checker": "rational-polynomial-coefficients.v1"}')
    assert site["classification"] == "NOT_A_CHECKER_CALLABLE"


def test_a_module_constant_under_a_checker_key_is_resolved_to_its_value():
    site = _one("""
CHECKER = "domain.v1"
record = {"checker": CHECKER}
""")
    assert site["classification"] == "NOT_A_CHECKER_CALLABLE"
    assert site["constant"] == "domain.v1"


def test_the_dataclass_field_itself_is_not_a_construction_site():
    site = _one("""
class OperatorSpec:
    checker = None
""")
    assert site["classification"] == "FIELD_DECLARATION"


# --- conservativity: these must NOT be called representable ------------------

HOSTILE = {
    "calls_out": "make(checker=lambda d: Status(check(d)['status']))",
    "reads_an_attribute": "make(checker=lambda d: d.value and Status.PASS)",
    "closes_over_a_free_name": "make(checker=lambda d: Status.PASS if FLAG else Status.FAIL)",
    "comprehension": "make(checker=lambda d: Status.PASS if all(x for x in d) else Status.FAIL)",
    "unbounded_path": "make(checker=lambda d: Status.PASS if d[k] == 1 else Status.FAIL)",
    "nested_lambda": "make(checker=lambda d: (lambda e: Status.PASS)(d))",
    "ordering_compare": "make(checker=lambda d: Status.PASS if d['n'] > 3 else Status.FAIL)",
}


@pytest.mark.parametrize("name", sorted(HOSTILE))
def test_the_classifier_never_calls_an_unrecognised_checker_representable(name):
    site = _one(HOSTILE[name])
    assert site["classification"] != "DSL_REPRESENTABLE", name
    assert site["classification"] != "CONSTANT_STATUS", name
    assert site["dsl"] is None, name


def test_an_ordering_comparison_is_an_extension_candidate_not_a_rejection():
    """`>` is pure and bounded and simply absent from the grammar. Separating
    'needs a bigger language' from 'cannot be certified' is the whole point of
    the census, so the two must not collapse into one bucket."""
    site = _one(HOSTILE["ordering_compare"])
    assert site["classification"] == "NEEDS_DSL_EXTENSION"


def test_a_checker_that_touches_the_host_is_not_representable():
    site = _one("make(checker=lambda d: Status.PASS if open('/etc/passwd') else Status.FAIL)")
    assert site["classification"] == "NOT_REPRESENTABLE"


# --- the conditional fragment is translated and means the same thing ---------

REPRESENTABLE = {
    "has": "make(checker=lambda d: Status.PASS if 'status' in d else Status.CANNOT_CHECK)",
    "eq": "make(checker=lambda d: Status.PASS if d['status'] == 'PASS' else Status.FAIL)",
    "type": "make(checker=lambda d: Status.PASS if isinstance(d['output'], dict) else Status.FAIL)",
    "not": "make(checker=lambda d: Status.FAIL if not ('status' in d) else Status.PASS)",
    "and": ("make(checker=lambda d: Status.PASS if ('status' in d) and "
            "(d['status'] == 'PASS') else Status.FAIL)"),
    "or": ("make(checker=lambda d: Status.PASS if ('status' in d) or "
           "('output' in d) else Status.CANNOT_CHECK)"),
    "nested_path": ("make(checker=lambda d: Status.PASS if d['output']['value'] == 0 "
                    "else Status.FAIL)"),
    "nested_if": ("make(checker=lambda d: (Status.PASS if d['status'] == 'PASS' "
                  "else Status.FAIL) if 'status' in d else Status.CANNOT_CHECK)"),
}


@pytest.mark.parametrize("name", sorted(REPRESENTABLE))
def test_each_grammar_construct_is_recognised_and_admitted(name):
    site = _one(REPRESENTABLE[name])
    assert site["classification"] == "DSL_REPRESENTABLE", (name, site["classification"])
    certificate = PCC.issue_certificate(site["dsl"])
    PCC.verify_certificate(certificate)


def _compiled(source: str):
    node = [n for n in ast.walk(ast.parse(source)) if isinstance(n, ast.Lambda)][0]
    return eval(compile(ast.Expression(body=node), "<t>", "eval"),  # noqa: S307
                {"__builtins__": {"isinstance": isinstance, "dict": dict, "list": list,
                                  "tuple": tuple, "str": str, "int": int, "float": float,
                                  "bool": bool}, "Status": SV.Status}, {})


@pytest.mark.parametrize("name", sorted(REPRESENTABLE))
def test_the_translation_returns_what_the_original_returns_where_it_is_defined(name):
    """Proposition 1, mechanically, over the whole candidate battery."""
    source = REPRESENTABLE[name]
    site = _one(source)
    certificate = PCC.issue_certificate(site["dsl"])
    original = _compiled(source)
    compared = more_defined = 0
    for candidate in C.DIFFERENTIAL_CANDIDATES:
        translated, _ = PCC.evaluate(certificate, candidate)
        try:
            produced = original(candidate)
        except Exception:                            # noqa: BLE001 - the interesting case
            more_defined += 1
            continue
        assert produced == translated, (name, candidate, produced, translated)
        compared += 1
    assert compared, name


def test_the_calculus_is_strictly_more_defined_and_that_is_counted_not_hidden():
    """``d['status'] == 'PASS'`` raises on a candidate with no ``status`` key; the
    translation returns FAIL. The census must count these rather than treat the
    original's exception as agreement."""
    source = REPRESENTABLE["eq"]
    site = _one(source)
    certificate = PCC.issue_certificate(site["dsl"])
    original = _compiled(source)
    raised = 0
    for candidate in C.DIFFERENTIAL_CANDIDATES:
        translated, _ = PCC.evaluate(certificate, candidate)
        try:
            original(candidate)
        except Exception:                            # noqa: BLE001
            raised += 1
            assert translated in (SV.Status.PASS, SV.Status.FAIL, SV.Status.CANNOT_CHECK)
    assert raised, "this fixture is supposed to exercise the more-defined case"


# --- the census over the real tree ------------------------------------------

@pytest.fixture(scope="module")
def real() -> dict:
    """The census over the real tree.

    In CI the census step runs first and publishes its receipt; these tests then
    assert against THAT artifact rather than recomputing a private one. It is
    cheaper, and it checks the thing that actually ships instead of a parallel
    computation that could drift from it.
    """
    published = os.environ.get("CHECKER_CENSUS_RECEIPT")
    if published and pathlib.Path(published).is_file():
        return json.loads(pathlib.Path(published).read_text())
    root = HERE.parent.parent
    if not (root / ".git").exists():
        pytest.skip("not a git checkout")
    return C.census(root)


def test_no_tracked_python_file_was_left_unparsed(real):
    """A syntax error would hide every site in that file, and a census whose zero
    rests on an unparsed file is not a zero."""
    assert real["population"]["python_files_unparsed"] == []
    assert real["population"]["python_files_parsed"] == \
        real["population"]["python_files_tracked"]


def test_the_population_is_the_tracked_tree_and_is_not_small(real):
    assert real["population"]["python_files_tracked"] > 1000
    assert real["sites_total"] > 0


def test_production_supplies_no_checker_callable(real):
    """TRIPWIRE. Today every ``src/`` site is either the dataclass field itself or
    a string naming a checker domain, so production constructs no checker and
    every checker reaching CHECK is host-supplied. If this fails, the population
    has changed and R0A_CHECKER_CENSUS_V1.md must be rewritten before anything is
    concluded from it."""
    allowed = {"FIELD_DECLARATION", "NOT_A_CHECKER_CALLABLE"}
    offenders = [(s["path"], s["line"], s["classification"])
                 for s in real["sites"]
                 if s["bucket"] == "PRODUCTION" and s["classification"] not in allowed]
    assert not offenders, offenders


def test_every_translated_site_was_admitted_by_the_certified_calculus(real):
    admission = real["dsl_admission"]
    assert admission["admission_failures"] == []
    assert admission["admitted_by_the_certified_calculus"] == admission["translated"]


def test_the_differential_check_found_no_disagreement(real):
    assert real["differential_check"]["disagreements"] == 0
    assert real["differential_check"]["failures"] == []


def test_the_census_declares_what_it_cannot_see(real):
    """An audited zero is only worth anything next to its blind spots."""
    assert len(real["what_this_census_cannot_see"]) >= 3
    assert real["site_shapes_searched"] == list(C.SITE_SHAPES)
