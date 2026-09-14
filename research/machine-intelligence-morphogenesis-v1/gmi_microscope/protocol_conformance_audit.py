"""B1: can conformance to the common protocol be measured from the artifacts?

B1 asks every derived family to follow one protocol.  The honest way to close it
is not to assert conformance but to MEASURE it.  This audit tried to do that
mechanically, by reading the committed receipts and witness sources of the 19
derived families.

It reports a negative about the METHOD and a positive about the CAUSE:

  * Every requirement signal that could be validated against a hand-adjudicated
    answer FAILS -- receipt vocabulary misses known-true conformance, and
    widening the same patterns to witness source saturates at 18-19/19.
  * The reason is exhibited, not guessed: the corpus has no shared protocol
    vocabulary.  Twelve families construct a matched negative control and give
    it NINE different names, with no token common to all of them.

So conformance is not recoverable from the artifacts as currently emitted.  The
repair is a declared protocol block; its schema and validator are below, and the
validator honestly reports that 0 of 19 families currently emit one.

Run from research/machine-intelligence-morphogenesis-v1 (needs the whole tree,
so this is an audit, not a witness -- it cannot run in a one-file temp dir).
"""

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RESULTS = os.path.join(ROOT, "microscopes", "results")

FAMILIES = {
    "B2 finite-state":      ("finite_state_witness.py",            "STAGE_FINITE_STATE_V1.json"),
    "B3 linear/kernel":     ("linear_family_witness.py",           "STAGE_LINEAR_FAMILY_V1.json"),
    "B4 neural arch":       ("neural_architecture_witness.py",     "STAGE_NEURAL_ARCHITECTURE_V1.json"),
    "B4 credit assign":     ("credit_assignment_witness.py",       "STAGE_CREDIT_ASSIGNMENT_V1.json"),
    "B4 update law":        ("update_law_witness.py",              "STAGE_UPDATE_LAW_V1.json"),
    "B5 equivariance":      ("equivariance_witness.py",            "STAGE_EQUIVARIANCE_V1.json"),
    "B6 gated recurrence":  ("gated_recurrence_witness.py",        "STAGE_GATED_RECURRENCE_V1.json"),
    "B7 dynamic routing":   ("dynamic_routing_witness.py",         "STAGE_DYNAMIC_ROUTING_V1.json"),
    "B8 message passing":   ("message_passing_witness.py",         "STAGE_MESSAGE_PASSING_V1.json"),
    "B9 state space":       ("state_space_witness.py",             "STAGE_STATE_SPACE_V1.json"),
    "B10 conditional spec": ("conditional_specialization_witness.py", "STAGE_CONDITIONAL_SPECIALIZATION_V1.json"),
    "B11 exemplar/param":   ("exemplar_parametric_witness.py",     "STAGE_EXEMPLAR_PARAMETRIC_V1.json"),
    "B13 belief state":     ("belief_state_witness.py",            "STAGE_BELIEF_STATE_V1.json"),
    "B14 symbolic rewrite": ("symbolic_rewrite_witness.py",        "STAGE_SYMBOLIC_REWRITE_V1.json"),
    "B15 program library":  ("program_library_witness.py",         "STAGE_PROGRAM_LIBRARY_V1.json"),
    "B16 search frontier":  ("search_frontier_witness.py",         "STAGE_SEARCH_FRONTIER_V1.json"),
    "B17 generative":       ("generative_family_witness.py",       "STAGE_GENERATIVE_FAMILY_V1.json"),
    "B18 control":          ("control_family_witness.py",          "STAGE_CONTROL_FAMILY_V1.json"),
    "B19 continual":        ("continual_regimes_witness.py",       "STAGE_CONTINUAL_REGIMES_V1.json"),
}

_missing = [f"{fam}: {f}"
            for fam, (w, r) in FAMILIES.items()
            for f, base in ((w, HERE), (r, RESULTS))
            if not os.path.exists(os.path.join(base, f))]
assert not _missing, (
    "audited artifacts do not exist, so every signal would silently read as "
    "absent and the whole audit would be vacuous: " + "; ".join(_missing))

