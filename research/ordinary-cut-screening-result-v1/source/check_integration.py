"""Authored integration only; never imports a retained result or parent catalogue."""
from pathlib import Path
import hashlib,json,os,subprocess,sys,tempfile,unittest
ROOT=Path(__file__).resolve().parent
PARENT=ROOT.parent/"ordinary-cut-screen-revival-v1"
sys.path[:0]=[str(ROOT/"source"),str(PARENT/"donor/lark-runtime")]
import syntax_adapter as SA
from screen_work import Work
from screen import screen
from syntax_engine import SyntaxUnknown
from retained_inputs import occurrences,validate
PARAMS=[{"id":"V"+str(i),"type":"class"} for i in range(3)]
def row(label,typecode,pattern,floats,essential=None):
 return {"label":label,"kind":"$a","statement":[typecode]+pattern,
 "floating":[{"label":"f"+v,"statement":[t,v]} for t,v in floats],
 "essential":[{"label":"h"+str(i),"statement":p} for i,p in enumerate(essential or [])],"dv":[]}
def syntax():
 return [row("rel","wff",["X","rel","Y"],[("class","X"),("class","Y")]),
  row("merge","class",["(","X","merge","Y",")"],[("class","X"),("class","Y")]),
  row("then","wff",["(","P","then","Q",")"],[("wff","P"),("wff","Q")])]
def theorem():return row("refl","|-",["(","P","then","P",")"],[("wff","P")])
def body(query=None,premises=None):
 return {"parameters":PARAMS,"query":query or ["|-","(","V0","rel","V1","then","V0","rel","V1",")"],
         "premises":[] if premises is None else premises}
def execute(rows=None,b=None,work=None):
 w=Work() if work is None else work;p=SA.SyntaxPool(syntax()+[theorem()] if rows is None else rows,w)
 return screen(body() if b is None else b,p,w),p,w
