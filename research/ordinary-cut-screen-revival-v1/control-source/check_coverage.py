"""Nine authored controls for coverage metadata; no original data or 17-test replay."""
from pathlib import Path
import hashlib,json,os,sys,unittest
ROOT=Path(__file__).resolve().parent
BASE=ROOT.parent
sys.path[:0]=[str(ROOT/"source"),str(BASE/"donor/lark-runtime")]
import syntax_engine as S
PARAMS=[{"id":"V"+str(i),"type":"class"} for i in range(3)]
ROWS=[{"label":"relation","kind":"$a","statement":["wff","X","rel","Y"],
 "floating":[{"label":"fx","statement":["class","X"]},{"label":"fy","statement":["class","Y"]}],
 "essential":[],"dv":[]}]
BAD={"label":"nonlinear","kind":"$a","statement":["wff","P","P"],
 "floating":[{"label":"fp","statement":["wff","P"]}],"essential":[],"dv":[]}
TOKENS=["V0","rel","V1"]
OBSERVED=[]
def engine(incomplete=False):return S.SyntaxEngine(ROWS+([BAD] if incomplete else []),PARAMS)
def stop():raise S.SyntaxUnknown("AUTHORED_PRE_RESOURCE")
def post():
 calls=[0]
 def callback():
  calls[0]+=1
  if calls[0]==2:raise S.SyntaxUnknown("AUTHORED_POST_PARSE_RESOURCE")
 return callback
class CoverageControls(unittest.TestCase):
 def check(self,r,status,grammar,coverage):
  OBSERVED.append({"control":self.id(),"result":r})
  self.assertEqual(r["status"],status)
  self.assertIs(r["grammar_coverage_complete"],grammar)
  self.assertIs(r["coverage_complete"],coverage)
  self.assertIs(r["native_acceptance"],False)
 def test_supported_positive(self):
  e=engine();r=e.prove("wff",TOKENS)
  self.check(r,"SYNTAX_PROVED",True,True)
  self.assertEqual(r["proof"],["cut-f0","cut-f1","relation"])
  self.assertTrue(e.checker("wff",TOKENS))
 def test_incomplete_positive_witness(self):
  e=engine(True);r=e.prove("wff",TOKENS)
  self.check(r,"SYNTAX_PROVED",False,False)
  self.assertEqual(r["proof"],["cut-f0","cut-f1","relation"])
  self.assertTrue(e.checker("wff",TOKENS))
 def test_complete_nonmembership(self):
  e=engine();self.check(e.prove("wff",["ABSENT"]),"NOT_DERIVABLE_REGISTERED_GRAMMAR",True,True)
  with self.assertRaises(ValueError):e.checker("wff",["ABSENT"])
 def test_incomplete_no_witness(self):
  e=engine(True);self.check(e.prove("wff",["ABSENT"]),"UNKNOWN",False,False)
  with self.assertRaises(S.SyntaxUnknown):e.checker("wff",["ABSENT"])
 def test_input_refusal_before_parse(self):
  for wanted,tokens in [("wff",["V0"]*513),("OTHER",TOKENS),("wff",()),("wff",[])]:
   e=engine();self.check(e.prove(wanted,tokens),"UNKNOWN",True,False)
   self.assertEqual(e.work["parse_calls"],0)
   with self.assertRaises(S.SyntaxUnknown):e.checker(wanted,tokens)
 def test_pre_resource_refusal(self):
  e=engine();self.check(e.prove("wff",TOKENS,stop),"UNKNOWN",True,False)
  self.assertEqual(e.work["parse_calls"],0)
  with self.assertRaises(S.SyntaxUnknown):e.checker("wff",TOKENS,stop)
 def test_post_parse_resource_refusal(self):
  e=engine();self.check(e.prove("wff",TOKENS,post()),"UNKNOWN",True,False)
  self.assertEqual(e.work["parse_calls"],1)
  with self.assertRaises(S.SyntaxUnknown):e.checker("wff",TOKENS,post())
 def test_replay_failure_stays_unknown(self):
  original=S.replay
  def reject(*args):raise ValueError("AUTHORED_REPLAY_REFUSAL")
  S.replay=reject
  try:
   e=engine();self.check(e.prove("wff",TOKENS),"UNKNOWN",True,False)
   self.assertEqual(e.work["parse_calls"],1)
   with self.assertRaises(S.SyntaxUnknown):e.checker("wff",TOKENS)
  finally:S.replay=original
 def test_unknown_exception_is_not_negative_valueerror(self):
  self.assertFalse(issubclass(S.SyntaxUnknown,ValueError))
  def frozen_matcher_seam():
   try:engine().checker("wff",TOKENS,stop)
   except ValueError:return "NEGATIVE"
  with self.assertRaises(S.SyntaxUnknown):frozen_matcher_seam()
if __name__=="__main__":
 suite=unittest.defaultTestLoader.loadTestsFromTestCase(CoverageControls)
 ids=[case.id() for case in suite]
 result=unittest.TextTestRunner(verbosity=2).run(suite)
 modules={}
 for name,module in sorted(sys.modules.items()):
  value=getattr(module,"__file__",None)
  if value and Path(value).is_file():
   p=Path(value).resolve();b=p.read_bytes()
   modules[name]={"path":str(p),"bytes":len(b),"sha256":hashlib.sha256(b).hexdigest()}
 payload={"schema":"ordinary.syntax-coverage-controls.v1","pid":os.getpid(),"parent_pid":os.getppid(),
  "cwd":os.getcwd(),"argv":sys.argv,"python":sys.executable,"sys_path":sys.path,
  "tests":ids,"tests_run":result.testsRun,"success":result.wasSuccessful(),
  "failures":[[c.id(),t] for c,t in result.failures],"errors":[[c.id(),t] for c,t in result.errors],
  "observations":OBSERVED,"imported_modules":modules,
  "scope":"Authored syntax coverage metadata only; no actual screening, extraction or native calls."}
 with (Path(sys.argv[1])/"CONTROLS.json").open("x") as handle:
  json.dump(payload,handle,indent=2,sort_keys=True,allow_nan=False);handle.write("\n")
 raise SystemExit(0 if result.wasSuccessful() else 1)