# --------------------------------------------------------------------------
# 1  HAND-ADJUDICATED GROUND TRUTH
#
# "Does this family construct a matched negative control?" -- decided by reading
# the receipt, recording the key that carries it and the field that makes it a
# control (an arm that is supposed to FAIL, reported alongside one that passes).
# Families with no such arm are recorded as False, which is what gives the
# signal validation both polarities.  A reader can check every row against the
# committed receipt.
# --------------------------------------------------------------------------
TWIN_TRUTH = {
    "B2 finite-state":      ("stateless",                     "sufficient=false at accuracy 0.5029"),
    "B4 neural arch":       ("negative_twin",                 "matched obligation, net_cost reported"),
    "B5 equivariance":      ("negative_twin",                 "obligation has_11, sharing must not pay"),
    "B7 dynamic routing":   ("negative_ecology",              "fixed reader priced against dynamic"),
    "B8 message passing":   ("negative_twin",                 "cheapest_access incidental"),
    "B10 conditional spec": ("twins",                         "matched catalogue arrangement"),
    "B14 symbolic rewrite": ("relation_twin",                 "distinct_rows vs pairs"),
    "B15 program library":  ("collapsing_control",            "best_saving negative by construction"),
    "B17 generative":       ("iterative_structural_negative", "denominators that cannot be reached"),
    "B18 control":          ("exploration_twin",              "min_regret_if_explores_* split vs tied"),
    "B19 continual":        ("substrate_control",             "costs for expand/modulate substrate"),
    # no matched-failing arm in the receipt:
    "B3 linear/kernel":     (None, "identification curve only"),
    "B6 gated recurrence":  (None, "crossover and pressure, no failing twin arm"),
    "B9 state space":       (None, "compression/horizon/recovery only"),
    "B11 exemplar/param":   (None, "knn is a comparator, not a control that must fail"),
    "B13 belief state":     (None, "factorization/point_estimate, no failing arm"),
    "B16 search frontier":  (None, "compile_vs_search comparison, no failing arm"),
    "B4 credit assign":     (None, "forward/reverse regimes, no failing arm"),
    "B4 update law":        (None, "hypothesis_A/B flags record a refuted hypothesis, "
                                   "which is not a matched control arm"),
}

# "Does this family replicate at a real regime (not a toy enumeration)?"
# Adjudicated False for all 19: every receipt reports exhaustive enumeration or
# small closed-form ladders.  This is the corpus's own stated scope.
REALSCALE_TRUTH = {fam: False for fam in FAMILIES}

# The adjudication above is itself checkable: every named key must really be a
# top-level key of that family's receipt, and no family adjudicated False may be
# hiding one under an obvious control-like name.  Without this, a mis-attributed
# key would be scored as a signal MISS and would overstate the finding.
def _verify_adjudication():
    problems = []
    for fam, (key, _why) in TWIN_TRUTH.items():
        d = json.load(open(os.path.join(RESULTS, FAMILIES[fam][1])))
        ks = set(d) if isinstance(d, dict) else set()
        if key is None:
            hiding = sorted(k for k in ks if re.search(
                r"twin|control|negative|stateless|impossib|anti_rig", k))
            if hiding:
                problems.append("%s adjudicated False but receipt has %s" % (fam, hiding))
        elif key not in ks:
            problems.append("%s: named key %r is not in its receipt (has %s)"
                            % (fam, key, sorted(ks)))
    assert not problems, "adjudication does not match the receipts: " + "; ".join(problems)


_verify_adjudication()

# the two signals under test, exactly as a vocabulary proxy would define them
SIG_TWIN = r"twin|negative|control|matched"
SIG_REALSCALE = r"\b(?:real[- ]regime|real[- ]scale|production|full[- ]scale)\b"
# Word-bounded like the rest.  This removes one of the two false positives
# ("reproduction", of a receipt) and leaves the other standing: B14 writes
# "production system", a rewrite-systems term.  So the signal still has ZERO
# true positives -- boundaries fix the lexical artefact and cannot fix the
# semantic one, which is why precision stays at zero.


def _strip_declaration(src):
    """Remove the emitted OUT["protocol"] = {...} statement from witness source.

    The same reason the block is stripped from the receipt: once a witness
    declares its conformance, the declaration's own field names ("lower_bound",
    "negative_control", "coordinate") are words in the source, and a proxy that
    reads them is measuring the declaration rather than the derivation.  Leaving
    it in moved the saturation count from 4 of 8 to 5 of 8 with no change to any
    derivation.
    """
    i = src.find('OUT["protocol"]')
    if i < 0:
        return src
    j = src.find("{", i)
    if j < 0:
        return src
    depth = 0
    for k in range(j, len(src)):
        if src[k] == "{":
            depth += 1
        elif src[k] == "}":
            depth -= 1
            if depth == 0:
                return src[:i] + src[k + 1:]
    return src


