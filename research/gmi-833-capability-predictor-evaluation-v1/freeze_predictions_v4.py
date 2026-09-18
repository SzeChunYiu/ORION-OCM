"""Freeze the power-revival predictions (SIGMA_SYN2 / SIGMA_ARCH2).

Adds a POINT-VALUE census to the power block: the defect this revival fixes is
that every identified point on the V1 universes was degenerate.  The census is
computed from predictions only -- no outcome oracle is consulted -- so tuning the
grid against it before the freeze is legitimate, and after the freeze it is
fixed.

Run:  python3 -I -B freeze_predictions_v4.py
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import heldout_universes_v1 as hu    # noqa: E402
import heldout_universes_v2 as hv2   # noqa: E402
import heldout_universes_v3 as hv3   # noqa: E402
import heldout_universes_v4 as hv4   # noqa: E402
import freeze_predictions_v1 as fp   # noqa: E402


def point_value_census(parent):
    counts = {}
    for k_index in range(len(parent.K_M_VALUES)):
        for r_value in parent.R_VALUES:
            for d_value in parent.D_VALUES:
                for b_value in parent.B_VALUES:
                    for h_value in parent.H_VALUES:
                        for u_id, u_kind, u_mask, alpha in parent.U_VALUES:
                            for contract in parent.CONTRACTS:
                                for tau in parent.TAU_VALUES:
                                    entry = (k_index, r_value, d_value, b_value, h_value,
                                             u_id, u_kind, u_mask, alpha, contract, tau)
                                    emission = parent.evaluate(entry)[0]
                                    if emission.disposition != "IDENTIFIED":
                                        continue
                                    key = fp.frac_str(emission.value)
                                    counts[key] = counts.get(key, 0) + 1
    nondegenerate = sum(v for k, v in counts.items() if k not in ("UNSATISFIED", "0"))
    return {
        "point_values": dict(sorted(counts.items())),
        "distinct_point_values": len(counts),
        "nondegenerate_point_emissions": nondegenerate,
        "degenerate_point_emissions": sum(counts.get(k, 0) for k in ("UNSATISFIED", "0")),
    }


def main():
    parent = hu.load_parent()
    base = hu.sigma_1()
    baseline = hu.code_fingerprint(parent)
    prior = [("SIGMA_1", base), ("SIGMA_SYN", hu.SYN_RAW), ("SIGMA_ARCH", hu.ARCH_RAW),
             ("SIGMA_REAL", hu.REAL_RAW), ("SIGMA_REAL2", hv2.REAL2_RAW),
             ("SIGMA_REAL3", hv3.REAL3_RAW)]
    out = {
        "schema": "GMI_833_K_EVAL_FROZEN_PREDICTIONS_V4",
        "amends": ("adds SIGMA_SYN2 and SIGMA_ARCH2; every earlier freeze and "
                   "universe module is left byte-identical"),
        "claim_ceiling": fp.CLAIM_CEILING,
        "parent_file_blob_sha": hu.git_blob_sha(hu.PARENT_FILE),
        "universes": [],
    }
    samples = []
    for builder in (hv4.sigma_syn2, hv4.sigma_arch2):
        spec = builder()
        name = spec["__name__"]
        certs = [hu.disjointness_certificate(raw, label, spec["UNIVERSE"], name)
                 for label, raw in prior]
        clean = dict((k, v) for k, v in spec.items() if not k.startswith("__"))
        fingerprint = hu.install_universe(parent, clean)
        sdig, _payload = fp.spec_digest(spec)
        summary, stream = fp.sweep(parent, name)
        summary["spec_sha256"] = sdig
        summary["disjointness"] = certs
        summary["curves"] = fp.build_curves(parent)
        summary["power"].update(point_value_census(parent))
        summary["parent_code_unchanged"] = (fingerprint[0] == baseline[0])
        out["universes"].append(summary)
        prior.append((name, tuple(spec["UNIVERSE"])))
        lines = stream.rstrip("\n").split("\n")
        samples.append("# universe=%s rows=%d rule=every_101st_row" % (name, len(lines)))
        for i in range(0, len(lines), 101):
            samples.append(name + "\t" + lines[i])
    body = fp.canonical_json(out)
    text = json.dumps(json.loads(body), indent=2, sort_keys=True)
    with open(os.path.join(HERE, "FROZEN_PREDICTIONS_V4.json"), "w") as handle:
        handle.write(text)
        handle.write("\n")
    with open(os.path.join(HERE, "FROZEN_PREDICTION_SAMPLE_V4.tsv"), "w") as handle:
        handle.write("\n".join(samples) + "\n")
    sys.stdout.write(text)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
