"""Reuse existing G1 field primitives with the full qualified Stanza archive."""
from ocm.kso.warrant import WarrantProfile
from ocm.store.evidence import Channel
from g1_field import ROOT, MODEL, CLIA, FIXTURE, SCOPE, payload, put
import g1_stanza_profile as P


def setup(runtime, source_models, profile):
    bundle = P.prepare(runtime.root, source_models, profile)
    if FIXTURE in runtime.state.ks.ids:
        current = payload(runtime.state.ks, MODEL)
        if current.get("stanza_profile") != profile:
            raise ValueError("existing vessel donor mismatch; use a fresh state")
        return payload(runtime.state.ks, FIXTURE)
    _, prior = runtime.admit_evidence({"prior": "fixed G1 public task and checker grammar contracts"},
        Channel.INSTRUCTION, "host-prior", scope=SCOPE)
    put(runtime, ROOT, {"prior": prior}, WarrantProfile.of({prior}), ())
    _, model = runtime.admit_evidence({"stanza_profile": profile},
        Channel.OBSERVATION, "qualified-training-artifact", scope=SCOPE)
    archive_bytes = sum(p.stat().st_size for p in bundle.rglob("*") if p.is_file())
    put(runtime, MODEL, {"sha256": profile["model_sha256"], "bytes": archive_bytes,
        "stanza_profile": profile, "training": {"lineage_sha256": profile["training_lineage_sha256"]},
        "architecture": "Stanza recurrent POS/lemma/graph parser; qualified nocharlm/noTransformer",
        "parameters": {"unique_elements": 58559868, "frozen_vectors": 25000000}},
        WarrantProfile.of({model}), certificate="OBSERVATION", kind="model")
    put(runtime, CLIA, {"prior": "public CLIA specifications and independently checked output grammar"},
        WarrantProfile.of({prior}))
    fixture = {"model_evidence": model, "prior": prior, "model_sha256": profile["model_sha256"],
        "profile_id": profile["id"], "archive_bytes": archive_bytes, "revocation_unit": "whole model version"}
    put(runtime, FIXTURE, fixture, WarrantProfile.of({prior}))
    runtime.persist()
    return fixture
