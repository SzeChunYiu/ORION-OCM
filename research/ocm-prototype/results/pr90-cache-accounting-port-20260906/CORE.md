# PR90: account for retained cache storage

Classification: INFRASTRUCTURE. This port begins at Claude's exact updated
5888bdc6baf3e4bf069701caf1b1a11e2adfe415, preserving its independent digest,
mutable-registry validation fixes, comments, tests and qualification history.

The only production change is index_resources in space.py:
- count materialized evidence-frozenset entries and its shallow container bytes;
- count materialized atom/edge mapping-proxy container bytes;
- do not charge the underlying shared dictionary entries twice.

This reports shallow cache storage on the current Python host.
It does not report recursive retained memory, process RSS or asymptotic runtime.

## Executed controls

The new 44-line test file leaves Claude's existing test file byte-identical.
It materializes each view and both nonempty/empty evidence sets, compares the
observed counter increment to the actual returned container's sys.getsizeof,
checks entry ownership and unchanged digest, and checks that observation itself
does not materialize optional caches.

- New controls before port: 4 genuine accounting failures, 1 clean no-alarm pass.
- Claude's existing controls plus new controls after port: 30 passed.
- Complete M1 suite after port: 87 passed.
- No green failures, errors or skips. Exact timings/commands/hashes are in
  [verification.json](verification.json); raw logs/XML are under raw/.
- No model inference, performance benchmark or current engineering recorder.
  Final-main integration and current qualification remain a separate next stage.

## Historical custody

Both earlier independently executed repair packets are preserved byte-for-byte:
[digest repair](../pr90-digest-compatibility-repair-20260906/CORE.md) and
[registry repair](../pr90-registry-compatibility-repair-20260906/CORE.md).
Their 54 files describe their original source states; this port does not
relabel those old executions as tests of the newer Claude branch.
Every preexisting tracked file except space.py remains byte-identical.
The current engineering selector is retained, not claimed current for this port.
[ARTIFACTS.json](ARTIFACTS.json) binds this compact new packet.
