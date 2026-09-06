"""One fixed qualified recurrent bundle; data custody shared by native and OCM."""
from pathlib import Path
import hashlib
import json
import shutil
from stanza_donor import require_hash

QUAL_SHA = "0e4da5ff3e8612bec4cf4a54954bb41fc0412ca21de616237d2af4460a6cf6de"
LOCK_SHA = "025016b2716073c74e7eb364d0f5a2d33fbd6d48cf00a287665bf10c6b3573a7"
PACKAGES_SHA = "49ecd3c96e371d5a678c81b7f7661e33fde3527096bb642397f65a925578a2e5"
LINEAGE_SHA = "48d9feb2e1e7cd04ac1daf4181f00b1273645f64f13f472037a863ce90ce4519"
CLOSURE = "dae9ad20c7bdb98838a19d47d42996af181c89a6aca0a646fd63d6b46e9568cb"
RESOURCES_SHA = "4e41c1df152146fa26ed0c006a08feea7a60bb3414bb6d57dbda24ad2e3cb99c"
RESOURCES_BYTES = 457371
MODELS = {
    "models/en/pos/combined_nocharlm.pt": "de777e494a74b387b3f64682a216b3497dbdbf76f7e69efca0ea1e16915fbf2d",
    "models/en/lemma/combined_nocharlm.pt": "775d42962ae209d4ff2fc3a799a9438333a44aa6ede3a7368dc07afd573d79d3",
    "models/en/depparse/combined_nocharlm.pt": "93c7c704cc5878db89e4bfb5bb5744e138448693da65773e88a8a4f8c5983ac1",
    "models/en/pretrain/conll17.pt": "edde4c195f91ba45aab3f3a6254202011f284559da8a5ead5e62ce522f819c5e",
}
SIZES = dict(zip(MODELS, (23692310, 2465184, 108883461, 106701210)))
EXTRAS = {"cvc5": "1.3.4", "z3-solver": "5.1.0.0", "sexpdata": "1.0.2"}


def encoded(data):
    return json.dumps(data, sort_keys=True, separators=(",", ":")).encode()


def digest_bytes(data):
    return hashlib.sha256(data).hexdigest()


def digest(data):
    return digest_bytes(encoded(data))


def describe(packages):
    if digest(packages) != PACKAGES_SHA:
        raise ValueError("qualified runtime package inventory changed")
    data = {"schema": "g1.stanza-recurrent.v1", "model_sha256": CLOSURE,
        "models": MODELS, "model_sizes": SIZES, "resources_sha256": RESOURCES_SHA,
        "resources_bytes": RESOURCES_BYTES, "packages": packages, "clia_additions": EXTRAS,
        "qualification_sha256": QUAL_SHA, "runtime_lock_sha256": LOCK_SHA,
        "training_lineage_sha256": LINEAGE_SHA, "model_bytes": sum(SIZES.values()),
        "prior_note": "All four checkpoints include learned parameters, dictionaries and vocabularies; no retraining.",
        "compiled_state": "Pipeline allocations are transient; exact attributable bytes UNKNOWN, process RSS measured."}
    return {**data, "id": digest(data)}


def validate(profile):
    if not isinstance(profile, dict) or profile != describe(profile.get("packages")):
        raise ValueError("fixed Stanza profile binding")
    return profile


def from_qualification(root):
    root = Path(root)
    require_hash(root/"qualification-manifest-v1.json", QUAL_SHA)
    require_hash(root/"runtime-lock-v1.json", LOCK_SHA)
    require_hash(root/"training-lineage-v1.json", LINEAGE_SHA)
    return describe(json.loads((root/"runtime-lock-v1.json").read_text())["packages"])


def inventory(profile):
    validate(profile)
    return {**{p: {"sha256": h, "bytes": profile["model_sizes"][p]} for p, h in profile["models"].items()},
        "models/resources.json": {"sha256": profile["resources_sha256"], "bytes": profile["resources_bytes"]}}


def verify_archive(bundle, profile):
    bundle = Path(bundle)
    for name, binding in inventory(profile).items():
        path = bundle/name
        if path.is_symlink() or path.stat().st_size != binding["bytes"]:
            raise ValueError("archive size/type mismatch: " + name)
        require_hash(path, binding["sha256"])
    if (bundle/"profile.json").read_bytes() != encoded(profile):
        raise ValueError("archived profile changed")
    expected = {*inventory(profile), "profile.json"}
    actual = {str(p.relative_to(bundle)) for p in bundle.rglob("*") if p.is_file()}
    if actual != expected:
        raise ValueError("unexpected archive file inventory")
    return bundle



def verify_models(source_models, profile):
    for name, binding in inventory(profile).items():
        path = Path(source_models)/name.removeprefix("models/")
        if path.is_symlink() or path.stat().st_size != binding["bytes"]:
            raise ValueError("source model size/type mismatch: " + name)
        require_hash(path, binding["sha256"])
    return inventory(profile)

def prepare(state, source_models, profile):
    """Both arms copy and validate the exact same complete bundle once."""
    validate(profile)
    bundle = Path(state)/"archive"/profile["id"]
    if bundle.exists():
        return verify_archive(bundle, profile)
    bundle.mkdir(parents=True)
    for name, binding in inventory(profile).items():
        source = Path(source_models)/name.removeprefix("models/")
        require_hash(source, binding["sha256"])
        target = bundle/name; target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    with (bundle/"profile.json").open("xb") as output:
        output.write(encoded(profile))
    return verify_archive(bundle, profile)


def archive_path(state, profile):
    validate(profile)
    return Path(state)/"archive"/profile["id"]
