"""Write CINV + publication RESULT.json."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[0].parent / "publication-constitution-v1"))

from audit import audit
from gate import review_proposed_work


def main(out: Path) -> dict:
    cinv = audit()
    proto = json.loads((Path(__file__).resolve().parents[0].parent / "publication-constitution-v1" / "PROTOCOL.json").read_text())
    result = {
        "schema": "ocm.cinv-and-publication.v1",
        "cinv_terminal": cinv["terminal"],
        "cinv": cinv,
        "publication_terminal": "PUBLICATION_CONSTITUTION_FROZEN_WITH_GAPS",
        "section16": proto["section16"],
        "section20_example_ok": review_proposed_work({
            "principle": "epistemic contract",
            "mechanism": "failure memory",
            "prediction": "dead-end reduction",
            "evidence": "G3.2",
            "parent": "TMS",
            "closure": "G3.2",
        }),
        "claim_ceiling": "Live invariant tests plus a freeze document. Missing E4/fresh-host marked MISSING, not invented.",
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"cinv": cinv["terminal"], "publication": result["publication_terminal"], "n_pass": cinv["n_pass"]}))
    return result


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent / "RESULT.json"
    main(target)
