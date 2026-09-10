#!/usr/bin/env python3
"""Independent STRIPS plan validator (P1_PIPELINE_FREEZE_V1.json).

Validates a candidate plan against a PDDL domain theory + instance facts ONLY,
per the public PDDL STRIPS semantics (types, positive preconditions,
delete/add effects, goal test). It is the frozen independent oracle of the
policy table: it imports NOTHING from the mechanism (src/ocm), nothing from
the family emitters -- Python stdlib only (re, sys). p1_selftest.py enforces
this by scanning this file's imports.

Exit codes (distinct on purpose -- "could not check" is never "checked"):
  0  VALID        every step's preconditions hold, all effects applied,
                  goal reached after the final step
  1  INVALID      plan is well-formed but wrong: unknown action, arity/type
                  mismatch, violated precondition, or goal not reached
  3  CANNOT_CHECK domain/problem/plan unparseable or uses an unsupported
                  feature (with reason on stdout)

Supported PDDL subset: (define (domain ...)) with :requirements (only :strips
:typing), :types (single-inheritance), :constants, :predicates, :action with
:parameters/:precondition (positive literals, `and`)/:effect (literals and
`(not lit)`, `and`); problems with (:domain ..) (:objects ..) (:init ..)
(:goal (and ..)); plans as one grounded action call per line.  Anything else
(ADL, :derived, :durative-actions, negative/quantified/disjunctive
preconditions, conditional effects) is refused with CANNOT_CHECK.
"""
import re
import sys

VALID, INVALID, CANNOT_CHECK = 0, 1, 3
ROOT_TYPE = "object"
ALLOWED_REQUIREMENTS = {":strips", ":typing"}
UNSUPPORTED_REQUIREMENTS = {
    ":adl", ":derived-predicates", ":durative-actions", ":time",
    ":universal-preconditions", ":existential-preconditions",
    ":quantified-preconditions", ":disjunctive-preconditions",
    ":negative-preconditions", ":conditional-effects", ":action-costs",
    ":numeric-fluents", ":object-fluents", ":constraints", ":preferences",
    ":safety", ":htn",
}


class CannotCheck(Exception):
    """The inputs cannot be checked under the supported semantics."""


def tokenize(text):
    """PDDL tokenizer: ;-comments to EOL, parens/symbols."""
    text = re.sub(r";[^\n]*", "", text)
    tokens, cur = [], []
    for ch in text:
        if ch in "()":
            if cur:
                tokens.append("".join(cur))
                cur = []
            tokens.append(ch)
        elif ch.isspace():
            if cur:
                tokens.append("".join(cur))
                cur = []
        else:
            cur.append(ch)
    if cur:
        tokens.append("".join(cur))
    return tokens


def parse_exprs(text, what):
    """Parse all top-level s-expressions; refuse trailing garbage."""
    tokens = tokenize(text)
    pos, out = 0, []

    def read(k):
        nonlocal pos
        tok = tokens[k]
        if tok == "(":
            k += 1
            lst = []
            while k < len(tokens) and tokens[k] != ")":
                lst.append(read(k))
                k = pos
            if k >= len(tokens):
                raise CannotCheck(f"unbalanced parentheses in {what}")
            pos = k + 1
            return lst
        if tok == ")":
            raise CannotCheck(f"unexpected ) in {what}")
        pos = k + 1
        return tok

    while pos < len(tokens):
        out.append(read(pos))
        pos = pos
    if not out or not isinstance(out[0], list):
        raise CannotCheck(f"{what}: no s-expression found")
    return out


def parse_typed(names, what, where):
    """Split a `?v - t ?w - u`-style token list into [(name, type), ...].

    Supertype names are NOT validated here: PDDL :types declares supertypes
    after first use (logistics does), so membership is checked once the whole
    section is parsed.
    """
    pairs, buf, i = [], [], 0
    while i < len(names):
        if names[i] == "-":
            if not buf or i + 1 >= len(names):
                raise CannotCheck(f"{where}: malformed typed list in {what}")
            pairs.extend((n, names[i + 1]) for n in buf)
            buf, i = [], i + 2
        else:
            buf.append(names[i])
            i += 1
    if buf:  # untyped names inherit the root type
        pairs.extend((n, ROOT_TYPE) for n in buf)
    return pairs


