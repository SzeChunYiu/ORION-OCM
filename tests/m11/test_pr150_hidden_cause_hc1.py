"""Protected HC1: hidden cause, intervention-identifiable minimum, alias refusal, parent parity."""
from __future__ import annotations

import hashlib

from ocm.selfmodel import diagnose as DG
from ocm.selfmodel import model as SM

LAYERS = (
    SM.Layer.D0_PARAMETER,
    SM.Layer.D1_ROUTING,
    SM.Layer.D2_OPERATOR,
    SM.Layer.D5_VOCABULARY,
    SM.Layer.D6_LEARNING_POLICY,
    SM.Layer.D3_REPRESENTATION,
)


def _cause(seed: int) -> SM.Layer:
    raw = hashlib.sha256(f"E150-HC1|{seed}".encode()).digest()
    return LAYERS[int.from_bytes(raw[:8], "big") % len(LAYERS)]


def _parent_minimum(ablations) -> str | None:
    touched = {layer: [] for layer in LAYERS}
    for a in ablations:
        touched[a.layer].append(a.task_succeeded)
    for layer in LAYERS:
        if any(touched[layer]):
            return layer.value
    return None


def _failure(seed: int, ablations) -> SM.FailureRecord:
    # The hidden cause and seed are evaluator-only: neither is included in this record.
    return SM.FailureRecord(
        f"hc1-{seed}", "anonymous-episode", "failure", "wrong action", "restore obligation",
        (f"ev:hc1:{seed}:trace",), LAYERS, tuple(ablations), {}, "LIVE", "high", 1, "research",
    )


def test_hc1_protected_40_hidden_causes_parent_sufficient():
    exact = aliases = disagreements = false_jumps = interventions = 0
    for seed in range(9201, 9241):
        hidden = _cause(seed)  # evaluator-only
        alias = seed % 5 == 0
        ci = LAYERS.index(hidden)
        ablations = []
        for i, layer in enumerate(LAYERS):
            restored = False if alias else i >= ci
            ablations.append(SM.AblationEvidence(f"intervene-{layer.value}", layer, restored, f"ev:hc1:{seed}:{layer.value}"))
        failure = _failure(seed, ablations)
        diagnosis = DG.diagnose(failure)
        parent = _parent_minimum(ablations)
        interventions += len(ablations)
        disagreements += int(diagnosis.minimum_sufficient != parent)
        if alias:
            aliases += int(diagnosis.minimum_sufficient is None and set(diagnosis.unknown) == set())
            allowed, _ = DG.escalation_allowed(diagnosis, None)
            false_jumps += int(allowed)
        else:
            exact += int(diagnosis.minimum_sufficient == hidden.value)
            # A broader successful intervention must not induce a broader repair than the minimum.
            false_jumps += int(diagnosis.minimum_sufficient != hidden.value)

    assert exact == 32
    assert aliases == 8
    assert disagreements == 0
    assert interventions == 240
    assert false_jumps == 0
    # Terminal: PARENT_SUFFICIENT.  OCM and the same-information symbolic parent are identical here.
