"""Exact deficit matrix for six derived-component lesions (L5).

Six lesions each remove one derived mechanism while the search basis
(delta/F, query/teach, t0/t1) stays intact. Table is 0/1 measured on
six task families. CPython 3.8 safe.
"""

TASKS = ("T_mem", "T_att", "T_plan", "T_causal", "T_social", "T_consol")

LESIONS = ("none", "L_mem", "L_att", "L_plan", "L_causal", "L_social", "L_consol", "L_basis")

# rows: lesion -> {task: 0/1}
_TABLE = {
    "none":     {"T_mem": 1, "T_att": 1, "T_plan": 1, "T_causal": 1, "T_social": 1, "T_consol": 1},
    "L_mem":    {"T_mem": 0, "T_att": 1, "T_plan": 1, "T_causal": 1, "T_social": 1, "T_consol": 0},
    "L_att":    {"T_mem": 1, "T_att": 0, "T_plan": 1, "T_causal": 1, "T_social": 0, "T_consol": 1},
    "L_plan":   {"T_mem": 1, "T_att": 1, "T_plan": 0, "T_causal": 1, "T_social": 1, "T_consol": 1},
    "L_causal": {"T_mem": 1, "T_att": 1, "T_plan": 1, "T_causal": 0, "T_social": 1, "T_consol": 1},
    "L_social": {"T_mem": 1, "T_att": 1, "T_plan": 1, "T_causal": 1, "T_social": 0, "T_consol": 1},
    "L_consol": {"T_mem": 1, "T_att": 1, "T_plan": 1, "T_causal": 1, "T_social": 1, "T_consol": 0},
    "L_basis":  {"T_mem": 1, "T_att": 1, "T_plan": 0, "T_causal": 1, "T_social": 1, "T_consol": 1},
}

_MECHANISM = {
    "none": "intact",
    "L_mem": "retention disabled (state reset before each step)",
    "L_att": "conditional routing disabled (fixed to x0)",
    "L_plan": "lookahead disabled (depth 0, no EVC expansion)",
    "L_causal": "adjustment disabled (empty adjustment set)",
    "L_social": "opponent model disabled (opponent state hidden)",
    "L_consol": "replay disabled (no M*_t saving)",
    "L_basis": "basis removed (t1 unavailable) — control, not a derived lesion",
}

_TWIN_NOTE = {
    "L_mem": "shared retention with L_consol (both hurt T_consol)",
    "L_att": "shared routing with L_social (both hurt T_social)",
}


def _check_lesion(name):
    if name not in _TABLE:
        raise ValueError("unknown lesion: %r" % (name,))
    return name


def _check_task(name):
    if name not in TASKS:
        raise ValueError("unknown task: %r" % (name,))
    return name


def success(task, lesion):
    """0/1 score of lesion on task."""
    _check_lesion(lesion)
    _check_task(task)
    return _TABLE[lesion][task]


def row(lesion):
    """Copy of the row for a lesion."""
    _check_lesion(lesion)
    return dict(_TABLE[lesion])


def table():
    """Full deficit table lesion -> task -> 0/1 (copy)."""
    return {k: dict(v) for k, v in _TABLE.items()}


def mechanism(lesion):
    _check_lesion(lesion)
    return _MECHANISM[lesion]


def is_derived_lesion(name):
    _check_lesion(name)
    return name not in ("none", "L_basis")


def double_dissociated(la, lb, ta, tb):
    """True iff la hurts ta not tb, and lb hurts tb not ta (strict)."""
    _check_lesion(la)
    _check_lesion(lb)
    _check_task(ta)
    _check_task(tb)
    return (success(ta, la) == 0 and success(tb, la) == 1 and
            success(tb, lb) == 0 and success(ta, lb) == 1)


def all_double_dissociations():
    """Enumerate all strict double-dissociation quadruples."""
    out = []
    for la in LESIONS:
        for lb in LESIONS:
            if la >= lb:
                continue
            for ta in TASKS:
                for tb in TASKS:
                    if ta >= tb:
                        continue
                    if double_dissociated(la, lb, ta, tb):
                        out.append((la, lb, ta, tb))
    return out


def summary():
    return {
        "lesions": len(LESIONS),
        "tasks": len(TASKS),
        "table_entries": len(LESIONS) * len(TASKS),
        "derived_lesions": sum(1 for l in LESIONS if is_derived_lesion(l)),
        "double_dissociations": len(all_double_dissociations()),
    }
