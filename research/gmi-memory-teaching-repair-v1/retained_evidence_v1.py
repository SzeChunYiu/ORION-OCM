"""Static retained records only; no historical candidate or learner execution."""
import json
from fractions import Fraction as F
from sources_v1 import verify_sources, sha

PREFIX = "research/machine-intelligence-morphogenesis-v1/microscopes/results/"
NAMES = {"compiled_search", "constant_emitter", "exemplar_table", "gradient_net_h2",
         "gradient_net_h4", "hamming_knn_k3", "particles_p4", "program_search",
         "soft_retrieval"}

def parse_niche(raw):
    packet = json.loads(raw, parse_float=F)
    if set(packet) != {"band", "ecologies", "interventions", "results", "schema", "seed"}:
        raise ValueError("unexpected retained schema")
    if packet["schema"] != "OpenNicheTestV1":
        raise ValueError("wrong schema")
    results, ecologies = packet["results"], packet["ecologies"]
    expected = {"E_open"+str(i) for i in range(1, 13)}
    if set(results) != expected or set(ecologies) != expected:
        raise ValueError("ecology coverage")
    if len(packet["interventions"]) != 6 or len(set(packet["interventions"])) != 6:
        raise ValueError("intervention declarations")
    admitted, winners, scores = [], [], []
    for name in sorted(results):
        record = results[name]
        if set(record) != {"best_constant", "rows"} or set(record["rows"]) != NAMES:
            raise ValueError("row coverage")
        if record["best_constant"] != ecologies[name]["best_constant"]:
            raise ValueError("baseline copies disagree")
        for row_name, row in record["rows"].items():
            if set(row) != {"admissible", "min_over_six"}:
                raise ValueError("row schema")
            if type(row["admissible"]) is not bool:
                raise ValueError("admission flag must be Boolean")
            score = row["min_over_six"]
            if type(score) not in (int, F) or not 0 <= score <= 1:
                raise ValueError("invalid capability")
            if row["admissible"]:
                admitted.append([name, row_name])
        search = record["rows"]["program_search"]["min_over_six"]
        top = max(row["min_over_six"] for row in record["rows"].values())
        if search == top:
            winners.append(name)
        scores.append(search)
    return dict(rows=108, ecologies=12, admitted=admitted,
                search_top_including_ties=winners, minimum_search=min(scores),
                O1_all_search_admitted=all(results[e]["rows"]["program_search"]["admissible"]
                                            for e in results),
                O2_search_always_top=len(winners)==12,
                O3_all_search_at_least_0887=all(s >= F(887,1000) for s in scores),
                recorded=packet, provenance="UNVERIFIABLE_FROM_RETAINED_FIELDS")

def boundary(baseline, upper=F(1), margin=F(1,24)):
    for x in (baseline, upper, margin):
        if type(x) not in (int, F) or x < 0:
            raise ValueError("exact nonnegative contract required")
    return upper-baseline < margin

def rounded_difference(a, b, radius=F(1,20000)):
    if radius < 0:
        raise ValueError("invalid envelope")
    return (a-b-2*radius, a-b+2*radius)

def retained(root):
    sources = verify_sources(root)
    packet = sources[("PR597", PREFIX+"STAGE_OPEN_NICHE_V1.json")]
    niche = parse_niche(packet)
    names = ("STAGE_COMPONENT_LESION_V1.json", "STAGE_MEMORY_REGIME_WITNESS_V1.json",
             "STAGE_TEACHING_CULTURE_WITNESS_V1.json")
    others = {name: json.loads(sources[("PR597",PREFIX+name)], parse_float=F)
              for name in names}
    return dict(open_niche=niche, open_niche_sha256=sha(packet),
                other_retained_records=others,
                old_scripts_executed=False, new_learner_observations=False)
