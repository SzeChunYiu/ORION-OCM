"""Complete current scientific receipt, separate from original authorities."""
import json
from census_v1 import census
from witnesses_v1 import pair_results,orientation_result,rung_pairs
from source_evidence_v1 import original_results
from scm_v1 import from_units,complete_laws
from fiber_v1 import uniform_root_models,solve_fiber

def run():
    witness=from_units(rung_pairs()['three_treatment_supported'][0])
    result={'schema':'GMI_CAUSAL_RUNG_REPAIR_V1','authored_exposed_controls':True,
            'census':census(),'rung_pairs':pair_results(),
            'finite_solver':solve_fiber(uniform_root_models(3),complete_laws(witness)),
            'faithful_orientation_counterexample':orientation_result(),
            'original_source':original_results(),
            'parent_owned_bounds':'Tian--Pearl2000 equation25',
            'native_campaign_calls':0,'finite_sample_or_physical_claim':False}
    return result

def encoded(value):
    return (json.dumps(value,sort_keys=True,indent=2,default=str)+'\n').encode()
