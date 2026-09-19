#!/usr/bin/env python3
"""Revival producer for gmi-833-ae-instruments-v1 (FREEZE_V3_REVIVAL_ADDENDUM.md).

Created AFTER the V3 addendum commit. Three sub-producers, selected by the
first argument; each writes only V3 artifacts and touches no V1 record.

  python3 -B produce_revival_v1.py train   <pkg_dir> <cache_dir> <Cid>
      Revival A: one fresh PERSISTENT-GRU run (seed_c + 13, registered modes,
      V1 checkpoints and probe) and one fresh control (m := 0), written to
      REAL_RUNS/<Cid>/train_v3.json.  Uses the V1 training producer's code
      unchanged (imported), so the protocol is byte-identical to V1.

  python3 -B produce_revival_v1.py corpus  <pkg_dir> <cache_dir> [C11 ...]
      Revival C: the five registered fresh datasets, built by the V1 corpus
      producer's extractors and Instrument IV code (imported), each with its
      SYMCOMP companion, written to REAL_RUNS/C1x/corpus.json.

  python3 -B produce_revival_v1.py energy  <pkg_dir> <cache_dir> <Cid>
      Revival B: the V1 energy protocol with the pre-registered load gate;
      /proc/loadavg is read before the resolution probe and after the last
      round and both readings are recorded; written to
      REAL_RUNS/energy_v3/rapl_rounds.json (admissibility is decided by the
      stdlib routes from the recorded readings, never here).
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

ADDENDUM_V3_COMMIT = "02dfb2f293b748674669f7ef5432cc2b97d33d26"
SEED_OFFSET_V3 = 13

REGISTER_V3 = [
    {"id": "C11", "name": "LANG_2701", "domain": "language", "extractor": "raw", "T": 160000,
     "source": "https://www.gutenberg.org/cache/epub/2701/pg2701.txt",
     "sha256": "907420db6c4b68c70e2988cd2ad9c8cf79138667a01b63376d18dd17fef1a18b"},
    {"id": "C12", "name": "VISION_RIVER", "domain": "vision", "extractor": "jpeg_grey_raster", "T": 160000,
     "source": "/usr/share/backgrounds/ryan-stone-skykomish-river.jpg",
     "sha256": "0902c595631088127f1fe314f055ea9b91dc7ff3c22b24986313a4d69e66f0e5"},
    {"id": "C13", "name": "AUDIO_RL", "domain": "audio", "extractor": "wav_payload_44", "T": 160000,
     "source": "/usr/share/sounds/alsa/Rear_Left.wav",
     "sha256": "1679e0557701864d55b742a0abd3fe5f50d95b1bfcb55ffad4b597dcc7e3c7b8"},
    {"id": "C14", "name": "CODE_STDLIB2", "domain": "code", "extractor": "raw_concat", "T": 160000,
     "source": "/usr/lib/python3.8/typing.py+/usr/lib/python3.8/re.py+/usr/lib/python3.8/collections/__init__.py+/usr/lib/python3.8/argparse.py+/usr/lib/python3.8/inspect.py",
     "member_sha256": ["d05cefb32dc9b6da9a82986af83b5818ff811ed416aeebb9948d38d8dabffce5",
                       "4326ef93e3cf336c06523426187dce705c12f9fdc0a562a7cd00ab1739b14c2d",
                       "386526d59e0c4fb3198bfa17ba3dc66684f6a9b45d0a679d0bc55448cd8550e1",
                       "cc1e3c3a7cb538c32270a77b6f62ac7e91ff5b5a9261607ccbb3e6afe57c44f7",
                       "6018c433712f5906a6ba19ce9debdf48d3c0174ed2449b82e007cf466182fb40"]},
    {"id": "C15", "name": "LEX_BRITISH", "domain": "lexicon", "extractor": "raw", "T": 160000,
     "source": "/usr/share/dict/british-english",
     "sha256": "3462bd63f3a692ca0fd3c6251e2052ccda094a6a06263d84f591b1c96952d204"},
]


def loadavg():
    with open("/proc/loadavg") as f:
        return f.read().split()[:3]


def run_train(pkg, cache_dir, cid):
    import produce_train_v1 as P  # V1 code, unchanged
    out_dir = os.path.join(pkg, "REAL_RUNS", cid)
    with open(os.path.join(cache_dir, cid + "_streams.json")) as f:
        cache = json.load(f)
    T, ntr, seed = cache["T"], cache["n_train"], cache["seed"]
    modes = P.hex_to_bits(cache["modes"], T)
    bits = P.hex_to_bits(cache["bits"]["base"], T)
    s3 = seed + SEED_OFFSET_V3
    X, Y = P.make_xy(bits, modes)
    gm, gl, ck, steps = P.train_gru(s3, X, Y, ntr, P.H_GRU, P.EPOCHS, ckpt=True, modes=modes)
    real = {"seed": s3, "H": P.H_GRU, "optimizer_steps": steps, "final_train_loss": gl[-1],
            "ckpt": {"seed": s3, "steps": P.CKPT_STEPS, "probe": P.PROBE, "warmup": P.WARMUP, "records": ck}}
    print(cid, "v3 real run done", flush=True)
    zero = [0] * T
    X0, Y0 = P.make_xy(bits, zero)
    gc, gcl, ckc, stepsc = P.train_gru(s3, X0, Y0, ntr, P.H_GRU, P.EPOCHS, ckpt=True, modes=zero)
    ctrl = {"seed": s3, "H": P.H_GRU, "optimizer_steps": stepsc, "final_train_loss": gcl[-1],
            "ckpt": {"seed": s3, "steps": P.CKPT_STEPS, "probe": P.PROBE, "warmup": P.WARMUP, "records": ckc}}
    print(cid, "v3 control done", flush=True)
    rec = {"schema": "GMI_833_AE_INSTRUMENTS_TRAIN_V3_RECORD_V1", "id": cid, "addendum_v3_commit": ADDENDUM_V3_COMMIT,
           "seed_offset": SEED_OFFSET_V3, "torch": P.torch.__version__, "threads": P.torch.get_num_threads(),
           "loadavg_start": LOAD_START, "loadavg_end": loadavg(),
           "real_run": real, "control_immediate_only": ctrl}
    with open(os.path.join(out_dir, "train_v3.json"), "w") as f:
        json.dump(rec, f, indent=1, sort_keys=True)
    print(cid, "train_v3 written", flush=True)


def run_corpus(pkg, cache_dir, only):
    import produce_corpus_v1 as C  # V1 code, unchanged
    os.makedirs(cache_dir, exist_ok=True)
    out_dir = os.path.join(pkg, "REAL_RUNS")
    for entry in REGISTER_V3:
        if only and entry["id"] not in only:
            continue
        C.build_dataset(entry, cache_dir, out_dir)
        # SYMCOMP companion for every fresh dataset (V1 built it for C1 only)
        p = os.path.join(out_dir, entry["id"], "corpus.json")
        with open(p) as f:
            rec = json.load(f)
        ntr = rec["n_train"]
        train = C.bits_msb(bytes.fromhex(rec["train_bits_hex"]), ntr)
        ev = C.bits_msb(bytes.fromhex(rec["eval_bits_hex"]), rec["n_eval"])
        tr2 = train + [1 - b for b in train]
        ev2 = ev + [1 - b for b in ev]
        rec["instrument_iv_symcomp"] = C.instrument_iv(tr2, ev2)
        rec["schema"] = "GMI_833_AE_INSTRUMENTS_CORPUS_RECORD_V3"
        rec["addendum_v3_commit"] = ADDENDUM_V3_COMMIT
        with open(p, "w") as f:
            json.dump(rec, f, indent=1, sort_keys=True)
        print(entry["id"], "symcomp added", flush=True)


def run_energy(pkg, cache_dir, cid):
    import produce_energy_v1 as E  # V1 protocol, unchanged
    load0 = loadavg()
    # produce_energy_v1.main writes REAL_RUNS/energy; redirect by a temporary pkg view
    tmp_pkg = os.path.join(cache_dir, "v3_energy_pkg")
    os.makedirs(os.path.join(tmp_pkg, "REAL_RUNS"), exist_ok=True)
    sys.argv = ["produce_energy_v1.py", tmp_pkg, cache_dir, cid]
    E.main()
    load1 = loadavg()
    with open(os.path.join(tmp_pkg, "REAL_RUNS", "energy", "rapl_rounds.json")) as f:
        rec = json.load(f)
    rec["schema"] = "GMI_833_AE_INSTRUMENTS_ENERGY_V3_RECORD_V1"
    rec["addendum_v3_commit"] = ADDENDUM_V3_COMMIT
    rec["loadavg_before_resolution_probe"] = load0
    rec["loadavg_after_last_round"] = load1
    out_dir = os.path.join(pkg, "REAL_RUNS", "energy_v3")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "rapl_rounds.json"), "w") as f:
        json.dump(rec, f, indent=1, sort_keys=True)
    print("energy_v3 written; loadavg", load0, load1, flush=True)


LOAD_START = None


def main():
    global LOAD_START
    kind, pkg, cache_dir = sys.argv[1], sys.argv[2], sys.argv[3]
    LOAD_START = loadavg()
    if kind == "train":
        run_train(pkg, cache_dir, sys.argv[4])
    elif kind == "corpus":
        run_corpus(pkg, cache_dir, sys.argv[4:])
    elif kind == "energy":
        run_energy(pkg, cache_dir, sys.argv[4])
    else:
        raise SystemExit("unknown kind " + kind)


if __name__ == "__main__":
    main()
