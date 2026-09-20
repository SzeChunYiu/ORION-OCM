# Next foundation repair: N01/N02 evidence and freeze requirements

Read-only audit baseline: main `1f0648194b55afe8fec07d158ae0f5d3c9b31505`.
This record does not implement the next repair, alter historical files, or close
any atom. The failure attribution is to the original R0 checker's incomplete
validation and R1/R2's insufficiently specified representation boundary.

## N01: verified original R0 checker omissions

The true baseline passes `check_r0.main()`. Four isolated mutations also pass
the complete main function with return code 0 and its six original hostiles:

| Mutated field | Replacement | Observed result |
|---|---|---|
| first atomic row status | ABSOLUTE_TRUTH | MAIN_ACCEPTED 0 |
| first atomic row evidence_kind | INVALID_EVIDENCE | MAIN_ACCEPTED 0 |
| first parent role | GMI_NOVELTY | MAIN_ACCEPTED 0 |
| candidate fixed-point theorem status | CONJECTURE -> PROVED | MAIN_ACCEPTED 0 |

The freeze requires controlled vocabularies, parent ownership and no unsupported
fixed-point promotion. The checker validates theorem-status vocabulary, but not
atomic status/evidence vocabularies or parent roles; PROVED is an allowed theorem
status and has no claim-specific evidence gate there.

These findings concern the historical standalone checker. They do **not** show
that current snapshot hashes permit rewriting frozen artifacts. The original
`validate()` also accepts deletion of one R0 atom, but the full main function's
unchanged row-count receipt rejects that deletion; it is not a full-checker
bypass and must not be reported as one.

Reproduce without files or repository mutation, on billy-laptop from a repository
containing the baseline commit:

```sh
/home/billy/.local/bin/python3.12 -I -B - <<'PY'
import subprocess, json, copy, contextlib, io
rev = "1f0648194b55afe8fec07d158ae0f5d3c9b31505"
base = "research/gmi-1068-grand-unified-v2-r0/"
def raw(name):
    return subprocess.check_output(
        ["/usr/bin/git", "show", rev + ":" + base + name], text=True)
ns = {"__name__": "audit", "__file__": base + "check_r0.py"}
exec(compile(raw("check_r0.py"), base + "check_r0.py", "exec"), ns)
names = ["ATOMIC_CHECKLIST_V1.json", "THEORY_DAG_V1.json",
         "PARENT_REGISTRY_V1.json", "THEOREM_STATUS_V1.json",
         "MERGE_GATE_V1.json", "RESULT_V1.json"]
original = {n: json.loads(raw(n)) for n in names}
cases = [("baseline", None),
         ("atomic_status", (0, "rows", "status", "ABSOLUTE_TRUTH")),
         ("evidence_kind", (0, "rows", "evidence_kind", "INVALID_EVIDENCE")),
         ("parent_role", (2, "entries", "role", "GMI_NOVELTY")),
         ("candidate_promotion", (3, "entries", "status", "PROVED"))]
for label, mutation in cases:
    data = copy.deepcopy(original)
    if mutation is not None:
        n, collection, field, value = mutation
        data[names[n]][collection][0][field] = value
    ns["load"] = lambda n: copy.deepcopy(data[n])
    with contextlib.redirect_stdout(io.StringIO()):
        result = ns["main"]()
    print(label, "MAIN_ACCEPTED", result)
PY
```

Governance completion can be positive: R0-001/002/003/004/005/006/007 concern
delivering a constitution, hypothesis freeze, registries, DAG and merge gate.
Their delivery can be independently adjudicated without pretending the theory
is complete. R0-008 additionally needs a repaired successor auditor.
The original freeze commit `852b7665f86798c334bfd0eccafb5cfb0de463c5`
contains only FREEZE_V1.md, before registry implementation. Closure still needs
exact source/content/custody and requirement-level checks, not file existence.

## N02: recoverability is invariant; primitive-symbol count is not

Fix a model class M and declared observations p:M->P (process reduct) and
o:M->O (objective). A decoder d:image(p)->O satisfying d(p(m))=o(m) exists
iff p(m)=p(n) implies o(m)=o(n). Necessity substitutes into d. Sufficiency
defines d at a process value to be the common objective value of its fiber.
This is a classical well-defined-function proof; it gives no computable decoder.

A pair with the same p and different o therefore refutes every uniform decoder.
Bijective encodings of M,P,O commuting with these observations preserve this
property: transport a decoder by the inverse process encoding and the objective
encoding. The inverse translations prove the reverse implication.
Unrestricted categorical equivalence without these observation correspondences
is not enough. Packing (p,o) into one field preserves all information while
changing field count.

A stronger signature counterexample needs no arbitrary packing. In an
associative typed composition presentation, replace the named identity operation
by the axiom that each object has a two-sided unit. Such a unit is unique:
for units e,e' at one object, e=e composed with e'=e'. The identity operation is
then explicitly definable by this unique property. Thus deleting its *symbol*
can preserve the theory; deleting the *unit requirement* generally cannot.
Historical R1's deletion witnesses cannot establish symbol-count minimality
across this class of equivalent presentations.

There is also an R2 domain-leakage requirement. Historical context is typed as
nu:Hist(C)->?W, while the reverse independence witness keeps only stateValue
fixed across different process models. If the context object contains its
declared Hist(C) domain, that domain already exposes admitted histories.
The witness does not establish equality of those complete typed contexts.

A precise repair fixes an ambient typed history universe H and an external
evaluator nu:H->?W, independently of an admission predicate R on H. A small
countermodel uses the ambient category with identities at 0,1 and two parallel
arrows a,b:0->1. Identities-only and all-arrows are both wide subcategories.
On the full category, evaluators assigning (nu(a),nu(b))=(1,0) or (0,1)
reverse preference with identical processes. With one evaluator fixed, the two
subcategories differ in reachability. All comparisons now share one declared
ambient domain. This supports semantic independence, not two primitive symbols.

## Parent ownership and the next freeze

[Barrett and Halvorson, Morita Equivalence](https://arxiv.org/pdf/1506.04675),
Theorem 3.1, gives uniqueness of definitional expansion; Theorem 4.1 treats
Morita expansion up to isomorphism. Section 4.1 permits new product, coproduct,
subsort and quotient sorts. These are parent-owned distinctions, not GMI
novelty. The decoder and unit arguments above are elementary direct proofs.
The existing #833 AG3 package also distinguishes renaming, term, compiler and
model equivalence, and shows why raw bounded simulation need not preserve
observations; reuse its distinctions without promoting its finite census.

Before implementation freeze: declare the translation class, observable
correspondences, admissibility/context domains, identity-symbol elimination and
claim-specific R0 validation rules. Require no-alarm controls on genuine data,
the four real mutations above, missing/duplicate atoms, cyclic DAG and source
ownership failures. Mechanize decoder obstruction and equivalence transport;
test a lossless packed encoding and an intentionally lossy encoding separately.
Integrate V5's subcategory closure and nonlinear aggregation boundaries.

Target atoms are R1-001/006/007/009/010 and R2-006/007/008/009, plus R2-002/003/004
for the repaired common-domain countermodels. Adjudicate each complete original
requirement separately. Do not convert proving these conditional statements
into global primitive-count minimality or whole-programme closure.
