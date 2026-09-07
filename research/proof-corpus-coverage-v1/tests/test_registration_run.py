"""Complete registrar qualification with authored five-row inputs only."""
from pathlib import Path
import json
import pytest
from registration_fixture import inputs, registrar_fixture


def test_complete_toy_registration_seals_all_rows_and_four_assignments(tmp_path, monkeypatch):
    m, args = registrar_fixture(tmp_path, monkeypatch)
    called=[];order=m.ordered_population
    def ordered(rows, commit):
        assert (args["out"] / "GIT.json").is_file()
        assert (args["out"] / "POLICY.json").is_file()
        assert all((args["out"] / "inputs" / name).is_file() for name in m.policy.INPUTS)
        called.append(True);return order(rows,commit)
    monkeypatch.setattr(m,"ordered_population",ordered)
    seal=m.register(**args)
    assert called == [True]
    value=json.loads(Path(seal["path"]).read_bytes())
    assert value["state"]=="REGISTERED_NO_DISPATCH"
    actual=inputs.inventory(args["out"]);actual.pop("SEAL.json")
    assert actual==value["files"]
    population=json.loads((args["out"] / "POPULATION.json").read_bytes())
    assignment=json.loads((args["out"] / "ASSIGNMENTS.json").read_bytes())
    assert population["count"]==len(population["rows"])==5
    assert assignment["denominator"]==assignment["continuation_cursor"]==len(assignment["rows"])==4
    assert [r["key"] for r in assignment["rows"]]==[r["key"] for r in population["rows"][:4]]
    assert [r["assignment_rank"] for r in assignment["rows"]]==[0,1,2,3]
    for row in assignment["rows"]:
        assert row["state"]=="ASSIGNED_NO_DISPATCH"
        assert [s["stage"] for s in row["stages"]]==list(m.policy.STAGES)
        assert all(s["state"]=="NOT_DISPATCHED" and s["measured_cost"] is None for s in row["stages"])
    result=json.loads((args["out"] / "REGISTRATION.json").read_bytes())
    assert result["semantic_checks_reached"]==result["git_proof_blob_bodies_read"]==0
    assert result["wrapper_source_parsed"] is False
    with pytest.raises(ValueError,match="fresh"):m.register(**args)


@pytest.mark.parametrize("what",["input","document","loaded_source","invalid_metadata"])
def test_refuse_before_order_when_authority_or_population_invalid(tmp_path,monkeypatch,what):
    m,args=registrar_fixture(tmp_path,monkeypatch)
    def forbidden(*a):raise AssertionError("assignment must not be reached")
    monkeypatch.setattr(m,"ordered_population",forbidden)
    if what=="input":(args["directory"] / "GRAPH.json").write_text("changed")
    elif what=="document":(args["package"] / "DESIGN.md").write_text("changed")
    elif what=="loaded_source":Path(next(iter(args["sources"].values()))["path"]).write_text("changed")
    else:
        p=args["directory"] / "GRAPH.json";g=json.loads(p.read_bytes());g["nodes"]["beta"]["wrapper_sha256"]="f"*64
        p.write_bytes(inputs.canonical(g));m.policy.INPUTS[p.name]=(inputs.digest(p.read_bytes()),p.stat().st_size)
    with pytest.raises(ValueError):m.register(**args)
    assert not (args["out"] / "SEAL.json").exists()
    assert not (args["out"] / "POPULATION.json").exists()


@pytest.mark.parametrize("when",["original","copied_input","copied_source"])
def test_freeze_drift_after_git_refuses_before_order(tmp_path,monkeypatch,when):
    m,args=registrar_fixture(tmp_path,monkeypatch);verify=m.verify_git
    def changed(*a,**k):
        value=verify(*a,**k)
        if when=="original":p=args["directory"] / "GRAPH.json"
        elif when=="copied_input":p=args["out"] / "inputs/GRAPH.json"
        else:p=next((args["out"] / "sources").glob("*.py"))
        p.write_bytes(p.read_bytes()+b" ")
        return value
    monkeypatch.setattr(m,"verify_git",changed)
    def forbidden(*a):raise AssertionError("assignment after frozen-byte drift")
    monkeypatch.setattr(m,"ordered_population",forbidden)
    with pytest.raises(ValueError,match="binding differs"):m.register(**args)
    assert not (args["out"] / "SEAL.json").exists()


@pytest.mark.parametrize("name",["POPULATION.json","POLICY.json","GIT.json","STARTED.json"])
def test_persistent_output_mutation_cannot_be_adopted_by_final_seal(tmp_path,monkeypatch,name):
    m,args=registrar_fixture(tmp_path,monkeypatch);write=m.write_bytes
    def changed(path,value):
        write(path,value)
        if Path(path).name=="ASSIGNMENTS.json":
            victim=args["out"] / name;victim.write_bytes(victim.read_bytes()+b" ")
    monkeypatch.setattr(m,"write_bytes",changed)
    with pytest.raises(ValueError,match="binding|custody|inventory"):m.register(**args)
    assert not (args["out"] / "SEAL.json").exists()


def test_output_symlink_never_seals(tmp_path,monkeypatch):
    m,args=registrar_fixture(tmp_path,monkeypatch);write=m.write_bytes
    def changed(path,value):
        write(path,value)
        if Path(path).name=="ASSIGNMENTS.json":(args["out"] / "extra-link").symlink_to(args["directory"] / "GRAPH.json")
    monkeypatch.setattr(m,"write_bytes",changed)
    with pytest.raises(ValueError,match="symlink"):m.register(**args)
    assert not (args["out"] / "SEAL.json").exists()


def test_loaded_source_drift_after_assignment_refuses_final_seal(tmp_path,monkeypatch):
    m,args=registrar_fixture(tmp_path,monkeypatch);order=m.ordered_population
    def changed(*a):
        value=order(*a)
        p=Path(next(iter(args["sources"].values()))["path"]);p.write_bytes(p.read_bytes()+b" ")
        return value
    monkeypatch.setattr(m,"ordered_population",changed)
    with pytest.raises(ValueError,match="binding differs"):m.register(**args)
    assert (args["out"]/'POPULATION.json').is_file()
    assert not (args["out"]/'SEAL.json').exists()
