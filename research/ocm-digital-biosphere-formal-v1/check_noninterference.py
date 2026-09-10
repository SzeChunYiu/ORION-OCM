#!/usr/bin/env python3
"""BIO-NI-1 -- protected-assay noninterference over the kernel factorization.

Section 3 of issue #296 states the obligation as

    protected assay state NOT IN ancestors_of(birth/death/resource-transition)

This module turns that sentence into a decidable predicate over the DECLARED
kernel factorization, because a failure here invalidates every spontaneous- or
general-cognition claim for the run, and prose is not checkable.

Why `reads` is load-bearing
---------------------------
Ancestry is a reachability property over BOTH halves of the edge relation.
WORLD_STATE_AND_DYNAMICS_V1 declared only `writes`. With no incoming edges the
ancestor set of any sink collapses to the sink itself, so the predicate would
have returned PASS for every world, including a leaking one. That is a VACUOUS
PASS, not a false negative -- the instrument could not fail. AMEND_1 supplies
the reads sets; this checker consumes them.

Exit codes are DISTINCT on purpose. "Could not check" must never be reported as
"checked and fine":

    0 PASS          closure of the sinks is disjoint from the protected names
    2 VIOLATION     a directed path exists; the witness path is emitted
    3 CANNOT_CHECK  a kernel omitted reads or writes, or a name is unresolvable
    4 USAGE         bad invocation

Both directions are asserted before any verdict is trusted -- see selftest().
A gate only ever seen not firing has not been validated. The pattern is taken
from research/ocm-form-oracle-v1/oracle/c_immutability.py selftest().
"""
from __future__ import annotations

import json
import os
import sys
from typing import Dict, Iterable, List, Mapping, Sequence, Set, Tuple

PASS = "PASS"
VIOLATION = "VIOLATION"
CANNOT_CHECK = "CANNOT_CHECK"

EXIT = {PASS: 0, VIOLATION: 2, CANNOT_CHECK: 3}

HERE = os.path.dirname(os.path.abspath(__file__))


class NIResult(dict):
    """Verdict plus its evidence. dict so it serialises straight to JSON."""

    @property
    def verdict(self) -> str:
        return self["verdict"]

    @property
    def exit_code(self) -> int:
        return EXIT[self["verdict"]]


def _covers(declared: str, target: str) -> bool:
    """Does a declared name cover a target name?

    Exact match, or dotted-prefix containment so that a kernel declaring it
    reads the whole organism record `x` is treated as reading `x.a` too.
    Coarse declarations are ALWAYS the more permissive reading. Treating
    reads=['x'] as not covering 'x.a' would let a coarse declaration launder a
    fine-grained read, which is precisely the leak this gate exists to catch.
    """
    if declared == target:
        return True
    if target.startswith(declared + "."):
        return True
    if declared.startswith(target + "."):
        return True
    return False


def _resolve(names: Iterable[str], universe: Set[str]) -> Set[str]:
    out: Set[str] = set()
    for n in names:
        for u in universe:
            if _covers(n, u):
                out.add(u)
    return out


def build_graph(kernels: Mapping[str, Mapping[str, Sequence[str]]]
                ) -> Tuple[Dict[str, Set[str]], Set[str], List[str]]:
    """Return (parents, state_names, problems).

    `parents[node]` is the set of nodes with an edge INTO node, so ancestor
    closure is a plain BFS over `parents`.

    Edges:  r -> k  for every r in reads(k)
            k -> w  for every w in writes(k)
    """
    problems: List[str] = []
    state_names: Set[str] = set()
    for kname, decl in kernels.items():
        if not isinstance(decl, Mapping):
            problems.append("kernel %s: declaration is not a mapping" % kname)
            continue
        for field in ("reads", "writes"):
            if field not in decl or decl[field] is None:
                problems.append("kernel %s: no %s declared" % (kname, field))
            elif not isinstance(decl[field], (list, tuple)):
                problems.append("kernel %s: %s is not a list" % (kname, field))
            else:
                state_names.update(str(x) for x in decl[field])

    parents: Dict[str, Set[str]] = {}
    for kname, decl in kernels.items():
        if not isinstance(decl, Mapping):
            continue
        reads = decl.get("reads") or []
        writes = decl.get("writes") or []
        knode = "kernel:" + kname
        parents.setdefault(knode, set())
        for r in reads:
            for u in _resolve([str(r)], state_names):
                parents.setdefault(u, set())
                parents[knode].add(u)
        for w in writes:
            for u in _resolve([str(w)], state_names):
                parents.setdefault(u, set()).add(knode)
    return parents, state_names, problems


