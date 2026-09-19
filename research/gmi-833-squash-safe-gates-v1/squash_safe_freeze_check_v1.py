"""Squash-safe freeze-custody check for the #833 gates (parent: PR #1053 freeze).

The custody rule every #833 package must satisfy is "the freeze was committed
BEFORE any implementation". On a linear history that is a theorem of the
commit graph: the freeze file's add-commit is a proper ancestor of every
implementation file's add-commit. A squash merge destroys the proof: the
freeze and the implementation first appear together in ONE commit on main, so
the ordering can no longer be re-derived there, and every branch that later
merges main inherits the same unprovable shape.

This checker does exactly one of four things and says which:

  FREEZE_ORDER_OK               exit 0  the strict ordering proof holds.
  FREEZE_ORDER_NOT_REDERIVABLE  exit 0  freeze + implementation share a
                                        squash-shaped commit; ONLY the ordering
                                        assertion is withheld, everything that
                                        is still derivable from HEAD (and from
                                        the source freeze commit when it is
                                        reachable) was checked and is listed.
  FREEZE_ORDER_VIOLATION        exit 1  a check that could run, failed.
  FREEZE_ORDER_COULD_NOT_CHECK  exit 2  no git history to check against.

"Not re-derivable" is never "checked and fine": the state line lists what was
checked, and a freeze missing at HEAD, a pinned blob that differs, a source
freeze commit whose tree already holds an implementation artifact, or a parent
commit that already holds the package, all stay hard failures (PR #1053 freeze,
scope rules 1-3).

Usage (all paths under --pkg are relative to it):

  python3 -I -B squash_safe_freeze_check_v1.py --repo . \
      --pkg research/<package> --freeze FREEZE_V1.md \
      --impl executor_v1.py --impl 'REAL_RUNS*' --impl RESULT_V1.json \
      [--freeze-commit <sha> | --freeze-commit-file FREEZE_COMMIT.txt] \
      [--freeze-blob <blob sha>] [--present-at-freeze <file> ...] [--label <name>]

  --impl '*'   means every file of the package other than the freeze and the
               --present-at-freeze files (the "freeze precedes every other
               file" gate shape).
"""
import argparse
import fnmatch
import os
import re
import subprocess
import sys

EXIT_OK = 0
EXIT_VIOLATION = 1
EXIT_COULD_NOT_CHECK = 2

GIT = "/usr/bin/git" if os.path.exists("/usr/bin/git") else "git"
SQUASH_SUBJECT = re.compile(r"\(#[0-9]+\)\s*$")
SHA_RE = re.compile(r"^[0-9a-f]{7,40}$")


class Violation(Exception):
    pass


class CouldNotCheck(Exception):
    pass


