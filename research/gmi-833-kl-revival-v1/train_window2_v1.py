"""Row-L window 2 (FREEZE_V1_AMENDMENT_1.md 3-4): the parent instrument via
``train_continual_v4`` UNCHANGED -- same ``pilot`` and ``run`` -- driven over
``POSTERIOR_SOURCES_V2.json`` with the registered sequence ids T41..T46 (POS)
and T51..T56 (NEG).  ``run`` names its receipt ``cl4_<sid>.json``; the file is
renamed to the registered ``cl5_<sid>.json`` after it is written.  Nothing
about training, seeds, criterion or scoring changes.

Usage: python3 -B train_window2_v1.py POSTERIOR_SOURCES_V2.json REAL_RUNS_L5 [START]

``START`` (default 0) is the first admitted index to run: the registered
replacement rule (FREEZE_V1.md 4.6 clause 2) continues the same ordered list,
so a replacement record whose first entries equal the committed window-2
record is run from index 6 onward (T47/T57, ...), never re-training T41-T46.
"""

import json
import os
import sys

import torch

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import train_continual_v4 as T  # noqa: E402

POS_BASE = 41
NEG_BASE = 51


def main():
    torch.set_num_threads(4)
    with open(sys.argv[1]) as f:
        record = json.load(f)
    outdir = sys.argv[2]
    start = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    for n, src in enumerate(record["admitted"]):
        if n < start:
            continue
        pos_id = "T%02d" % (POS_BASE + n)
        neg_id = "T%02d" % (NEG_BASE + n)
        path = src["local_path"]
        if T.sha256_file(path) != src["sha256"]:
            raise RuntimeError("posterior source bytes drifted: %s" % src["source_id"])
        b_prop = T.pilot(pos_id, path, outdir)
        if b_prop is None:
            print(src["source_id"], "AT_FLOOR_OR_CEILING -> not scored", flush=True)
            continue
        for sid, fam, seq in ((pos_id, "POS", T.POS_SEQ), (neg_id, "NEG", T.NEG_SEQ)):
            T.run((sid, fam, path, seq, T.UOFF, b_prop, src["source_id"]), outdir)
            os.replace(os.path.join(outdir, "cl4_%s.json" % sid),
                       os.path.join(outdir, "cl5_%s.json" % sid))


if __name__ == "__main__":
    main()
