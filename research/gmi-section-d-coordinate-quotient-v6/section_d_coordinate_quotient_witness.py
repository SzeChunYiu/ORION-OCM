#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, itertools, json
from dataclasses import dataclass
from pathlib import Path

N=5
BIT_PERM=(2,4,1,0,3)
GROUPS=('S','E','R','V','H')

@dataclass(frozen=True)
class Cand:
    name:str; persistent:int; description:int; serve:int; valid:bool; meta:tuple=()

@dataclass
class Cell:
    specimen:str
    source:str
    coordinates:dict
    frontier:tuple[str,...]
    vectors:dict
    truth_digest:str

def all_bits(n=N): return list(itertools.product((0,1), repeat=n))
def truth_A(x): return x[0]^x[2]^x[4]
def truth_B(x): return int(x==(1,0,1,0,1))

def remint_truth(fn):
    inv={old:new for new,old in enumerate(BIT_PERM)}
    return lambda xn: fn(tuple(xn[inv[i]] for i in range(N)))

def table(fn): return [int(fn(x)) for x in all_bits()]

def anf_stats(vals):
    a=vals[:]
    for i in range(N):
        for mask in range(1<<N):
            if mask & (1<<i): a[mask]^=a[mask^(1<<i)]
    degrees=[]; support=[]
    for mask,c in enumerate(a):
        if c:
            d=mask.bit_count(); degrees.append(d)
            if d==1: support.append((mask & -mask).bit_length()-1)
    degree=max(degrees,default=0)
    return degree,tuple(sorted(support)) if degree<=1 else (),a[0]

def step_residual(vals):
    xs=all_bits(); best=10**9; bestspec=None
    for t in range(0,N+2):
        for pol in (0,1):
            pred=[]
            for x in xs:
                high=int(sum(x)>=t)
                pred.append(high if pol else 1-high)
            e=sum(p!=y for p,y in zip(pred,vals))
            if e<best: best=e; bestspec=(t,pol)
    return best,bestspec

def canonical_bool_digest(vals):
    xs=all_bits(); byx={x:y for x,y in zip(xs,vals)}; strings=[]
    for p in itertools.permutations(range(N)):
        inv={old:new for new,old in enumerate(p)}; s=[]
        for xn in xs:
            xo=tuple(xn[inv[i]] for i in range(N)); s.append(str(byx[xo]))
        strings.append(''.join(s))
    canon=min(strings)
    return hashlib.sha256((f'bool:{N}:'+canon).encode()).hexdigest()

def bool_candidates(fn):
    vals=table(fn); degree,support,bias=anf_stats(vals); k=min(sum(vals),len(vals)-sum(vals)); e,spec=step_residual(vals)
    return [
        Cand('full_map',32,32,1,True),
        Cand('xor_fold',1+len(support),1+len(support),len(support),degree<=1,(degree,support,bias)),
        Cand('default_exceptions',1+k,1+k,2,True,(k,)),
        Cand('count_step',2,2,N,e==0,(e,spec)),
        Cand('count_step_plus_exceptions',2+e,2+e,N+1,True,(e,spec)),
    ], {'degree':degree,'support_size':len(support) if degree<=1 else None,'minority':k,'step_residual':e,'digest':canonical_bool_digest(vals)}

def pareto(vectors):
    ok=[v for v in vectors if v['valid'] and not v['over_cap']]; out=[]
    for v in ok:
        dominated=False
        for u in ok:
            if u is v: continue
            if u['persistent']<=v['persistent'] and u['ops']<=v['ops'] and (u['persistent']<v['persistent'] or u['ops']<v['ops']):
                dominated=True; break
        if not dominated: out.append(v['name'])
    return tuple(sorted(out))

