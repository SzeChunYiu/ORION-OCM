# Cache accounting

Syntax requests and cache hits/misses are separate. Invalid-domain or prelookup resource
refusals do not make a cache lookup; they have explicit bypass/refusal counters.
UNKNOWN returned by a miss is counted as an uncacheable result. It is recomputed if asked
again, and its actual computation/parse time remains charged.

cache_entries is the observed increase in functools currsize after insertion.
cache_stored_key_tokens and cache_stored_proof_labels count retained payload lengths
for those inserted entries. cache_lookup_key_tokens counts tokens presented at lookups.
cache_returned_proof_labels counts fresh proof-list materializations on misses and hits.
No eviction occurs. Python object overhead remains visible through process RSS rather
than being claimed equal to these logical payload counts.

The immutable library snapshot byte count is exact canonical UTF-8 JSON length;
read-only view objects are additional resident memory. Namespace/context-key bytes and
cold library preparation are recorded. Grammar construction includes cache setup and
its context copy; those nested intervals must not be added twice.

parse_emit_wall_s, parse_calls, input_tokens and emitted_proof_labels advance only on
actual underlying computation. A hit returns no historical parser duration.
cache_compute_wall_s encloses the miss computation and packing. cache_request_wall_s
encloses each request; cache_management_wall_s is its remainder outside that miss
interval. These are nested attribution timers, not independent additive costs.

A post-computation deadline refusal retains actual parse time even though its terminal
is UNKNOWN. A prelookup refusal records no parse because none occurred, while its
request wall and refusal count remain explicit. Internal Earley chart operations and
interrupted proof-label work remain uninstrumented, not asserted zero.

FUTURE-RUN.json binds the complete original opportunity and first-screen cost records.
No concrete driver/observer or execution gate is supplied by this prototype tranche.
