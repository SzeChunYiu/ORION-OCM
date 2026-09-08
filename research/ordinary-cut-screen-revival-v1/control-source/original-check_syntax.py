"""Authored syntax interfaces only: no retained cut or ordinary screening is run."""
from pathlib import Path
import copy,hashlib,importlib.util,json,sys,unittest
ROOT=Path(__file__).resolve().parent
manifest=json.loads((ROOT/"donor/LARK-FILES.json").read_bytes())
for name,pin in manifest["files"].items():
 raw=(ROOT/"donor/lark-runtime"/name).read_bytes()
 assert {"bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest()}==pin
sys.path[:0]=[str(ROOT/"source"),str(ROOT/"donor/lark-runtime")]
from syntax_engine import SyntaxEngine,SyntaxUnknown
from proof_replay import replay
PARAMS=[{"id":"V"+str(i),"type":"class"} for i in range(3)]
def contract(label,kind,pattern,floats,essential=None,dv=None):
 return {"label":label,"kind":"$a","statement":[kind]+pattern,
 "floating":[{"label":"f_"+v,"statement":[t,v]} for t,v in floats],
 "essential":essential or [],"dv":dv or []}
def library():
 return [
 contract("r_relation","wff",["X","rel","Y"],[("class","X"),("class","Y")]),
 contract("r_then","wff",["(","P","then","Q",")"],[("wff","P"),("wff","Q")]),
 contract("r_merge","class",["(","X","merge","Y",")"],[("class","X"),("class","Y")]),
 contract("r_not","wff",["NOT","P"],[("wff","P")]),
 contract("r_truth","wff",["YES"],[])]
def engine(rows=None):return SyntaxEngine(library() if rows is None else rows,PARAMS)

class SyntaxControls(unittest.TestCase):
 def test_legacy_failure_reproduced_on_authored_implication(self):
  p=ROOT/"original/donor/vendor/legacy_class_terms.py"
  spec=importlib.util.spec_from_file_location("authored_legacy",p)
  old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
  with self.assertRaisesRegex(ValueError,"wff operator"):
   old.syntax("wff",["(","A","C_","B","->","B","C_","C",")"])
 def test_generic_mixed_syntax_and_independent_expected_witness(self):
  e=engine();r=e.prove("wff",["(","V0","rel","V1","then","(","V1","merge","V2",")","rel","V0",")"])
  self.assertEqual(r["status"],"SYNTAX_PROVED")
  self.assertEqual(r["proof"],["cut-f0","cut-f1","r_relation","cut-f1","cut-f2","r_merge","cut-f0","r_relation","r_then"])
  self.assertFalse(r["native_acceptance"])
 def test_unknown_operator_is_registered_grammar_nonmembership(self):
  r=engine().prove("wff",["V0","NOT_REGISTERED","V1"])
  self.assertEqual(r["status"],"NOT_DERIVABLE_REGISTERED_GRAMMAR")
 def test_repeated_composite_images_remain_legal(self):
  r=engine().prove("wff",["(","V0","merge","V1",")","rel","(","V0","merge","V1",")"])
  self.assertEqual(r["proof"],["cut-f0","cut-f1","r_merge","cut-f0","cut-f1","r_merge","r_relation"])
 def test_mandatory_float_order_is_not_expression_order(self):
  e=engine([contract("reverse","wff",["Y","rel","X"],[("class","X"),("class","Y")])])
  self.assertEqual(e.prove("wff",["V0","rel","V1"])["proof"],["cut-f1","cut-f0","reverse"])
 def test_nullary_constructor_preserves_existing_stack(self):
  r=engine().prove("wff",["(","V0","rel","V1","then","YES",")"])
  self.assertEqual(r["proof"],["cut-f0","cut-f1","r_relation","r_truth","r_then"])
 def test_unary_type_conversions_and_positive_cycle_terminate(self):
  rows=[contract("up","wff",["X"],[("class","X")]),
        contract("down","class",["P"],[("wff","P")])]
  e=engine(rows);r=e.prove("wff",["V0"])
  self.assertEqual(r["status"],"SYNTAX_PROVED")
  self.assertTrue(replay(r["proof"],"wff",["V0"],e.compiled))
 def test_ambiguous_rules_return_one_replayed_witness(self):
  rows=library();duplicate=copy.deepcopy(rows[0]);duplicate["label"]="r_other";rows.append(duplicate)
  e=engine(rows);r=e.prove("wff",["V0","rel","V1"])
  self.assertEqual(r["status"],"SYNTAX_PROVED")
  self.assertIn(r["proof"][-1],{"r_relation","r_other"})
  self.assertTrue(replay(r["proof"],"wff",["V0","rel","V1"],e.compiled))
 def test_unsupported_nonlinearity_is_unknown_without_a_witness(self):
  rows=library()+[contract("nonlinear","wff",["P","P"],[("wff","P")])]
  e=engine(rows)
  self.assertEqual(e.prove("wff",["SOMETHING"])["status"],"UNKNOWN")
  self.assertEqual(e.prove("wff",["V0","rel","V1"])["status"],"SYNTAX_PROVED")
 def test_essential_and_DV_contracts_are_not_silently_complete(self):
  for field,value in [("essential",[{"label":"e","statement":["|-","P"]}]),("dv",[["P","Q"]])]:
   rows=library();rows[1][field]=value
   r=engine(rows).prove("wff",["UNREGISTERED"])
   self.assertEqual(r["status"],"UNKNOWN")
   self.assertFalse(r["coverage_complete"])
 def test_resource_refusal_cannot_be_swallowed_as_negative_type(self):
  def refuse():raise SyntaxUnknown("AUTHORED_RESOURCE_BOUND")
  e=engine();r=e.prove("wff",["V0","rel","V1"],refuse)
  self.assertEqual(r["status"],"UNKNOWN")
  with self.assertRaises(SyntaxUnknown):e.checker("wff",["V0","rel","V1"],refuse)
  self.assertFalse(issubclass(SyntaxUnknown,ValueError))
 def test_post_parse_resource_refusal_stays_unknown(self):
  calls=[0]
  def refuse_after_parse():
   calls[0]+=1
   if calls[0]==2:raise SyntaxUnknown("AUTHORED_POST_PARSE_BOUND")
  e=engine();r=e.prove("wff",["V0","rel","V1"],refuse_after_parse)
  self.assertEqual(e.work["parse_calls"],1)
  self.assertEqual(r["status"],"UNKNOWN")
 def test_wrong_type_and_wrong_proof_are_rejected(self):
  e=engine();self.assertEqual(e.prove("class",["V0","rel","V1"])["status"],"NOT_DERIVABLE_REGISTERED_GRAMMAR")
  with self.assertRaises(ValueError):replay(["cut-f0","cut-f1","r_then"],"wff",["V0","rel","V1"],e.compiled)
 def test_token_boundary_is_unknown_and_trailing_known_token_is_negative(self):
  e=engine()
  self.assertEqual(e.prove("wff",["V0"]*513)["status"],"UNKNOWN")
  self.assertEqual(e.prove("wff",["V0","rel","V1","V2"])["status"],"NOT_DERIVABLE_REGISTERED_GRAMMAR")
 def test_compiled_frame_detaches_caller_mutation(self):
  rows=library();e=engine(rows);rows[0]["statement"][2]="MUTATED"
  self.assertEqual(e.prove("wff",["V0","rel","V1"])["status"],"SYNTAX_PROVED")
 def test_invalid_grammar_construction_is_unknown_exception(self):
  rows=library();rows.append(copy.deepcopy(rows[0]))
  with self.assertRaises(SyntaxUnknown):engine(rows)
 def test_wff_context_regression_and_absent_setvar_inhabitants(self):
  params=[{"id":"V"+str(i),"type":"wff"} for i in range(3)]
  e=SyntaxEngine(library(),params)
  self.assertEqual(e.prove("wff",["(","V0","then","NOT","V1",")"])["proof"],["cut-f0","cut-f1","r_not","r_then"])
  self.assertEqual(e.prove("setvar",["V0"])["status"],"NOT_DERIVABLE_REGISTERED_GRAMMAR")
if __name__=="__main__":unittest.main(verbosity=2)