def literal(expr, types, where, allow_not):
    """One ground-or-lifted atom, or (not atom) when allow_not -> (neg, atom)."""
    neg = False
    if isinstance(expr, list) and expr and expr[0] == "not":
        if not allow_not or len(expr) != 2 or not isinstance(expr[1], list):
            raise CannotCheck(f"{where}: unsupported negation {expr}")
        expr, neg = expr[1], True
    if not isinstance(expr, list) or not expr:
        raise CannotCheck(f"{where}: bad literal {expr}")
    pred, args = expr[0], [a for a in expr[1:]]
    for a in args:
        if isinstance(a, list):
            raise CannotCheck(f"{where}: nested/functional term {expr}")
    return neg, (pred, tuple(args))


def body(exprs, where):
    """(and a b) / single a -> [atoms]; refuse everything else."""
    if len(exprs) == 1:
        exprs = exprs[0]
        if isinstance(exprs, list) and exprs and exprs[0] == "and":
            exprs = exprs[1:]
        elif exprs == "and":
            exprs = []
        else:
            exprs = [exprs]
    out = []
    for e in exprs:
        neg, atom = literal(e, None, where, allow_not=False)
        if neg:
            raise CannotCheck(f"{where}: negative precondition {e}")
        out.append(atom)
    return out


class Domain:
    def __init__(self, text):
        top = parse_exprs(text, "domain")
        if top[0][0] != "define" or len(top[0]) < 2 or top[0][1][0] != "domain":
            raise CannotCheck("domain: not a (define (domain ..))")
        self.name = top[0][1][1]
        self.types, self.constants, self.predicates = {ROOT_TYPE: None}, {}, {}
        self.actions = {}
        for sec in top[0][2:]:
            if not (isinstance(sec, list) and sec):
                raise CannotCheck(f"domain {self.name}: bad section {sec}")
            key = sec[0]
            if key == ":requirements":
                bad = [r for r in sec[1:] if isinstance(r, str) and
                       r not in ALLOWED_REQUIREMENTS]
                if bad:
                    raise CannotCheck(f"domain {self.name}: unsupported requirements {bad}")
            elif key == ":types":
                for n, t in parse_typed(sec[1:], ":types", f"domain {self.name}"):
                    self.types[n] = t
            elif key == ":constants":
                for n, t in parse_typed(sec[1:], ":constants", f"domain {self.name}"):
                    self.constants[n] = t
            elif key == ":predicates":
                self._parse_predicates(sec[1:])
            elif key == ":action":
                self._parse_action(sec)
            else:
                raise CannotCheck(f"domain {self.name}: unsupported section {key}")
        for t, sup in self.types.items():
            if sup is not None and sup not in self.types:
                raise CannotCheck(f"domain {self.name}: type {t} has unknown supertype {sup}")
        for n, t in self.constants.items():
            if t not in self.types:
                raise CannotCheck(f"domain {self.name}: constant {n} has unknown type {t}")

    def _parse_predicates(self, decls):
        for d in decls:
            if not (isinstance(d, list) and len(d) >= 1):
                raise CannotCheck(f"domain {self.name}: bad predicate {d}")
            name = d[0]
            params = parse_typed(d[1:], "predicate", f"domain {self.name} predicate {name}")
            self.predicates[name] = [t for _, t in params]
        for name, ts in self.predicates.items():
            for t in ts:
                if t not in self.types:
                    raise CannotCheck(f"domain {self.name}: predicate {name} uses unknown type {t}")

    def _parse_action(self, sec):
        if len(sec) < 2 or not isinstance(sec[1], str):
            raise CannotCheck(f"domain {self.name}: bad :action {sec}")
        name = sec[1]
        if name in self.actions:
            raise CannotCheck(f"domain {self.name}: duplicate action {name}")
        act = {"params": {}, "pre": [], "del": [], "add": []}
        seen, i = set(), 2
        while i < len(sec):
            k = sec[i]
            if k not in (":parameters", ":precondition", ":effect") or i + 1 >= len(sec):
                raise CannotCheck(f"domain {self.name}: action {name}: bad field {k}")
            if k in seen:
                raise CannotCheck(f"domain {self.name}: action {name}: repeated {k}")
            seen.add(k)
            val = sec[i + 1]
            if k == ":parameters":
                if not isinstance(val, list):
                    raise CannotCheck(f"domain {self.name}: action {name}: bad :parameters")
                for v, t in parse_typed(val, ":parameters", f"domain {self.name} action {name}"):
                    if not v.startswith("?"):
                        raise CannotCheck(f"domain {self.name}: action {name}: parameter {v} lacks ?")
                    if t not in self.types:
                        raise CannotCheck(f"domain {self.name}: action {name}: unknown type {t}")
                    act["params"][v] = t
            elif k == ":precondition":
                act["pre"] = body([val], f"domain {self.name} action {name} precondition")
            else:
                act["del"], act["add"] = self._parse_effect(val, name)
            i += 2
        self._check_atoms(name, act)
        self.actions[name] = act

    def _parse_effect(self, val, name):
        exprs = val[1:] if (isinstance(val, list) and val and val[0] == "and") else [val]
        dels, adds = [], []
        for e in exprs:
            neg, atom = literal(e, None, f"domain {self.name} action {name} effect", allow_not=True)
            (dels if neg else adds).append(atom)
        return dels, adds

    def _check_atoms(self, name, act):
        pvars = act["params"]
        for where, atoms in (("precondition", act["pre"]),
                             ("delete effect", act["del"]), ("add effect", act["add"])):
            for pred, args in atoms:
                if pred not in self.predicates:
                    raise CannotCheck(
                        f"domain {self.name}: action {name} {where} uses undeclared predicate {pred}")
                if len(args) != len(self.predicates[pred]):
                    raise CannotCheck(
                        f"domain {self.name}: action {name} {where}: predicate {pred} arity mismatch")
                for a, t in zip(args, self.predicates[pred]):
                    if a.startswith("?") and a not in pvars:
                        raise CannotCheck(
                            f"domain {self.name}: action {name} {where}: unbound variable {a}")
                    if not a.startswith("?") and a not in self.constants:
                        raise CannotCheck(
                            f"domain {self.name}: action {name} {where}: unknown constant {a}")
                    elif not a.startswith("?") and not self._is_subtype(self.constants[a], t):
                        raise CannotCheck(
                            f"domain {self.name}: action {name} {where}: constant {a} of type "
                            f"{self.constants[a]} is not of required type {t}")

    def _is_subtype(self, t, u):
        while t is not None:
            if t == u:
                return True
            t = self.types.get(t)
        return False


