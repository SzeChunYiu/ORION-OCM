"""Independently ablatable kernels. Identity kernel = ablation."""
from __future__ import annotations

KERNEL_NAMES = (
    "K_world", "K_senseact", "K_learn", "K_social", "K_assemble",
    "K_birthdeath", "K_mut", "K_inherit",
)


def identity(world):
    return world


def enabled(spec):
    """spec maps kernel name -> True (on) or False (identity)."""
    out = {}
    for name in KERNEL_NAMES:
        out[name] = bool(spec.get(name, True))
    return out


def assert_independent_ablation(spec_a, spec_b):
    """Spec-level independence: exactly one kernel bit differs.

    Previously returned ok=True for every input, so the BIO-T kernel-ablation
    row could not fail. Dynamics independence is checked by
    ocm-microearths-exhaustive-v1/ablation.py, not here.
    """
    keys = set(spec_a) | set(spec_b)
    diffs = [k for k in keys if spec_a.get(k, True) != spec_b.get(k, True)]
    return {"n_diffs": len(diffs), "diffs": diffs, "ok": len(diffs) == 1}
