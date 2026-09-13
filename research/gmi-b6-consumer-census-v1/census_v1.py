"""Full deterministic source-bound census. Does not run any saved genotype."""
from contract_v1 import sha
from inputs_v1 import load_inputs
from native_roles_v1 import native_contract
from graph_census_v1 import describe, summarize
from cohorts_v1 import read_cohorts, source_rows
from source_population_v1 import population_evidence
from oracle_v1 import compare


def run(base=None):
    binding, files = load_inputs() if base is None else load_inputs(base)
    kinds, roles = native_contract(files)
    arms, raw, subset = read_cohorts(files)
    sources, source_raw = source_rows(files)
    def analyze(rows):
        result = []
        for row in rows:
            description = describe(row["label"], row["text"], kinds, roles)
            compare(row, description, roles)
            description["origin"] = row["origin"]
            if "recorded_fingerprint" in row:
                description["recorded_fingerprint"] = row["recorded_fingerprint"]
                description["standard_capability"] = row["standard_capability"]
            result.append(description)
        return result
    all_graphs, scan_graphs, source_graphs = analyze(raw), analyze(subset), analyze(source_raw)
    source_summary = []
    for sid, (member, source) in sorted(sources.items()):
        rows = [r for r in source_graphs if r["origin"]["member"] == member]
        source_summary.append({"member": member, "receipt_id": sid,
                               "summary": summarize(rows),
                               "GRAD_graphs": [r for r in rows if "GRAD" in r["kinds"]]})
    legacy = sum(any(e["kind"] in ("DOT", "LINEAR") for e in r["direct_dense_consumers"])
                 for r in scan_graphs)
    return {"schema": "B6_CONSUMER_CENSUS_RECEIPT_V1", "status": "STATIC_CENSUS_VERIFIED",
            "pr_head": binding["pr_head"], "reviewed_head": binding["reviewed_head"], "prior_main": binding["prior_main"],
            "input_archive_sha256": binding["archive_sha256"],
            "native_source_sha256": {p: sha(v) for p, v in files.items() if p.startswith("native/")},
            "native_roles": roles, "native_kinds": sorted(kinds),
            "all_arm_rows": all_graphs, "all_arm_summary": summarize(all_graphs),
            "legacy_scan_rows": scan_graphs, "legacy_scan_summary": summarize(scan_graphs),
            "legacy_incomplete_whitelist_count": legacy,
            "source_archive_summaries": source_summary,
            "source_population_evidence": population_evidence(arms, sources, source_graphs),
            "recorded_arm_archive_cells_including_duplicate_arm": sum(a["archive_cells_filled"] for a in arms.values()),
            "independent_oracle_row_comparisons": len(raw) + len(subset) + len(source_raw),
            "prior_raw_pruned_strings_and_six_caps_identical": True,
            "scope": {"deduplication": "exact serialized genotype bytes; not graph isomorphism",
                      "adjacency": "native parameter ports through identity EDGE only",
                      "output_ancestry": "syntactic; not causal or lifetime dependency completeness",
                      "source_seed_matches": "recorded fingerprint identity; not invocation authentication",
                      "all_final_archive_or_search_graphs_observed": False,
                      "causal_coefficient_use_or_admissible_learning_established": False,
                      "new_search_ecology_priming_timing_calls": 0}}