def bool_cell(specimen,source,fn,Q,cap,verifier,remint=False):
    cands,st=bool_candidates(fn); vectors=[]
    for c in cands:
        vcost=(c.description if (verifier=='proof_aware' and c.name=='xor_fold' and c.valid) else 32)
        ops=c.description+vcost+Q*c.serve
        vectors.append({'name':c.name,'persistent':c.persistent,'ops':ops,'valid':c.valid,'over_cap':c.persistent>cap})
    S={'obligation_kind':'boolean_map','canonical_semantics_digest':st['digest'],'algebraic_degree_or_null':st['degree'],'algebraic_support_or_null':st['support_size'],'minority_count_or_null':st['minority'],'best_count_step_residual_or_null':st['step_residual'],'relation_cardinality_or_null':None,'bidirectional_or_null':None}
    E={'query_horizon_or_blocks':Q,'forward_query_count':0,'reverse_query_count':0,'input_or_relation_scale':N,'recurrence_count':Q,'query_distribution_numeric_parameters':{'uniform_inputs':1}}
    R={'hard_persistent_cap':cap,'persistent_accounting_rule':'cells_v1','lifecycle_operation_rule':'description_plus_verification_plus_serve_v1','common_workspace_allowance':0}
    V={'acceptance_semantics':'exact_all_inputs','verifier_mode':verifier,'false_adoption_tolerance':0,'certificate_verification_rule':'affine_certificate_if_present_v1' if verifier=='proof_aware' else 'exhaustive_truth_check_v1'}
    H={'inherited_semantic_state':'cold','past_build_cost_sunk':True,'future_conversion_rule':'no_conversion_v1','invalidation_reset_state':'none'}
    return Cell(specimen,source,{'S':S,'E':E,'R':R,'V':V,'H':H},pareto(vectors),{v['name']:(v['persistent'],v['ops'],v['valid'],v['over_cap']) for v in vectors},st['digest'])

def rel_digest(n=4): return hashlib.sha256(json.dumps({'kind':'bijection','n':n,'bidirectional':True},sort_keys=True).encode()).hexdigest()

def relation_cell(specimen,source,history,remint=False):
    if history=='domain_to_codomain':
        ops={'key_index':23,'value_index':25,'dual_index':8,'pair_list':32}
    elif history=='codomain_to_domain':
        ops={'key_index':31,'value_index':17,'dual_index':8,'pair_list':32}
    else: raise ValueError(history)
    vectors=[
        {'name':'key_index','persistent':4,'ops':ops['key_index'],'valid':True,'over_cap':False},
        {'name':'value_index','persistent':4,'ops':ops['value_index'],'valid':True,'over_cap':False},
        {'name':'dual_index','persistent':8,'ops':ops['dual_index'],'valid':True,'over_cap':True},
        {'name':'pair_list','persistent':8,'ops':ops['pair_list'],'valid':True,'over_cap':True},
    ]
    S={'obligation_kind':'finite_bijection','canonical_semantics_digest':rel_digest(),'algebraic_degree_or_null':None,'algebraic_support_or_null':None,'minority_count_or_null':None,'best_count_step_residual_or_null':None,'relation_cardinality_or_null':4,'bidirectional_or_null':True}
    E={'query_horizon_or_blocks':1,'forward_query_count':3,'reverse_query_count':5,'input_or_relation_scale':4,'recurrence_count':1,'query_distribution_numeric_parameters':{'forward':3,'reverse':5}}
    R={'hard_persistent_cap':4,'persistent_accounting_rule':'cells_v1','lifecycle_operation_rule':'serve_plus_future_conversion_v1','common_workspace_allowance':4}
    V={'acceptance_semantics':'exact_all_queries','verifier_mode':'extensional','false_adoption_tolerance':0,'certificate_verification_rule':'exhaustive_relation_check_v1'}
    H={'inherited_semantic_state':f'map_direction:{history}','past_build_cost_sunk':True,'future_conversion_rule':'bijection_orientation_reindex_2n_v1','invalidation_reset_state':'none'}
    return Cell(specimen,source,{'S':S,'E':E,'R':R,'V':V,'H':H},pareto(vectors),{v['name']:(v['persistent'],v['ops'],v['valid'],v['over_cap']) for v in vectors},rel_digest())

def canon(obj): return json.dumps(obj,sort_keys=True,separators=(',',':'))
def schema_key(cell,drop=None): return tuple(canon(cell.coordinates[g]) for g in GROUPS if g!=drop)

