"""Exact-source mutable-registry compatibility and cache-accounting observations."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, importlib, json, sys, types

ROOT=Path(__file__).resolve().parent
SHA=lambda b:hashlib.sha256(b).hexdigest()

def load(arm):
    name="_registry_review_"+arm
    package=types.ModuleType(name);package.__path__=[str(ROOT/arm)]
    sys.modules[name]=package
    return importlib.import_module(name+".space"),importlib.import_module(name+".types")

def make(S,T):
    reg=T.TypeRegistry()
    a=S.Atom("a","claim",warrant=S.WarrantProfile.of({"a-support"}))
    b=S.Atom("b","model",warrant=S.WarrantProfile.of({"b-support"}))
    edge=S.Hyperedge("e",("a",),("b",),"SUPPORT",warrant=S.WarrantProfile.of({"e-support"}))
    return S.KnowledgeSpace((a,b),(edge,),reg),reg

def observe(S,T,case):
    space,reg=make(S,T)
    if case in ("remove_atom_then_add","remove_atom_then_no_add"):
        reg.atom_types.remove("claim")
    elif case in ("remove_relation_then_add","remove_relation_then_no_add"):
        del reg.relation_types["SUPPORT"]
    elif case=="replace_relation_dict_then_add":
        reg.relation_types={"COMPOSITION":T.RelationSpec("COMPOSITION",executable=True)}
    elif case=="replace_atom_set_then_add":
        reg.atom_types={"model","goal"}
    elif case=="additive_registry_extension":
        reg.register_atom_type("new_type")
    row={"case":case}
    try:
        if case in ("clean_edges","remove_relation_then_add","replace_relation_dict_then_add"):
            out=space.with_edges(S.Hyperedge("new",("a",),("b",),"COMPOSITION"))
        elif case=="remove_relation_then_no_add":
            out=space.with_edges()
        elif case=="remove_atom_then_no_add":
            out=space.with_atoms()
        else:
            out=space.with_atoms(S.Atom("c","new_type" if case=="additive_registry_extension" else "goal"))
        row.update(status="RETURNED",same_instance=out is space)
        try:
            out.validate();row["returned_space_validation"]="VALID"
        except Exception as exc:
            row.update(returned_space_validation="INVALID",validation_error_type=type(exc).__name__,validation_error=str(exc))
    except Exception as exc:
        row.update(status="REJECTED",error_type=type(exc).__name__,error=str(exc))
    return row

def resources(S,T):
    space,_=make(S,T)
    space.atom_map();space.edge_map()
    for x in space.ids:
        space.incident_edges(x);space.outgoing_edges(x)
    before=space.index_resources().as_dict()
    old_keys=sorted(space.__dict__)
    space.atom_view;space.edge_view;space.evidence_universe()
    new_keys=sorted(set(space.__dict__)-set(old_keys))
    return {"documented_scope":S.KnowledgeSpace.index_resources.__doc__,"before":before,
            "after":space.index_resources().as_dict(),"new_cached_keys":new_keys,
            "new_shallow_bytes":{key:sys.getsizeof(space.__dict__[key]) for key in new_keys},
            "evidence_ids":len(space.evidence_universe()),"total_process_memory_claim":False}

bindings=json.loads((ROOT/"source-bindings.json").read_text())
for path,v in bindings["files"].items():
    if SHA((ROOT/path).read_bytes())!=v["sha256"]:raise RuntimeError("SOURCE_DRIFT")
cases=("clean_atoms","clean_edges","additive_registry_extension","remove_atom_then_add",
       "remove_atom_then_no_add","remove_relation_then_add","remove_relation_then_no_add",
       "replace_relation_dict_then_add","replace_atom_set_then_add")
rows={arm:[observe(*load(arm),case) for case in cases] for arm in ("baseline","candidate")}
for arm in rows:
    if any(r["status"]!="RETURNED" or r["returned_space_validation"]!="VALID" for r in rows[arm][:3]):
        raise RuntimeError("CLEAN_NO_ALARM_FAILED")
regressions=[b["case"] for a,b in zip(rows["baseline"],rows["candidate"]) if a["status"]=="REJECTED" and b["status"]=="RETURNED" and b.get("returned_space_validation")=="INVALID"]
result={"schema":"pr90.mutable-registry.control.v1","terminal":"COMPATIBILITY_REGRESSION_PROVED" if regressions else "NO_REGRESSION_OBSERVED",
        "utc":datetime.now(timezone.utc).isoformat(),"python":sys.version,"executable":sys.executable,
        "source_bindings":bindings,"control_sha256":SHA(Path(__file__).read_bytes()),"rows":rows,
        "regression_cases":regressions,"cache_accounting":resources(*load("candidate")),
        "scope":"isolated exact-source API control; no runtime, model, solver, broad suite, or timing comparison"}
for path,v in bindings["files"].items():
    if SHA((ROOT/path).read_bytes())!=v["sha256"]:raise RuntimeError("POST_SOURCE_DRIFT")
(ROOT/"observed.json").write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps({"terminal":result["terminal"],"clean_controls_per_arm":3,"regression_cases":regressions,
                  "new_cache_shallow_bytes":result["cache_accounting"]["new_shallow_bytes"],
                  "index_resources_changed":result["cache_accounting"]["before"]!=result["cache_accounting"]["after"],
                  "observed_sha256":SHA((ROOT/"observed.json").read_bytes())},indent=2))
