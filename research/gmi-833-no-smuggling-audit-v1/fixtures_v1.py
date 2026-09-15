from __future__ import annotations

def clean_record():
    sig=lambda **k:k
    return {
      "search_visible_identifiers":["add","index_read"],
      "denylist":{"version":"D1","entries":["transformer","self_attention","conv2d","lstm_gate","rag_retriever"]},
      "primitives":[
        {"id":"add","features":sig(arity=2,types="scalar->scalar",state_access="none",locality="local",addressability=False,content_dependent_routing=False,parameter_sharing=False,recurrence=False,stochasticity=False,verifier_access=False,resource_class="O(1)")},
        {"id":"index_read","features":sig(arity=2,types="store,index->value",state_access="read",locality="addressed",addressability=True,content_dependent_routing=False,parameter_sharing=False,recurrence=False,stochasticity=False,verifier_access=False,resource_class="O(1)")},
      ],
      "target_fingerprints":[
        {"name":"content_route_weighted_aggregate","required_features":{"content_dependent_routing":True,"locality":"global","resource_class":"O(n^2)"}},
        {"name":"translation_shared_local_kernel","required_features":{"locality":"neighborhood","parameter_sharing":True}},
      ],
      "cost":{"coordinates":["compute","memory"],"candidates":[{"id":"a","resources":{"compute":"1","memory":"1"}},{"id":"b","resources":{"compute":"2","memory":"2"}}],"scalarizations":[{"name":"w1","weights":{"compute":"1","memory":"1"}},{"name":"w2","weights":{"compute":"2","memory":"1"}}],"claim_mode":"CONDITIONAL","target_adjustments":{},"operator_costs":[{"operator":"add","target_privileged":False,"cost":"1"}]},
      "search":{"candidates":[{"id":"a","objective":"0"},{"id":"b","objective":"1"}],"budget":2,"strategies":[{"name":"forward","order":["a","b"]},{"name":"reverse","order":["b","a"]}],"tie_rule":"FIRST_SEEN","pruning_rule":"NONE","stopping_rule":"BUDGET","randomness":"NONE","seeds":[],"exhaustive_certificate":True},
      "evaluation":{"uses_architecture_ids_in_score":False,"target_id_bonus":"0","thresholds_frozen_pre_outcome":True,"posthoc_classifier_feeds_score":False,"metric_rankings":{"task_error":["a","b"],"resource_error":["a","b"]},"claim_mode":"CONDITIONAL"},
      "ecology":{"frame_status":"KNOWN","frame":[{"id":"e0","target_favoring":False},{"id":"e1","target_favoring":True}],"sample_ids":["e0","e1"],"matched_negative_registered":True,"inclusion_rule":"CENSUS","exclusion_rule":"NONE","claim_requires_representativeness":True},
    }

def lexical_hostile(name): r=clean_record(); r["search_visible_identifiers"]=[name]; return r

def semantic_rename_hostile():
    r=clean_record(); r["search_visible_identifiers"]=["mix"]
    r["primitives"]=[{"id":"mix","features":{"arity":3,"types":"sequence->sequence","state_access":"read","locality":"global","addressability":True,"content_dependent_routing":True,"parameter_sharing":False,"recurrence":False,"stochasticity":False,"verifier_access":False,"resource_class":"O(n^2)"}}]; return r

def local_shared_hostile():
    r=clean_record(); r["search_visible_identifiers"]=["local_apply"]
    r["primitives"]=[{"id":"local_apply","features":{"arity":2,"types":"grid,kernel->grid","state_access":"read","locality":"neighborhood","addressability":False,"content_dependent_routing":False,"parameter_sharing":True,"recurrence":False,"stochasticity":False,"verifier_access":False,"resource_class":"O(n)"}}]; return r

def cost_reversal_hostile():
    r=clean_record(); r["cost"]={"coordinates":["compute","memory"],"candidates":[{"id":"compute_light","resources":{"compute":"1","memory":"4"}},{"id":"memory_light","resources":{"compute":"4","memory":"1"}}],"scalarizations":[{"name":"compute_price_high","weights":{"compute":"4","memory":"1"}},{"name":"memory_price_high","weights":{"compute":"1","memory":"4"}}],"claim_mode":"UNIVERSAL_WINNER","target_adjustments":{},"operator_costs":[]}; return r

def zero_cost_hostile(): r=clean_record(); r["cost"]["operator_costs"]=[{"operator":"magic_route","target_privileged":True,"cost":"0"}]; return r

def search_order_hostile():
    r=clean_record(); r["search"]={"candidates":[{"id":"a","objective":"0"},{"id":"b","objective":"0"}],"budget":1,"strategies":[{"name":"forward","order":["a","b"]},{"name":"reverse","order":["b","a"]}],"tie_rule":"FIRST_SEEN","pruning_rule":"NONE","stopping_rule":"BUDGET","randomness":"NONE","seeds":[],"exhaustive_certificate":False}; return r

def evaluation_id_hostile(): r=clean_record(); r["evaluation"]["uses_architecture_ids_in_score"]=True; r["evaluation"]["target_id_bonus"]="1"; return r

def evaluation_metric_hostile(): r=clean_record(); r["evaluation"]["metric_rankings"]={"metric_a":["a","b"],"metric_b":["b","a"]}; r["evaluation"]["claim_mode"]="UNIVERSAL_RANKING"; return r

def ecology_bias_hostile():
    r=clean_record(); r["ecology"]["frame"]=[{"id":"n0","target_favoring":False},{"id":"n1","target_favoring":False},{"id":"p0","target_favoring":True},{"id":"p1","target_favoring":True}]; r["ecology"]["sample_ids"]=["p0","p1"]; r["ecology"]["matched_negative_registered"]=False; return r

def unknown_frame_hostile():
    r=clean_record(); r["ecology"]={"frame_status":"UNKNOWN_FRAME","sample_ids":["x"],"matched_negative_registered":False,"inclusion_rule":"UNKNOWN","exclusion_rule":"UNKNOWN","claim_requires_representativeness":True}; return r

def missing_disclosure_hostile(block):
    r=clean_record(); del r[{"lexical":"search_visible_identifiers","semantic":"primitives","cost":"cost","search":"search","evaluation":"evaluation","ecology":"ecology"}[block]]; return r
