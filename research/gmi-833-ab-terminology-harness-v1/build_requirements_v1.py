#!/usr/bin/env python3
"""Author AB_ROW_REQUIREMENTS_V1.json from the live comment text.

Every required comparison term below is quoted from the AB row's own text.
test_ab_harness_v1.py asserts that each required term (or, for a slashed
alternation, each of its alternatives' distinguishing head) literally occurs in
the verbatim row text, so no requirement can be invented and none softened.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
COMMENT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "ISSUE_COMMENT_5684607872_SNAPSHOT.md")

# rowid -> (evidence_kind, bound_crosswalk_term, required_terms)
# required term forms:
#   "x"                        -> must be covered
#   {"any_of": [...]}          -> at least one alternative must be covered
REQ = {
 "AB01": ("CROSSWALK_COLUMNS", None, ["legacy GMI term","proposed paper term","academic field",
          "canonical term(s)","match","citations","definition","migration rule"]),
 "AB03": ("CROSSWALK_ROW", "morphology", ["architecture","computational architecture","model class",
          "representation","algorithm","computational mechanism",
          "structure across heterogeneous computational organizations"]),
 "AB04": ("CROSSWALK_ROW", "machine species", [{"any_of":["algorithm class","configuration class"]},
          "model family","architecture family","behavioral phenotype","equivalence class"]),
 "AB05": ("CROSSWALK_ROW", "ecology", ["task distribution","environment","problem distribution",
          "instance space","operating regime"]),
 "AB06": ("CROSSWALK_ROW", "niche", ["region of instance space","operating regime",
          "performance region","domain of competence"]),
 "AB07": ("CROSSWALK_ROW", "selection", ["algorithm selection","model selection","architecture search",
          {"any_of":["hyperparameter selection","configuration selection"]},"evolutionary selection"]),
 "AB09": ("CROSSWALK_ROW", "phase law / phase diagram", ["phase diagram","control-parameter space",
          "regime map","crossover map"]),
 "AB10": ("CROSSWALK_ROW", ["prior-free","architecture-prior-free"],
          ["architecture-agnostic","architecture-uncommitted",
          "family-agnostic search","architecture-prior-free"]),
 "AB11": ("CROSSWALK_ROW", "inductive bias", ["inductive bias"]),
 "AB12": ("CROSSWALK_ROW", "hypothesis class / possibility space",
          ["hypothesis class","search space","program space","possibility space"]),
 "AB13": ("CROSSWALK_ROW+PARENT_PACKAGE", "DSL/grammar",
          ["DSL","grammar","primitive set","search space","search strategy","bias"]),
 "AB14": ("CROSSWALK_ROW", "neutral search", ["family-blind enumerative search",
          "architecture-agnostic search","grammar-based synthesis","evolutionary search"]),
 "AB15": ("CROSSWALK_ROW", "remint", ["independent regeneration","re-randomization",
          "relabeling control","fresh-instance replication","independent replication"]),
 "AB16": ("CROSSWALK_ROW", "negative twin", ["matched negative control","counterfactual control",
          "ablation","placebo condition","negative control"]),
 "AB17": ("CROSSWALK_ROW", "parent subtraction", [{"any_of":["comparison to strongest baselines",
          "strongest-baseline comparison"]},"subsumption analysis","reduction","ablation","novelty analysis"]),
 "AB18": ("CROSSWALK_ROW", "carrier", ["state representation","state space","memory substrate",
          "computational substrate","representation space"]),
 "AB19": ("CROSSWALK_ROW", "quotient", ["quotient","equivalence classes","state abstraction",
          {"any_of":["minimal sufficient representation","minimal sufficient state"]}]),
 "AB20": ("CROSSWALK_ROW", "capability ceiling", ["upper bound","impossibility result","capacity bound",
          "information-theoretic limit",{"any_of":["sample bound","communication bound","complexity bound"]}]),
 "AB21": ("CROSSWALK_ROW", "development", ["online learning","continual learning","meta-learning",
          "self-modification","architecture adaptation","developmental learning","evolution"]),
 "AB22": ("CROSSWALK_ROW", "evolvability", ["evolvability",
          {"any_of":["evolutionary-computation","evolutionary computation"]},"ALife"]),
 "AB23": ("CROSSWALK_ROW", "open-ended", [{"any_of":["open-ended evolution","open-endedness"]}]),
 "AB24": ("CROSSWALK_ROW", "novel intelligence", ["novel implementation","novel architecture",
          "novel algorithmic mechanism","novel model class",
          {"any_of":["novel computational paradigm","computational paradigm"]},"novel capability profile"]),
 "AB26": ("CROSSWALK_ROW", "unseen form", ["held-out architecture","predicted morphology",
          "novel mechanism","new computational class"]),
 "AB27": ("CROSSWALK_ROW", "cognition terms", ["working","episodic","semantic","procedural",
          "memory","attention","metacognition","theory of mind"]),
 "AB28": ("CROSSWALK_ROW+PARENT_PACKAGE", "cognition terms", ["operational criteria"]),
 "AB29": ("CROSSWALK_ROW", "causal terms", ["SCM","intervention","counterfactual"]),
 "AB30": ("CROSSWALK_ROW", "uncertainty terms", ["aleatoric","epistemic","confidence set",
          "credible set","calibration","identifiability","partial identification"]),
 "AB31": ("CROSSWALK_ROW", "verification", ["formal verification","empirical validation","evaluation",
          "testing","certification","verifier feedback"]),
 "AB32": ("CROSSWALK_ROW", ["proof","proof (computer-assisted)","proof (finite enumeration)"],
          ["exhaustive finite computation","certificate","computer-assisted"]),
 "AB33": ("CROSSWALK_ROW", "derive", ["recover","select","fit","construct","reproduce","explain"]),
 "AB34": ("CROSSWALK_ROW", "predict", [{"any_of":["temporal/epistemic separation","temporal","epistemic"]},
          "post-hoc explanation","reconstruction"]),
 "AB35": ("CROSSWALK_ROW", "discover", ["encoded","named","privileged","parent reduction"]),
 "AB36": ("ARTIFACT", "banned list", [{"any_of":["banned","avoid"]},"misleading","manuscripts"]),
 "AB37": ("ARTIFACT", "ci gate", ["CI", "gate"]),
}


def main():
    src = open(COMMENT).read().split("\n")
    cur = None
    n = 0
    rows = {}
    for l in src:
        if l.startswith("### "):
            cur = l.split(".")[0].replace("### ", "")
            n = 0
        elif l.startswith("- [ ] ") and cur == "AB":
            n += 1
            rows["AB%02d" % n] = l
    out = {"schema": "GMI_AB_ROW_REQUIREMENTS_V1", "issue": 833,
           "comment_id": 5684607872,
           "anchor": "### AB. Academic terminology and ontology normalization",
           "extraction_rule": "Each required comparison term is quoted from the row's own text. "
                              "A slashed alternation in the row becomes an any_of requirement over its "
                              "alternatives. test_ab_harness_v1 asserts every required term literally "
                              "occurs in the verbatim row text.",
           "rows": []}
    for rid in sorted(REQ):
        kind, term, reqs = REQ[rid]
        out["rows"].append({"row_id": rid, "verbatim": rows[rid], "evidence_kind": kind,
                            "crosswalk_term": term, "required_terms": reqs})
    out["rows_not_in_scope"] = {k: rows[k] for k in sorted(rows) if k not in REQ}
    path = os.path.join(HERE, "AB_ROW_REQUIREMENTS_V1.json")
    json.dump(out, open(path, "w"), indent=2, sort_keys=False)
    print("wrote %s rows=%d not_in_scope=%d" % (path, len(out["rows"]), len(out["rows_not_in_scope"])))


if __name__ == "__main__":
    main()