OBS=[];STARTUPS=[]
class Integration(unittest.TestCase):
 def keep(self,r):OBS.append({"test":self.id(),"screen":r});self.assertFalse(r["native_acceptance"])
 def test_full_declared_parent_and_mixed_syntax(self):
  q=["|-","(","(","V0","merge","V1",")","rel","V2","then","(","V0","merge","V1",")","rel","V2",")"]
  r,p,w=execute(b=body(q));self.keep(r)
  self.assertEqual((r["P1_total"],r["P1_visited"]),(4,4));self.assertTrue(r["coverage_complete"])
  self.assertEqual(r["aliases"][0]["proof"],["cut-f0","cut-f1","merge","cut-f2","rel","refl"])
  self.assertEqual(w["grammar_contracts_read"],4);self.assertEqual(w["P1_assertions_visited"],4)
  self.assertGreater(w["parse_calls"],0);self.assertGreater(w["parse_emit_wall_s"],0)
 def test_positive_survives_other_unknown(self):
  bad=row("unusable","|-",["Z"],[("UNSUPPORTED","Z")])
  r,_,_=execute(syntax()+[theorem(),bad]);self.keep(r)
  self.assertEqual(r["status"],"ALIAS_FOUND_PROOF_READY");self.assertFalse(r["coverage_complete"])
  self.assertEqual(r["reasons"][-1]["label"],"unusable");self.assertEqual(r["P1_visited"],5)
 def test_complete_negative(self):
  r,_,_=execute(syntax());self.keep(r)
  self.assertEqual(r["status"],"SCREENED_NEGATIVE_IN_DOMAIN");self.assertTrue(r["coverage_complete"])
 def test_incomplete_negative(self):
  bad=row("nonlinear","wff",["P","P"],[("wff","P")])
  r,_,_=execute(syntax()+[bad]);self.keep(r)
  self.assertEqual(r["status"],"UNKNOWN");self.assertFalse(r["grammar_coverage_complete"])
 def test_positive_witness_in_incomplete_grammar(self):
  bad=row("nonlinear","wff",["P","P"],[("wff","P")])
  q=["|-","V0","rel","V1"];r,_,_=execute(syntax()+[bad],body(q,[q]));self.keep(r)
  self.assertEqual(r["status"],"ALIAS_FOUND_PROOF_READY");self.assertFalse(r["coverage_complete"])
  self.assertEqual(r["aliases"][0]["proof"],["cut-h0"])
 def test_construction_unknown_cached_once(self):
  saved=SA.SyntaxEngine
  def refuse(*a):raise SyntaxUnknown("AUTHORED_CONSTRUCTION")
  SA.SyntaxEngine=refuse
  try:
   w=Work();p=SA.SyntaxPool(syntax(),w)
   for _ in range(2):
    r=screen(body(),p,w);self.keep(r);self.assertEqual(r["reasons"][0]["stage"],"construction")
   self.assertEqual(w["grammar_construction_attempts"],1)
  finally:SA.SyntaxEngine=saved
 def test_ground_refusal(self):
  r,_,w=execute(b=body(["|-"]+["V0"]*513));self.keep(r)
  self.assertEqual(r["status"],"UNKNOWN");self.assertEqual(r["reasons"][0]["stage"],"ground_guard")
  self.assertEqual(w.get("P1_assertions_visited",0),0)
 def test_matcher_unknown_is_not_cached_negative(self):
  saved=SA.Context.checker
  def refuse(self,wanted,tokens):
   if wanted=="wff" and tokens==["V0"]:raise SyntaxUnknown("AUTHORED_SUBSTITUTION")
   return saved(self,wanted,tokens)
  SA.Context.checker=refuse
  try:
   r,_,_=execute();self.keep(r)
   self.assertEqual(r["status"],"UNKNOWN");self.assertTrue(any(x["stage"]=="rule_match" for x in r["reasons"]))
  finally:SA.Context.checker=saved
 def test_proof_refusal(self):
  saved=SA.Context.proof
  def refuse(*a):raise SyntaxUnknown("AUTHORED_PROOF")
  SA.Context.proof=refuse
  try:
   r,_,_=execute();self.keep(r)
   self.assertEqual(r["status"],"UNKNOWN");self.assertTrue(any(x["stage"]=="syntax_proof" for x in r["reasons"]))
  finally:SA.Context.proof=saved
 def test_token_and_soft_wall_refusal(self):
  for w in (Work(maximum=0),Work(seconds=-1)):
   r,_,w=execute(work=w);self.keep(r)
   self.assertEqual(r["status"],"UNKNOWN");self.assertTrue(w.exhausted);self.assertFalse(r["coverage_complete"])
 def test_context_reuse_and_distinct_context(self):
  r,p,w=execute();screen(body(),p,w)
  self.assertEqual(w["grammar_construction_attempts"],1)
  p.context([{"id":"V"+str(i),"type":"wff"} for i in range(3)])
  self.assertEqual(w["grammar_construction_attempts"],2)
 def test_ordered_repeated_premise_use_and_omission(self):
  q=["|-","V0","rel","V1"];extra=["|-","V1","rel","V2"]
  same=row("reuse","|-",["P"],[("wff","P")],[["|-","P"],["|-","P"]])
  r,_,_=execute(syntax()+[same],body(q,[extra,q]));self.keep(r)
  aliases=[x for x in r["aliases"] if x["kind"]=="one_logical_assertion"]
  self.assertEqual(aliases[0]["premise_indices"],[1,1])
  self.assertEqual(aliases[0]["proof"],["cut-f0","cut-f1","rel","cut-h1","cut-h1","reuse"])
 def test_occurrences_not_deduplicated_and_inventory_bound(self):
  c={"status":"CUT_PROPOSAL","canonical_id":"same","body":body()}
  old={"roots":[{"ordinal":1,"label":"root","cuts":[c,{"status":"UNKNOWN"},c]}],
       "terminal":"TRAINING_ONLY_OPPORTUNITY_RECORDED","inputs_unchanged":True,"sources_unchanged":True,
       "request_unchanged":True,"P1_contracts":{"bytes":1,"sha256":"x"}}
  records=validate(old,syntax(),{"bytes":1,"sha256":"x"},3,2)
  self.assertEqual([x["cut_index"] for x in records],[0,2])
  self.assertEqual([x["occurrence_index"] for x in records],[0,1])
  with self.assertRaises(ValueError):validate(old,syntax()[:-1],{"bytes":1,"sha256":"x"},3,2)
  with self.assertRaises(ValueError):validate(old,syntax(),{"bytes":1,"sha256":"y"},3,2)
 def test_exact_isolated_entry_refusals(self):
  with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
   tmp=Path(tmp)
   for i,request in enumerate([{"schema":"WRONG"},{"schema":"ordinary.retained-screening-request.v1","gate_path":None}]):
    path=tmp/("request"+str(i)+".json");path.write_text(json.dumps(request))
    argv=[sys.executable,"-I","-S","-B",str(ROOT/"run_screening.py"),str(path),str(tmp/("out"+str(i)))]
    p=subprocess.run(argv,cwd=tmp,capture_output=True,text=True)
    STARTUPS.append({"argv":argv,"cwd":str(tmp),"request":request,"exit_code":p.returncode,"stdout":p.stdout,"stderr":p.stderr})
    self.assertEqual(p.returncode,1);self.assertIn("ValueError:",p.stderr);self.assertNotIn("ModuleNotFoundError",p.stderr)
    self.assertFalse((tmp/("out"+str(i))).exists())
if __name__=="__main__":
 suite=unittest.defaultTestLoader.loadTestsFromTestCase(Integration);ids=[x.id() for x in suite]
 result=unittest.TextTestRunner(verbosity=2).run(suite)
 modules={}
 for name,m in sorted(sys.modules.items()):
  path=getattr(m,"__file__",None)
  if path and Path(path).is_file():
   p=Path(path).resolve();raw=p.read_bytes()
   modules[name]={"path":str(p),"bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest()}
 payload={"schema":"ordinary.screening-integration-controls.v1","pid":os.getpid(),"parent_pid":os.getppid(),
 "cwd":os.getcwd(),"argv":sys.argv,"python":sys.executable,"sys_path":sys.path,"tests":ids,"tests_run":result.testsRun,
 "success":result.wasSuccessful(),"failures":[[x.id(),t] for x,t in result.failures],"errors":[[x.id(),t] for x,t in result.errors],
 "observations":OBS,"startups":STARTUPS,"imported_modules":modules,
 "scope":"Authored source integration only; no saved proposal/P1 parsing or screening, native, extraction, export or learner."}
 with (Path(sys.argv[1])/"CONTROLS.json").open("x") as f:json.dump(payload,f,indent=2,sort_keys=True,allow_nan=False);f.write("\n")
 raise SystemExit(0 if result.wasSuccessful() else 1)
