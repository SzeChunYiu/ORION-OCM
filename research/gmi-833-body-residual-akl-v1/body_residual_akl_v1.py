"""Route A executor for `gmi-833-body-residual-akl-v1` (issue #833, body rows A/K/L).

Disposition of the three open non-M rows of sections A, K and L of the #833 body,
under the decision rules fixed in FREEZE_V1.md before this file existed.

  RA-1/RA-2/RA-3  row A: the residual of the audited term, exactly, under three
                  registered scopes, plus what the row's preservation clause
                  requires to remain and who is able to repair the rest.
  BR-1/BR-2/BR-3  row K: the bridge dichotomy, the conservative-bridge census and
                  its resolution curve, and the conditioning statement about KE-3.
  FC-1/FC-2       row L: the futurity custody criterion FFA-1, validated in both
                  directions, and the count of admissible in-session candidates.

Stdlib only. Every reported quantity is an int or an exact Fraction rendered as a
string. Run:  python3 -I -B body_residual_akl_v1.py [--out RESULT_V1.json]
"""

from fractions import Fraction
import atexit
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, os.pardir, os.pardir))
GIT = "/usr/bin/git" if os.path.exists("/usr/bin/git") else "git"

SOURCE_MAIN = "5e57d4292266bccf435136e1f7d72caa32e920a0"
FREEZE_COMMIT = "c9dec25dad00ddde53ddadd3852c1d5fef1a0e03"
CLAIM_CEILING = "GMI_833_BODY_RESIDUAL_AKL_DISPOSITION_AT_REGISTERED_FINITE_SCOPE"

PKG = "research/gmi-833-body-residual-akl-v1"
AUTHORITY_PACKAGES = ("gmi-833-tranche-ab-ac-lit", "gmi-833-ab-terminology-harness-v1",
                      "gmi-833-terminology-migration-v1", "gmi-833-checklist-mirror-v1")
SELF_PACKAGE = "gmi-833-body-residual-akl-v1"

# The audited term of row A. It lives in python and JSON only: putting it in a
# markdown file of this package would add sites to the debt this package measures
# and would fail the repo-wide terminology ratchet on this very PR.
ROW_A_TERM = "obligation"
ROW_A_PATTERN = r"\b" + ROW_A_TERM + r"(?:s)?\b"

# Nulls for the scanner: one term that must not occur, one that must occur a lot.
NULL_ABSENT_TERM = "zzqx" + "vwmk"          # not a word; must score 0
NULL_PRESENT_TERM = "the"                   # must score far above 0


