"""Intended native outcomes for exposed authored fixtures; no scored target selection."""
import copy
from ControlPackets import declaration, family, names
from EnvironmentControls import PASS, PREPARED, expected


def refusal(stage, reason):
    policy = ("EXCLUDED_DEPENDENCY", "UNREGISTERED_AXIOM", "INDEPENDENT_TARGET_MISMATCH",
              "PRIMITIVE_IDENTITY_MISMATCH", "REGISTERED_AXIOM_HEADER_MISMATCH", "REGISTERED_PRIMITIVE_MISMATCH")
    return expected("REJECTED" if reason.startswith(policy) else "CANNOT_CHECK", stage, reason)


def change_decl(name, key, value):
    return lambda source, primitive, policy: declaration(source, name).__setitem__(key, value)


def drop_registered_axiom(source, primitive, policy):
    table = names(primitive)
    primitive[:] = [row for row in primitive if not ("axiom" in row and table[row["axiom"]["name"]] == "Fixture.evidence")]


def change_family(kind):
    def mutate(source, primitive, policy):
        group = family(source, "Fixture.Tree")
        if kind == "missing":
            group["recs"].pop()
        elif kind == "rhs":
            group["recs"][0]["rules"][0]["rhs"] = 0
        elif kind == "extra":
            extra = copy.deepcopy(group["recs"][0])
            extra["name"] = next(key for key, value in names(source).items() if value == "u")
            group["recs"].append(extra)
        elif kind == "ctor":
            group["ctors"][0]["numFields"] += 1
    return mutate


def no_nat_registry(source, primitive, policy):
    table = names(primitive)
    primitive[:] = [row for row in primitive if not ("inductive" in row and any(
        table[item["name"]] == "Nat" for item in row["inductive"]["types"]))]


def cases():
    result = [{"id": "composition", "purpose": "Exposed implication composition with no imported proof dependency", "checks": [
        {"expected": PASS},
        {"invalid_type": True, "expected": expected("REJECTED", "kernel", "")},
        {"target_constant": True, "expected": refusal("candidate_dependencies_and_kernel", "EXCLUDED_DEPENDENCY")},
        {"declarations": True, "expected": refusal("candidate_packet", "CANDIDATE_DECLARATION")},
        {"normalization": "unsupported", "expected": refusal("registration", "NORMALIZATION_VERSION")},
    ]}]
    for target in ("polymorphic", "defined", "opaqueUse", "mutualRecursor", "nested", "projection", "naturalLiteral", "stringLiteral", "quotient"):
        result.append({"id": target, "target": target, "purpose": "Fresh checked parent-format roundtrip: " + target})
    result += [
        {"id": "resource-baseline", "stress": True, "purpose": "Valid 2000-identity-application candidate under normal kernel settings"},
        {"id": "resource-refusal", "stress": True,
         "mutate": lambda s, p, q: q.update(max_heartbeats=1, max_rec_depth=10),
         "purpose": "Same valid stress candidate with insufficient checking resources is CANNOT_CHECK",
         "checks": [{"expected": refusal("kernel_resource", "DETERMINISTIC_TIMEOUT")}]},
        {"id": "opaque-axiom", "target": "opaqueAxiom", "roots": ["Fixture.opaqueEvidence"], "axioms": ["Fixture.evidence"],
         "purpose": "Transitive axiom inside opaque body is independently registered and reported"},
        {"id": "unused-allowed-axiom", "axioms": ["Fixture.evidence"],
         "purpose": "Larger authorized assumption set narrows to empty reached set and restores cold"},
        {"id": "missing-axiom-registry", "axioms": ["Fixture.evidence"], "mutate": drop_registered_axiom,
         "purpose": "An allowed name cannot authorize its own source header", "prepare": refusal("axiom_registry", "MISSING_REGISTERED_AXIOM_HEADER")},
        {"id": "changed-axiom-header", "axioms": ["Fixture.evidence"], "mutate": change_decl("Fixture.evidence", "type", 0),
         "purpose": "Changed source axiom type conflicts with independent registry", "prepare": refusal("primitive_identity", "PRIMITIVE_IDENTITY_MISMATCH")},
        {"id": "unallowed-opaque-axiom", "target": "opaqueAxiom", "roots": ["Fixture.opaqueEvidence"],
         "purpose": "Opaque body does not hide an unapproved axiom", "prepare": refusal("closure_and_replay", "UNREGISTERED_AXIOM")},
        {"id": "changed-target", "mutate": change_decl("Fixture.composition", "type", 0),
         "purpose": "Source cannot self-authorize a changed target", "prepare": refusal("independent_target_and_policy", "INDEPENDENT_TARGET_MISMATCH")},
        {"id": "changed-universes", "target": "polymorphic", "mutate": lambda s, p, q: q.__setitem__("target_level_params", []),
         "purpose": "Ordered independent target universes remain authoritative", "prepare": refusal("independent_target_and_policy", "INDEPENDENT_TARGET_MISMATCH")},
        {"id": "changed-withheld-proof", "mutate": change_decl("Fixture.composition", "value", 0),
         "purpose": "Withheld proof body is irrelevant to preparation; original candidate is checked independently"},
        {"id": "alias-exclusion", "roots": ["Fixture.aliasComposition"],
         "purpose": "Explicit alias dependency cannot reintroduce the excluded theorem", "prepare": refusal("closure_and_replay", "EXCLUDED_DEPENDENCY")},
        {"id": "unsafe-opaque", "target": "opaqueUse", "mutate": change_decl("Fixture.opaqueIdentity", "isUnsafe", True),
         "purpose": "Unsafe reached opaque is refused before replay", "prepare": refusal("closure_and_replay", "UNSAFE_OR_PARTIAL")},
        {"id": "partial-definition", "target": "defined", "mutate": change_decl("Fixture.identity", "safety", "partial"),
         "purpose": "Partial reached definitions are explicitly unsupported", "prepare": refusal("closure_and_replay", "UNSAFE_OR_PARTIAL")},
        {"id": "changed-primitive-body", "target": "naturalLiteral", "mutate": change_decl("Nat.add", "value", 0),
         "purpose": "Primitive body identity is checked beyond name/type", "prepare": refusal("primitive_identity", "PRIMITIVE_IDENTITY_MISMATCH")},
        {"id": "missing-primitive-registry", "target": "naturalLiteral", "mutate": no_nat_registry,
         "purpose": "Reached kernel builtin requires independent primitive record coverage", "prepare": refusal("primitive_coverage", "MISSING_REGISTERED_PRIMITIVE")},
    ]
    for kind, reason in (("missing", "MISSING_DEPENDENCY"), ("rhs", "Invalid recursor Fixture.Forest.rec"), ("extra", "No such recursor u"), ("ctor", "Invalid constructor Fixture.Tree.leaf")):
        result.append({"id": "family-" + kind, "target": "mutualRecursor", "mutate": change_family(kind),
                       "purpose": "Generated family counterpart falsifier: " + kind, "prepare": refusal("closure_and_replay", reason)})
    return result
