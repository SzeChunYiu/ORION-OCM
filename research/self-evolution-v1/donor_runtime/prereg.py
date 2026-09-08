"""Commitment-derived pre-registration (CL-D4).

Human-subjects pre-registration relies on a trusted timestamp and good faith.  A
machine programme can do better: make the protected draw a deterministic
function of the plan, so that choosing tasks after seeing outcomes is not merely
discouraged but *visible*.

    plan             canonical JSON of the frozen protocol
    commitment       sha256(plan)
    protected_seed   sha256(commitment || "protected-draw-v1")
    pilot_seed       sha256(commitment || "pilot-v1")
    permutation_seed sha256(commitment || "permutation-v1")

Consequences that matter to a reviewer:

* the protected worlds cannot have been chosen after the outcomes were seen
  without changing the commitment;
* any third party can re-derive the exact protected draw from the published plan
  and check that the reported worlds are the ones the plan implies;
* editing the analysis plan changes the commitment and therefore changes the
  draw, which makes silent analysis drift mechanically visible rather than a
  matter of trust.

The pilot stream is disjoint from the protected stream by construction, so pilot
data cannot be relabelled as confirmatory without the digests disagreeing.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Mapping

__all__ = ["Commitment", "canonical_json", "commit"]


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@dataclass(frozen=True)
class Commitment:
    """A frozen plan and the seed streams it determines."""

    plan: Mapping[str, Any]
    commitment: str
    protected_seed: str
    pilot_seed: str
    permutation_seed: str

    def stream(self, label: str) -> int:
        """A derived integer stream for any registered sub-draw."""
        return int(_sha((self.commitment + "||" + label).encode()), 16)

    def as_dict(self) -> dict:
        return {
            "commitment_sha256": self.commitment,
            "protected_seed": self.protected_seed,
            "pilot_seed": self.pilot_seed,
            "permutation_seed": self.permutation_seed,
            "plan": dict(self.plan),
        }


def commit(plan: Mapping[str, Any]) -> Commitment:
    body = canonical_json(plan).encode()
    c = _sha(body)
    return Commitment(
        plan=plan,
        commitment=c,
        protected_seed=_sha((c + "||protected-draw-v1").encode()),
        pilot_seed=_sha((c + "||pilot-v1").encode()),
        permutation_seed=_sha((c + "||permutation-v1").encode()),
    )