def ancestors_of(parents: Mapping[str, Set[str]], seeds: Iterable[str]
                 ) -> Tuple[Set[str], Dict[str, str]]:
    """Reflexive-transitive closure over reversed edges. Returns (set, came_from)."""
    seen: Set[str] = set()
    came_from: Dict[str, str] = {}
    stack = list(seeds)
    for s in stack:
        seen.add(s)
    while stack:
        node = stack.pop()
        for p in parents.get(node, ()):
            if p not in seen:
                seen.add(p)
                came_from[p] = node
                stack.append(p)
    return seen, came_from


def _path(came_from: Mapping[str, str], start: str) -> List[str]:
    path = [start]
    cur = start
    guard = 0
    while cur in came_from and guard < 10000:
        cur = came_from[cur]
        path.append(cur)
        guard += 1
    return path


def check_noninterference(kernels: Mapping[str, Mapping[str, Sequence[str]]],
                          protected: Iterable[str],
                          sinks: Iterable[str]) -> NIResult:
    """Execute BIO-NI-1. See NONINTERFERENCE_CHECK_SPEC_V1.json."""
    parents, universe, problems = build_graph(kernels)
    if problems:
        return NIResult(verdict=CANNOT_CHECK, reason="; ".join(sorted(problems)),
                        witness_path=None, checked_kernels=0)

    sink_nodes = _resolve([str(s) for s in sinks], universe)
    if not sink_nodes:
        return NIResult(verdict=CANNOT_CHECK,
                        reason="no declared sink resolves against the state vocabulary: %s"
                               % sorted(str(s) for s in sinks),
                        witness_path=None, checked_kernels=len(kernels))

    protected_nodes = _resolve([str(p) for p in protected], universe)
    if not protected_nodes:
        return NIResult(verdict=CANNOT_CHECK,
                        reason="no protected name resolves against the state vocabulary; "
                               "a PASS over an empty protected set is vacuous",
                        witness_path=None, checked_kernels=len(kernels))

    closure, came_from = ancestors_of(parents, sink_nodes)
    hits = sorted(protected_nodes & closure)
    if hits:
        return NIResult(verdict=VIOLATION,
                        reason="protected state reaches a selection sink: %s" % ", ".join(hits),
                        witness_path=_path(came_from, hits[0]),
                        checked_kernels=len(kernels))
    return NIResult(verdict=PASS, reason="", witness_path=None,
                    checked_kernels=len(kernels))


# --------------------------------------------------------------------------
# Declaration loading
# --------------------------------------------------------------------------

def load_declaration(dirpath: str = HERE) -> Tuple[Dict, List[str], List[str]]:
    """Assemble kernels/protected/sinks from the frozen artifacts."""
    amend = json.load(open(os.path.join(dirpath, "WORLD_STATE_AND_DYNAMICS_V1_AMEND_1.json")))
    base = json.load(open(os.path.join(dirpath, "WORLD_STATE_AND_DYNAMICS_V1.json")))
    reads = amend["kernel_reads"]
    base_kernels = base.get("kernels") or {}
    kernels: Dict[str, Dict[str, List[str]]] = {}
    for kname, kdecl in base_kernels.items():
        entry = {"writes": list(kdecl.get("writes") or [])}
        if kname in reads:
            entry["reads"] = list(reads[kname]["reads"])
        kernels[kname] = entry
    # The assay machinery is observer-side and NOT part of the primary law P,
    # but it must be a node-bearing kernel: it is what WRITES the protected
    # names. Without it those names are absent from the state vocabulary and
    # the closure is vacuous. See AMEND_1 observer_side_kernels.
    obs = (amend.get("observer_side_kernels") or {}).get("K_assay")
    if obs:
        kernels["K_assay"] = {"reads": list(obs["reads"]), "writes": list(obs["writes"])}
    protected = list(amend["protected_names_must_not_appear_in_any_reads_closure"])
    sinks = ["mu", "H.lineage"] + list(amend["resource_transition_sinks"]["names"])
    return kernels, protected, sinks


# --------------------------------------------------------------------------
# Selftest -- BOTH directions, before any verdict is trusted
# --------------------------------------------------------------------------

