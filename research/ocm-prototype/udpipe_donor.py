"""ADAPT forms-only UDPipe1 inference; no annotation or gold-reader imports."""
import hashlib
from importlib.metadata import version
import time
from syntax_contract import validate_tokens

_MODELS = {}


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def predict(tokens, archive, expected_sha256):
    try:
        return _predict(tokens, archive, expected_sha256)
    except (OSError, ImportError) as exc:
        return {"status": "CANNOT_CHECK", "reason": "DONOR_UNAVAILABLE", "detail": str(exc)}


def _predict(tokens, archive, expected_sha256):
    start = time.perf_counter()
    validate_tokens(tokens)
    if version("ufal.udpipe") != "1.4.0.1":
        return {"status": "CANNOT_CHECK", "reason": "UDPIPE_VERSION"}
    if not archive.is_file() or sha256(archive) != expected_sha256:
        return {"status": "CANNOT_CHECK", "reason": "MODEL_BINDING"}
    hash_seconds = time.perf_counter() - start
    import ufal.udpipe as u
    key = (str(archive.resolve()), expected_sha256)
    loaded = key not in _MODELS
    if loaded:
        model = u.Model.load(str(archive))
        if model is None:
            return {"status": "CANNOT_CHECK", "reason": "MODEL_LOAD"}
        _MODELS[key] = model
    model = _MODELS[key]
    sentence = u.Sentence()
    for form in tokens:
        sentence.addWord(form)
    assert all(not w.upostag and not w.lemma and w.head < 0 for w in list(sentence.words)[1:])
    error = u.ProcessingError()
    if not model.tag(sentence, u.Model.DEFAULT, error):
        return {"status": "CANNOT_CHECK", "reason": "TAGGER_ERROR", "detail": error.message}
    if not model.parse(sentence, u.Model.DEFAULT, error):
        return {"status": "CANNOT_CHECK", "reason": "PARSER_ERROR", "detail": error.message}
    words = [{"id": w.id, "form": w.form, "head": w.head, "deprel": w.deprel,
              "upos": w.upostag} for w in list(sentence.words)[1:]]
    # Recheck before releasing a version-bound observation. This is trusted-host
    # custody, not adversarial process isolation or evidence of parse correctness.
    if sha256(archive) != expected_sha256:
        return {"status": "CANNOT_CHECK", "reason": "MODEL_CHANGED"}
    return {"status": "PREDICTED", "words": words, "model_sha256": expected_sha256,
            "model_loaded": loaded, "initial_hash_seconds": hash_seconds,
            "donor_wall_seconds": time.perf_counter() - start}
