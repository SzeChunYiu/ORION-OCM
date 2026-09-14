"""A repaired K4 cost model in which resources can actually be bought.

GMI_K4_COST_STRUCTURE_ROOT_CAUSE_V1 established that the frozen K4 cost model
contains no substitutions: every channel rises together, so a cost-minimising
search converges to SMALL and never to STRUCTURED, and the mechanism the
apparatus was built to detect cannot be expressed in the space it searches.

This is the repair that finding named. The frozen model is NOT modified --
gmi_k4_resource_native_v4 is imported and left exactly as it is, so every
registered campaign result stands. This module supplies an alternative pricing
and asks what changes.

Two corrections, each independently principled, each testable alone:

  R1  AMORTISE THE STORE.  The model already divides development_compute and
      description_compiler_burden by the reuse multiplier, which is per-use
      normalisation: total/r = build/r + serve. Building a store is a one-time
      cost and belongs in the same group, but state_storage is charged flat.
      PVR-3 accounts retention as C + S + (r-1)U, with S paid ONCE.

  R2  LET THE STORE DO WORK.  In the frozen model `state` and `work` come from
      two independently generated expressions, so nothing couples them. But a
      machine that has stored an answer does not recompute it. Serving work is
      reduced by what the store covers -- gated on the machine actually being
      able to find what it stored, which is what `retrieval` records.

  R3  AMORTISE DISCOVERY.  search_compute is gp * tokens, the cost of finding
      the candidate at all. It is paid once, exactly like development_compute,
      which the frozen model already divides by reuse -- but search_compute is
      left flat. Measured at reuse 64 the amortised development term is 0.38
      while the unamortised search term is 10.80, so the objective is roughly
      seven parts description length to one part everything else.

R2 is PVR-3 applied per query. None of the three mentions any family.
"""

import sys

sys.path.insert(0, ".")
import gmi_k4_search as base          # noqa: E402
import gmi_k4_resource_native_v4 as rn  # noqa: E402

CHANNELS = list(base.CHANNELS)

# How cheaply a machine can consult its own store. A machine with no retrieval
# cannot consult it at all, so storage buys it nothing -- which is the control
# that keeps R2 from being a blanket discount.
LOOKUP_RATIO = {"none": 1.0, "metric": 0.35, "exact_key": 0.05}

PER_USE = ("serve_compute_latency", "communication", "verification")
ONE_TIME_STORE = "state_storage"
# search_compute is gp * tokens: the cost of FINDING the candidate. Like
# development_compute it is paid once, but the frozen model amortises
# development and leaves search flat, so at high reuse the unamortised term
# dominates and the objective becomes description-length minimisation.
ONE_TIME_SEARCH = "search_compute"


def coverage(cand, state, scale):
    """Fraction of the working set the store already answers."""
    records = rn.task_env(scale)["records"]
    return min(1.0, float(state) / float(records)) if records else 0.0


def substitution_factor(cand, state, scale):
    """R2: multiplier on per-use work after the store is consulted."""
    ratio = LOOKUP_RATIO[cand.retrieval]
    if ratio >= 1.0:
        return 1.0
    hit = coverage(cand, state, scale)
    return (1.0 - hit) + hit * ratio


def lifecycle(cand, scale, profile, r1=True, r2=True, r3=True):
    """Repriced lifecycle. r1/r2 select which corrections are active, so each
    can be attributed separately rather than assumed jointly responsible."""
    cost = dict(rn.lifecycle(cand, scale, profile))
    state, _work = rn.resource_counts(cand, scale)
    reuse = max(1.0, float(profile.get("reuse_multiplier", 1.0)))

    if r2:
        f = substitution_factor(cand, state, scale)
        for k in PER_USE:
            cost[k] *= f
    if r1:
        cost[ONE_TIME_STORE] /= reuse
    if r3:
        cost[ONE_TIME_SEARCH] /= reuse
    return cost


def scalar(cost):
    return sum(float(cost[k]) for k in CHANNELS)