def load(fam):
    """Receipt text with the DECLARED protocol block removed.

    Sections 2-4 measure whether conformance is recoverable from the receipt
    WITHOUT a declaration -- that is the whole question they exist to answer.
    Once families declare a block, leaving it in makes every proxy trivially
    true: the twin signal fires on all 19 of 19 because the key name
    `negative_control` matches even where its value is null, against 10 of 19
    with the block removed.  A proxy that reads the declaration is measuring the
    declaration, not the artifact.  So the block is stripped here, and the
    sections keep measuring the non-declared part of every receipt, which is
    what the document says they do."""
    w, r = FAMILIES[fam]
    src = _strip_declaration(open(os.path.join(HERE, w)).read()).lower()
    d = json.load(open(os.path.join(RESULTS, r)))
    if isinstance(d, dict):
        d = {k: v for k, v in d.items() if k != "protocol"}
    flat = json.dumps(d).lower()
    return src, flat


def confusion(name, truth_map, signal_fn):
    """Score a signal against adjudicated truth, both polarities."""
    tp = fp = tn = fn = 0
    misses, falsepos = [], []
    for fam in sorted(FAMILIES):
        t = truth_map[fam]
        t = bool(t[0]) if isinstance(t, tuple) else bool(t)
        s = signal_fn(fam)
        if t and s:
            tp += 1
        elif t and not s:
            fn += 1
            misses.append(fam)
        elif s and not t:
            fp += 1
            falsepos.append(fam)
        else:
            tn += 1
    return {"signal": name, "tp": tp, "fp": fp, "tn": tn, "fn": fn,
            "missed": misses, "false_positive": falsepos}


