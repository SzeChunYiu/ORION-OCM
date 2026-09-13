"""Exact disjoint source fields and explicit overlaps; no inferred full archive."""
from contract_v1 import require, receipt_self_hash, same, sha, strict_json


def read_cohorts(files):
    manifest = strict_json(files["pr551/MANIFEST.json"])
    require(manifest["schema"] == "B6ArmEvidenceManifestV1", "arm manifest schema")
    arms, all_rows, scan_rows = {}, [], []
    def row(label, text, origin):
        return {"label": label, "text": text, "origin": origin}
    for name, metadata in sorted(manifest["arms"].items()):
        raw = files["pr551/" + name]
        require(len(raw) == metadata["bytes"] and sha(raw) == metadata["sha256"], "arm byte drift")
        arm = strict_json(raw)
        require(receipt_self_hash(arm) == arm["receipt_sha256"] == metadata["receipt_sha256_field"],
                "arm internal self hash drift")
        require(arm["schema"] == "StageB6DevelopmentArmV1", "arm schema")
        for field in ("pair", "arm", "seed"): same(arm[field], metadata[field], "arm metadata")
        same(arm["first_dense_admissible"]["found"], metadata["dense_found"], "hit metadata")
        same(arm["seeding"].get("source_receipt_sha256"), metadata["source_receipt_sha256"],
             "source reference metadata")
        label = f"{arm['pair']}/{arm['arm']}/S{arm['seed']}"
        require(label not in arms, "duplicate arm identity")
        arms[label] = arm
        for carrier, item in sorted(arm["final_best_genotypes"].items()):
            r = row(label + "/archive-best-" + carrier, item["genotype"],
                    {"member": "pr551/" + name, "fields": ["final_best_genotypes", carrier, "genotype"]})
            all_rows.append(r)
            if carrier == "DENSE": scan_rows.append(r)
        for field in ("genotype", "atrophied_genotype"):
            text = arm["first_admissible"][field]
            r = row(label + "/first-admissible/" + field, text,
                    {"member": "pr551/" + name, "fields": ["first_admissible", field]})
            all_rows.append(r)
            if field == "atrophied_genotype" and any(v[0] == "DENSE" for v in strict_json(text)["nodes"].values()):
                scan_rows.append(r)
    witness_name = "pr551/STAGE_B6_DENSE_WITNESS_SAME_CONTINUED_S1_billy.json"
    witness = strict_json(files[witness_name])
    for field in ("genotype_raw", "genotype_atrophied"):
        scan_rows.append(row("witness/" + field, witness[field],
                             {"member": witness_name, "fields": [field]}))
    prior = strict_json(files["prior/WITNESS.json"])
    same(witness["genotype_raw"], prior["raw_genotype"], "prior raw witness differs")
    same(witness["genotype_atrophied"], prior["verifier"]["atrophied_genotype"], "prior pruned differs")
    same(witness["reverified"]["caps_over_six"], prior["verifier"]["caps"], "prior six caps differ")
    return arms, all_rows, scan_rows


def source_rows(files):
    sources, rows = {}, []
    for member in sorted(files):
        if not member.startswith("sources/"): continue
        source = strict_json(files[member])
        require(source["schema"] == "StageB6DevelopmentSourceV1", "source schema")
        require(receipt_self_hash(source) == source["receipt_sha256"], "source self hash drift")
        require(source["receipt_sha256"] not in sources, "duplicate source receipt")
        sources[source["receipt_sha256"]] = (member, source)
        for cell, value in sorted(source["cells"].items()):
            rows.append({"label": member + "/cells/" + cell, "text": value["genotype"],
                         "origin": {"member": member, "fields": ["cells", cell, "genotype"]},
                         "recorded_fingerprint": value["fingerprint"],
                         "standard_capability": value["capability"]})
    return sources, rows
