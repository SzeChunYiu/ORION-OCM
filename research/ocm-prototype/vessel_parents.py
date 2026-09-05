"""Independently executed direct donors; finite catalogue build is charged."""
from fractions import Fraction
from itertools import product
import time

from ocm.language.interpret import interpret, Verdict
from ocm.language.meaning import canonical
from ocm.learning import methods as M
from ocm.runtime.ocm_runtime import OCMRuntime
from vessel_state import encode, restore_language
from vessel_ops import polynomial_check
from ocm.runtime.solve import Status


def run(root, language_request, polynomial_request):
    wall, cpu = time.perf_counter(), time.process_time()
    runtime = OCMRuntime(root)
    lexicon, constructions = restore_language(runtime.state.ks)
    language_start = time.perf_counter()
    language = interpret(language_request["utterance"], lexicon, constructions, revoked=runtime.state.revoked)
    language_elapsed = time.perf_counter() - language_start
    # Build without access to any test target: every program in lengths 0..4.
    build_wall, build_cpu = time.perf_counter(), time.process_time()
    catalogue, enumerated = {}, 0
    for length in range(5):
        for program in product(M.PRIMITIVES, repeat=length):
            enumerated += 1
            coefficients = M.PolynomialTask("catalogue", M.normal_form(program)).coefficients
            catalogue.setdefault(coefficients, program)
    build_seconds, build_cpu_seconds = time.perf_counter() - build_wall, time.process_time() - build_cpu
    catalogue_bytes = len(encode([[list(map(str, k)), v] for k, v in catalogue.items()]).encode())
    lookup_start = time.perf_counter()
    task = M.PolynomialTask("parent-query", tuple(Fraction(c) for c in polynomial_request["coefficients"]))
    program = catalogue.get(task.coefficients)
    proposal = {"status": "VERIFIED_POLYNOMIAL_IDENTITY" if program is not None else "EXHAUSTED_DECLARED_GRAMMAR",
                "program": program, "task_fingerprint": task.fingerprint}
    checked = polynomial_check(runtime.state.ks, polynomial_request, proposal, runtime.state.revoked)
    return {"independently_executed": True, "shared_solver_invoked": False,
        "language": {"verdict": language.verdict.value,
            "digest": canonical(language.meaning)[1] if language.verdict is Verdict.INTERPRETED else None,
            "wall_seconds": language_elapsed},
        "polynomial": {"program": program, "checked": checked is Status.PASS,
            "enumerated_programs": enumerated, "max_length": 4, "distinct_polynomials": len(catalogue),
            "catalogue_bytes": catalogue_bytes, "build_wall_seconds": build_seconds,
            "build_cpu_seconds": build_cpu_seconds, "lookup_and_check_seconds": time.perf_counter() - lookup_start},
        "wall_seconds": time.perf_counter() - wall, "cpu_seconds": time.process_time() - cpu,
        "scope": "Independently executed direct donor control using the same restored acquired language field; not independent acquisition, lifecycle or strong-LLM comparison"}