def main():
    out = {}
    print("=" * 96)
    print("B1 PROTOCOL CONFORMANCE -- can it be measured from the artifacts?")
    print("=" * 96)
    print("  %d derived families, each with a committed witness and receipt." % len(FAMILIES))

    # ---------------------------------------------------------------- 2
    print()
    print("-" * 96)
    print("2  VALIDATING THE SIGNALS (both polarities, against hand-adjudicated truth)")
    print("-" * 96)

    def twin_sig(fam):
        return bool(re.search(SIG_TWIN, load(fam)[1]))

    def real_sig(fam):
        return bool(re.search(SIG_REALSCALE, load(fam)[0]))

    cm_twin = confusion("matched negative control", TWIN_TRUTH, twin_sig)
    cm_real = confusion("real-regime replication", REALSCALE_TRUTH, real_sig)
    out["signal_validation"] = [cm_twin, cm_real]

    for cm in (cm_twin, cm_real):
        tot = cm["tp"] + cm["fp"] + cm["tn"] + cm["fn"]
        print()
        print("  signal: %s" % cm["signal"])
        print("    true pos %d   false pos %d   true neg %d   MISSED %d   (n=%d)"
              % (cm["tp"], cm["fp"], cm["tn"], cm["fn"], tot))
        if cm["missed"]:
            print("    misses a family whose answer is known TRUE : %s"
                  % ", ".join(cm["missed"]))
        if cm["false_positive"]:
            print("    fires on a family whose answer is known FALSE: %s"
                  % ", ".join(cm["false_positive"]))

    # the substring artefacts behind realscale's positives, named explicitly
    art = {}
    for fam in cm_real["false_positive"]:
        src = load(fam)[0]
        hits = sorted({src[max(0, m.start() - 22):m.start() + 24].strip().replace("\n", " ")
                       for m in re.finditer(SIG_REALSCALE, src)})
        art[fam] = hits[:3]
    out["realscale_false_positive_context"] = art
    if art:
        print()
        print("    what those false positives actually matched:")
        for fam, hits in art.items():
            for h in hits:
                print("      %-22s ...%s..." % (fam, h))

    assert cm_twin["fn"] > 0 or cm_real["fp"] > 0, (
        "both signals scored perfectly against adjudicated truth -- that would "
        "mean vocabulary proxies work, which contradicts the saturation test "
        "below; suspect the adjudication was copied from the signal")
    assert cm_real["tp"] == 0, (
        "the real-regime signal found a true positive, so the corpus would "
        "contain a real-regime replication -- re-adjudicate REALSCALE_TRUTH")

    # ---------------------------------------------------------------- 3
    print()
    print("-" * 96)
    print("3  WHY WIDENING DOES NOT RESCUE THE PROXY")
    print("-" * 96)
    # Word-boundary delimited.  An earlier version matched bare substrings and was
    # caught red-handed by this audit's own reproduction guard: a correction that
    # added the word "stated" to a witness moved the "state" count from 16 to 17,
    # because "state" is a prefix of "stated".  That is precisely the defect this
    # document reports in the real-regime signal ("production system",
    # "reproduction").  The boundaries below remove that class of false match.
    # They do NOT rescue the proxy -- the saturation is unchanged -- which is the
    # point: the method fails for structural reasons, not for want of tuning.
    KEYPAT = {
        "obligation-sufficient state": r"\b(?:state|states|carrier|carriers|memory|quotient|quotients|class|classes)\b",
        "lower bound proved":          r"\b(?:bound|bounds|minimal|minimum|lower|least|floor)\b",
        "constructive realization":    r"\b(?:realiz\w*|construct\w*|witness\w*|exhibit\w*|verified|machine|machines)\b",
        "complexity coordinate":       r"\b(?:cost|costs|cells|bits|states|rounds|width|depth|traffic)\b",
        "lifecycle/resource law":      r"\b(?:cost|costs|price|prices|charged|break_even|breakeven|budget)\b",
        "matched negative twin":       SIG_TWIN,
        "crossover prediction":        r"\b(?:crossover|break_even|breakeven|threshold|thresholds|window|windows|flip|flips)\b",
        "neutral recovery":            r"\b(?:recovery|recover|recovers|neutral)\b",
    }
    print("  %-30s %14s %16s" % ("requirement", "receipt only", "receipt+source"))
    sat = []
    widened = {}
    for label, pat in KEYPAT.items():
        a = b = 0
        for fam in FAMILIES:
            src, flat = load(fam)
            hit_r = bool(re.search(pat, flat))
            a += hit_r
            b += hit_r or bool(re.search(pat, src))
        widened[label] = {"receipt_only": a, "receipt_plus_source": b}
        flag = ""
        if b >= len(FAMILIES) - 1:
            flag = "  <-- saturates"
            sat.append(label)
        print("  %-30s %10d/%d %12d/%d%s"
              % (label, a, len(FAMILIES), b, len(FAMILIES), flag))
    out["widening_test"] = widened
    print()
    print("  > Receipt-only vocabulary MISSES conformance that is really there.")
    print("  > Widening the same patterns to witness source saturates %d of %d"
          % (len(sat), len(KEYPAT)))
    print("  > signals at %d-%d of %d, because every witness is a Python file"
          % (len(FAMILIES) - 1, len(FAMILIES), len(FAMILIES)))
    print("  > that says 'verify', 'cost' and 'threshold'.  The proxy fails in")
    print("  > BOTH directions, so neither setting is a measurement.")
    assert len(sat) >= 3, (
        "widening to source did not saturate, so the saturation argument for "
        "rejecting source-widened proxies does not hold -- recheck")

    # ---------------------------------------------------------------- 4
    print()
    print("-" * 96)
    print("4  THE CAUSE, EXHIBITED: no shared protocol vocabulary")
    print("-" * 96)
    names = {}
    for fam, (key, why) in sorted(TWIN_TRUTH.items()):
        if key:
            names.setdefault(key, []).append(fam)
    print("  %d families construct a matched negative control." % sum(len(v) for v in names.values()))
    print("  They give it %d different names:" % len(names))
    for key in sorted(names):
        print("      %-32s %s" % (key, ", ".join(names[key])))

    def toks(k):
        return set(t for t in re.split(r"[^a-z0-9]+", k) if t)

    common = set.intersection(*[toks(k) for k in names])
    out["control_synonyms"] = {"names": sorted(names), "families": sum(len(v) for v in names.values()),
                               "shared_tokens": sorted(common)}
    print()
    print("  tokens shared by ALL %d names: %s" % (len(names), sorted(common) or "NONE"))
    assert not common, (
        "the control names share a token, so a single-token regex would find "
        "them all and the no-shared-vocabulary claim is wrong")
    assert len(names) >= 6, (
        "fewer than six distinct names -- the vocabulary-divergence claim needs "
        "the census to actually be diverse")
    caught = [k for k in names if re.search(SIG_TWIN, k)]
    print("  the regex %r catches %d of %d names, and misses %s."
          % (SIG_TWIN, len(caught), len(names),
             ", ".join(sorted(set(names) - set(caught)))))
    print()
    print("  > This is why no vocabulary proxy can measure B1 conformance: the")
    print("  > construct is present, the word is not, and no word covers it.")

    # ---------------------------------------------------------------- 5
    print()
    print("-" * 96)
    print("5  THE REPAIR: a declared protocol block, and how many families emit one")
    print("-" * 96)
    SCHEMA = {
        "protocol": {
            "version": "B1/v1",
            "obligation": "<str: what the family must do, stated without family labels>",
            "state_sufficient": "<bool: a state set sufficient for the obligation was exhibited>",
            "lower_bound": "<int|null: proved floor on the native coordinate, null if none>",
            "upper_bound_construction": "<str|null: identifier of the exhibited realization>",
            "coordinate": "<str: the native complexity coordinate, e.g. 'states', 'cells'>",
            "resource_law": "<str|null: the lifecycle/reuse law charged>",
            "negative_control": "<str|null: receipt key of the arm that must fail>",
            "prediction_frozen_before_outcome": "<bool>",
            "neutral_search_blind_to_family": "<bool>",
            "replication": "<list[str]: independent re-derivations, e.g. ['disjoint-encoding']>",
        }
    }
    print("  schema (one block per receipt):")
    for line in json.dumps(SCHEMA, indent=2).splitlines():
        print("      " + line)

    required = set(SCHEMA["protocol"])
    compliant, partial = [], []
    for fam in sorted(FAMILIES):
        d = json.load(open(os.path.join(RESULTS, FAMILIES[fam][1])))
        blk = d.get("protocol") if isinstance(d, dict) else None
        if isinstance(blk, dict) and required <= set(blk):
            compliant.append(fam)
        elif isinstance(blk, dict):
            partial.append(fam)
    out["protocol_block"] = {"schema_fields": sorted(required),
                             "compliant": compliant, "partial": partial,
                             "total": len(FAMILIES)}
    print()
    print("  families emitting a complete protocol block: %d of %d"
          % (len(compliant), len(FAMILIES)))
    print("  families emitting a partial block:           %d of %d"
          % (len(partial), len(FAMILIES)))
    assert not compliant or len(compliant) == len(FAMILIES), (
        "some families emit a protocol block and some do not -- partial "
        "emission invites a reader to mistake it for partial conformance; "
        "either none or all")

    # ---------------------------------------------------------------- 6
    print()
    print("=" * 96)
    print("WHAT THIS AUDIT ESTABLISHES")
    print("=" * 96)
    print("  1. For the two requirements with hand-adjudicated answers, the")
    print("     vocabulary signal is wrong in both directions: it misses %d"
          % cm_twin["fn"])
    print("     real matched controls and its ONLY %d positives for real-regime"
          % cm_real["fp"])
    print("     replication are substring artefacts ('production system',")
    print("     'reproduction').  Adjudicated real-regime replication: 0 of %d."
          % len(FAMILIES))
    print("  2. Widening to witness source saturates %d of %d signals, so the"
          % (len(sat), len(KEYPAT)))
    print("     failure is not fixable by loosening the pattern.")
    print("  3. The cause is exhibited: %d families build a matched negative"
          % sum(len(v) for v in names.values()))
    print("     control under %d different names with no shared token." % len(names))
    print()
    if not compliant:
        print("  Therefore B1 conformance is NOT recoverable from the artifacts as")
        print("  currently emitted, for the requirements tested here.  That is a")
        print("  statement about the artifacts, not about the derivations: the")
        print("  constructs are present, they are simply not declared.")
    else:
        print("  THE REPAIR HAS BEEN APPLIED.  All %d families now declare a"
              % len(compliant))
        print("  protocol block, so conformance is readable from the artifacts")
        print("  without any of the proxies above.  Sections 2-4 are retained as")
        print("  the record of WHY declaration was necessary: they are what the")
        print("  corpus looked like before it, and they still hold against the")
        print("  non-declared parts of every receipt.")
        print()
        print("  What a declared block does NOT do is make itself true.  Each")
        print("  field was hand-adjudicated against the receipt it describes,")
        print("  and the block is only as good as that adjudication.  It moves")
        print("  the claim from unverifiable to checkable, not to proven.")
    print()
    print("  B1 is NOT closed by this audit.  Two of its requirements are")
    print("  measured (11 of 19 and 0 of 19); the rest are now DECLARED rather")
    print("  than measured, by %d of %d families, which is a different and"
          % (len(compliant), len(FAMILIES)))
    print("  weaker thing.  A declaration can be checked against its receipt")
    print("  and can be wrong; a measurement cannot be asserted into existence.")
    print()
    print("  Caveat carried forward, and it bears on the frozen-prediction")
    print("  requirement that this audit could NOT validate: a prediction")
    print("  computed earlier in the SAME run is not a pre-registration, and")
    print("  most of this corpus is retrospective.")

    os.makedirs(RESULTS, exist_ok=True)
    with open(os.path.join(RESULTS, "STAGE_PROTOCOL_CONFORMANCE_V1.json"), "w") as fh:
        json.dump(out, fh, indent=2, sort_keys=True)
    print()
    print("  receipt: microscopes/results/STAGE_PROTOCOL_CONFORMANCE_V1.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