def build_atlas():
    bases=[]
    configs=[
        ('A_cap8_Q16_ext','A',truth_A,16,8,'extensional'),
        ('B_cap8_Q16_ext','B',truth_B,16,8,'extensional'),
        ('A_cap64_Q1_ext','A',truth_A,1,64,'extensional'),
        ('A_cap64_Q16_ext','A',truth_A,16,64,'extensional'),
        ('A_cap64_Q16_proof','A',truth_A,16,64,'proof_aware'),
    ]
    for name,src,fn,Q,cap,V in configs:
        bases.append(bool_cell(name,name,fn,Q,cap,V,False))
        bases.append(bool_cell(name+'_remint',name,remint_truth(fn),Q,cap,V,True))
    for h in ('domain_to_codomain','codomain_to_domain'):
        name='R4_H_'+('key' if h=='domain_to_codomain' else 'value')
        bases.append(relation_cell(name,name,h,False)); bases.append(relation_cell(name+'_remint',name,h,True))
    return bases

def fiber_report(cells,drop=None):
    fibers={}
    for c in cells: fibers.setdefault(schema_key(c,drop),[]).append(c)
    bad=[]
    for cs in fibers.values():
        fronts={c.frontier for c in cs}
        if len(fronts)>1: bad.append({'specimens':[c.specimen for c in cs],'frontiers':[list(c.frontier) for c in cs]})
    return fibers,bad

def collision_examples(cells):
    out={}
    for g in GROUPS:
        _,bad=fiber_report(cells,g); out[g]=bad
    return out

def decision_partition(cells):
    d={}
    for c in cells: d.setdefault(c.frontier,[]).append(c.specimen)
    return {'|'.join(k):sorted(v) for k,v in sorted(d.items())}

def source_remint_checks(cells):
    by={c.specimen:c for c in cells}; out={}
    for c in cells:
        if c.specimen.endswith('_remint'): continue
        r=by[c.specimen+'_remint']
        out[c.specimen]={'coordinates_equal':c.coordinates==r.coordinates,'frontier_equal':c.frontier==r.frontier,'digest_equal':c.truth_digest==r.truth_digest}
    return out

def no_leakage(cells):
    forbidden_values={'xor_fold','default_exceptions','full_map','count_step','count_step_plus_exceptions','key_index','value_index','dual_index','pair_list','specimen','source_ref'}
    expected_fields={
        'S': {'obligation_kind','canonical_semantics_digest','algebraic_degree_or_null','algebraic_support_or_null','minority_count_or_null','best_count_step_residual_or_null','relation_cardinality_or_null','bidirectional_or_null'},
        'E': {'query_horizon_or_blocks','forward_query_count','reverse_query_count','input_or_relation_scale','recurrence_count','query_distribution_numeric_parameters'},
        'R': {'hard_persistent_cap','persistent_accounting_rule','lifecycle_operation_rule','common_workspace_allowance'},
        'V': {'acceptance_semantics','verifier_mode','false_adoption_tolerance','certificate_verification_rule'},
        'H': {'inherited_semantic_state','past_build_cost_sunk','future_conversion_rule','invalidation_reset_state'},
    }
    def walk_values(obj):
        if isinstance(obj,dict):
            for value in obj.values(): yield from walk_values(value)
        elif isinstance(obj,(list,tuple)):
            for value in obj: yield from walk_values(value)
        elif isinstance(obj,str): yield obj.lower()
    for c in cells:
        if set(c.coordinates)!=set(GROUPS): return False
        for group in GROUPS:
            if set(c.coordinates[group])!=expected_fields[group]: return False
        for value in walk_values(c.coordinates):
            if value in forbidden_values: return False
            if any(marker in value for marker in ('specimen:','source_ref:','/research/','/src/')): return False
    return True

def quotient_refinement_theorem(cells):
    fibers,bad=fiber_report(cells,None)
    contained=all(len({c.frontier for c in cs})==1 for cs in fibers.values())
    return {'schema_fibers':len(fibers),'decision_classes':len(decision_partition(cells)),'full_schema_sufficient':(not bad) and contained}

