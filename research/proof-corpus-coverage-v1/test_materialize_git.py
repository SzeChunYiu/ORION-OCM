"""Authored local objects only; no acquisition, checkout or project code execution."""
import hashlib,json,os,subprocess,time
from pathlib import Path
import pytest

def subject():
 import materialize_git as m
 return m

def command(repo,*args,data=None):
 env={"PATH":"/usr/bin","HOME":str(repo.parent),"GIT_CONFIG_NOSYSTEM":"1","GIT_CONFIG_GLOBAL":"/dev/null",
      "GIT_AUTHOR_NAME":"Fixture","GIT_AUTHOR_EMAIL":"fixture@example.invalid","GIT_COMMITTER_NAME":"Fixture",
      "GIT_COMMITTER_EMAIL":"fixture@example.invalid","GIT_AUTHOR_DATE":"2000-01-01T00:00:00+0000",
      "GIT_COMMITTER_DATE":"2000-01-01T00:00:00+0000"}
 p=subprocess.run(["/usr/bin/git","-c","core.hooksPath=/dev/null","--git-dir="+str(repo),*args],
                  input=data,capture_output=True,env=env,check=True)
 return p.stdout

def fixture(tmp_path,files=None):
 try:
  version=subprocess.run(["/usr/bin/git","--version"],capture_output=True,env={},timeout=5)
 except (OSError,subprocess.TimeoutExpired):
  pytest.skip("authored materialization fixture requires observable Git 2.25.1")
 if version.returncode!=0 or version.stdout!=b"git version 2.25.1\n":
  pytest.skip("authored materialization fixture requires Git 2.25.1; incompatible Git is not a pass")
 repo=tmp_path/"bare";command(repo,"init","--bare","--template=",str(repo))
 files=files or {"plain":("100644",b"exact\r\nbytes\x00"),
                 "program":("100755",b"#!/missing/do-not-execute\n"),"alias":("120000",b"plain"),
                 ".gitattributes":("100644",b"plain export-ignore\nprogram export-subst\n")}
 entries=[]
 for name,(mode,data) in files.items():
  oid=command(repo,"hash-object","-w","--stdin",data=data).strip()
  entries.append(mode.encode()+b" blob "+oid+b"\t"+name.encode()+b"\0")
 tree=command(repo,"mktree","-z",data=b"".join(entries)).decode().strip()
 commit=command(repo,"commit-tree",tree,"-m","authored").decode().strip()
 return repo,commit,tree,files

def run(m,repo,commit,tree,out,**kwargs):
 return m.materialize(repo,commit,tree,m.file_map(repo),out,deadline_monotonic=time.monotonic()+20,
                      acquisition_reference={"scope":"AUTHORED_FIXTURE"},**kwargs)

def test_exact_bytes_modes_symlink_and_detached_head(tmp_path):
 m=subject();repo,commit,tree,files=fixture(tmp_path);r=run(m,repo,commit,tree,tmp_path/"out")
 assert r["terminal"]=="MATERIALIZED",r
 ws=Path(r["workspace"])
 for name,(mode,data) in files.items():
  p=ws/name
  if mode=="120000":assert os.readlink(p).encode()==data
  else:
   assert p.read_bytes()==data
   assert p.stat().st_mode&0o777==(0o755 if mode=="100755" else 0o644)
 assert (ws/".git/HEAD").read_text()==commit+"\n"
 assert command(ws/".git","rev-parse","HEAD").decode().strip()==commit
 assert len(command(ws/".git","ls-files","--stage","-z").split(b"\0"))-1==len(files)
 assert not ((ws/".git/config").stat().st_mode&0o222)
 assert not (ws/".git/objects/info/alternates").exists()

def test_no_archive_filters_or_hooks(tmp_path):
 m=subject();repo,commit,tree,_=fixture(tmp_path)
 (repo/"config").write_text('[core]\n bare = true\n hooksPath = /missing/hooks\n[filter "evil"]\n clean = /missing/program\n')
 r=run(m,repo,commit,tree,tmp_path/"out")
 assert r["terminal"]=="MATERIALIZED",r
 assert (Path(r["workspace"])/"plain").read_bytes()==b"exact\r\nbytes\x00"
 assert "evil" not in (Path(r["workspace"])/".git/config").read_text()
 assert not any(x in c["argv"] for c in r["commands"] for x in ("checkout","archive","fetch","clone"))

def test_copied_objects_have_independent_storage(tmp_path):
 m=subject();repo,commit,tree,_=fixture(tmp_path);r=run(m,repo,commit,tree,tmp_path/"out")
 assert r["terminal"]=="MATERIALIZED",r
 for p in (repo/"objects").rglob("*"):
  if p.is_file():
   target=Path(r["workspace"])/".git"/p.relative_to(repo)
   assert p.read_bytes()==target.read_bytes() and p.stat().st_ino!=target.stat().st_ino

@pytest.mark.parametrize("target",["../outside","/etc/passwd","plain/../../outside",".git/config"])
def test_unsafe_symlink_refused_and_partial_records_retained(tmp_path,target):
 m=subject();repo,c,t,_=fixture(tmp_path,{"alias":("120000",target.encode())})
 r=run(m,repo,c,t,tmp_path/"out")
 assert r["terminal"]=="MATERIALIZE_REFUSED"
 assert (tmp_path/"out/RESULT.json").is_file()

