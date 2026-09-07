"""Actual authored Git→layout handoff; no acquired corpus or execution profile."""
import hashlib,json,os,stat,time
from pathlib import Path
import pytest
import corpus_layout as L
import materialize_git as M
import build_profile_policy as P
from test_materialize_git import fixture,command,run


def binding(path):
    raw=path.read_bytes()
    return {"path":str(path),"bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest()}


def authored(tmp_path,target="plain"):
    materials=[];rows=[]
    for name in ("alpha","corpus"):
        place=tmp_path/name;place.mkdir()
        bare,_,subtree,_=fixture(place,{"plain":("100644",b"authored bytes\n"),
                                      "link":("120000",target.encode())})
        top=b"040000 tree "+subtree.encode()+b"\tnested\0"
        if name=="corpus":
            lock=json.dumps({"packagesDir":".lake/packages","packages":rows},sort_keys=True).encode()
            blob=command(bare,"hash-object","-w","--stdin",data=lock).strip()
            top+=b"100644 blob "+blob+b"\tlake-manifest.json\0"
        tree=command(bare,"mktree","-z",data=top).decode().strip()
        commit=command(bare,"commit-tree",tree,"-m","authored handoff").decode().strip()
        result=run(M,bare,commit,tree,place/"material")
        assert result["terminal"]=="MATERIALIZED",result
        ws=Path(result["workspace"])
        assert stat.S_IMODE(ws.stat().st_mode)==0o755
        assert stat.S_IMODE((ws/"nested").stat().st_mode)==0o755
        materials.append({"name":name,"commit":commit,"tree":tree,
                          "receipt":binding(place/"material/RESULT.json")})
        if name=="alpha":rows.append({"name":name,"rev":commit})
    return list(reversed(materials)),binding(ws/"lake-manifest.json"),rows


def layout(data,out):
    materials,lock,rows=data
    return L._prepare(materials,lock,out,deadline_monotonic=time.monotonic()+20,
                      lock_validator=lambda raw:rows,authority_scope="AUTHORED_LAYOUT_ONLY")


@pytest.mark.parametrize("mask",[0o022,0o077])
@pytest.mark.parametrize("target",["plain","missing/leaf"])
def test_actual_nested_handoff_preserves_links_and_normalizes_directory_modes(tmp_path,mask,target):
    previous=os.umask(mask)
    try:
        data=authored(tmp_path,target)
        result=layout(data,tmp_path/"layout")
        assert result["terminal"]=="LAYOUT_READY",result
        for name,workspace in result["workspaces"].items():
            ws=Path(workspace)
            assert stat.S_IMODE(ws.stat().st_mode)==0o755
            assert stat.S_IMODE((ws/"nested").stat().st_mode)==0o755
            assert (ws/"nested/plain").read_bytes()==b"authored bytes\n"
            assert os.readlink(ws/"nested/link")==target
            for added in result["added_directories"][name]:
                assert stat.S_IMODE((ws/added).stat().st_mode)==0o755
            assert result["source_before"][name]==result["source_after"][name]
            if target=="plain":assert P.inventory(ws)
            else:
                assert not (ws/"nested/link").exists()
                with pytest.raises(FileNotFoundError):P.inventory(ws)
    finally:
        os.umask(previous)


@pytest.mark.parametrize("kind",["absolute","escape","metadata","metadata_chain","cycle"])
def test_layout_snapshot_keeps_prohibited_link_refusals(tmp_path,kind):
    root=tmp_path/"workspace";root.mkdir();(root/".git").mkdir()
    (root/".git/HEAD").write_text("metadata");(tmp_path/"outside").write_text("outside")
    if kind=="metadata_chain":(root/"indirect").symlink_to(".git")
    target={"absolute":str(tmp_path/"outside"),"escape":"../outside","metadata":".git/HEAD",
            "metadata_chain":"indirect/HEAD","cycle":"link"}[kind]
    (root/"link").symlink_to(target)
    with pytest.raises((ValueError,RuntimeError)):
        L.snapshot(root,time.monotonic()+10)


@pytest.mark.parametrize("relative",[".","nested"])
def test_materializer_refuses_unexpected_final_directory_mode(tmp_path,monkeypatch,relative):
    bare,_,tree,_=fixture(tmp_path)
    top=command(bare,"mktree",data=("040000 tree "+tree+"\tnested\n").encode()).decode().strip()
    commit=command(bare,"commit-tree",top,"-m","mode drift").decode().strip()
    original=M.Git.run;out=tmp_path/"out"
    def drift(self,*args):
        result=original(self,*args)
        if args==("rev-parse","--verify","HEAD"):(out/"workspace"/relative).chmod(0o700)
        return result
    monkeypatch.setattr(M.Git,"run",drift)
    result=run(M,bare,commit,top,out)
    assert result["terminal"]=="MATERIALIZE_REFUSED",result
    assert "OUTPUT_DIRECTORY_DRIFT" in result["error"]
    assert (out/"RESULT.json").is_file()


def test_layout_refuses_late_workspace_root_mode_drift(tmp_path,monkeypatch):
    data=authored(tmp_path);out=tmp_path/"layout";original=L.snapshot
    def drift(root,deadline):
        if root==out:(out/"materials/corpus/workspace").chmod(0o700)
        return original(root,deadline)
    monkeypatch.setattr(L,"snapshot",drift)
    result=layout(data,out)
    assert result["terminal"]=="LAYOUT_REFUSED" and "FINAL_LAYOUT_DRIFT" in result["error"]


@pytest.mark.parametrize("changed",[False,True])
def test_layout_rechecks_source_root_mode_after_copy(tmp_path,monkeypatch,changed):
    data=authored(tmp_path);original=L.copy_workspace
    def drift(source,*args):
        result=original(source,*args)
        if changed:source.chmod(0o700)
        return result
    monkeypatch.setattr(L,"copy_workspace",drift)
    result=layout(data,tmp_path/"layout")
    if changed:
        assert result["terminal"]=="LAYOUT_REFUSED" and "SOURCE_WORKSPACE_MODE" in result["error"]
    else:
        assert result["terminal"]=="LAYOUT_READY",result