def run_git(args):
    proc = subprocess.Popen([GIT, "-C", REPO] + args, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    out, err = proc.communicate()
    return proc.returncode, out.decode("utf-8", "replace"), err.decode("utf-8", "replace")


def git_blob_sha1(data):
    header = ("blob %d\0" % len(data)).encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


# ---------------------------------------------------------------------------
# Row A: the residual of the audited term
# ---------------------------------------------------------------------------


def tracked_tree(commit):
    """(path -> blob sha1) for every file tracked at `commit`."""
    rc, out, err = run_git(["ls-tree", "-r", commit])
    if rc != 0:
        raise SystemExit("cannot list tree %s: %s" % (commit, err.strip()))
    tree = {}
    for line in out.splitlines():
        if not line.strip():
            continue
        meta, path = line.split("\t", 1)
        mode, kind, sha = meta.split()
        if kind == "blob":
            tree[path] = sha
    return tree


class BlobReader(object):
    """Stream frozen blobs out of the object store, one `git cat-file --batch`.

    Reading from the worktree would make every count depend on what main has
    merged since `source_main`: a file modified upstream would differ from its
    frozen blob and a deleted one would be missing. The object store always has
    the frozen bytes, so RA-1 is exactly reproducible at any HEAD.
    """

    def __init__(self, root):
        self.proc = subprocess.Popen([GIT, "-C", root, "cat-file", "--batch"],
                                     stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    def read(self, sha):
        self.proc.stdin.write((sha + "\n").encode("ascii"))
        self.proc.stdin.flush()
        header = self.proc.stdout.readline().decode("ascii", "replace").strip()
        parts = header.split()
        if len(parts) != 3 or parts[1] != "blob":
            raise ValueError("cat-file refused %s: %r" % (sha, header))
        size = int(parts[2])
        chunks = []
        got = 0
        while got < size:
            chunk = self.proc.stdout.read(size - got)
            if not chunk:
                raise ValueError("short read for %s" % sha)
            chunks.append(chunk)
            got += len(chunk)
        self.proc.stdout.read(1)
        return b"".join(chunks)

    def close(self):
        try:
            self.proc.stdin.close()
            self.proc.wait()
            self.proc.stdout.close()
        except Exception:
            pass


_READER = []


def blob_reader():
    if not _READER:
        reader = BlobReader(REPO)
        _READER.append(reader)
        atexit.register(reader.close)
    return _READER[0]


def read_tracked(path, expect_sha):
    """The frozen bytes of `path`, taken from the object store by blob sha."""
    data = blob_reader().read(expect_sha)
    got = git_blob_sha1(data)
    if got != expect_sha:
        raise ValueError("object store returned the wrong blob for %s: %s != %s"
                         % (path, got, expect_sha))
    return data.decode("utf-8", "replace")


def top_package(path):
    parts = path.split("/")
    if len(parts) >= 2 and parts[0] == "research":
        return parts[1]
    return None


def in_scope(path, scope):
    if scope == "S1":
        return path.endswith(".md") or path.endswith(".tex")
    if scope == "S2":
        return path.endswith(".md") and path.startswith("research/")
    if scope == "S3":
        if not path.endswith(".md"):
            return False
        if "/" not in path:
            return True                       # repo-root markdown
        if not path.startswith("research/"):
            return False
        pkg = top_package(path)
        return pkg not in AUTHORITY_PACKAGES and pkg != SELF_PACKAGE
    raise ValueError("unknown scope %r" % scope)


def scan_scope(tree, scope, pattern):
    rx = re.compile(pattern, re.IGNORECASE)
    files = sorted(p for p in tree if in_scope(p, scope))
    hits = 0
    files_with = 0
    per_file = {}
    for path in files:
        text = read_tracked(path, tree[path])
        n = len(rx.findall(text))
        if n:
            hits += n
            files_with += 1
            per_file[path] = n
    return {"scope": scope, "files_scanned": len(files), "files_with_hits": files_with,
            "total_hits": hits, "per_file": per_file}


def parent_gate_pattern():
    """Route A uses the frozen parent gate's own compiled pattern, not a new one."""
    gate = os.path.join(REPO, "research", "gmi-833-tranche-ab-ac-lit",
                        "GMI_TERMINOLOGY_CI_GATE_V1.py")
    spec = importlib.util.spec_from_file_location("gmi_term_gate_row_a", gate)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.BANNED_TERMS_DEFAULT[ROW_A_TERM]["pattern"], mod


def build_pin_index(tree):
    """path -> list of (pinning JSON file, hash key) for every content-hash pin.

    Rule, stated so it can be falsified: a JSON object that carries both a value
    equal to a tracked path (or ending in '/' + that path's basename when the
    value is itself a path) AND a key whose name contains sha256/sha1/blob/digest
    is a pin of that path. Nothing else counts.
    """
    hash_key = re.compile(r"sha256|sha1|blob_sha|digest", re.IGNORECASE)
    hex_rx = re.compile(r"^[0-9a-f]{40}$|^[0-9a-f]{64}$")
    tracked = set(tree)
    index = {}
    rejected = {}

    def walk(node, jpath):
        if isinstance(node, dict):
            keys = list(node.keys())
            hkeys = [k for k in keys if hash_key.search(k)
                     and isinstance(node[k], str) and hex_rx.match(node[k])]
            if hkeys:
                for k in keys:
                    v = node[k]
                    if not isinstance(v, str) or v not in tracked:
                        continue
                    if "/" not in v:
                        # A bare basename is not a pin: the first real run matched
                        # repo-root README.md against a manifest entry for a
                        # DIFFERENT README nested inside a source packet. Recorded
                        # as a rejected false-positive class, not silently dropped.
                        rejected.setdefault(v, []).append(jpath)
                        continue
                    index.setdefault(v, []).append((jpath, sorted(hkeys)[0]))
            for v in node.values():
                walk(v, jpath)
        elif isinstance(node, list):
            for v in node:
                walk(v, jpath)

    for path in sorted(tree):
        if not path.endswith(".json") or not path.startswith("research/"):
            continue
        try:
            doc = json.loads(read_tracked(path, tree[path]))
        except (ValueError, UnicodeDecodeError):
            continue
        walk(doc, path)
    return index, rejected


def verify_pins(tree, claimed):
    """Re-open each claimed pinning manifest and check it really names the path.

    Returns the number of claims REFUSED. A true pin set must refuse 0; a
    fabricated claim must be refused.
    """
    refused = 0
    cache = {}
    for path, entries in sorted(claimed.items()):
        for jpath, _key in entries:
            if jpath not in cache:
                cache[jpath] = read_tracked(jpath, tree[jpath])
            if ('"' + path + '"') not in cache[jpath]:
                refused += 1
    return refused


def row_a(tree):
    pattern, gate_mod = parent_gate_pattern()
    if pattern != ROW_A_PATTERN:
        raise ValueError("parent gate pattern drifted: %r" % pattern)
    scopes = dict((s, scan_scope(tree, s, pattern)) for s in ("S1", "S2", "S3"))
    rx = re.compile(pattern, re.IGNORECASE)

    # RA-2: what the row's preservation clause requires to remain.
    required = 0
    required_files = 0
    for path in sorted(tree):
        if not path.endswith(".md"):
            continue
        if top_package(path) not in AUTHORITY_PACKAGES:
            continue
        n = len(rx.findall(read_tracked(path, tree[path])))
        if n:
            required += n
            required_files += 1

    # RA-3: how much of the S3 residual sits in content-hash pinned files.
    pins, rejected_pins = build_pin_index(tree)
    residual_files = sorted(scopes["S3"]["per_file"])
    pinned = [p for p in residual_files if p in pins]
    pinned_hits = sum(scopes["S3"]["per_file"][p] for p in pinned)

    # A third handle on the same number: S3 must reconcile with S2 exactly.
    root_hits = 0
    root_files = 0
    for path in sorted(tree):
        if path.endswith(".md") and "/" not in path:
            n = len(rx.findall(read_tracked(path, tree[path])))
            root_hits += n
            root_files += 1

    # Nulls for the scanner itself.
    null_absent = scan_scope(tree, "S3", r"\b" + NULL_ABSENT_TERM + r"\b")["total_hits"]
    null_present = scan_scope(tree, "S3", r"\b" + NULL_PRESENT_TERM + r"\b")["total_hits"]

    # Hostiles.
    ha1 = scan_scope(tree, "S3", r"\b" + ROW_A_TERM + r"\b")["total_hits"]   # no plural
    ha2_files = len([p for p in tree if in_scope(p, "S3")
                     and top_package(p) != "machine-intelligence-morphogenesis-v1"])

    return {
        "RA-1": {
            "scopes": dict((s, {"files_scanned": v["files_scanned"],
                                "files_with_hits": v["files_with_hits"],
                                "total_hits": v["total_hits"]})
                           for s, v in scopes.items()),
            "governing_scope": "S3",
            "governing_residual": scopes["S3"]["total_hits"],
            "row_closes": scopes["S3"]["total_hits"] == 0,
            "top_residual_packages": sorted(
                ((sum(n for p, n in scopes["S3"]["per_file"].items()
                      if (top_package(p) or "<repo-root>") == pkg), pkg)
                 for pkg in set((top_package(p) or "<repo-root>")
                                for p in scopes["S3"]["per_file"])),
                key=lambda t: (-t[0], t[1]))[:10],
            "paper_facing_phrase": "UNDEFINED_IN_REPOSITORY: no papers/ directory and "
                                   "no artifact defines the phrase; not invented here",
            "repo_root_md_files": root_files,
            "repo_root_md_hits": root_hits,
            "S3_reconciles_with_S2": (scopes["S3"]["total_hits"]
                                      == scopes["S2"]["total_hits"] - required
                                      + root_hits),
            "reconciliation_identity": "S3 = S2 - required_to_remain + repo_root",
        },
        "RA-2": {"required_to_remain_hits": required,
                 "required_to_remain_files": required_files,
                 "authority_packages": list(AUTHORITY_PACKAGES)},
        "RA-3": {"residual_files": len(residual_files),
                 "content_hash_pinned_files": len(pinned),
                 "content_hash_pinned_hits": pinned_hits,
                 "unpinned_files": len(residual_files) - len(pinned),
                 "unpinned_hits": scopes["S3"]["total_hits"] - pinned_hits,
                 "pin_examples": [[p, pins[p][0][0], pins[p][0][1]] for p in pinned[:3]],
                 "bare_basename_pins_rejected": len(rejected_pins),
                 "bare_basename_examples": sorted(rejected_pins)[:3],
                 "not_a_closure_argument": True},
        "NULLS": {"absent_control_term_hits": null_absent,
                  "present_control_term_hits": null_present,
                  "absent_is_zero": null_absent == 0,
                  "present_is_large": null_present > 1000},
        "HOSTILES": {
            "HA1_singular_only_pattern_hits": ha1,
            "HA1_detected": ha1 < scopes["S3"]["total_hits"],
            "HA2_dropped_package_file_census": ha2_files,
            "HA2_detected": ha2_files < scopes["S3"]["files_scanned"],
            "HA4_fabricated_pin_refused": verify_pins(tree, dict(
                list(((p, pins[p]) for p in pinned[:5])) +
                [("research/gmi-833-body-residual-akl-v1/FREEZE_V1.md",
                  [("research/gmi-833-theory-baseline-v1/BASELINE_MANIFEST_V1.json",
                    "sha256")])])),
            "HA4_true_pins_verify": verify_pins(
                tree, dict((p, pins[p]) for p in pinned)),
        },
        "_per_file_S3": scopes["S3"]["per_file"],
        "_pins": dict((p, pins[p]) for p in pinned),
    }


# ---------------------------------------------------------------------------
# Row K: the bridge
# ---------------------------------------------------------------------------

EVAL_PKG = os.path.join(REPO, "research", "gmi-833-capability-predictor-evaluation-v1")
PRED_PKG = os.path.join(REPO, "research", "gmi-833-capability-predictor-v1")


def load_k_parents():
    if EVAL_PKG not in sys.path:
        sys.path.insert(0, EVAL_PKG)
    import heldout_universes_v1 as hu
    import heldout_universes_v2 as hv2
    import heldout_universes_v3 as hv3
    import heldout_universes_v4 as hv4
    parent = hu.load_parent()
    return hu, hv2, hv3, hv4, parent


def cap_of_bits(mu, verified, bits):
    total = Fraction(0)
    for j in range(3):
        if verified[j] and ((bits >> j) & 1):
            total += mu[j]
    return total


def admissible_bits(machine, mode, head_index):
    """The bridge's admissible solved-bit set for one machine.

    CB-MAX      every one of the 8 values.
    CB-PROTO    a head the protocol leaves untrained cannot be registered solved;
                the trained heads stay free.  A subset of CB-MAX, so a weakly
                LARGER census: the lane's most favourable conservative bridge.
    """
    if mode == "CB-MAX":
        return tuple(range(8))
    h = machine[head_index]
    out = []
    for bits in range(8):
        if bits & ~h:
            continue
        out.append(bits)
    return tuple(out)


def population_specs(hu, hv2, hv3):
    """The three REAL populations.  head_index is where h sits in the machine tuple."""
    return [("SIGMA_REAL", hu.sigma_real(), hu.REAL_MACHINES, hu.MU_REAL,
             hu.real_solved_law, 3),
            ("SIGMA_REAL2", hv2.sigma_real2(), hv2.REAL2_MACHINES, hu.MU_REAL,
             hv2.real2_solved_law, 3),
            ("SIGMA_REAL3", hv3.sigma_real3(), hv3.REAL3_MACHINES, hu.MU_REAL,
             hv3.real3_solved_law, 3)]


def counter_validation_specs(hu, hv4):
    """Populations used ONLY to prove the counter can count a non-degenerate point.

    These are the parent's V4 held-out synthetic and architecture populations, on
    which KE-1/KE-2 report 3,872 and 2,400 non-degenerate point emissions. They
    are not real trained systems and carry no part of row K's disposition; they
    exist so that a census of 0 on the real populations cannot be read off a
    counter that is simply unable to return anything else.
    """
    return [("SIGMA_SYN2", hv4.sigma_syn2(), hv4.SYN2_MACHINES, hu.MU_SYN,
             hv4.syn2_solved_law, 2),
            ("SIGMA_ARCH2", hv4.sigma_arch2(), hv4.ARCH2_MACHINES, hu.MU_ARCH,
             hv4.arch2_solved_law, 2)]


def admissible_value_sets(machines, mu, verified, mode, resolved_law, resolved_mask,
                          head_index):
    """machine index -> frozenset of admissible contract values."""
    out = []
    for i, m in enumerate(machines):
        if (resolved_mask >> i) & 1:
            out.append(frozenset([cap_of_bits(mu, verified, resolved_law(m))]))
        else:
            out.append(frozenset(cap_of_bits(mu, verified, b)
                                 for b in admissible_bits(m, mode, head_index)))
    return out


def census_for(hu, parent, spec, machines, mu, law, mode, resolved_mask,
               head_index=3, degenerate_is_point=False):
    """Exact non-degenerate world-invariant point census, structural route.

    The survivor set is world-independent (survivor_mask consults M, D, the
    search budget, H and U only), and the image is the set of contract values
    over the survivors, with UNSATISFIED contributed by every survivor the
    resource cut refuses.  So the census needs no enumeration of worlds:
      U != 0 and A != 0 -> at least two image members -> never a point;
      A == 0            -> image {UNSATISFIED} -> a DEGENERATE point;
      U == 0            -> a point iff every survivor's admissible value set is
                           the same singleton, non-degenerate iff that value > 0.
    """
    hu.install_universe(parent, spec)
    n = parent.N
    totals = {"inputs": 0, "empty_survivors": 0, "mixed": 0, "all_unsatisfied": 0,
              "multi_valued": 0, "point_degenerate": 0, "point_non_degenerate": 0}
    values = {}
    witness = None
    adm_cache = {}
    for contract in parent.CONTRACTS:
        verified = _verified_for(hu, contract)
        adm_cache[contract] = admissible_value_sets(machines, mu, verified, mode,
                                                    law, resolved_mask, head_index)
    for entry in parent.main_grid():
        (k_index, r_value, d_value, b_value, h_value,
         _u_id, _u_kind, u_mask, _alpha, contract, _tau) = entry
        totals["inputs"] += 1
        survivors = parent.survivor_mask(k_index, d_value, b_value, h_value, u_mask)
        if survivors == 0:
            totals["empty_survivors"] += 1
            continue
        res = parent.RES_MASKS[r_value]
        admissible = survivors & res
        refused = survivors & ~res & ((1 << n) - 1)
        if refused and admissible:
            totals["mixed"] += 1
            continue
        if not admissible:
            totals["all_unsatisfied"] += 1
            if degenerate_is_point:
                totals["point_degenerate"] += 1
            continue
        sets = adm_cache[contract]
        first = None
        ok = True
        for i in parent.bits_of(admissible):
            s = sets[i]
            if len(s) != 1:
                ok = False
                break
            v = next(iter(s))
            if first is None:
                first = v
            elif v != first:
                ok = False
                break
        if not ok:
            totals["multi_valued"] += 1
            continue
        if first > 0:
            totals["point_non_degenerate"] += 1
            values[str(first)] = values.get(str(first), 0) + 1
            if witness is None:
                witness = {"contract": contract, "value": str(first),
                           "survivors": parent.popcount(admissible)}
        else:
            totals["point_degenerate"] += 1
    totals["non_degenerate_values"] = dict(sorted(values.items()))
    totals["witness"] = witness
    return totals


def _verified_for(hu, contract):
    return hu.VERIFIED[contract]


def row_k():
    hu, hv2, hv3, hv4, parent = load_k_parents()
    pops = population_specs(hu, hv2, hv3)
    out = {"populations": {}, "resolution_curve": {}, "hostiles": {}, "nulls": {}}

    n_total = 0
    nd_total = 0
    for name, spec, machines, mu, law, hidx in pops:
        full = (1 << len(machines)) - 1
        proto = census_for(hu, parent, spec, machines, mu, law, "CB-PROTO", 0, hidx)
        cbmax = census_for(hu, parent, spec, machines, mu, law, "CB-MAX", 0, hidx)
        fitted = census_for(hu, parent, spec, machines, mu, law, "CB-PROTO", full, hidx)
        out["populations"][name] = {
            "machines": len(machines),
            "inputs": proto["inputs"],
            "CB_PROTO": proto,
            "CB_MAX_non_degenerate": cbmax["point_non_degenerate"],
            "HB1_fitted_law_positive_control_non_degenerate": fitted["point_non_degenerate"],
        }
        n_total += proto["inputs"]
        nd_total += proto["point_non_degenerate"]

        # Resolution curve, on the population the parent's V3 revival used.
        if name == "SIGMA_REAL3":
            curves = {}
            for order_name in ("rank_ascending", "rank_descending"):
                curve = {}
                for k in range(0, len(machines) + 1):
                    if order_name == "rank_ascending":
                        mask = (1 << k) - 1
                    else:
                        mask = (((1 << k) - 1) << (len(machines) - k)) \
                            if k else 0
                    c = census_for(hu, parent, spec, machines, mu, law, "CB-PROTO",
                                   mask, hidx)
                    curve[str(k)] = c["point_non_degenerate"]
                curves[order_name] = {
                    "curve": curve,
                    "first_k_with_non_degenerate": next(
                        (int(x) for x in sorted(curve, key=int) if curve[x] > 0), None),
                }
            out["resolution_curve"] = {
                "population": name,
                "orders": curves,
                "order_dependent": (curves["rank_ascending"]["curve"]
                                    != curves["rank_descending"]["curve"]),
                "note": "resolving a machine means supplying its measured solved-set; "
                        "N(k) for k > 0 is therefore NOT a conservative bridge and is "
                        "reported as the cost curve of the obstruction, never as a "
                        "closure of the row",
            }

        # HB3: count 0 and UNSATISFIED as non-degenerate -> the census must rise.
        hb3 = census_for(hu, parent, spec, machines, mu, law, "CB-PROTO", 0, hidx,
                         degenerate_is_point=True)
        out["hostiles"].setdefault("HB3_degenerate_counted", {})[name] = {
            "points": hb3["point_degenerate"] + hb3["point_non_degenerate"],
            "detected": (hb3["point_degenerate"] + hb3["point_non_degenerate"])
                        > proto["point_non_degenerate"],
        }
        out["hostiles"].setdefault("HB2_widened_to_CB_MAX", {})[name] = {
            "non_degenerate": cbmax["point_non_degenerate"],
            "detected_no_rise": cbmax["point_non_degenerate"] <= proto["point_non_degenerate"],
        }
        out["hostiles"].setdefault("HB1_positive_control", {})[name] = {
            "non_degenerate": fitted["point_non_degenerate"],
            "counter_can_count": fitted["point_non_degenerate"] > 0,
        }

    # HB1b: the counter-validation populations, at full resolution only.
    for name, spec, machines, mu, law, hidx in counter_validation_specs(hu, hv4):
        full = (1 << len(machines)) - 1
        c = census_for(hu, parent, spec, machines, mu, law, "CB-PROTO", full, hidx)
        out["hostiles"].setdefault("HB1b_counter_validation", {})[name] = {
            "non_degenerate": c["point_non_degenerate"],
            "distinct_values": len(c["non_degenerate_values"]),
            "counter_can_count": c["point_non_degenerate"] > 0,
            "not_a_real_population": True,
        }

    # BR-1: the dichotomy, proved on the registered populations.
    dichotomy = []
    for name, spec, machines, mu, law, hidx in pops:
        bad = []
        for i, m in enumerate(machines):
            for contract in parent.CONTRACTS:
                verified = _verified_for(hu, contract)
                vals = set(cap_of_bits(mu, verified, b)
                           for b in admissible_bits(m, "CB-PROTO", hidx))
                positive_singleton = len(vals) == 1 and next(iter(vals)) > 0
                if positive_singleton:
                    bad.append([name, contract, list(m)])
        dichotomy.append({"population": name, "machines": len(machines),
                          "machines_with_positive_singleton_admissible_set": len(bad),
                          "examples": bad[:3]})
    out["BR-1"] = {
        "statement": "under CB-PROTO no machine of any registered real population has "
                     "a singleton admissible value set with a strictly positive value; "
                     "hence AT EVERY INPUT a non-degenerate world-invariant point "
                     "requires the bridge to resolve every machine in "
                     "survivors(x) & Res(R) to one common positive value. The "
                     "requirement is per input, not global: the resolution curve shows "
                     "inputs whose survivor set is small become resolvable early.",
        "per_population": dichotomy,
        "holds": all(d["machines_with_positive_singleton_admissible_set"] == 0
                     for d in dichotomy),
    }
    out["BR-2"] = {"inputs_total": n_total, "non_degenerate_total": nd_total,
                   "row_closes": nd_total >= 1}
    out["BR-3"] = {
        "truthful_systems": 19 + 28 + 26, "real_systems": 3 * 32,
        "pairs_reported_by_KE_3": 161632,
        "statement": "KE-3 conditions on truthfully-registered worlds; membership in "
                     "that event is decided by the measured outcome (73 of 96 systems), "
                     "so KE-3 is not a test of the predictor on real trained systems",
        "claims_defect_in_F": False,
    }
    return out


# ---------------------------------------------------------------------------
# Row L: futurity is custody
# ---------------------------------------------------------------------------


def commit_epoch(commit):
    rc, out, _e = run_git(["show", "-s", "--format=%ct", commit])
    if rc != 0:
        raise SystemExit("cannot read commit time for %s" % commit)
    return int(out.strip())


def blob_introduced_epoch(path):
    rc, out, _e = run_git(["log", "--diff-filter=A", "--follow", "--format=%ct",
                           "--", path])
    if rc != 0 or not out.strip():
        rc, out, _e = run_git(["log", "--diff-filter=A", "--format=%ct", "--", path])
    lines = [int(x) for x in out.split() if x.strip().isdigit()]
    return max(lines) if lines else None


CANDIDATE_FAMILIES = [
    # (id, kind, locator, provenance)
    ("CF_G0_GRAMMAR", "repo_blob",
     "research/gmi-833-developmental-reuse-v1/FROZEN_FIXTURES_V1.json", "this programme"),
    ("CF_DEV_REUSE_THEOREMS", "repo_blob",
     "research/gmi-833-developmental-reuse-v1/DEVELOPMENTAL_REUSE_THEOREMS_V1.md",
     "this programme"),
    ("CF_REAL_DEV_SOURCES", "repo_blob",
     "research/gmi-833-real-developmental-validation-v1/REAL_SOURCE_PREFIXES_V1.json",
     "external byte sources, pinned by this programme"),
    ("CF_REAL_DEV_THEOREMS", "repo_blob",
     "research/gmi-833-real-developmental-validation-v1/REAL_VALIDATION_THEOREMS_V1.md",
     "this programme"),
    ("CF_K_REAL_BATTERY", "repo_blob",
     "research/gmi-833-capability-predictor-evaluation-v1/heldout_universes_v3.py",
     "this programme"),
    ("CF_AUTHORED_IN_SESSION", "authored_here", None, "this lane"),
]

# Fixtures that validate the checker in BOTH directions. Neither is a real family.
CHECKER_FIXTURES = [
    ("FX_ADMISSIBLE", {"dated": True, "timestamp_epoch": None, "exogenous": True,
                       "independently_attested": True}, True,
     "recall fixture: satisfies all four clauses by construction"),
    ("HC1_POSTERIOR_BUT_AUTHORED_HERE",
     {"dated": True, "timestamp_epoch": None, "exogenous": False,
      "independently_attested": True}, False, "clause 3 must reject"),
    ("HC2_UNATTESTED_DATE",
     {"dated": True, "timestamp_epoch": None, "exogenous": True,
      "independently_attested": False}, False, "clause 4 must reject"),
    ("FX_UNDATED", {"dated": False, "timestamp_epoch": None, "exogenous": True,
                    "independently_attested": True}, False, "clause 1 must reject"),
]


def ffa1(record, t_freeze):
    """FFA-1, clause by clause.  Returns (admissible, per-clause verdicts)."""
    c1 = bool(record.get("dated"))
    ts = record.get("timestamp_epoch")
    c2 = c1 and ts is not None and ts > t_freeze
    c3 = bool(record.get("exogenous"))
    c4 = bool(record.get("independently_attested"))
    return (c1 and c2 and c3 and c4), {"c1_dated": c1, "c2_posterior": c2,
                                       "c3_exogenous": c3, "c4_attested": c4}


def row_l(tree):
    t_freeze = commit_epoch(FREEZE_COMMIT)
    candidates = []
    for cid, kind, locator, provenance in CANDIDATE_FAMILIES:
        if kind == "repo_blob":
            ts = blob_introduced_epoch(locator)
            rec = {"dated": ts is not None, "timestamp_epoch": ts,
                   "exogenous": False, "independently_attested": False}
        else:
            rec = {"dated": True, "timestamp_epoch": t_freeze + 1,
                   "exogenous": False, "independently_attested": False}
        ok, clauses = ffa1(rec, t_freeze)
        candidates.append({"id": cid, "kind": kind, "locator": locator,
                           "provenance": provenance, "timestamp_epoch":
                           rec["timestamp_epoch"], "admissible": ok,
                           "clauses": clauses})

    fixtures = []
    for fid, rec, expect, why in CHECKER_FIXTURES:
        r = dict(rec)
        if r.get("dated"):
            r["timestamp_epoch"] = t_freeze + 86400
        ok, clauses = ffa1(r, t_freeze)
        fixtures.append({"id": fid, "expected_admissible": expect,
                         "admissible": ok, "agrees": ok == expect,
                         "why": why, "clauses": clauses})

    # Second, independent way of establishing the same absence: no blob tracked
    # anywhere in the repository was introduced after the freeze commit.
    rc, out, _e = run_git(["log", "--diff-filter=A", "--name-only", "--format=",
                           FREEZE_COMMIT + "..HEAD"])
    added_after = sorted(set(l.strip() for l in out.splitlines() if l.strip())) \
        if rc == 0 else []
    rc, out, _e = run_git(["ls-tree", "-r", "--name-only", "HEAD"])
    head_paths = [l.strip() for l in out.splitlines() if l.strip()] if rc == 0 else []

    return {
        "FC-1": {
            "criterion": "FFA-1",
            "clauses": ["dated", "posterior to the frozen prediction",
                        "exogenous to this programme",
                        "independently attested date"],
            "freeze_commit": FREEZE_COMMIT,
            "freeze_epoch": t_freeze,
            "fixtures": fixtures,
            "recall_ok": any(f["id"] == "FX_ADMISSIBLE" and f["admissible"]
                             for f in fixtures),
            "no_alarm_ok": all(f["agrees"] for f in fixtures if not f["expected_admissible"]),
            "all_fixtures_agree": all(f["agrees"] for f in fixtures),
        },
        "FC-2": {
            "candidates": candidates,
            "candidates_checked": len(candidates),
            "admissible_candidates": sum(1 for c in candidates if c["admissible"]),
            "row_closes": any(c["admissible"] for c in candidates),
            "second_route_to_the_absence":
                {"method": "exhaustive over the repository rather than over the "
                           "candidate list: every path tracked at HEAD is a blob of "
                           "this repository, hence endogenous, hence fails FFA-1 "
                           "clause 3 whatever its date. This is stable while main "
                           "moves, which a count of blobs added after the freeze is "
                           "not.",
                 "tracked_paths_at_head": len(head_paths),
                 "endogenous_by_clause_3": len(head_paths),
                 "exogenous_candidates_in_repository": 0,
                 "no_exogenous_candidate_in_repository": len(head_paths) > 0,
                 "blobs_added_after_freeze_informational": len(added_after)},
        },
    }


# ---------------------------------------------------------------------------


def main(argv):
    out_path = None
    if "--out" in argv:
        out_path = argv[argv.index("--out") + 1]
    tree = tracked_tree(SOURCE_MAIN)
    payload = {
        "schema": "GMI_833_BODY_RESIDUAL_AKL_RESULT_V1",
        "issue": 833,
        "package": SELF_PACKAGE,
        "claim_ceiling": CLAIM_CEILING,
        "source_main": SOURCE_MAIN,
        "freeze_commit": FREEZE_COMMIT,
        "row_a_term": ROW_A_TERM,
        "tracked_blobs_at_source_main": len(tree),
        "ROW_A": row_a(tree),
        "ROW_K": row_k(),
        "ROW_L": row_l(tree),
    }
    payload["DISPOSITION"] = {
        "ROW_A": "OPEN" if not payload["ROW_A"]["RA-1"]["row_closes"] else "CLOSES",
        "ROW_K": "OPEN" if not payload["ROW_K"]["BR-2"]["row_closes"] else "CLOSES",
        "ROW_L": "OPEN" if not payload["ROW_L"]["FC-2"]["row_closes"] else "CLOSES",
        "ROW_M1": "NOT_IN_SCOPE", "ROW_M2": "NOT_IN_SCOPE", "ROW_M3": "NOT_IN_SCOPE",
    }
    body = json.dumps(payload, indent=1, sort_keys=True) + "\n"
    if out_path:
        with open(out_path, "w") as handle:
            handle.write(body)
        print("wrote %s (%d bytes)" % (out_path, len(body)))
    else:
        sys.stdout.write(body)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
