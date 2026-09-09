"""PDEV-3 candidate change grammar: morphology space over the frozen donor runtime.

Cognitive machine under search (issue #217 / #149 / #151):

    M_t = (F_t, O_t, Pi_t, C)

A candidate is a *declarative morphology configuration*: which basic-unit forms
hold cognition, how the knowledge space is structured/factored, how acquisition
and routing are organised. Every configuration is executable through the
pinned donor runtime (vendored, byte-identical) and measured by the frozen
external meter in ``pdev_runner``.

Operator directives incorporated (2026-09-09, recorded in PROTOCOL.json):
  1. morphology widening - basic-unit FORM and knowledge-space STRUCTURE are
     first-class C3/C5 candidate dimensions, not extra parameters bolted on.
  2. quality-diversity selection - the grammar exposes the descriptor-relevant
     axes so illumination search can target genuinely different forms.

``C`` (checker, authority, meter, evaluator, adoption boundary) is not
expressible in this grammar: unknown keys, protected prefixes and protected
tokens are rejected at parse time (fail closed), mirroring
``ocm.selfmodel.proposal.touches_protected_target``.

Python 3.8+ stdlib only; deterministic; no I/O.
"""
from __future__ import annotations

import hashlib
import json
import math
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

SCHEMA = "pdev217.candidate_grammar.v1"

# ---------------------------------------------------------------------------
# Dimensions. Values are strings/ints only; the grammar is a product space.
# ---------------------------------------------------------------------------

S_UNITS: Tuple[str, ...] = ("feature", "family_key", "vector", "scan")
#: feature     = production-rule unit with a feature index (FeatureArm body)
#: family_key  = typed-relation channel unit on family identity (FamilyKeyIndex)
#: vector      = nearest-neighbour store unit (VectorIndex)
#: scan        = unindexed exhaustive working-memory unit (ExactScanParent)

D_UNITS: Tuple[str, ...] = ("learned", "lazy", "recompute", "cooc", "all_evidence")
#: learned      = learned dependency-graph unit
#: lazy         = lazy learner unit
#: recompute    = full recomputation parent unit
#: cooc         = co-occurrence graph unit
#: all_evidence = all-evidence unit

S_FEATURES: Tuple[str, ...] = ("prefix9",) + tuple(
    "fl%03d" % i for i in range(511)
)
#: knowledge-space factoring key for feature units: the registered 511-feature
#: language (every non-empty subset of the 9-position pool, canonical order)
#: plus the hand-specified 9-prefix. Resolved to a Feature in pdev_runner.

BUCKET_BOUNDS: Tuple[int, ...] = (2, 4, 8)
#: partition-quotient granularity of the knowledge space (adequacy bound on
#: bucket size; drives re-index triggering and k). 4 is the donor default.

GROWTH_SCHEDULES: Tuple[int, ...] = (1, 2, 5)
#: acquisition growth chunking: 1 = single install+grow event, >1 = staged
#: growth in chunks (more maintenance events, possibly different re-indexing).

S_COMPOSITES: Tuple[str, ...] = ("none", "in_store_first_refusal")
#: none                     = single unit per domain
#: in_store_first_refusal   = two units instantiated; queries whose family is
#:   declared in-store are routed to the exact family-key unit first (the #214
#:   attention/retrieval first-refusal mechanism transferred), everything else
#:   to the configured s_unit. Both stores are built and charged.

D_COMPOSITES: Tuple[str, ...] = ("none", "escalate_on_stale")
#: none                = single unit
#: escalate_on_stale   = cheap unit answers; families with stale survivors
#:   escalate to the learned unit for those revocations only. Both charged.

DIMENSIONS: Tuple[Tuple[str, Tuple[Any, ...]], ...] = (
    ("s_unit", S_UNITS),
    ("s_feature", S_FEATURES),
    ("s_choose", (True, False)),
    ("s_reindex", (True, False)),
    ("s_bucket", BUCKET_BOUNDS),
    ("s_growth", GROWTH_SCHEDULES),
    ("s_composite", S_COMPOSITES),
    ("d_unit", D_UNITS),
    ("d_composite", D_COMPOSITES),
)