class Problem:
    def __init__(self, text, domain):
        top = parse_exprs(text, "problem")
        if top[0][0] != "define" or len(top[0]) < 2 or top[0][1][0] != "problem":
            raise CannotCheck("problem: not a (define (problem ..))")
        self.name = top[0][1][1]
        self.objects, self.init, self.goal = dict(domain.constants), set(), []
        for sec in top[0][2:]:
            if not (isinstance(sec, list) and sec):
                raise CannotCheck(f"problem {self.name}: bad section {sec}")
            key = sec[0]
            if key == ":domain":
                if len(sec) != 2 or sec[1] != domain.name:
                    raise CannotCheck(
                        f"problem {self.name}: :domain {sec[1:]} != domain {domain.name}")
            elif key == ":objects":
                for n, t in parse_typed(sec[1:], ":objects", f"problem {self.name}"):
                    if t not in domain.types:
                        raise CannotCheck(f"problem {self.name}: object {n} unknown type {t}")
                    self.objects[n] = t
            elif key == ":init":
                for d in sec[1:]:
                    neg, atom = literal(d, None, f"problem {self.name} :init", allow_not=False)
                    if neg:
                        raise CannotCheck(f"problem {self.name}: negated :init fact {d}")
                    self._check_ground(atom, domain, ":init")
                    self.init.add(atom)
            elif key == ":goal":
                if len(sec) != 2:
                    raise CannotCheck(f"problem {self.name}: bad :goal")
                self.goal = body([sec[1]], f"problem {self.name} :goal")
                for atom in self.goal:
                    self._check_ground(atom, domain, ":goal")
            else:
                raise CannotCheck(f"problem {self.name}: unsupported section {key}")

    def _check_ground(self, atom, domain, where):
        pred, args = atom
        if pred not in domain.predicates:
            raise CannotCheck(f"problem {self.name} {where}: undeclared predicate {pred}")
        if len(args) != len(domain.predicates[pred]):
            raise CannotCheck(f"problem {self.name} {where}: predicate {pred} arity mismatch")
        for a, t in zip(args, domain.predicates[pred]):
            if a not in self.objects:
                raise CannotCheck(f"problem {self.name} {where}: undeclared object {a}")
            if not domain._is_subtype(self.objects[a], t):
                raise CannotCheck(
                    f"problem {self.name} {where}: object {a} of type "
                    f"{self.objects[a]} is not of required type {t}")


