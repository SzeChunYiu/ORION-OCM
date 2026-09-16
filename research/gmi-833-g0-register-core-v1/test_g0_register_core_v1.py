from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("g0", ROOT / "g0_register_core_v1.py")
g0 = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = g0
spec.loader.exec_module(g0)

class Unknown:
    pass

class TestSyntaxAndSemantics(unittest.TestCase):
    def test_instruction_classes_exact(self): self.assertEqual(g0.INSTRUCTION_CLASS_NAMES,("READ","INC","DECJZ","EMIT","HALT"))
    def test_read_emit_identity(self):
        p=g0.Program(("r",),"read",{"read":g0.Read("r","emit"),"emit":g0.Emit("r","halt"),"halt":g0.Halt()}); r=g0.execute(p,(7,),10); self.assertEqual((r.terminal,r.output),("HALTED",(7,)))
    def test_inc_dec_semantics(self):
        p=g0.Program(("r",),"i",{"i":g0.Inc("r","d"),"d":g0.DecJz("r","emit","halt"),"emit":g0.Emit("r","halt"),"halt":g0.Halt()}); r=g0.execute(p,(),10); self.assertEqual(r.terminal,"HALTED"); self.assertEqual(dict(r.registers)["r"],0); self.assertEqual(r.output,(0,))
    def test_missing_register_fail_closed(self):
        p=g0.Program(("r",),"i",{"i":g0.Inc("x","halt"),"halt":g0.Halt()}); r=g0.execute(p,(),10); self.assertEqual(r.terminal,"MALFORMED_PROGRAM"); self.assertIn("MISSING_REGISTER",r.reason)
    def test_missing_label_fail_closed(self):
        p=g0.Program(("r",),"i",{"i":g0.Inc("r","missing")}); r=g0.execute(p,(),10); self.assertEqual(r.terminal,"MALFORMED_PROGRAM"); self.assertIn("MISSING_LABEL",r.reason)
    def test_unknown_instruction_fail_closed(self):
        p=g0.Program(("r",),"x",{"x":Unknown()}); r=g0.execute(p,(),10); self.assertEqual(r.terminal,"MALFORMED_PROGRAM"); self.assertIn("UNKNOWN_INSTRUCTION",r.reason)
    def test_input_underflow_fail_closed(self):
        p=g0.Program(("r",),"read",{"read":g0.Read("r","halt"),"halt":g0.Halt()}); self.assertEqual(g0.execute(p,(),10).terminal,"INPUT_UNDERFLOW")
    def test_step_budget_fail_closed(self):
        p=g0.Program(("r",),"loop",{"loop":g0.Inc("r","loop")}); r=g0.execute(p,(),5); self.assertEqual(r.terminal,"STEP_BUDGET_EXHAUSTED"); self.assertEqual(r.resources.steps,5)
    def test_falling_off_is_malformed_not_success(self):
        p=g0.Program(("r",),"x",{"x":g0.Inc("r","gone")}); self.assertEqual(g0.execute(p,(),10).terminal,"MALFORMED_PROGRAM")
    def test_nonnatural_input_rejected(self):
        p=g0.Program(("r",),"read",{"read":g0.Read("r","halt"),"halt":g0.Halt()}); self.assertEqual(g0.execute(p,(-1,),10).terminal,"MALFORMED_PROGRAM")
    def test_resource_recount(self):
        p=g0.requirement_witnesses()["DECJZ"]
        for inp in ((0,),(1,)):
            r=g0.execute(p,inp,20); self.assertEqual(g0.recount_resources(p,r.trace),r.resources)
    def test_resource_vector_exact(self):
        p=g0.Program(("r",),"read",{"read":g0.Read("r","inc"),"inc":g0.Inc("r","dec"),"dec":g0.DecJz("r","emit","emit"),"emit":g0.Emit("r","halt"),"halt":g0.Halt()}); self.assertEqual(g0.execute(p,(0,),10).resources.as_tuple(),(5,5,3,3,1,1))

class TestRelativeMinimality(unittest.TestCase):
    def test_all_positive_requirements(self): self.assertEqual(g0.verify_positive_requirements(),{"REQ-IN":True,"REQ-OUT":True,"REQ-GEN":True,"REQ-BRANCH":True,"REQ-TERM":True})
    def test_read_necessity_bounded_census(self): self.assertEqual(g0.bounded_absence_census()["READ"]["violations"],0)
    def test_emit_necessity_bounded_census(self): self.assertEqual(g0.bounded_absence_census()["EMIT"]["violations"],0)
    def test_inc_necessity_bounded_census(self): self.assertEqual(g0.bounded_absence_census()["INC"]["violations"],0)
    def test_decjz_necessity_bounded_census(self): self.assertEqual(g0.bounded_absence_census()["DECJZ"]["violations"],0)
    def test_halt_necessity_bounded_census(self): self.assertEqual(g0.bounded_absence_census()["HALT"]["violations"],0)
    def test_absence_census_sizes(self): self.assertEqual({k:v["programs_checked"] for k,v in g0.bounded_absence_census().items()},{"READ":81,"INC":81,"DECJZ":49,"EMIT":81,"HALT":100})