#: Change class each dimension belongs to (issue #149 / M11 vocabulary).
DIMENSION_CLASS: Dict[str, str] = {
    "s_unit": "C3",       # basic-unit form = representation of rule cognition
    "s_feature": "C3",    # knowledge-space factoring
    "s_choose": "C4",     # feature discovery at install = learning policy
    "s_reindex": "C4",    # noticing and repairing growth = learning policy
    "s_bucket": "C3",     # partition-quotient granularity
    "s_growth": "C4",     # acquisition schedule
    "s_composite": "C5",  # cognitive organisation across units
    "d_unit": "C3",
    "d_composite": "C5",
}

#: Legal write set per class: dimensions a candidate of that class may touch.
LEGAL_WRITE_SET: Dict[str, Tuple[str, ...]] = {
    "C0": (),  # resource/search allowance: expressed by the search envelope,
               # never by editing measured cognition; grammar-level no-op here
    "C1": (),  # routing policy in this grammar is expressed through the C5
               # composite (which unit serves which request stream); kept
               # empty so single-key C1 edits stay in the parent's vocabulary
    "C2": ("s_composite", "d_composite"),  # composition of learned operators
    "C3": ("s_unit", "s_feature", "s_bucket", "d_unit"),
    "C4": ("s_choose", "s_reindex", "s_growth"),
    "C5": ("s_composite", "d_composite"),
}
#: Union grammar: any registered dimension may be edited by C3/C4/C5-typed
#: candidates; the union write set is what random/QD arms sample from.
UNION_WRITE_SET: Tuple[str, ...] = tuple(name for name, _ in DIMENSIONS)

PROTECTED_PREFIXES = ("adoption.", "assurance.", "constitution.", "meter.",
                      "authority.", "checker.", "evaluator.", "runner.",
                      "protected", "task.", "suite.")
PROTECTED_TOKENS = ("adoption", "assurance", "constitution", "meter",
                    "authority", "charge", "budget", "threshold", "evaluator",
                    "checker", "preservation", "protected", "grade", "score")

#: The #149 canonical g2 machine, mapped into the morphology grammar.
INCUMBENT_G0: Dict[str, Any] = {
    "s_unit": "feature",
    "s_feature": "prefix9",
    "s_choose": False,
    "s_reindex": False,
    "s_bucket": 4,
    "s_growth": 1,
    "s_composite": "none",
    "d_unit": "lazy",
    "d_composite": "none",
}


def _walk_strings(value: Any) -> Iterable[str]:
    if isinstance(value, Mapping):
        for key, child in value.items():
            yield str(key)
            yield from _walk_strings(child)
    elif isinstance(value, (list, tuple)):
        for child in value:
            yield from _walk_strings(child)
    elif isinstance(value, str):
        yield value


def touches_protected(config: Mapping[str, Any]) -> Optional[str]:
    """Fail-closed protected-boundary check (mirrors M11 E7 hostile semantics)."""
    for key in config:
        if any(str(key).startswith(prefix) for prefix in PROTECTED_PREFIXES):
            return "protected_prefix:" + str(key)
    for text in _walk_strings(config):
        low = text.lower()
        for token in PROTECTED_TOKENS:
            if token in low:
                return "protected_token:" + token
    return None


def validate(config: Mapping[str, Any]) -> List[str]:
    """Return a list of legality violations; empty list = legal candidate."""
    problems: List[str] = []
    if not isinstance(config, Mapping):
        return ["config is not a mapping"]
    protected = touches_protected(config)
    if protected:
        return ["candidate reaches C: " + protected]
    allowed = {name for name, _ in DIMENSIONS}
    for key in config:
        if key not in allowed:
            problems.append("unknown dimension (outside grammar): " + str(key))
    options = dict(DIMENSIONS)
    for name, values in DIMENSIONS:
        if name in config and config[name] not in values:
            problems.append("unregistered value for %s: %r" % (name, config[name]))
    if problems:
        return problems
    # Structural legality constraints. Feature-specific knobs are meaningful
    # only when the feature unit is instantiated; elsewhere they must stay at
    # neutral values so structurally equivalent candidates collapse exactly.
    if config.get("s_choose") is True and config.get("s_unit") != "feature":
        problems.append("s_choose requires the feature unit form")
    if config.get("s_reindex") is True and config.get("s_choose") is not True:
        problems.append("s_reindex requires s_choose (no key to re-index)")
    if config.get("s_unit") != "feature":
        if config.get("s_feature") != "prefix9":
            problems.append("s_feature set but feature unit not instantiated")
        if config.get("s_choose") is not False or config.get("s_reindex") is not False:
            problems.append("s_choose/s_reindex set but feature unit not instantiated")
    return problems