def parse_plan(text):
    """One grounded action call per line -> [(name, (args...))]; blank/;-only
    lines skipped.  Anything unparseable is CANNOT_CHECK (malformed plan)."""
    steps = []
    for k, line in enumerate(text.splitlines(), 1):
        line = re.sub(r";[^\n]*", "", line).strip()
        if not line:
            continue
        exprs = parse_exprs(line, f"plan line {k}")
        if len(exprs) != 1 or not isinstance(exprs[0], list) or not exprs[0]:
            raise CannotCheck(f"plan line {k}: not a single action call: {line!r}")
        call = exprs[0]
        if not all(isinstance(a, str) for a in call):
            raise CannotCheck(f"plan line {k}: nested term in {line!r}")
        if any(a.startswith("?") for a in call):
            raise CannotCheck(f"plan line {k}: unbound variable in {line!r}")
        steps.append((call[0], tuple(call[1:])))
    return steps


def validate(domain_text, problem_text, plan_text):
    """Full check. Returns (exit_code, reason); never raises for plan faults."""
    try:
        dom = Domain(domain_text)
        prob = Problem(problem_text, dom)
        steps = parse_plan(plan_text)
    except CannotCheck as exc:
        return CANNOT_CHECK, str(exc)
    state = set(prob.init)
    for k, (name, args) in enumerate(steps, 1):
        act = dom.actions.get(name)
        if act is None:
            return INVALID, f"step {k}: unknown action {name!r}"
        pnames = list(act["params"])
        if len(args) != len(pnames):
            return INVALID, (f"step {k}: action {name} expects {len(pnames)} "
                             f"argument(s), got {len(args)}")
        binding = dict(zip(pnames, args))
        for v, a in binding.items():
            if a not in prob.objects:
                return INVALID, f"step {k}: undeclared object {a!r}"
            if not dom._is_subtype(prob.objects[a], act["params"][v]):
                return INVALID, (f"step {k}: {name} argument {a!r} of type "
                                 f"{prob.objects[a]} is not of required type {act['params'][v]}")

        def ground(atom):
            return (atom[0], tuple(binding.get(t, t) for t in atom[1]))

        for atom in act["pre"]:
            g = ground(atom)
            if g not in state:
                return INVALID, f"step {k}: precondition {fmt(g)} not satisfied"
        for atom in act["del"]:
            state.discard(ground(atom))
        for atom in act["add"]:
            state.add(ground(atom))
    missing = [fmt(a) for a in prob.goal if a not in state]
    if missing:
        return INVALID, f"goal not reached: {', '.join(missing)}"
    return VALID, f"valid plan: {len(steps)} step(s), goal reached"


def fmt(atom):
    return "(" + " ".join([atom[0]] + list(atom[1])) + ")"


def validate_files(domain_path, problem_path, plan_path):
    try:
        texts = []
        for p in (domain_path, problem_path, plan_path):
            with open(p) as fh:
                texts.append(fh.read())
    except OSError as exc:
        return CANNOT_CHECK, f"cannot read input: {exc}"
    return validate(*texts)


def main(argv):
    if len(argv) != 4:
        print("usage: p1_validator.py <domain.pddl> <problem.pddl> <plan>")
        print("CANNOT_CHECK: expected exactly 3 input files")
        return CANNOT_CHECK
    code, reason = validate_files(argv[1], argv[2], argv[3])
    label = {VALID: "VALID", INVALID: "INVALID", CANNOT_CHECK: "CANNOT_CHECK"}[code]
    print(f"{label}: {reason}")
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
