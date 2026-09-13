"""Item 6: does the accounting force a PARTITION of memory into distinct regimes?

Three conditions are already derived and each names a different thing to store:

  * item 7 consolidation -> store the retention-equivalence QUOTIENT (size ceil(log2 N_t))
  * item 7 replay        -> store RAW EXPERIENCE as the side channel (size ~ episodes)
  * item 10 chunking     -> store COMPILED SUB-QUOTIENTS above the PVR-3 threshold
  * the execution/development cut -> WITHIN-EVENT state, never persisted

If these are genuinely different regimes they must have different GROWTH LAWS in
experience. This enumerates all four over a stream and checks.

Complete enumeration; no sampling.
"""
import json

H = list(range(16))
bit = lambda k: (lambda h: (h >> k) & 1)

# a stream of obligations: 3 genuinely new distinctions, the rest derived from them
# three genuinely new distinctions, then obligations that RECUR -- recurrence is what the
# procedural regime responds to, so the stream must contain it or the witness cannot
# exercise all four regimes.
_xor01 = lambda h: (h & 1) ^ ((h >> 1) & 1)
_and12 = lambda h: ((h >> 1) & 1) & ((h >> 2) & 1)
STREAM = [bit(0), bit(1), bit(2),
          _xor01, _and12, _xor01, _and12, _xor01,
          lambda h: 1 - (h & 1), _and12, _xor01, _and12]

C_DERIVE, S_CHUNK, U_INVOKE = 4, 3, 1
CHUNK_THRESHOLD = 1 + S_CHUNK / (C_DERIVE - U_INVOKE)      # PVR-3

rows = []
sigs = [() for _ in H]
seen_patterns = {}
for t, q in enumerate(STREAM, 1):
    sigs = [s + (q(h),) for s, h in zip(sigs, H)]
    N = len(set(sigs))
    semantic_bits = (N - 1).bit_length()          # the quotient: ceil(log2 N_t)
    episodic_records = t                          # raw experience: one record per obligation seen
    # a "pattern" recurs when an obligation is a repeat of an earlier response map
    key = tuple(q(h) for h in H)
    seen_patterns[key] = seen_patterns.get(key, 0) + 1
    procedural_chunks = sum(1 for k, r in seen_patterns.items() if r > CHUNK_THRESHOLD)
    working_state = 1                             # within-event, not persisted across the cut
    rows.append({"t": t, "N_t": N, "semantic_bits": semantic_bits,
                 "episodic_records": episodic_records,
                 "procedural_chunks": procedural_chunks,
                 "working_state": working_state})

print("PVR-3 chunk threshold: recurrence > %.2f" % CHUNK_THRESHOLD)
print("\n t  N_t  semantic(bits)  episodic(records)  procedural(chunks)  working")
for r in rows:
    print(" %-2d %-4d %-15d %-18d %-19d %d" % (r["t"], r["N_t"], r["semantic_bits"],
          r["episodic_records"], r["procedural_chunks"], r["working_state"]))

first, last = rows[0], rows[-1]
growth = {
  "semantic":   (first["semantic_bits"], last["semantic_bits"]),
  "episodic":   (first["episodic_records"], last["episodic_records"]),
  "procedural": (first["procedural_chunks"], last["procedural_chunks"]),
  "working":    (first["working_state"], last["working_state"]),
}
print("\ngrowth over %d obligations (first -> last):" % len(rows))
for k, (a, b) in growth.items():
    print("  %-11s %d -> %-3d  (factor %.2f)" % (k, a, b, b / max(1, a)))
print("\ndistinct growth laws?", len({g for g in growth.values()}) == len(growth))
json.dump({"schema": "MemoryRegimePartitionWitnessV1",
           "chunk_threshold": CHUNK_THRESHOLD, "rows": rows, "growth": {k: list(v) for k, v in growth.items()}},
          open("microscopes/results/STAGE_MEMORY_REGIME_WITNESS_V1.json", "w"), indent=1, sort_keys=True)
print("written")