def is_legal(config: Mapping[str, Any]) -> bool:
    return not validate(config)


def canonical(config: Mapping[str, Any]) -> str:
    return json.dumps(config, sort_keys=True, separators=(",", ":"))


def digest(config: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical(config).encode()).hexdigest()[:16]


def is_noop(config: Mapping[str, Any], parent: Mapping[str, Any]) -> bool:
    """Structural no-op: identical canonical form (cosmetic renames collapse)."""
    return canonical(config) == canonical(parent)


def changed_dimensions(config: Mapping[str, Any],
                       parent: Mapping[str, Any]) -> List[str]:
    return sorted(key for key in UNION_WRITE_SET if config.get(key) != parent.get(key))


def infer_change_class(config: Mapping[str, Any],
                       parent: Mapping[str, Any]) -> Optional[str]:
    """Minimum REGISTERED-WRITABLE class covering every edited dimension.

    M11 apply legality: the declared class must be legal for EVERY edited
    dimension (``edit_classes[dim]`` = the classes whose write set contains
    ``dim``, plus C5).  A single-class edit set is covered by that class; an
    edit set spanning several classes is only writable as C5 (the union/
    organizational class, legal everywhere).  The M11 ordering
    C0<C1<C2<C4<C3<C5 is respected because C5 sits last in it.
    """
    changed = changed_dimensions(config, parent)
    if not changed:
        return None
    needed = {DIMENSION_CLASS[name] for name in changed}
    if len(needed) == 1:
        return next(iter(needed))
    return "C5"


def size_accounting(config: Mapping[str, Any],
                    parent: Mapping[str, Any]) -> Dict[str, Any]:
    """Change-complexity accounting: edited dimensions and information bits."""
    options = dict(DIMENSIONS)
    changed = changed_dimensions(config, parent)
    bits = 0.0
    for name in changed:
        bits += math.log2(len(options[name]))
    return {"edited_dimensions": changed,
            "edit_count": len(changed),
            "edit_bits": round(bits, 4),
            "config_bits": round(sum(math.log2(len(v)) for _, v in DIMENSIONS), 4)}


def rollback_plan(config: Mapping[str, Any]) -> str:
    cls = "C3/C4/C5"
    return ("M11 exact data rollback to incumbent_fingerprint; reopen all "
            "derived caches; morphology config is plain data so restoration "
            "is the serialized incumbent snapshot (%s)" % cls)


def sample_space_size() -> int:
    n = 1
    for _, values in DIMENSIONS:
        n *= len(values)
    return n


def config_from_json(text: str) -> Dict[str, Any]:
    config = json.loads(text)
    problems = validate(config)
    if problems:
        raise ValueError("illegal candidate: " + "; ".join(problems))
    return config


def enumerate_neighbourhood(parent: Mapping[str, Any],
                            structural_only: bool = False) -> List[Dict[str, Any]]:
    """All legal single-dimension edits (program-repair arm's move set).

    ``structural_only`` skips the 511-value feature axis (large neighbourhoods
    are composed by callers with explicit caps, never enumerated blindly).
    """
    options = dict(DIMENSIONS)
    out: List[Dict[str, Any]] = []
    for name, values in options.items():
        if structural_only and name == "s_feature":
            continue
        for value in values:
            child = dict(parent)
            child[name] = value
            if is_legal(child) and not is_noop(child, parent):
                out.append(child)
    return out
