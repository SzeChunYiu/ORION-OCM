"""Source-bound engineering checks of the existing ORION-V2 -> OCM method contract.

This review tool never imports a proposal, grants adoption, or changes existing runtime state.
It runs only the fixed checks below after resolving pinned Git objects and checking
the working bytes. Its finite checks are not a proof of general semantic parity.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ANCHORS = {
    "theory": "b15abb41e1f9219ea793a15c5e641ac6579adb35",
    "runtime": "09f8c9527e2c385504b067035d1764e2860d6cc3",
}
THEORY_PREFIX = "research/machine-epistemics-theory/method_learning_v1/"
THEORY_FILES = {
    THEORY_PREFIX + "THEORY.md", THEORY_PREFIX + "check.py",
    "research/machine-epistemics-theory/ME_FOUNDATION_V1.md",
}
HEADINGS = {
    "M1": "M1: finite completeness and bounded convergence",
    "M2": "M2: examples, counterexamples and mathematical solutions",
    "M3": "M3: method learning and evidence lifecycle",
    "M4": "M4: convergence of experimental identification",
}
AUTHORITY = {
    "runtime_adoption": "NOT_GRANTED",
    "scientific_validation": "NOT_ESTABLISHED",
    "independent_semantic_parity": "NOT_ESTABLISHED",
    "novelty": "NOT_ESTABLISHED",
    "M11": "HISTORICAL_ADOPTION_CELLS_REOPENED",
    "M12": "PROTECTED_REEVALUATION_REQUIRED",
}


class CheckError(Exception):
    def __init__(self, status, reason):
        self.status, self.reason = status, reason
        super().__init__(reason)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def git(root, *args):
    try:
        result = subprocess.run(["git", "-C", str(root), *args], capture_output=True,
                                check=False, timeout=20)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise CheckError("CANNOT_CHECK", "Git object access unavailable") from exc
    if result.returncode:
        raise CheckError("CANNOT_CHECK", "Required Git object is unavailable")
    return result.stdout


def safe_path(root, relative):
    if (type(relative) is not str or not relative or "\\" in relative
            or PurePosixPath(relative).is_absolute()
            or any(p in {"", ".", ".."} for p in relative.split("/"))):
        raise CheckError("REJECTED", "Non-canonical file reference")
    path = root
    for part in relative.split("/"):
        path = path / part
        if path.is_symlink():
            raise CheckError("REVALIDATION_REQUIRED", "Symbolic source reference")
    return path


def section(text, heading):
    marker = "## " + heading + "\n"
    if text.count(marker) != 1:
        raise CheckError("REJECTED", "Source section is missing or ambiguous")
    return text.split(marker, 1)[1].split("\n## ", 1)[0].strip()


def expected_files(root, role):
    if role == "theory":
        return THEORY_FILES
    tracked = git(root, "ls-tree", "-r", "--name-only", ANCHORS[role]).decode().splitlines()
    return {p for p in tracked if p.startswith("src/")} | {"pyproject.toml"}


def verify_bindings(manifest, roots, revoked=()):
    """Verify an engineering packet; external source validity remains an assumption.

    Revocation IDs are host-provided row IDs. They affect this eligibility check,
    not the immutable historical packet. This is not an authenticated revocation service.
    """
    if (type(manifest) is not dict
            or set(manifest) != {"schema", "repositories", "rows", "authority"}
            or manifest["schema"] != "ocm.theory-runtime-engineering.v1"
            or manifest["authority"] != AUTHORITY):
        raise CheckError("REJECTED", "Unknown schema or changed authority boundary")
    if type(roots) is not dict or set(roots) != set(ANCHORS):
        raise CheckError("CANNOT_CHECK", "Both repository roots are required")
    repos = manifest["repositories"]
    if type(repos) is not dict or set(repos) != set(ANCHORS):
        raise CheckError("REJECTED", "Incomplete repository binding")
    contents = {}
    for role, anchor in ANCHORS.items():
        root, spec = Path(roots[role]).resolve(), repos[role]
        if (type(spec) is not dict or set(spec) != {"commit", "files"}
                or spec["commit"] != anchor or type(spec["files"]) is not dict):
            raise CheckError("REJECTED", "Repository anchor differs from reviewed identity")
        files = spec["files"]
        if set(files) != expected_files(root, role):
            raise CheckError("REJECTED", "Source file inventory is incomplete or extended")
        if role == "runtime":
            # Additional source files can alter imports even when old bytes are intact.
            present = set()
            for path in (root / "src").rglob("*"):
                rel = path.relative_to(root).as_posix()
                if "__pycache__" in path.parts or path.suffix in {".pyc", ".pyo"}:
                    continue
                if path.is_file() or path.is_symlink():
                    present.add(rel)
            if present != {p for p in files if p.startswith("src/")}:
                raise CheckError("REVALIDATION_REQUIRED", "Current runtime source inventory changed")
        contents[role] = {}
        for rel, binding in sorted(files.items()):
            path = safe_path(root, rel)
            if type(binding) is not dict or set(binding) != {"git_blob", "sha256"}:
                raise CheckError("REJECTED", "Malformed content binding")
            entry = git(root, "ls-tree", anchor, "--", rel).decode().strip().split()
            if len(entry) != 4 or entry[0] != "100644" or entry[1] != "blob":
                raise CheckError("REJECTED", "Expected a tracked regular source file")
            raw = git(root, "show", anchor + ":" + rel)
            if entry[2] != binding["git_blob"] or digest(raw) != binding["sha256"]:
                raise CheckError("REJECTED", "Packet differs from pinned Git source")
            try:
                current = path.read_bytes()
            except OSError as exc:
                raise CheckError("CANNOT_CHECK", "Required working source unavailable") from exc
            if current != raw:
                raise CheckError("REVALIDATION_REQUIRED", "Working source differs from pinned source")
            contents[role][rel] = raw
    rows = manifest["rows"]
    if (type(rows) is not list or len(rows) != len(HEADINGS)
            or any(type(r) is not dict for r in rows)
            or [r.get("id") for r in rows] != list(HEADINGS)):
        raise CheckError("REJECTED", "Obligation row set changed")
    theory = contents["theory"][THEORY_PREFIX + "THEORY.md"].decode()
    for row in rows:
        if (set(row) != {"id", "heading", "source_scope", "source_status", "parent_status",
                        "consumer_paths", "reopen_conditions"}
                or row["heading"] != HEADINGS[row["id"]]
                or row["source_scope"] != section(theory, row["heading"])
                or row["source_status"] != "PROVED_SCOPE_LIMITED"
                or row["parent_status"] != "PARENT_SUFFICIENT"
                or row["reopen_conditions"] != ["source_or_runtime_change", "source_revocation",
                                               "counterexample", "scope_or_assumption_change"]):
            raise CheckError("REJECTED", "Theorem scope, status or reopening contract changed")
        consumers = row["consumer_paths"]
        wanted = (["src/ocm/science/finite_identification.py"] if row["id"] == "M4"
                  else ["src/ocm/learning/methods.py"])
        if consumers != wanted:
            raise CheckError("REJECTED", "Consumer obligation mapping changed")
    if type(revoked) not in {tuple, list, frozenset, set} or any(type(x) is not str for x in revoked):
        raise CheckError("REJECTED", "Malformed host revocation set")
    if set(revoked) - set(HEADINGS):
        raise CheckError("CANNOT_CHECK", "Unknown revocation identity")
    if revoked:
        raise CheckError("REVALIDATION_REQUIRED", "Host revoked source support: " + ",".join(sorted(revoked)))
    return {"status": "SOURCE_BINDINGS_VERIFIED", "rows": list(HEADINGS),
            "source_files": {role: len(v) for role, v in contents.items()},
            "authority": dict(AUTHORITY)}


def require(condition, message):
    if not condition:
        raise CheckError("ENGINEERING_CHECK_FAILED", message)


def prepare_clean_sources(manifest, roots, destination):
    """Copy only checked source/data bytes into a new, empty import tree.

    Ordinary imports may read an existing bytecode cache even with Python -B.
    A private new tree avoids attributing such code to verified source bytes.
    The host's Python interpreter and standard library remain trusted inputs.
    """
    clean = {}
    for role, spec in manifest["repositories"].items():
        target = destination / role
        target.mkdir()  # Refuse a pre-existing tree, including caches.
        clean[role] = target
        for rel, binding in spec["files"].items():
            try:
                data = safe_path(Path(roots[role]), rel).read_bytes()
            except OSError as exc:
                raise CheckError("CANNOT_CHECK", "Source unavailable during isolated copy") from exc
            require(digest(data) == binding["sha256"], "Source changed before isolated execution")
            copied = safe_path(target, rel)
            copied.parent.mkdir(parents=True, exist_ok=True)
            with copied.open("xb") as stream:
                stream.write(data)
    return clean


def finite_checks(roots):
    from fractions import Fraction
    from itertools import combinations, product

    # Fresh standalone execution prevents testing an installed package from another checkout.
    if any(n == "ocm" or n.startswith("ocm.") for n in sys.modules):
        raise CheckError("CANNOT_CHECK", "Use a fresh process for runtime binding")
    sys.path.insert(0, str(Path(roots["runtime"]).resolve() / "src"))
    from ocm.learning import methods as M
    from ocm.science.finite_identification import ModelClass, Observation, ExperimentLearner
    from ocm.evaluation.method_learning_eval import evaluate

    source_path = Path(roots["theory"]) / (THEORY_PREFIX + "check.py")
    spec = importlib.util.spec_from_file_location("bound_v2_method_check", source_path)
    source = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(source)
    source_result = source.check()
    require(source_result["status"] == "FINITE_CALIBRATION_PASS", "V2 reference check failed")

    programs = tuple(p for n in range(4) for p in product(M.PRIMITIVES, repeat=n))
    samples = tuple(Fraction(x, 2) for x in range(-3, 4))
    for program in programs:
        for x in samples:
            require(M.execute(program, x) == M.evaluate_polynomial(M.normal_form(program), x),
                    "Numeric and polynomial semantics differ")
    targets = sorted({M.normal_form(p) for p in programs})
    for i, coefficients in enumerate(targets):
        task = M.PolynomialTask(str(i), coefficients)
        baseline = M.solve(task, M.SearchBudget(200, 3))
        guided = M.solve(task, M.SearchBudget(200, 3), M.GeneratorMethod((("inc", "square"),)))
        require(M.verify_solution(task, baseline) and M.verify_solution(task, guided),
                "Declared finite grammar solution lost")
        require(guided.slots <= 2 * baseline.slots, "Primitive fallback search-slot bound violated")
    # A candidate matching x=0,1 is not a polynomial identity: x differs from x^2.
    require(all(M.execute((), x) == M.execute(("square",), x) for x in (0, 1)),
            "Sample-only counterexample control was not constructed")
    require(M.normal_form(()) != M.normal_form(("square",)), "Samples became a proof")
    identity = M.PolynomialTask("sample-fitting-wrong-candidate", (0, 1))
    wrong = M.SearchResult(identity.fingerprint, M.GeneratorMethod().fingerprint,
                           "VERIFIED_POLYNOMIAL_IDENTITY", ("square",), 1, 1, (0, 1), 1)
    require(not M.verify_solution(identity, wrong), "Actual verifier accepted sample-only evidence")
    require(M.solve(M.PolynomialTask("budget", (1,)), M.SearchBudget(0, 3)).status == "BUDGET_EXHAUSTED",
            "Empty search budget became success")

    cases = revisions = 0
    universe = tuple(product((0, 1), repeat=3))
    for size in range(1, 5):
        for hypotheses in combinations(universe, size):
            model = ModelClass(("q0", "q1", "q2"), tuple(
                (str(i), tuple(map(str, row))) for i, row in enumerate(hypotheses)))
            for truth_index, truth in enumerate(hypotheses):
                learner, history, version = ExperimentLearner(model), [], hypotheses
                while len(version) > 1:
                    before = learner.assess()
                    q = source.choose_query(version)
                    require(before["next_query"] == f"q{q}", "Theory/runtime experiment selection differs")
                    eid = f"simulated:{len(history)}"
                    learner.observe(Observation(eid, f"q{q}", str(truth[q]), "SIMULATED", model.fingerprint))
                    history.append((eid, q, truth[q]))
                    version = tuple(row for row in version if row[q] == truth[q])
                    expected = tuple(str(i) for i, row in enumerate(hypotheses) if row in version)
                    require(learner.assess()["survivors"] == expected, "Compatible model set differs")
                require(learner.assess()["survivors"] == (str(truth_index),)
                        and len(history) <= size - 1, "Finite identification bound violated")
                for revoked, _, _ in history:
                    expected = tuple(str(i) for i, row in enumerate(hypotheses)
                                     if all(row[q] == answer for eid, q, answer in history if eid != revoked))
                    require(learner.assess((revoked,))["survivors"] == expected,
                            "Revoked observation still constrains model set")
                    revisions += 1
                cases += 1
    with tempfile.TemporaryDirectory(prefix="ocm-bound-method-") as directory:
        learned = evaluate(Path(directory))
    require(learned["validation"]["accepted"] is True
            and learned["revocation"] == "REUSE_REFUSED_AFTER_RESTART", "Persistent generator lifecycle differs")
    return {"theory_calibration": source_result,
            "M1": {"distinct_targets": len(targets), "maximum_program_length": 3, "slot_bound_holds": True},
            "M2": {"programs": len(programs), "numeric_comparisons": len(programs) * len(samples),
                   "sample_only_identity_refused": True},
            "M3": {"learned_fragments": learned["learned_fragments"],
                   "held_out": learned["validation"]["held_out"], "revocation": learned["revocation"]},
            "M4": {"identification_cases": cases, "single_observation_revocations": revisions},
            "limits": "Finite engineering checks; shared premises are not independently validated; no protected study."}


def package_inventory():
    return {name: digest((HERE / name).read_bytes())
            for name in ("check.py", "test_bindings.py", "MANIFEST_V1.json", "README.md")}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--theory", type=Path, required=True)
    parser.add_argument("--runtime", type=Path, default=HERE.parents[1])
    parser.add_argument("--out", type=Path)
    parser.add_argument("--revoke-row", action="append", default=[])
    args = parser.parse_args(argv)
    roots = {"theory": args.theory, "runtime": args.runtime}
    try:
        package_before = package_inventory()
        manifest = json.loads((HERE / "MANIFEST_V1.json").read_text())
        bindings = verify_bindings(manifest, roots, args.revoke_row)
        with tempfile.TemporaryDirectory(prefix="ocm-bound-source-") as directory:
            clean = prepare_clean_sources(manifest, roots, Path(directory))
            checks = finite_checks(clean)
        require(verify_bindings(manifest, roots) == bindings, "Source changed during verification")
        require(package_inventory() == package_before, "Integration checker changed during verification")
        result = {"schema": "ocm.theory-runtime-replay.v1",
                  "status": "ENGINEERING_CHECKS_PASS__SCOPED_INTEGRATION_ONLY",
                  "anchors": ANCHORS, "bindings": bindings, "checks": checks,
                  "package_inventory": package_before, "python": sys.version,
                  "authority": dict(AUTHORITY)}
        code = 0
    except CheckError as exc:
        result = {"status": exc.status, "reason": exc.reason, "authority": dict(AUTHORITY)}
        code = 2 if exc.status in {"CANNOT_CHECK", "REVALIDATION_REQUIRED"} else 1
    output = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        # Never replace a historical run or silently rewrite a prior receipt.
        with args.out.open("x") as destination:
            destination.write(output)
    else:
        print(output, end="")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
