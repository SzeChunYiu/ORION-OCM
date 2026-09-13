import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import unittest
from itertools import product
from memory_machine_v1 import *
from memory_witnesses_v1 import expected,run_memory
from memory_costs_v1 import intervention_schedule

class MemoryTests(unittest.TestCase):
    def test_all_truth_tables_and_complete_roundtrip(self):
        for h in product((0,1),repeat=2):
            for compact in (False,True):
                image=construct(h,compact)
                self.assertEqual(decode(encode(image)),image)
                self.assertEqual([service(image,q)["answer"] for q in range(3)],
                                 [expected(h,q) for q in range(3)])

    def test_data_compression_is_not_complete_image_compression(self):
        raw,small=construct((1,0)),construct((1,0),True)
        self.assertEqual((len(raw.data),len(small.data)),(3,2))
        self.assertEqual((len(encode(raw)),len(encode(small))),(32,37))
        self.assertEqual((setup(raw,False)["total_operations"],
                          setup(small,True)["total_operations"]),(73,84))
        self.assertEqual(sum(service(raw,q)["instructions"] for q in range(3)),6)
        self.assertEqual(sum(service(small,q)["instructions"] for q in range(3)),8)

    def test_shared_slot_has_two_effects(self):
        image=construct((1,0),True)
        lesion=zero_slot(image,0)
        self.assertEqual([q for q in range(3) if service(image,q)["answer"]
                          !=service(lesion,q)["answer"]],[0,2])

    def test_code_locality_not_global_resource_equality(self):
        image=construct((1,1),True)
        lesion=replace_query(image,2,("L0","EMIT"))
        for q in (0,1):
            self.assertEqual(service(image,q),service(lesion,q))
        self.assertNotEqual(service(image,2)["answer"],service(lesion,2)["answer"])
        self.assertNotEqual(len(encode(image)),len(encode(lesion)))

    def test_no_hidden_image_cache(self):
        image=construct((1,0),True)
        service(image,0)
        self.assertEqual(service(zero_slot(image,0),0)["answer"],0)
        snapshot=encode(image)
        self.assertEqual(service(restore(snapshot),0)["answer"],1)

    def test_stack_only_is_not_all_controller_memory(self):
        image=replace_query(construct((0,0),True),2,("EMIT0",))
        self.assertEqual(service(image,2,0)["answer"],0)
        self.assertGreater(service(image,2,0)["workspace_bits"],0)
        with self.assertRaises(ValueError):
            service(construct((0,0),True),2,0)

    def test_correlated_promise(self):
        errors={}
        for h in product((0,1),repeat=2):
            image=replace_query(construct(h,True),2,("EMIT0",))
            errors[h]=service(image,2)["answer"]!=expected(h,2)
        self.assertFalse(errors[(0,0)] or errors[(1,1)])
        self.assertEqual(sum(errors.values()),2)

    def test_sham_restore_and_intervention_charges(self):
        image=construct((1,1),True)
        edit=intervention(image,zero_slot(image,0))
        self.assertEqual(edit["read_bits"],37)
        self.assertEqual(edit["write_bits"],37)
        self.assertEqual(edit["snapshot_read_write_operations"],74)
        self.assertEqual(decode(encode(image)),image)
        self.assertEqual(restore(encode(image)),image)

    def test_complete_arm_schedule_charges(self):
        row=intervention_schedule(construct((1,0),True),True)
        self.assertEqual(len(row["stages"]),6)
        self.assertEqual(row["events"]["snapshot_retention_bit_time"],6*37)
        self.assertEqual(row["events"]["snapshot_read_bits"],3*37)
        self.assertEqual(row["events"]["snapshot_release_bits"],37)
        for stage in row["stages"][1:]:
            self.assertGreater(stage["events"]["validation_checks"],0)
            self.assertGreater(stage["events"]["controller_reset_bits"],0)
            self.assertGreater(stage["events"]["instructions"],0)
        restores=[s for s in row["stages"] if s["arm"].startswith("restore")]
        for stage in restores:
            self.assertEqual(stage["image"],row["snapshot_bits"])
            self.assertEqual(stage["service"],row["stages"][0]["service"])
            self.assertEqual(stage["events"]["snapshot_read_bits"],37)

    def test_malformed_image(self):
        bits=encode(construct((1,0)))
        for bad in (bits+"0",bits[:-1],"x"+bits[1:],bits[:2]+"000"+bits[5:]):
            with self.assertRaises(ValueError):
                decode(bad)

    def test_all_witness_records(self):
        result=run_memory()
        self.assertEqual(len(result["rows"]),8)
        self.assertEqual([x["classes"] for x in result["growth"]],[2,4,8,16])

if __name__=="__main__":
    unittest.main()
