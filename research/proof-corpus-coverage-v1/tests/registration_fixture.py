"""Authored metadata and tiny local Git objects; never select real corpus rows."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import os
import subprocess
import sys
from types import ModuleType

PACKAGE = Path(__file__).resolve().parents[1]
boot = ModuleType("registration_test_boot")
boot.__file__ = str(PACKAGE / "coverage_boot.py")
exec(compile((PACKAGE / "coverage_boot.py").read_bytes(), boot.__file__, "exec"), boot.__dict__)
for name, (relative, digest) in boot.PARENTS.items():
    boot.load_module(name, PACKAGE.parent / relative, digest)
population = boot.load_module("coverage_population", PACKAGE / "coverage_population.py")
custody = boot.load_module("coverage_git", PACKAGE / "coverage_git.py")
inputs = sys.modules["env_inputs"]
Snapshot = sys.modules["corpus_git"].Snapshot


def metadata(keys=("alpha", "beta")):
    bodies = {}; files = {}; solutions = {}; nodes = {}
    for key in keys:
        for path in (f"Theorems/Thm_{key}.lean", f"P2M/Sol/S_{key}.lean"):
            body = ("authored metadata fixture " + path + "\n").encode()
            bodies[path] = body
            files[path] = {"path": path, "mode": "100644", "oid": sha256(body).hexdigest()[:40],
                           "bytes": len(body), "sha256": sha256(body).hexdigest(), "state": "ACCEPTED"}
        wp, sp = f"Theorems/Thm_{key}.lean", f"P2M/Sol/S_{key}.lean"
        solutions[key] = dict(files[sp], imports=["P2M.Util"], solution_id="P2M.Sol.S_" + key,
                              solution_bytes=files[sp]["bytes"], solution_sha256=files[sp]["sha256"])
        nodes[key] = dict(dependencies=[], wrapper_sha256=files[wp]["sha256"],
                          solution_sha256=files[sp]["sha256"])
    source = dict(commit="a" * 40, tree="b" * 40, identity="PINNED_GIT_BLOBS", files=files,
                  verified_tree_objects={})
    graph = dict(edge_count=0, graph_kind="LEXICAL_THEOREM_IMPORT_GRAPH", nodes=nodes,
                 node_count=len(keys), semantic_dependencies_verified=False, topological_order=list(keys))
    refresh(graph)
    return source, graph, solutions, bodies


def refresh(graph):
    graph["graph_sha256"] = inputs.digest(inputs.canonical(graph["nodes"]))


def git(root, *args, data=None):
    env = {"PATH": "/usr/bin:/bin", "HOME": "/nonexistent", "LC_ALL": "C.UTF-8",
           "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null",
           "GIT_AUTHOR_NAME": "Authored fixture", "GIT_COMMITTER_NAME": "Authored fixture",
           "GIT_AUTHOR_EMAIL": "fixture@example.invalid", "GIT_COMMITTER_EMAIL": "fixture@example.invalid",
           "GIT_AUTHOR_DATE": "2026-09-07T00:00:00Z", "GIT_COMMITTER_DATE": "2026-09-07T00:00:00Z"}
    return subprocess.run(["/usr/bin/git", "--no-replace-objects", "-c", "protocol.allow=never",
                           "--git-dir=" + str(root), *args], input=data, env=env,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True).stdout


def git_metadata(tmp_path, keys=("alpha", "beta")):
    source, graph, solutions, bodies = metadata(keys)
    bare = tmp_path / "authored.git"; bare.mkdir()
    git(bare, "init", "--bare", "--template=")
    tree = {}
    for path, body in bodies.items():
        oid = git(bare, "hash-object", "-w", "--stdin", data=body).decode().strip()
        source["files"][path]["oid"] = oid
        cursor = tree; parts = path.split("/")
        for part in parts[:-1]: cursor = cursor.setdefault(part, {})
        cursor[parts[-1]] = oid
    def emit_tree(node):
        lines = []
        for name, child in sorted(node.items()):
            mode, kind, oid = ("040000", "tree", emit_tree(child)) if isinstance(child, dict) else ("100644", "blob", child)
            lines.append(f"{mode} {kind} {oid}\t{name}\n")
        return git(bare, "mktree", data="".join(lines).encode()).decode().strip()
    tree_oid = emit_tree(tree)
    source["commit"] = git(bare, "commit-tree", tree_oid, data=b"authored fixture\n").decode().strip()
    with Snapshot(bare, source["commit"]) as snapshot:
        source["tree"] = snapshot.tree
        source["verified_tree_objects"] = deepcopy(snapshot.tree_objects)
    for key, row in solutions.items(): row["oid"] = source["files"][row["path"]]["oid"]
    return source, graph, solutions, bare


def registrar_fixture(tmp_path, monkeypatch):
    registrar, records = boot.boot(PACKAGE)
    source, graph, solutions, bare = git_metadata(tmp_path, ("alpha", "beta", "gamma", "delta", "epsilon"))
    directory = tmp_path / "inventory"; directory.mkdir()
    values = {"CORPUS_SOURCE.json": source, "GRAPH.json": graph, "SOLUTIONS.json": solutions}
    for name, value in values.items(): (directory / name).write_bytes(inputs.canonical(value))
    (directory / "WRAPPERS.json").write_bytes(b"Opaque authored source bytes: deliberately not JSON.\n")
    policy = registrar.policy
    for name, value in {"COMMIT":source["commit"], "TREE":source["tree"], "PAIRS":5,"FILES":10,"EDGES":0}.items():
        monkeypatch.setattr(policy, name, value)
    monkeypatch.setattr(policy, "INPUTS", {p.name:(sha256(p.read_bytes()).hexdigest(),p.stat().st_size) for p in directory.iterdir()})
    package = tmp_path / "documents";package.mkdir()
    (package / "DESIGN.md").write_text("Authored five-pair qualification only. Four assigned; no dispatch.\n")
    monkeypatch.setattr(policy,"DOCUMENTS",{"DESIGN.md":sha256((package / "DESIGN.md").read_bytes()).hexdigest()})
    interpreter={"path":str(Path(sys.executable).resolve()),**inputs.file_record(Path(sys.executable).resolve())}
    monkeypatch.setattr(policy,"PYTHON_SHA256",interpreter["sha256"])
    source_dir=tmp_path / "loaded-sources";source_dir.mkdir()
    copied={}
    for name,record in records.items():
        destination=source_dir/(name+".py");destination.write_bytes(Path(record["path"]).read_bytes())
        copied[name]={"path":str(destination),**inputs.file_record(destination)}
    output=tmp_path / "registration";output.mkdir()
    inputs.write_json(output / "STARTED.json",{"state":"NO_DISPATCH","scope":"AUTHORED_TOY_FIXTURE"})
    return registrar,dict(directory=directory,bare=bare,out=output,package=package,sources=copied,interpreter=interpreter,started_record={"path":str(output / "STARTED.json"),**inputs.file_record(output / "STARTED.json")})