def git(root, *args):
    p = subprocess.Popen([GIT, "-C", root] + list(args), stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    out, err = p.communicate()
    return p.returncode, out.decode("utf-8", "replace"), err.decode("utf-8", "replace")


def lines(text):
    return [l.strip() for l in text.splitlines() if l.strip()]


def tree_has(root, rev, path):
    rc, _o, _e = git(root, "cat-file", "-e", "%s:%s" % (rev, path))
    return rc == 0


def ls_tree(root, rev, prefix):
    rc, out, err = git(root, "ls-tree", "-r", "--name-only", rev, "--", prefix)
    if rc != 0:
        raise CouldNotCheck("CANNOT_LIST_TREE:%s:%s" % (rev, err.strip()))
    return lines(out)


def add_commit(root, path):
    """Earliest commit that ADDS path on HEAD's history, or None.

    --topo-order: parents strictly before children (commit dates can lie).
    -m: a file first introduced IN a merge commit (conflict resolution, or a
    smuggled add) is invisible to --diff-filter=A without it; with it the
    merge shows as the add, and a file merged in from a branch still resolves
    to its earlier branch commit because that commit is topologically first.
    """
    rc, out, err = git(root, "log", "--reverse", "--topo-order", "-m",
                       "--diff-filter=A", "--format=%H", "--", path)
    if rc != 0:
        raise CouldNotCheck("CANNOT_WALK_HISTORY:%s" % err.strip())
    ls = lines(out)
    return ls[0] if ls else None


def first_package_commit(root, pkg):
    rc, out, err = git(root, "log", "--reverse", "--topo-order", "--format=%H", "--", pkg)
    if rc != 0:
        raise CouldNotCheck("CANNOT_WALK_HISTORY:%s" % err.strip())
    ls = lines(out)
    return ls[0] if ls else None


def parents_of(root, sha):
    rc, out, _e = git(root, "rev-list", "--parents", "-n", "1", sha)
    if rc != 0:
        raise CouldNotCheck("CANNOT_READ_PARENTS:%s" % sha)
    return out.split()[1:]


def subject_of(root, sha):
    rc, out, _e = git(root, "log", "-1", "--format=%s", sha)
    if rc != 0:
        raise CouldNotCheck("CANNOT_READ_SUBJECT:%s" % sha)
    return out.strip()


def is_ancestor(root, a, b):
    rc, _o, err = git(root, "merge-base", "--is-ancestor", a, b)
    if rc == 0:
        return True
    if rc == 1:
        return False
    raise CouldNotCheck("CANNOT_TEST_ANCESTRY:%s..%s:%s" % (a, b, err.strip()))


def blob_of(root, rev, path):
    rc, out, _e = git(root, "rev-parse", "--verify", "-q", "%s:%s" % (rev, path))
    return out.strip() if rc == 0 else None


def commit_reachable(root, sha):
    rc, _o, _e = git(root, "cat-file", "-e", sha + "^{commit}")
    return rc == 0


def full_sha(root, sha):
    rc, out, _e = git(root, "rev-parse", "--verify", "-q", sha + "^{commit}")
    return out.strip() if rc == 0 else sha


def short(sha):
    return sha[:8]


def expand_impl(patterns, head_rel, excluded):
    """fnmatch each pattern against the package's HEAD file list."""
    out = []
    for pat in patterns:
        hits = [f for f in head_rel
                if f not in excluded and fnmatch.fnmatchcase(f, pat)]
        if not hits:
            raise Violation("IMPL_PATTERN_MATCHES_NOTHING_AT_HEAD:%s" % pat)
        for h in hits:
            if h not in out:
                out.append(h)
    return out


def read_pinned_commit(args, root, pkg):
    if args.freeze_commit:
        sha = args.freeze_commit.strip()
    elif args.freeze_commit_file:
        path = os.path.join(root, pkg, args.freeze_commit_file)
        try:
            with open(path, "r") as fh:
                first = fh.readline().split()
        except OSError:
            raise Violation("FREEZE_COMMIT_FILE_UNREADABLE:%s" % args.freeze_commit_file)
        if not first:
            raise Violation("FREEZE_COMMIT_FILE_EMPTY:%s" % args.freeze_commit_file)
        sha = first[0]
    else:
        return None
    if not SHA_RE.match(sha):
        raise Violation("PINNED_FREEZE_COMMIT_NOT_A_SHA:%s" % sha)
    return sha


def check(args):
    root = args.repo
    pkg = args.pkg.strip("/")
    checked = []

    rc, _o, err = git(root, "rev-parse", "--show-toplevel")
    if rc != 0:
        raise CouldNotCheck("NOT_A_GIT_REPO:%s" % err.strip())
    rc, _o, err = git(root, "rev-parse", "--verify", "-q", "HEAD^{commit}")
    if rc != 0:
        raise CouldNotCheck("NO_HEAD_COMMIT")
    rc, out, _e = git(root, "rev-parse", "--is-shallow-repository")
    if rc == 0 and out.strip() == "true":
        raise CouldNotCheck("SHALLOW_CLONE_HAS_NO_HISTORY")

    freeze_rel = args.freeze
    freeze_path = pkg + "/" + freeze_rel

    # 1. Everything derivable from HEAD alone.
    if not tree_has(root, "HEAD", freeze_path):
        raise Violation("FREEZE_FILE_ABSENT_AT_HEAD:%s" % freeze_path)
    checked.append("freeze_present_at_head")
    head_files = ls_tree(root, "HEAD", pkg + "/")
    head_rel = [f[len(pkg) + 1:] for f in head_files if f.startswith(pkg + "/")]
    excluded = set([freeze_rel] + list(args.present_at_freeze))
    for f in args.present_at_freeze:
        if f not in head_rel:
            raise Violation("FROZEN_ARTIFACT_ABSENT_AT_HEAD:%s" % f)
    if args.present_at_freeze:
        checked.append("frozen_artifacts_present_at_head:%d" % len(args.present_at_freeze))
    impl = expand_impl(args.impl, head_rel, excluded)
    if not impl:
        raise Violation("NO_IMPLEMENTATION_FILES_NAMED")

    head_blob = blob_of(root, "HEAD", freeze_path)
    if args.freeze_blob:
        if head_blob != args.freeze_blob.strip():
            raise Violation("FREEZE_BYTES_DIFFER_FROM_PINNED_BLOB:head=%s pinned=%s"
                            % (head_blob, args.freeze_blob.strip()))
        checked.append("freeze_blob_matches_pin")

    # 2. The ordering proof, file by file.
    fz = add_commit(root, freeze_path)
    if fz is None:
        raise Violation("FREEZE_FILE_HAS_NO_ADD_COMMIT:%s" % freeze_path)
    shared = []
    strict = 0
    for f in impl:
        p = pkg + "/" + f
        ic = add_commit(root, p)
        if ic is None:
            raise Violation("IMPL_NOT_IN_HISTORY:%s" % p)
        if ic == fz:
            shared.append(f)
            continue
        if not is_ancestor(root, fz, ic):
            raise Violation("FREEZE_DOES_NOT_PRECEDE:%s freeze=%s impl=%s"
                            % (p, short(fz), short(ic)))
        strict += 1

    state = "OK"
    if shared:
        # The freeze and at least one implementation file first appear in the
        # same commit. That is legitimate ONLY for a squash-publication commit:
        # exactly one parent, a "(#N)" pull-request subject, and a parent that
        # holds neither the freeze nor any implementation artifact (PR #1053
        # freeze rule 2/3). Any other shared commit is the POST_HOC shape #976
        # filed and stays a violation.
        ps = parents_of(root, fz)
        subj = subject_of(root, fz)
        if len(ps) != 1 or not SQUASH_SUBJECT.search(subj):
            raise Violation("FREEZE_AND_IMPL_SHARE_NON_SQUASH_COMMIT:%s parents=%d subject=%r files=%s"
                            % (short(fz), len(ps), subj, ",".join(shared)))
        for par in ps:
            if tree_has(root, par, freeze_path):
                raise Violation("PARENT_ALREADY_CONTAINS:%s@%s" % (freeze_path, short(par)))
            for f in impl:
                if tree_has(root, par, pkg + "/" + f):
                    raise Violation("PARENT_ALREADY_CONTAINS:%s@%s" % (pkg + "/" + f, short(par)))
        checked.append("squash_shape:%s" % short(fz))
        checked.append("parent_lacks_freeze_and_impl")
        if first_package_commit(root, pkg) == fz:
            # PR #1053 freeze rule 2, literally: the first package commit holds
            # the freeze and the package path is absent from every parent.
            for par in ps:
                if ls_tree(root, par, pkg + "/"):
                    raise Violation("PACKAGE_PRESENT_IN_PARENT:%s" % short(par))
            checked.append("pkg_absent_from_parents")
        else:
            # A later squash (a revival freeze on an already-published package):
            # the parent legitimately holds earlier files. Say so, and how many.
            n_par = sum(len(ls_tree(root, par, pkg + "/")) for par in ps)
            checked.append("later_squash_pkg_files_in_parent:%d" % n_par)
        checked.append("shared_with_freeze:%d" % len(shared))
        state = "NOT_REDERIVABLE"
    if strict:
        checked.append("strict_order:%d" % strict)

    # 3. The source freeze commit, when the package pins one and it is reachable.
    pinned = read_pinned_commit(args, root, pkg)
    if pinned is not None:
        if not commit_reachable(root, pinned):
            checked.append("freeze_tree:UNREACHABLE:%s" % pinned)
        else:
            pinned_full = full_sha(root, pinned)
            names = ls_tree(root, pinned_full, pkg + "/")
            rel = [n[len(pkg) + 1:] for n in names]
            if freeze_rel not in rel:
                raise Violation("FREEZE_FILE_ABSENT_AT_PINNED_COMMIT:%s@%s"
                                % (freeze_rel, short(pinned_full)))
            for f in args.present_at_freeze:
                if f not in rel:
                    raise Violation("FROZEN_ARTIFACT_ABSENT_AT_PINNED_COMMIT:%s@%s"
                                    % (f, short(pinned_full)))
            for pat in args.impl:
                for n in rel:
                    if n not in excluded and fnmatch.fnmatchcase(n, pat):
                        raise Violation("IMPLEMENTATION_REACHABLE_FROM_FREEZE:%s@%s"
                                        % (n, short(pinned_full)))
            pinned_blob = blob_of(root, pinned_full, freeze_path)
            if pinned_blob != head_blob:
                raise Violation("FREEZE_BYTES_DIFFER_FROM_PINNED_COMMIT:head=%s at_%s=%s"
                                % (head_blob, short(pinned_full), pinned_blob))
            checked.append("freeze_tree_clean:%s" % short(pinned_full))
            checked.append("freeze_blob_matches_pinned_commit")
            if is_ancestor(root, pinned_full, "HEAD"):
                # The pinned commit survives on HEAD's history: the pin must
                # also precede every implementation add (the original gates'
                # own assertion), and it must be the freeze file's add commit.
                for f in impl:
                    ic = add_commit(root, pkg + "/" + f)
                    if ic == pinned_full or not is_ancestor(root, pinned_full, ic):
                        raise Violation("PINNED_FREEZE_DOES_NOT_PRECEDE:%s pinned=%s impl=%s"
                                        % (f, short(pinned_full), short(ic)))
                checked.append("pinned_commit_ancestor_of_head")
            else:
                checked.append("pinned_commit_not_on_head_history")

    return state, fz, checked


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", default=".")
    ap.add_argument("--pkg", required=True)
    ap.add_argument("--freeze", required=True, help="freeze file, relative to --pkg")
    ap.add_argument("--impl", action="append", default=[],
                    help="implementation/outcome file or fnmatch pattern, relative to --pkg")
    ap.add_argument("--present-at-freeze", action="append", default=[],
                    help="frozen artifact that must exist at HEAD and in the pinned freeze tree")
    ap.add_argument("--freeze-commit", default=None)
    ap.add_argument("--freeze-commit-file", default=None,
                    help="file (relative to --pkg) whose first token is the freeze commit sha")
    ap.add_argument("--freeze-blob", default=None, help="expected git blob sha of the freeze at HEAD")
    ap.add_argument("--label", default=None)
    args = ap.parse_args(argv)
    if not args.impl:
        ap.error("at least one --impl is required")
    label = args.label or (args.pkg.rstrip("/").split("/")[-1] + ":" + args.freeze)
    try:
        state, fz, checked = check(args)
    except Violation as v:
        print("FREEZE_ORDER_VIOLATION:%s [%s]" % (v, label))
        return EXIT_VIOLATION
    except CouldNotCheck as c:
        print("FREEZE_ORDER_COULD_NOT_CHECK:%s [%s]" % (c, label))
        return EXIT_COULD_NOT_CHECK
    print("FREEZE_ORDER_%s:%s checked:%s [%s]" % (state, fz, ",".join(checked), label))
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