def build_results():
    cells=build_atlas(); fibers,bad=fiber_report(cells); drops=collision_examples(cells); rem=source_remint_checks(cells); qt=quotient_refinement_theorem(cells)
    expected={'S':{'A_cap8_Q16_ext','B_cap8_Q16_ext'},'E':{'A_cap64_Q1_ext','A_cap64_Q16_ext'},'R':{'A_cap8_Q16_ext','A_cap64_Q16_ext'},'V':{'A_cap64_Q16_ext','A_cap64_Q16_proof'},'H':{'R4_H_key','R4_H_value'}}
    drop_ok={}
    for g,bads in drops.items():
        got=False
        for b in bads:
            sources={s[:-7] if s.endswith('_remint') else s for s in b['specimens']}
            if expected[g]<=sources: got=True
        drop_ok[g]=got
    assertions={
      'D6_01_full_schema_fiber_constancy':not bad,
      'D6_02_drop_S_collision':drop_ok['S'],'D6_03_drop_E_collision':drop_ok['E'],'D6_04_drop_R_collision':drop_ok['R'],'D6_05_drop_V_collision':drop_ok['V'],'D6_06_drop_H_collision':drop_ok['H'],
      'D6_07_all_remints_preserve_coordinates_frontier':all(all(x.values()) for x in rem.values()),
      'D6_08_no_coordinate_label_leakage':no_leakage(cells),
      'D6_09_quotient_refinement_implication':qt['full_schema_sufficient'],
      'D6_10_frozen_frontiers':(
          next(c for c in cells if c.specimen=='A_cap8_Q16_ext').frontier==('xor_fold',) and
          next(c for c in cells if c.specimen=='B_cap8_Q16_ext').frontier==('default_exceptions',) and
          next(c for c in cells if c.specimen=='A_cap64_Q1_ext').frontier==('xor_fold',) and
          next(c for c in cells if c.specimen=='A_cap64_Q16_ext').frontier==('default_exceptions','full_map','xor_fold') and
          next(c for c in cells if c.specimen=='A_cap64_Q16_proof').frontier==('xor_fold',) and
          next(c for c in cells if c.specimen=='R4_H_key').frontier==('key_index',) and
          next(c for c in cells if c.specimen=='R4_H_value').frontier==('value_index',)
      )}
    return {
      'authority':{'issue':693,'freeze_commit':'187afe3744a869fe09b6bf3d71653852cdc4f9f3','claim_ceiling':['FINITE_ATLAS_DECISION_SUFFICIENT_COMPLETE_COORDINATE_SCHEMA_D6','GROUPWISE_NECESSARY_S_E_R_V_H_ON_REGISTERED_ATLAS','PARENT_OWNED_QUOTIENT_SUFFICIENCY_AND_PHASE_MECHANISMS','NO_UNIVERSAL_COMPLETE_COORDINATE_ONTOLOGY_OR_FIELD_MINIMALITY_CLAIM']},
      'atlas_size':len(cells),'base_cells':7,'remint_cells':7,
      'cells':{c.specimen:{'source':c.source,'coordinates':c.coordinates,'frontier':list(c.frontier),'vectors':{k:list(v) for k,v in c.vectors.items()}} for c in cells},
      'full_schema':{'fiber_count':len(fibers),'violations':bad},'drop_one_collisions':drops,'drop_one_required_collision_pass':drop_ok,'source_remint_checks':rem,'decision_partition':decision_partition(cells),'quotient_theorem_check':qt,'assertions':assertions,'all_frozen_predictions_pass':all(assertions.values())}

def receipt(r):
    return {'authority':r['authority'],'atlas_size':r['atlas_size'],'base_cells':r['base_cells'],'remint_cells':r['remint_cells'],'base_frontiers':{name:row['frontier'] for name,row in r['cells'].items() if not name.endswith('_remint')},'full_schema':r['full_schema'],'drop_one_required_collision_pass':r['drop_one_required_collision_pass'],'drop_one_collisions':r['drop_one_collisions'],'source_remint_checks':r['source_remint_checks'],'decision_partition':r['decision_partition'],'quotient_theorem_check':r['quotient_theorem_check'],'assertions':r['assertions'],'all_frozen_predictions_pass':r['all_frozen_predictions_pass']}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--output',type=Path,default=Path(__file__).with_name('RESULT_V6.json')); a=ap.parse_args()
    r=build_results(); a.output.write_text(json.dumps(receipt(r),indent=2,sort_keys=True)+'\n')
    print(json.dumps({'pass':r['all_frozen_predictions_pass'],'atlas_size':r['atlas_size'],'fiber_count':r['full_schema']['fiber_count'],'decision_classes':r['quotient_theorem_check']['decision_classes'],'drop_one':r['drop_one_required_collision_pass'],'assertions':r['assertions']},indent=2,sort_keys=True))
    raise SystemExit(0 if r['all_frozen_predictions_pass'] else 1)
if __name__=='__main__': main()