def test_symlink_chain_escape_refused(tmp_path):
 m=subject();repo,c,t,_=fixture(tmp_path,{"a":("120000",b"."),"b":("120000",b"a/../outside")})
 assert run(m,repo,c,t,tmp_path/"out")["terminal"]=="MATERIALIZE_REFUSED"

@pytest.mark.parametrize("path",["objects/info/alternates","objects/info/http-alternates","objects/pack/evil.promisor"])
def test_external_object_dependencies_refused(tmp_path,path):
 m=subject();repo,c,t,_=fixture(tmp_path);p=repo/path;p.parent.mkdir(exist_ok=True,parents=True);p.write_text("/outside\n")
 r=run(m,repo,c,t,tmp_path/"out")
 assert r["terminal"]=="MATERIALIZE_REFUSED" and "EXTERNAL_OBJECT" in r["error"]

def test_source_identity_mismatch_before_git(tmp_path):
 m=subject();repo,c,t,_=fixture(tmp_path);expected=m.file_map(repo);(repo/"config").write_text("changed")
 r=m.materialize(repo,c,t,expected,tmp_path/"out",deadline_monotonic=time.monotonic()+20,acquisition_reference={})
 assert r["terminal"]=="MATERIALIZE_REFUSED" and not r["commands"]

def test_existing_output_never_reused(tmp_path):
 m=subject();repo,c,t,_=fixture(tmp_path);out=tmp_path/"out";out.mkdir();(out/"keep").write_text("keep")
 with pytest.raises(FileExistsError):run(m,repo,c,t,out)
 assert (out/"keep").read_text()=="keep"

def test_expired_shared_deadline_preserves_refusal(tmp_path):
 m=subject();repo,c,t,_=fixture(tmp_path)
 r=m.materialize(repo,c,t,m.file_map(repo),tmp_path/"out",deadline_monotonic=time.monotonic()-1,acquisition_reference={})
 assert r["terminal"]=="MATERIALIZE_REFUSED" and "DEADLINE" in r["error"] and not r["commands"]

def test_wrong_registered_tree_refuses(tmp_path):
 m=subject();repo,c,t,_=fixture(tmp_path)
 r=run(m,repo,c,"0"*40,tmp_path/"out")
 assert r["terminal"]=="MATERIALIZE_REFUSED"

def test_gitlink_refuses(tmp_path):
 m=subject();repo,c,_,_=fixture(tmp_path)
 tree=command(repo,"mktree",data=("160000 commit "+c+"\tsubmodule\n").encode()).decode().strip()
 commit=command(repo,"commit-tree",tree,"-m","gitlink").decode().strip()
 r=run(m,repo,commit,tree,tmp_path/"out")
 assert r["terminal"]=="MATERIALIZE_REFUSED" and "MODE" in r["error"]

def test_corrupt_object_even_rebound_inventory_refuses(tmp_path):
 m=subject();repo,c,t,_=fixture(tmp_path)
 p=repo/"objects"/c[:2]/c[2:];p.chmod(0o644);p.write_bytes(b"not a git object")
 r=run(m,repo,c,t,tmp_path/"out")
 assert r["terminal"]=="MATERIALIZE_REFUSED"

@pytest.mark.parametrize("deadline",[float("inf"),float("nan"),True])
def test_invalid_deadline_refused_before_dispatch(tmp_path,deadline):
 m=subject();repo,c,t,_=fixture(tmp_path)
 r=m.materialize(repo,c,t,m.file_map(repo),tmp_path/"out",deadline_monotonic=deadline,acquisition_reference={})
 assert r["terminal"]=="MATERIALIZE_REFUSED" and "DEADLINE" in r["error"] and not r["commands"]

def test_cleanup_spools_available_batch_stdout(tmp_path,monkeypatch):
 subject()
 import materialize_objects as o
 from types import SimpleNamespace
 records=tmp_path/"records";records.mkdir()
 g=o.Git(tmp_path/"git",records,time.monotonic()+10,[])
 reader,writer=os.pipe();os.write(writer,b"retained tail");os.close(writer)
 p=SimpleNamespace(stdout=os.fdopen(reader,"rb"),returncode=7,pid=123,poll=lambda:7)
 def absent(*args):raise ProcessLookupError()
 monkeypatch.setattr(o.os,"killpg",absent)
 streams=[(records/(n+".bin")).open("xb") for n in ("stdin","stdout","stderr")]
 c={"record":str(records)}
 g.finish(p,c,streams,time.monotonic());p.stdout.close()
 assert (records/"stdout.bin").read_bytes()==b"retained tail"
 assert c["returncode"]==7 and c["group_absent"] is True

def test_nested_unicode_paths_and_shared_tree_reconstruct(tmp_path):
 m=subject();repo,c,t,files=fixture(tmp_path)
 raw=b"".join(b"040000 tree "+t.encode()+b"\t"+name.encode()+b"\0" for name in ("α","β"))
 top=command(repo,"mktree","-z",data=raw).decode().strip()
 commit=command(repo,"commit-tree",top,"-m","nested").decode().strip()
 r=run(m,repo,commit,top,tmp_path/"out")
 assert r["terminal"]=="MATERIALIZED",r
 for name in ("α","β"):
  for leaf,(mode,data) in files.items():
   p=Path(r["workspace"])/name/leaf
   assert (os.readlink(p).encode() if mode=="120000" else p.read_bytes())==data
 assert len([x for x in r["objects"] if x["kind"]=="tree"])==2
