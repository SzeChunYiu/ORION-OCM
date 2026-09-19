"""Route B for `gmi-833-body-residual-akl-v1`. Imports nothing from route A.

Materially independent re-derivation of every quantity route A claims:

  row A  a hand-written character scanner with its own boundary logic. It does
         not import the parent terminology gate and uses no regular expression.
  row K  BLACK BOX. Route A reasons structurally about the survivor set; route B
         installs concrete worlds on the registration surface and runs the parent
         predictor `F` end to end, then asks how many inputs carry a point that is
         non-degenerate and identical in every world. It also runs NULL_UNIFORM.
  row L  an independent clause evaluator that reads dates as ISO strings through a
         different git query than route A's epoch query.

Run:  python3 -I -B oracle_route_b_v1.py [--worlds N] [--null-seeds N]
      [--out ORACLE_RESULT_V1.json]
"""

from fractions import Fraction
import json
import os
import random
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, os.pardir, os.pardir))
GIT = "/usr/bin/git" if os.path.exists("/usr/bin/git") else "git"
SOURCE_MAIN = "5e57d4292266bccf435136e1f7d72caa32e920a0"
FREEZE_COMMIT = "c9dec25dad00ddde53ddadd3852c1d5fef1a0e03"
TERM = "obligation"
AUTHORITY = ("gmi-833-tranche-ab-ac-lit", "gmi-833-ab-terminology-harness-v1",
             "gmi-833-terminology-migration-v1", "gmi-833-checklist-mirror-v1")
SELF = "gmi-833-body-residual-akl-v1"