def selftest(dirpath: str = HERE) -> Dict[str, object]:
    """Validate the gate on the real declaration BEFORE trusting any verdict.

    Asserts the no-alarm case as well as four alarm cases. A checker that has
    only ever been seen not firing has not been validated, and a checker that
    cries wolf on its first real run gets switched off.
    """
    kernels, protected, sinks = load_declaration(dirpath)
    cases: Dict[str, object] = {}

    # 1. no-alarm: the clean declared factorization must PASS.
    clean = check_noninterference(kernels, protected, sinks)
    assert clean.verdict == PASS, ("no-alarm case failed: clean declaration "
                                   "returned %s (%s)" % (clean.verdict, clean["reason"]))
    cases["no_alarm_clean"] = clean.verdict

    # 2. alarm, direct: birth/death reads the assay field.
    direct = {k: {"reads": list(v.get("reads", [])), "writes": list(v["writes"])}
              for k, v in kernels.items()}
    direct["K_birthdeath"]["reads"].append("x.a")
    r = check_noninterference(direct, protected, sinks)
    assert r.verdict == VIOLATION, "direct-leak case did not fire: %s" % r.verdict
    assert r["witness_path"], "VIOLATION emitted no witness path"
    cases["alarm_direct"] = r.verdict

    # 3. alarm, indirect: assay moves energy, energy moves reproduction.
    #    This is the H-LEAK-ASSAY-ENERGY hostile.
    indirect = {k: {"reads": list(v.get("reads", [])), "writes": list(v["writes"])}
                for k, v in kernels.items()}
    indirect["K_senseact"]["reads"].append("x.a")
    r = check_noninterference(indirect, protected, sinks)
    assert r.verdict == VIOLATION, "indirect-leak case did not fire: %s" % r.verdict
    cases["alarm_indirect"] = r.verdict

    # 4. alarm, prefix laundering: a coarse read of the whole record.
    coarse = {k: {"reads": list(v.get("reads", [])), "writes": list(v["writes"])}
              for k, v in kernels.items()}
    coarse["K_birthdeath"]["reads"].append("x")
    r = check_noninterference(coarse, protected, sinks)
    assert r.verdict == VIOLATION, "prefix-laundering case did not fire: %s" % r.verdict
    cases["alarm_prefix"] = r.verdict

    # 4b. alarm, MULTI-HOP: x.a -> K_learn -> x.F -> K_senseact -> x.r.
    #     Proves the closure is genuinely transitive and not a one-step
    #     membership test. K_learn writes no sink itself, so a one-step
    #     checker would return PASS here and miss a real leak.
    multihop = {k: {"reads": list(v.get("reads", [])), "writes": list(v["writes"])}
                for k, v in kernels.items()}
    multihop["K_learn"]["reads"].append("x.a")
    r = check_noninterference(multihop, protected, sinks)
    assert r.verdict == VIOLATION, "multi-hop leak case did not fire: %s" % r.verdict
    assert len(r["witness_path"]) >= 4, ("multi-hop witness too short (%s); the closure "
                                         "is not traversing" % r["witness_path"])
    cases["alarm_multihop"] = r.verdict
    cases["alarm_multihop_witness"] = r["witness_path"]

    # 4c. no-alarm DISCRIMINATOR: a protected name written by K_assay and read
    #     by nothing must stay silent even though it is present in the graph.
    #     Without this the PASS above could just mean "resolution is broken".
    quiet = {k: {"reads": list(v.get("reads", [])), "writes": list(v["writes"])}
             for k, v in kernels.items()}
    quiet["K_assay"]["writes"].append("assay_scratch")
    r = check_noninterference(quiet, list(protected) + ["assay_scratch"], sinks)
    assert r.verdict == PASS, ("no-alarm discriminator fired on an unread protected "
                               "name: %s (%s)" % (r.verdict, r["reason"]))
    cases["no_alarm_unread_protected"] = r.verdict

    # 5. cannot-check: an incomplete declaration is NOT a pass.
    #    This is the H-LEAK-HIDDEN-EDGE hostile.
    incomplete = {k: dict(v) for k, v in kernels.items()}
    incomplete["K_social"] = {"writes": list(kernels["K_social"]["writes"])}
    r = check_noninterference(incomplete, protected, sinks)
    assert r.verdict == CANNOT_CHECK, "incomplete declaration returned %s" % r.verdict
    cases["cannot_check_incomplete"] = r.verdict

    # 6. cannot-check: an empty protected set must not pass vacuously.
    r = check_noninterference(kernels, [], sinks)
    assert r.verdict == CANNOT_CHECK, "empty protected set returned %s" % r.verdict
    cases["cannot_check_empty_protected"] = r.verdict

    return {"BIO_NI_1_SELFTEST": "OK", "cases": cases,
            "n_kernels": len(kernels), "n_protected": len(protected), "sinks": sinks}


def main(argv: Sequence[str]) -> int:
    if len(argv) > 2:
        print("usage: check_noninterference.py [--selftest]", file=sys.stderr)
        return 4
    if len(argv) == 2 and argv[1] == "--selftest":
        print(json.dumps(selftest(), indent=1, sort_keys=True))
        return 0
    if len(argv) == 2:
        print("usage: check_noninterference.py [--selftest]", file=sys.stderr)
        return 4
    selftest()                      # never trust a verdict from an unvalidated gate
    kernels, protected, sinks = load_declaration()
    res = check_noninterference(kernels, protected, sinks)
    print(json.dumps(res, indent=1, sort_keys=True))
    return res.exit_code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
