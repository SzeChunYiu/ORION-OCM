"""Identical forms-only Stanza proposals and structure checks for both arms."""
import time
from stanza_donor import document_words, load_pipeline
from syntax_contract import validate as syntax_validate, validate_tokens
import g1_stanza_profile as P

SYNTAX_OPERATOR = "syntax:stanza-recurrent"
_PIPELINES = {}


def inference_context():
    import torch
    return torch.inference_mode()


def predict(tokens, bundle, profile):
    start = time.perf_counter()
    try:
        validate_tokens(tokens)
        P.validate(profile)
        hash_wall = 0.0
        key = (str(bundle.resolve()), profile["id"])
        loaded = key not in _PIPELINES
        loading = time.perf_counter()
        if loaded:
            hashing = time.perf_counter()
            P.verify_archive(bundle, profile)
            hash_wall += time.perf_counter() - hashing
            plan = {"models": profile["models"], "packages": profile["packages"]}
            acquired = load_pipeline(plan, model_root=bundle/"models")
            hashing = time.perf_counter()
            P.verify_archive(bundle, profile)
            hash_wall += time.perf_counter() - hashing
            _PIPELINES[key] = acquired
        pipeline, loads = _PIPELINES[key]
        load_wall = time.perf_counter() - loading
        forms = list(tokens)
        with inference_context():
            document = pipeline([forms])
    except (OSError, ImportError, ValueError, RuntimeError, KeyError, TypeError) as exc:
        return {"status": "CANNOT_CHECK", "reason": "DONOR_OR_CUSTODY_UNAVAILABLE",
                "detail": type(exc).__name__ + ": " + str(exc), "donor_wall_seconds": time.perf_counter()-start}
    try:
        words = document_words(document, forms)
    except (ValueError, TypeError, AttributeError, IndexError) as exc:
        return {"status": "INPUT_CONTRACT_MISMATCH", "reason": str(exc),
                "donor_wall_seconds": time.perf_counter()-start}
    return {"status": "PREDICTED", "words": words, "model_sha256": profile["model_sha256"],
        "profile_id": profile["id"], "model_loaded": loaded, "checkpoint_loads": loads,
        "load_boundary_hash_seconds": hash_wall, "load_and_hash_seconds": load_wall,
        "donor_wall_seconds": time.perf_counter()-start,
        "cache_scope": "One process and exact archive/profile; no pipeline survives process restart.",
        "custody_scope": "Trusted fixed-source pipeline; full hashes at load and worker entry/end, not every sentence."}


def check(profile, request, output):
    """Structural validity and model custody only; no gold or correctness oracle."""
    P.validate(profile)
    if output.get("status") == "CANNOT_CHECK":
        return {"status": "CANNOT_CHECK", "reason": output.get("reason")}
    if output.get("status") != "PREDICTED" or output.get("model_sha256") != profile["model_sha256"]:
        return {"status": "FAIL", "reason": "MODEL_OR_OUTPUT_BINDING"}
    reason = syntax_validate(output.get("words"), request["tokens"])
    return {"status": "FAIL" if reason else "PASS", "reason": reason,
            "scope": "STRUCTURE_ONLY_NO_GOLD_CORRECTNESS"}