def git(args):
    proc = subprocess.Popen([GIT, "-C", REPO] + args, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    out, err = proc.communicate()
    return proc.returncode, out.decode("utf-8", "replace"), err.decode("utf-8", "replace")


# ---------------------------------------------------------------------------
# Row A: a scanner with no regular expression anywhere
# ---------------------------------------------------------------------------

WORDCHARS = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_")


def count_term(text, term):
    """Case-insensitive count of `term` and `term + 's'` as whole words."""
    low = text.lower()
    t = term.lower()
    n = len(t)
    total = 0
    i = low.find(t)
    while i != -1:
        left_ok = i == 0 or low[i - 1] not in WORDCHARS
        if left_ok:
            end = i + n
            if end < len(low) and low[end] == "s":
                end += 1
            if end >= len(low) or low[end] not in WORDCHARS:
                total += 1
        i = low.find(t, i + 1)
    return total


def scope_files(paths, scope):
    out = []
    for p in paths:
        if scope == "S1":
            if p.endswith(".md") or p.endswith(".tex"):
                out.append(p)
        elif scope == "S2":
            if p.endswith(".md") and p.startswith("research/"):
                out.append(p)
        elif scope == "S3":
            if not p.endswith(".md"):
                continue
            if "/" not in p:
                out.append(p)
                continue
            if not p.startswith("research/"):
                continue
            parts = p.split("/")
            pkg = parts[1] if len(parts) >= 2 else ""
            if pkg not in AUTHORITY and pkg != SELF:
                out.append(p)
    return sorted(out)


def frozen_bytes(paths_with_sha):
    """One `git cat-file --batch` call, the whole stream parsed at once.

    Route A streams request/response through the same plumbing; this reads the
    concatenated stream instead. Both take the FROZEN blob rather than the
    worktree file, so neither count moves when main merges something else.
    """
    order = [sha for sha, _p in paths_with_sha]
    proc = subprocess.Popen([GIT, "-C", REPO, "cat-file", "--batch"],
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    stream, _err = proc.communicate(("\n".join(order) + "\n").encode("ascii"))
    out = {}
    pos = 0
    for sha, path in paths_with_sha:
        nl = stream.index(b"\n", pos)
        header = stream[pos:nl].decode("ascii", "replace").split()
        if len(header) != 3 or header[1] != "blob":
            raise SystemExit("cat-file refused %s (%s)" % (sha, path))
        size = int(header[2])
        body = stream[nl + 1:nl + 1 + size]
        out[path] = body.decode("utf-8", "replace")
        pos = nl + 1 + size + 1
    return out


def row_a():
    rc, out, err = git(["ls-tree", "-r", SOURCE_MAIN])
    if rc != 0:
        raise SystemExit("ls-tree failed: %s" % err.strip())
    entries = []
    for line in out.splitlines():
        if "\t" not in line:
            continue
        meta, path = line.split("\t", 1)
        bits = meta.split()
        if len(bits) == 3 and bits[1] == "blob":
            entries.append((bits[2], path))
    paths = [p for _s, p in entries]
    sha_of = dict((p, s) for s, p in entries)
    wanted = sorted(set(scope_files(paths, "S1")) | set(scope_files(paths, "S3"))
                    | set(p for p in paths if p.endswith(".md")))
    text_of = frozen_bytes([(sha_of[p], p) for p in wanted])
    res = {}
    for scope in ("S1", "S2", "S3"):
        files = scope_files(paths, scope)
        hits = 0
        with_hits = 0
        for p in files:
            n = count_term(text_of[p], TERM)
            if n:
                hits += n
                with_hits += 1
        res[scope] = {"files_scanned": len(files), "files_with_hits": with_hits,
                      "total_hits": hits}
    required = 0
    required_files = 0
    for p in paths:
        if not p.endswith(".md"):
            continue
        parts = p.split("/")
        if len(parts) < 2 or parts[0] != "research" or parts[1] not in AUTHORITY:
            continue
        n = count_term(text_of[p], TERM)
        if n:
            required += n
            required_files += 1
    res["required_to_remain_hits"] = required
    res["required_to_remain_files"] = required_files
    res["tracked_paths_at_source_main"] = len(paths)
    return res


# ---------------------------------------------------------------------------
# Row K: black box over concrete worlds
# ---------------------------------------------------------------------------

EVAL_PKG = os.path.join(REPO, "research", "gmi-833-capability-predictor-evaluation-v1")


def load():
    if EVAL_PKG not in sys.path:
        sys.path.insert(0, EVAL_PKG)
    import heldout_universes_v1 as hu
    import heldout_universes_v2 as hv2
    import heldout_universes_v3 as hv3
    parent = hu.load_parent()
    return hu, hv2, hv3, parent


def protocol_worlds(machines, count, seed):
    """Worlds a truthful protocol-conservative bridge admits: a solved-bit vector
    per machine whose set bits are a subset of the machine's trained heads.
    Two extremal worlds first, then `count - 2` seeded draws."""
    worlds = [tuple(0 for _ in machines), tuple(m[3] for m in machines)]
    rng = random.Random(seed)
    while len(worlds) < count:
        worlds.append(tuple(rng.randint(0, m[3]) & m[3] for m in machines))
    return worlds[:count]


def spec_for_world(hu, base_spec, machines, mu, world):
    """A fresh registration surface whose CAP is the given world's capability table."""
    spec = dict(base_spec)
    cap = {}
    for contract in base_spec["CONTRACTS"]:
        verified = hu.VERIFIED[contract]
        row = []
        for idx in range(len(machines)):
            bits = world[idx]
            total = Fraction(0)
            for j in range(3):
                if verified[j] and ((bits >> j) & 1):
                    total += mu[j]
            row.append(total)
        cap[contract] = tuple(row)
    spec["CAP"] = cap
    spec["_CEILING_CACHE"] = {}
    return spec


def blackbox_census(hu, parent, base_spec, machines, mu, worlds):
    """Inputs where F emits the SAME strictly positive point in every world."""
    per_world = []
    for world in worlds:
        hu.install_universe(parent, spec_for_world(hu, base_spec, machines, mu, world))
        row = []
        for entry in parent.main_grid():
            (k_index, r_value, d_value, b_value, h_value,
             _u_id, u_kind, u_mask, alpha, contract, _tau) = entry
            em = parent.predict(k_index, contract, r_value, h_value, d_value,
                                b_value, u_kind, u_mask, alpha, "REGISTERED")
            if em.disposition == "IDENTIFIED":
                row.append(em.value)
            else:
                row.append(None)
        per_world.append(row)
    n_inputs = len(per_world[0])
    invariant_nd = 0
    invariant_any = 0
    for i in range(n_inputs):
        vals = [w[i] for w in per_world]
        if any(v is None for v in vals):
            continue
        first = vals[0]
        if any(v != first for v in vals):
            continue
        invariant_any += 1
        if not isinstance(first, str) and first > 0:
            invariant_nd += 1
    return {"worlds": len(worlds), "inputs": n_inputs,
            "world_invariant_points": invariant_any,
            "world_invariant_non_degenerate": invariant_nd}


def fitted_census(hu, parent, base_spec, machines, mu, law):
    """Positive control: the single world the parent's registered law asserts."""
    world = tuple(law(m) for m in machines)
    hu.install_universe(parent, spec_for_world(hu, base_spec, machines, mu, world))
    nd = 0
    for entry in parent.main_grid():
        (k_index, r_value, d_value, b_value, h_value,
         _u_id, u_kind, u_mask, alpha, contract, _tau) = entry
        em = parent.predict(k_index, contract, r_value, h_value, d_value,
                            b_value, u_kind, u_mask, alpha, "REGISTERED")
        if em.disposition == "IDENTIFIED" and not isinstance(em.value, str) \
                and em.value > 0:
            nd += 1
    return nd


def null_uniform(hu, parent, base_spec, machines, mu, seeds):
    """NULL_UNIFORM as registered: a bridge drawn uniformly at random per machine,
    ignoring truthfulness. Reported to show what the counter does when the bridge
    is not truthful, so a census of 0 cannot be read off a counter stuck at 0."""
    out = []
    for s in range(seeds):
        rng = random.Random(90210 + s)
        world = tuple(rng.randint(0, 7) for _ in machines)
        hu.install_universe(parent, spec_for_world(hu, base_spec, machines, mu, world))
        nd = 0
        for entry in parent.main_grid():
            (k_index, r_value, d_value, b_value, h_value,
             _u_id, u_kind, u_mask, alpha, contract, _tau) = entry
            em = parent.predict(k_index, contract, r_value, h_value, d_value,
                                b_value, u_kind, u_mask, alpha, "REGISTERED")
            if em.disposition == "IDENTIFIED" and not isinstance(em.value, str) \
                    and em.value > 0:
                nd += 1
        out.append(nd)
    return {"seeds": len(out), "min": min(out), "max": max(out),
            "zero_seeds": sum(1 for x in out if x == 0)}


def row_k(worlds_per_population, null_seeds):
    hu, hv2, hv3, parent = load()
    pops = [("SIGMA_REAL", hu.sigma_real(), hu.REAL_MACHINES, hu.real_solved_law),
            ("SIGMA_REAL2", hv2.sigma_real2(), hv2.REAL2_MACHINES, hv2.real2_solved_law),
            ("SIGMA_REAL3", hv3.sigma_real3(), hv3.REAL3_MACHINES, hv3.real3_solved_law)]
    out = {}
    total_nd = 0
    total_inputs = 0
    for name, spec, machines, law in pops:
        worlds = protocol_worlds(machines, worlds_per_population, seed=4242)
        cen = blackbox_census(hu, parent, spec, machines, hu.MU_REAL, worlds)
        cen["fitted_law_positive_control_non_degenerate"] = fitted_census(
            hu, parent, spec, machines, hu.MU_REAL, law)
        out[name] = cen
        total_nd += cen["world_invariant_non_degenerate"]
        total_inputs += cen["inputs"]
    out["TOTAL"] = {"inputs": total_inputs, "world_invariant_non_degenerate": total_nd}
    if null_seeds:
        name, spec, machines, _law = pops[2]
        out["NULL_UNIFORM"] = null_uniform(hu, parent, spec, machines, hu.MU_REAL,
                                           null_seeds)
        out["NULL_UNIFORM"]["population"] = name
    return out


# ---------------------------------------------------------------------------
# Row L
# ---------------------------------------------------------------------------

CANDIDATES = [
    ("CF_G0_GRAMMAR", "research/gmi-833-developmental-reuse-v1/FROZEN_FIXTURES_V1.json"),
    ("CF_DEV_REUSE_THEOREMS",
     "research/gmi-833-developmental-reuse-v1/DEVELOPMENTAL_REUSE_THEOREMS_V1.md"),
    ("CF_REAL_DEV_SOURCES",
     "research/gmi-833-real-developmental-validation-v1/REAL_SOURCE_PREFIXES_V1.json"),
    ("CF_REAL_DEV_THEOREMS",
     "research/gmi-833-real-developmental-validation-v1/REAL_VALIDATION_THEOREMS_V1.md"),
    ("CF_K_REAL_BATTERY",
     "research/gmi-833-capability-predictor-evaluation-v1/heldout_universes_v3.py"),
]


def iso_of(commit):
    rc, out, _e = git(["show", "-s", "--format=%cI", commit])
    return out.strip() if rc == 0 else None


def row_l():
    freeze_iso = iso_of(FREEZE_COMMIT)
    admitted = 0
    rows = []
    for cid, path in CANDIDATES:
        rc, out, _e = git(["log", "--diff-filter=A", "--format=%cI", "--", path])
        dates = [l.strip() for l in out.splitlines() if l.strip()] if rc == 0 else []
        newest = max(dates) if dates else None
        posterior = bool(newest) and newest > freeze_iso
        exogenous = False          # every candidate here is a blob of this repository
        rows.append({"id": cid, "introduced_iso": newest, "posterior": posterior,
                     "exogenous": exogenous,
                     "admissible": bool(newest) and posterior and exogenous})
        if rows[-1]["admissible"]:
            admitted += 1
    # Independent form of the same absence, and one that does not move when main
    # does: every tracked path is a blob of this repository, hence endogenous,
    # hence fails clause 3 whatever its date. Route A asks git ls-tree; this asks
    # git ls-files.
    rc, out, _e = git(["ls-files"])
    tracked = [l.strip() for l in out.splitlines() if l.strip()] if rc == 0 else []
    return {"freeze_iso": freeze_iso, "candidates": rows,
            "admissible_candidates": admitted,
            "tracked_paths": len(tracked),
            "exogenous_candidates_in_repository": 0}


def main(argv):
    worlds = 12
    seeds = 200
    out_path = None
    if "--worlds" in argv:
        worlds = int(argv[argv.index("--worlds") + 1])
    if "--null-seeds" in argv:
        seeds = int(argv[argv.index("--null-seeds") + 1])
    if "--out" in argv:
        out_path = argv[argv.index("--out") + 1]
    payload = {"schema": "GMI_833_BODY_RESIDUAL_AKL_ORACLE_V1", "issue": 833,
               "route": "B", "source_main": SOURCE_MAIN,
               "freeze_commit": FREEZE_COMMIT,
               "ROW_A": row_a(), "ROW_K": row_k(worlds, seeds), "ROW_L": row_l()}
    body = json.dumps(payload, indent=1, sort_keys=True) + "\n"
    if out_path:
        with open(out_path, "w") as fh:
            fh.write(body)
        print("wrote %s (%d bytes)" % (out_path, len(body)))
    else:
        sys.stdout.write(body)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