class TestMealyCompiler(unittest.TestCase):
    def fixture(self): return g0.Mealy(states=(0,1),start=0,delta={(0,0):0,(0,1):1,(1,0):1,(1,1):0},output={(0,0):0,(0,1):1,(1,0):1,(1,1):0})
    def test_fixture_compiles(self):
        m=self.fixture(); p=g0.compile_mealy(m); self.assertEqual(g0.validate_program(p),()); self.assertLessEqual(len(p.instructions),10*len(m.states)+2)
    def test_fixture_semantics(self):
        m=self.fixture()
        for w in g0.all_binary_words(4):
            r=g0.execute_compiled_mealy(m,w); self.assertEqual(r.terminal,"HALTED"); self.assertEqual(r.output,g0.direct_mealy(m,w)); self.assertLessEqual(r.resources.steps,6*len(w)+5)
    def test_exhaustive_census(self): self.assertEqual(g0.exhaustive_mealy_census(),{"machines":256,"words_per_machine":15,"comparisons":3840,"behavior_mismatches":0,"terminal_failures":0,"overhead_or_resource_failures":0,"max_program_instructions":22,"max_execution_steps":23})
    def test_corrupt_mealy_delta_rejected(self):
        m=self.fixture(); bad=g0.Mealy(m.states,m.start,{k:v for k,v in m.delta.items() if k!=(1,1)},m.output)
        with self.assertRaises(ValueError): g0.compile_mealy(bad)
    def test_corrupt_mealy_output_rejected(self):
        m=self.fixture(); badout=dict(m.output); badout[(1,1)]=2
        with self.assertRaises(ValueError): g0.compile_mealy(g0.Mealy(m.states,m.start,m.delta,badout))
    def test_compiler_label_corruption_fail_closed(self):
        p=g0.compile_mealy(self.fixture()); ins=dict(p.instructions); del ins["q1_read"]; bad=g0.Program(p.registers,p.start_label,ins); r=g0.execute(bad,(1,2),20); self.assertEqual(r.terminal,"MALFORMED_PROGRAM"); self.assertIn("MISSING_LABEL",r.reason)
    def test_private_eof_not_emitted(self): self.assertEqual((g0.execute_compiled_mealy(self.fixture(),()).terminal,g0.execute_compiled_mealy(self.fixture(),()).output),("HALTED",()))
    def test_invalid_external_code_does_not_halt_in_bound(self): self.assertEqual(g0.execute(g0.compile_mealy(self.fixture()),(3,),20).terminal,"STEP_BUDGET_EXHAUSTED")

class TestCounterCompositionRecurrence(unittest.TestCase):
    def test_counter_identity_census(self): self.assertEqual(g0.counter_fragment_census(),{"programs":49,"comparisons":49,"mismatches":0})
    def test_counter_fragment_rejects_io(self):
        p=g0.Program(("r",),"read",{"read":g0.Read("r","halt"),"halt":g0.Halt()})
        with self.assertRaises(ValueError): g0.execute_counter_fragment(p)
    def test_composition(self): self.assertEqual(g0.composition_control(),{"terminal":"HALTED","output":(1,1),"program_instructions":6,"steps":6})
    def test_composition_fresh_zero_link(self):
        p=g0.Program(("r",),"halt",{"halt":g0.Halt()}); q=g0.Program(("r",),"halt",{"halt":g0.Halt()}); c=g0.sequential_compose(p,q); self.assertIn("LINK::zero",c.registers); self.assertEqual(g0.execute(c,(),5).terminal,"HALTED")
    def test_recurrence_cycle(self): self.assertEqual(g0.recurrence_control(),{"terminal":"HALTED","loop_visits":4,"final_registers":(("r",0),)})
    def test_static_storage(self): self.assertEqual(g0.storage_control(),{"terminal":"HALTED","output":(1,),"final_registers":(("cell7",1),)})

class TestReceipt(unittest.TestCase):
    def test_receipt_green(self):
        r=g0.build_receipt(); self.assertEqual(r["terminal"],"GMI_833_G0_REGISTER_CORE_V1_ALL_GREEN"); self.assertEqual(r["claim_ceiling"],g0.CLAIM_CEILING); self.assertIn("UNBIASED_SEARCH",r["forbidden_promotions"])

if __name__=="__main__": unittest.main()
