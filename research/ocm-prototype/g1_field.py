"""Minimal G1 persistent field; content-bound donor archive counts as state."""
import json
import shutil
from ocm.kso.ids import content_hash
from ocm.kso.space import Atom, Hyperedge
from ocm.kso.types import Scope
from ocm.kso.warrant import WarrantProfile, meet_all_profiles
from ocm.store.evidence import Channel
from udpipe_donor import sha256

SCOPE = Scope.of("g1-pilot")
ROOT, MODEL, CLIA, FIXTURE = "g1:root", "g1:model", "g1:clia", "g1:fixture"


def encode(data):
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def payload(ks, atom_id):
    atom = ks.atom_map()[atom_id]
    data = json.loads(dict(atom.meta)["data"])
    if content_hash(data) != atom.content_ref:
        raise ValueError("field payload identity changed")
    return data


def put(runtime, atom_id, data, warrant, parents=(ROOT,), certificate="INSTRUCTION", kind="procedure"):
    if atom_id in runtime.state.ks.ids:
        if payload(runtime.state.ks, atom_id) != data:
            raise ValueError("field identity collision")
        return atom_id
    edges = tuple(Hyperedge("support:" + atom_id + ":" + p, (p,), (atom_id,),
                            "SUPPORT", warrant=warrant) for p in parents)
    runtime.admit_object(Atom(atom_id, kind, warrant, scope=SCOPE, quarantined=not parents,
        content_ref=content_hash(data), meta=(("data", encode(data)),)), edges, certificate)
    return atom_id


def warrant(runtime, parents):
    return meet_all_profiles(runtime.state.ks.atom_map()[p].warrant for p in parents)


def archive_path(runtime, digest):
    if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
        raise ValueError("invalid archive identity")
    return runtime.root / "archive" / (digest + ".udpipe")


def setup(runtime, model_path, training_manifest):
    digest = sha256(model_path)
    if FIXTURE in runtime.state.ks.ids:
        current = payload(runtime.state.ks, MODEL)
        if current["sha256"] != digest or current["training"] != training_manifest:
            raise ValueError("existing vessel model/training mismatch; use a fresh state directory")
        if sha256(archive_path(runtime, digest)) != digest:
            raise ValueError("persisted archive identity mismatch")
        return payload(runtime.state.ks, FIXTURE)
    target = archive_path(runtime, digest)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(model_path, target)
    if sha256(target) != digest:
        raise ValueError("archive copy mismatch")
    _, prior = runtime.admit_evidence({"prior": "fixed G1 public task and checker grammar contracts"},
        Channel.INSTRUCTION, "host-prior", scope=SCOPE)
    put(runtime, ROOT, {"prior": prior}, WarrantProfile.of({prior}), ())
    _, model_evidence = runtime.admit_evidence({"sha256": digest, "training": training_manifest},
        Channel.OBSERVATION, "training-artifact", scope=SCOPE)
    put(runtime, MODEL, {"sha256": digest, "bytes": target.stat().st_size, "training": training_manifest,
        "architecture": "UDPipe1 non-Transformer tagger and feedforward transition parser",
        "parameters": "CANNOT_CHECK: scalar count unavailable via public model API"},
        WarrantProfile.of({model_evidence}), certificate="OBSERVATION", kind="model")
    put(runtime, CLIA, {"prior": "public CLIA specifications and independently checked output grammar"},
        WarrantProfile.of({prior}))
    fixture = {"model_evidence": model_evidence, "prior": prior, "model_sha256": digest,
               "archive_bytes": target.stat().st_size, "revocation_unit": "whole model version"}
    put(runtime, FIXTURE, fixture, WarrantProfile.of({prior}))
    runtime.persist()
    return fixture
