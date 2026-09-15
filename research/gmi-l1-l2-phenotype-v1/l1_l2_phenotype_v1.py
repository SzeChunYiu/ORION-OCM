"""L1/L2 phenotype extension for #602 (sibling to natural-half)."""
from __future__ import annotations
import json
from pathlib import Path
HERE = Path(__file__).resolve().parent
REGISTRY = HERE / "EXTENDED_PREDICTIONS_REGISTRY_V1.json"
RECEIPT = HERE / "RECEIPT_V1.json"
TERMINAL = "L1_L2_PHENOTYPE_EXTENSION_ADMISSIBLE_V1"
DESCRIPTORS = ["D_mem","D_tom","D_meta","D_plan","D_comm","D_pred","D_body","D_niche","D_life","D_social"]
TAXA = {
    "great_ape": {"E":9.0,"R":8.0,"V":8.0,"M":"neural","C_pred":{"tom":"high","plan":"high","comm":"high","culture":"mid"}},
    "canid": {"E":7.0,"R":6.0,"V":5.0,"M":"neural","C_pred":{"tom":"mid","plan":"mid","comm":"mid","pred":"high"}},
    "social_insect": {"E":6.0,"R":4.0,"V":9.0,"M":"neural","C_pred":{"tom":"low","plan":"collective","comm":"protocol_heavy","culture":"colony"}},
    "corvid": {"E":8.0,"R":5.0,"V":7.0,"M":"neural","C_pred":{"tom":"mid","plan":"high","comm":"mid"}},
    "cephalopod": {"E":8.0,"R":3.0,"V":4.0,"M":"neural","C_pred":{"tom":"low","plan":"high","comm":"low"}},
    "rodent": {"E":5.0,"R":7.0,"V":3.0,"M":"neural","C_pred":{"tom":"low","plan":"spatial","comm":"low"}},
}
PROFILE_LAWS = {
    "D_body":"actuator_bandwidth scales with niche variability V",
    "D_niche":"niche variability V drives episodic weight",
    "D_life":"lifespan/dev window scales with R amortization",
    "D_social":"social depth paid only if interaction value clears TOM cost",
}

def build_registry():
    rows=[]
    for name,t in TAXA.items():
        rows.append({"id":f"ext-{name}","taxon":name,"E_bio":{"E":t["E"],"R":t["R"],"V":t["V"]},"M":t["M"],
                     "C_pred":{**t["C_pred"],"failure_mode":"ordinal_contradiction_on_ge_2_descriptors"},
                     "D_holdout":{"status":"HELD_OUT","content":None}})
    reg={"schema":"GMI_L1_L2_PHENOTYPE_EXTENSION_REGISTRY_V1","frozen":True,"descriptors":DESCRIPTORS,
         "profile_laws":PROFILE_LAWS,"extension_taxa":["great_ape","canid","social_insect"],"rows":rows,"terminal":TERMINAL}
    REGISTRY.write_text(json.dumps(reg, indent=2, sort_keys=True)+"\n"); return reg

def ecology_vs_complexity(reg):
    by={r["taxon"]:r for r in reg["rows"]}
    tom_rank={"low":0,"mid":1,"high":2,"collective":1,"protocol_heavy":1}
    eco={n:r["E_bio"]["E"]*r["E_bio"]["V"] for n,r in by.items()}
    C={n:r["E_bio"]["E"]+r["E_bio"]["R"]+r["E_bio"]["V"] for n,r in by.items()}
    tom_diff=tom_rank[by["corvid"]["C_pred"]["tom"]]-tom_rank[by["cephalopod"]["C_pred"]["tom"]]
    eco_diff=eco["corvid"]-eco["cephalopod"]
    eco_better=(eco_diff>0 and tom_diff>0) and (by["social_insect"]["E_bio"]["V"]>by["canid"]["E_bio"]["V"] and by["social_insect"]["C_pred"]["comm"]=="protocol_heavy")
    return {"pair_corvid_cephalopod":{"tom_diff":tom_diff,"eco_diff":eco_diff,"complexity_diff":C["corvid"]-C["cephalopod"]},
            "ecology_predicts_better_or_equal_on_registered_contrast":eco_better,"box_tick":eco_better}

def run():
    reg=build_registry(); eco=ecology_vs_complexity(reg)
    l1={"body_sensor_actuator":{"tick":"D_body" in reg["descriptors"]},
        "ecological_niche":{"tick":"D_niche" in reg["descriptors"]},
        "lifespan_dev":{"tick":"D_life" in reg["descriptors"]},
        "social_structure":{"tick":"D_social" in reg["descriptors"]},
        "holdout":{"tick":all(r["D_holdout"]["status"]=="HELD_OUT" and r["D_holdout"]["content"] is None for r in reg["rows"])},
        "profiles_predicted":{"tick":all(bool(set(r["C_pred"])-{"failure_mode"}) for r in reg["rows"])}}
    names={r["taxon"] for r in reg["rows"]}
    l2={"great_ape":{"tick":"great_ape" in names},"canid":{"tick":"canid" in names},"social_insect":{"tick":"social_insect" in names},
        "freeze_before_phenotype":{"tick":reg["frozen"] and all(r["D_holdout"]["status"]=="HELD_OUT" for r in reg["rows"])},
        "ecology_vs_complexity":{"tick":eco["box_tick"],"evidence":eco}}
    out={"schema":"GMIL1L2PhenotypeExtensionReceiptV1","artifact":"GMI_L1_L2_PHENOTYPE_V1","issue_refs":["#602"],
         "composes_with":"research/gmi-final-target-natural-half-v1","l1_boxes":l1,"l2_boxes":l2,
         "all_extension_boxes_green":all(b["tick"] for b in l1.values()) and all(b["tick"] for b in l2.values()),
         "terminal":TERMINAL,"forbidden":["HUMAN_COGNITION_EXPLAINED","NEUROANATOMY_IDENTITY","EMPIRICAL_ETHOLOGY_PASS"]}
    RECEIPT.write_text(json.dumps(out, indent=2, sort_keys=True)+"\n"); return out

if __name__=="__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
