import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import unittest
from collections import Counter
from fractions import Fraction as F
from teaching_machine_v1 import *
from teaching_costs_v1 import *
from teaching_witnesses_v1 import run_teaching

class TeachingTests(unittest.TestCase):
    def test_actual_decoders_against_independent_relation(self):
        for mode in (0,1):
            for message in MESSAGES:
                self.assertEqual(learn(message,mode),truth_table_oracle(message,mode))

    def test_all_encoders_and_service(self):
        for mode in (0,1):
            for h in HYPOTHESES:
                message=teach(h,mode)
                self.assertEqual(message,encoder_oracle(h,mode))
                learned=receive(pack(message,mode),mode)
                self.assertEqual(serve(learned,(0,1,0),Counter()),(h[0],h[1],h[0]))

    def test_actual_oracle_access(self):
        calls=[]
        def oracle(x):
            calls.append(x)
            return (1,0)[x]
        trace=Counter()
        self.assertEqual(acquire(oracle,trace),(1,0))
        self.assertEqual(calls,[0,1])
        self.assertEqual(trace["oracle"],2)

    def test_receiver_dependent_minimum(self):
        self.assertEqual(teach((0,0),0),(-1,-1))
        self.assertEqual(teach((0,0),1),(0,0))
        self.assertEqual(learn(teach((0,0),0),1),(1,1))
        with self.assertRaises(ValueError):
            receive(pack(teach((0,0),0),0),1)
        self.assertEqual(receive(pack(teach((0,0),1),1),1),(0,0))

    def test_truth_is_not_syntax_or_consistency(self):
        bits=pack((-1,-1),0)
        self.assertEqual(sum(receive(bits,0)!=h for h in HYPOTHESES),3)
        for h in HYPOTHESES:
            self.assertEqual(acquire(lambda x:h[x],Counter()),h)

    def test_invalid_symbols_and_missing_prices(self):
        for bits in ("01100","0","20000"):
            with self.assertRaises(ValueError):
                receive(bits,0)
        rates=prices(); rates.pop("oracle")
        with self.assertRaises(ValueError):
            total(Counter(oracle=1),rates)
        rates=prices(); rates["oracle"]=-1
        with self.assertRaises(ValueError):
            total(Counter(oracle=1),rates)

    def test_exact_fraction_boundary_and_tie(self):
        self.assertEqual(first_saving(F(3),F(4),F(1)),4)
        self.assertEqual(F(3)+4+(3-1),3*F(3))
        self.assertIsNone(first_saving(1,0,1))

    def test_runtime_retention_and_validation_are_charged(self):
        row=comparison((1,0),0,prices(),3,horizon=2,reservation=256)
        ev=row["taught_events"]
        self.assertEqual(ev["runtime_install"],3*256)
        self.assertEqual(ev["runtime_bit_time"],3*256*2)
        self.assertEqual(ev["model_bit_time"],3*2*2)
        self.assertEqual(ev["oracle"],2)
        self.assertEqual(ev["message_read"],2*5)
        self.assertEqual(ev["format_check"],2*5)
        self.assertGreater(ev["label_check"],0)
        self.assertGreater(ev["temporary_bit_time"],0)
        self.assertEqual(row["taught"],row["C"]+row["S"]+2*row["U"])

    def test_sender_keeps_channel_until_deliveries_complete(self):
        sent=sender((1,0),0)
        self.assertNotIn("message_release",sent["events"])
        self.assertEqual(receive(sent["bits"],0),(1,0))
        row=comparison((1,0),0,prices(),3)
        self.assertEqual(row["taught_events"]["message_release"],5)
        self.assertEqual(row["taught_events"]["message_read"],10)

    def test_shared_runtime_size_does_not_create_fake_advantage(self):
        a=comparison((0,1),1,prices(),4,reservation=1)
        b=comparison((0,1),1,prices(),4,reservation=1000)
        self.assertEqual(a["independent"]-a["taught"],b["independent"]-b["taught"])

    def test_actual_event_sum_boundaries_and_negative_price_case(self):
        result=run_teaching()
        self.assertEqual(len(result["rows"]),8)
        for row in result["rows"]:
            self.assertLess(row["at_boundary"]["taught"],row["at_boundary"]["independent"])

if __name__=="__main__":
    unittest.main()
