"""Finite exact eligibility from actual OCM kernels, warrants and decoder premises."""
from dataclasses import dataclass
from collections import Counter
from fractions import Fraction
from ocm.kso import navigation as N
from ocm.runtime import solve as SV
from representation_donor_imports import load
from representation_donor_grade import digest


def state_binding(ks):
    return digest({"field": ks.digest(), "registry": ks.registry})


@dataclass
class Policy:
    fixture: dict
    donors: dict
    blocks: tuple
    matrices: dict
    seed: list
    binding: str
    task_binding: str
    config_binding: str
    family: tuple
    eligibility: dict
    counts: Counter
    matrix_cells: int

    def call(self, name, *args):
        self.counts[name] += 1
        group, method = name.split(".")
        return getattr(self.donors[group], method)(*args)


def prepare(fixture, *, available_states=None):
    ks, task, cfg = (fixture[k] for k in ("ks", "task", "config"))
    if cfg.relevance is not None:
        raise ValueError("Initial decoder contract requires default relevance")
    blocks = tuple(tuple(ks.ids.index(x) for x in b) for b in fixture["blocks"])
    _, seed = SV.atomise(ks, task)
    if seed is None:
        raise ValueError("UNBOUND_QUERY")
    family = tuple(frozenset(R) for R in fixture["revocations"])
    available = family if available_states is None else tuple(available_states)
    p = Policy(fixture, load(), blocks, {}, seed, state_binding(ks), digest(task), digest(cfg), family, {}, Counter(), 0)
    lives, answers, Ps = {}, {}, {}
    bg = N.uniform_seed(ks)
    for R in available:
        if R not in family:
            raise ValueError("AVAILABLE_STATE_OUTSIDE_REGISTERED_FAMILY")
        for mode in N.NavigationMode:
            m = N.navigation_matrix(ks, revoked=R, mode=mode)
            p.matrices[(R, mode)] = m
            p.matrix_cells += sum(len(row) for row in m.rows)
        Ps[R] = p.matrices[(R, N.NavigationMode.WARRANTED)].as_lists()
        lives[R] = [a.liveness(R).value for a in ks.atoms]
        qs, bs = N.gated_seed(ks, seed, R), N.gated_seed(ks, bg, R)
        # These are the exact decoder outputs ONLY under the separately checked zero-incidence premise.
        answers[R] = [(cfg.alpha * q, cfg.alpha * b) for q, b in zip(qs, bs, strict=True)]
    warranted = p.call("f2.validate_multiscale_certificate", Ps, lives, answers, blocks, family)
    dynamic = "CANNOT_CHECK_MISSING_REGISTERED_STATE"
    reconstruction = "CANNOT_CHECK_MISSING_REGISTERED_STATE"
    if all(R in available for R in family):
        dynamic = "DYNAMIC_LUMPABILITY_ONLY" if all(p.call("f2.strong_lumpable", p.matrices[(R, N.NavigationMode.EXPLORATORY)].as_lists(), blocks) for R in family) else "REFINE_REQUIRED_NON_LUMPABLE"
        merged = [i for block in blocks if len(block) > 1 for i in block]
        # Both incoming AND outgoing mass matter. Lumpability alone does not reconstruct individuals.
        zero = all(m.rows[i][j] == 0 and m.rows[j][i] == 0 for m in p.matrices.values() for i in merged for j in range(len(ks.ids)))
        reconstruction = "EXACT_ZERO_INCIDENT_DECODER" if zero else "REFINE_REQUIRED_NONZERO_INCIDENT_KERNEL"
    p.eligibility = {"warranted": warranted, "exploratory": dynamic,
                     "reconstruction": reconstruction,
                     "registered_states": len(family), "available_states": len(available),
                     "revision_scope": "SNAPSHOT_FAMILY_ONLY; unregistered updates invalidate; finite-map checker is separate"}
    return p
