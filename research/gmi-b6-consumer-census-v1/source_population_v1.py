"""Validate selected-source metadata where available; absent parents remain unknown."""
from contract_v1 import require, same

CARRIERS = ("NONE", "DENSE", "TABLE", "KVSTORE", "PROGRAM")


def population_evidence(arms, sources, described_sources):
    checked, unknown, matches = [], [], []
    gradients = [r for r in described_sources if "GRAD" in r["kinds"]]
    by_fingerprint = {}
    for row in gradients:
        by_fingerprint.setdefault(row["recorded_fingerprint"], []).append(row)
    for label, arm in sorted(arms.items()):
        seeding = arm["seeding"]
        sid = seeding.get("source_receipt_sha256")
        if sid is not None and sid not in sources:
            unknown.append({"arm": label, "referenced_source_id": sid,
                            "status": "UNVERIFIABLE_FROM_PINNED_PACKET"})
        if sid in sources:
            member, source = sources[sid]
            same(source["ecology"], seeding["source_ecology"], "selected source ecology")
            same(source["seed"], arm["seed"], "selected source seed")
            selected = []
            for carrier in CARRIERS:
                cells = sorted((v for v in source["cells"].values() if v["carrier_raw"] == carrier),
                               key=lambda v: (-v["capability"], v["fingerprint"]))
                count = seeding["matched_k_per_carrier"][carrier]
                require(type(count) is int and 0 <= count <= len(cells), "invalid matched count")
                selected.extend(cells[:count])
            same(seeding["n_seeds"], len(selected), "selected seed count")
            for field, src in (("seed_fingerprints", "fingerprint"),
                               ("seed_source_capabilities", "capability"),
                               ("seed_carriers_raw", "carrier_raw")):
                same(seeding[field], [v[src] for v in selected], "selected population field: " + field)
            checked.append({"arm": label, "source_member": member, "selected_source_top_k_verified": True})
        for index, fp in enumerate(seeding.get("seed_fingerprints", [])):
            for row in by_fingerprint.get(fp, []):
                matches.append({"arm": label, "seed_index": index, "recorded_fingerprint": fp,
                                "known_source_graph": row["origin"],
                                "declared_source_id_matches": sid in sources and
                                sources[sid][0] == row["origin"]["member"]})
    return {"selected_source_checks": checked, "unavailable_selected_sources": unknown,
            "recorded_seed_fingerprint_matches_to_GRAD_graphs": matches,
            "all_matched_parent_archives_reconstructed": False,
            "seed_fingerprints_are_execution_authentication": False}
