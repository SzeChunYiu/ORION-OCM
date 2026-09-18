# V2 run logs, as they ran

These are the stdout and stderr of `run_real_scale_v2.py`,
`run_search_sample_v1.py` and `run_controls_v2.py` on laptop-billy, with **one
class of line removed**: LAPACK's
`** On entry to DLASCL parameter number N had an illegal value`, emitted by
route B's `numpy.linalg.lstsq` when a candidate design contains non-finite
values. Those candidates are discarded by the finiteness guard in `loss_of` and
are never scored, so the warnings carry no information about any result.

Nothing else was altered. No result line, timing, count or expression was
touched, added or reordered.
