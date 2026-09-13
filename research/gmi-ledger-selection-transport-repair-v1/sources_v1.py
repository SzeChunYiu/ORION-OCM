"""Pinned source loading without adjacent bytecode or cached source modules."""
import hashlib
import json
import types
from pathlib import Path

PR="4ae4f792b286ae2d960b31e6a87b9869029d5d06"
PR594="71786f3b10644e29418e2c1157e97a39ec0168f3"
BASE="633ba77d84b1e8bf93745b1b1a1137282bfe3434"
ADDED={
"gmi-developmental-capital-v1":("CORE.md","DEVELOPMENTAL_CAPITAL_V1.md","test_developmental_capital_v1.py"),
"gmi-learning-law-selection-v1":("CORE.md","ECOLOGY_PREDICTION_V1.md","LEARNING_LAW_SELECTION_THEOREM_V1.md",
                              "learning_law_selection_v1.py","test_ecology_prediction_v1.py","test_learning_law_selection_v1.py"),
"gmi-transport-ledger-v1":("CORE.md","TRANSPORT_LEDGER_V1.md","transport_model_v1.py","test_transport_ledger_v1.py")}
PR_PATHS={f"research/{d}/{f}" for d,fs in ADDED.items() for f in fs}|{
"research/gmi-grand-unification-v1/RECURSIVE_GAP_AUDIT_20260913.md",
"research/gmi-grand-unification-v1/THEOREM_REPLAY_INVENTORY_V1.json"}
PR594_PATHS={
'research/gmi-developmental-capital-v1/K2_REACHABILITY_CONDITION_V1.md',
'research/gmi-developmental-capital-v1/K2_RETRY_REGISTRATION_V1.md',
'research/gmi-developmental-capital-v1/test_developmental_capital_v1.py',
'research/gmi-grand-unification-v1/RECURSIVE_GAP_AUDIT_20260913.md',
'research/gmi-grand-unification-v1/THEOREM_REPLAY_INVENTORY_V1.json',
'research/gmi-learning-law-selection-v1/CORE.md',
'research/gmi-learning-law-selection-v1/DEFERRED_PREDICTIONS_V1.md',
'research/gmi-learning-law-selection-v1/LEARNING_LAW_SELECTION_THEOREM_V1.md',
'research/gmi-learning-law-selection-v1/learning_law_selection_v1.py',
'research/gmi-learning-law-selection-v1/test_deferred_predictions_v1.py',
'research/gmi-learning-law-selection-v1/test_learning_law_selection_v1.py',
'research/gmi-transport-ledger-v1/CORE.md',
'research/gmi-transport-ledger-v1/TRANSPORT_LEDGER_V1.md',
'research/gmi-transport-ledger-v1/test_transport_ledger_v1.py',
'research/gmi-transport-ledger-v1/transport_model_v1.py'}
PARENT_PATHS={
"research/gmi-delegation-cost-repair-v1/TYPED_DELEGATION_COST_THEOREM_V1.md",
"research/gmi-formal-derivation-v1/OPTIMIZATION.md",
"research/gmi-grand-unification-v1/CONTINUOUS_LIFT_BOUNDARY_THEOREM_V1.md",
"research/gmi-grand-unification-v1/CONSTRUCTIVE_SELECTION_ATTAINMENT_BRIDGE_V1.md",
"research/gmi-grand-unification-v1/EMPIRICAL_FRONTIER_IDENTIFICATION_THEOREM_V1.md",
"research/gmi-grand-unification-v1/PHENOMENOLOGY_REDUCTION_ATLAS_V1.md",
"research/m2-traversal-capital-v1/m2p1/CLAIM_LADDER.md",
"research/m2-traversal-capital-v1/m2p1/BEHAVIOURAL_RECEIPT.md",
"research/machine-intelligence-morphogenesis-v1/GMI_AXIOMS_AND_THEOREMS_V1.md",
"research/machine-intelligence-morphogenesis-v1/FACILITATED_VARIATION_OCM_PARENT_MAP_V1.md"}

def sha(data):
    return hashlib.sha256(data).hexdigest()

def verify_sources(root):
    root=Path(root)
    rows=json.loads((root/"SOURCE_BINDINGS_V1.json").read_bytes())
    expected=({("PR590",p) for p in PR_PATHS}|{("PR594",p) for p in PR594_PATHS}|
              {("PARENT",p) for p in PARENT_PATHS})
    keys=[(r["kind"],r["path"]) for r in rows]
    if len(keys)!=len(expected) or set(keys)!=expected:
        raise ValueError("source dependency coverage")
    result={}
    for row in rows:
        kind=row["kind"]; p=row["path"]
        prefix={"PR590":"raw/pr590/","PR594":"raw/pr594/","PARENT":"raw/parents/"}[kind]
        if set(row)!={"kind","commit","path","copy","bytes","sha256"}:
            raise ValueError("source row schema")
        if row["commit"]!={"PR590":PR,"PR594":PR594,"PARENT":BASE}[kind] or row["copy"]!=prefix+p:
            raise ValueError("source identity/path")
        path=root/row["copy"]
        if path.is_symlink() or not path.is_file():
            raise ValueError("nonregular source")
        data=path.read_bytes()
        if len(data)!=row["bytes"] or sha(data)!=row["sha256"]:
            raise ValueError("source content drift: "+p)
        result[(kind,p)]=data
    return result

def module_from_bytes(data,name,path):
    module=types.ModuleType(name)
    module.__file__=str(path)
    exec(compile(data,str(path),"exec"),module.__dict__)
    return module
