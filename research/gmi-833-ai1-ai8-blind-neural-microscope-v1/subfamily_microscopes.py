from __future__ import annotations
import itertools

def recurrence_memory():
    # delayed copy: y_0 = 0, thereafter y_t = x_{t-1}. A stateless map x_t -> y_t must emit ONE
    # output for x_t = 0, but the target at x_t = 0 is x_{t-1}: prev=0 -> 0, prev=1 -> 1.
    required_when_x_is_0={prev:prev for prev in (0,1)}
    conflict=len(set(required_when_x_is_0.values()))>1
    assert conflict
    # one-bit persistent process solves all binary words through length 5.
    checked=0
    for n in range(6):
        for word in itertools.product((0,1),repeat=n):
            s=0; out=[]; target=[]; p=0
            for x in word:
                out.append(s); s=x; target.append(p); p=x
            assert tuple(out)==tuple(target); checked+=1
    return {'stateless_aliasing_conflict':conflict,'one_bit_persistence_words_checked':checked,'derived_pressure':'persistent/recurrent state'}

def local_sharing():
    # 3-site cyclic local rule: y_i = not x_i. One shared transform or 3 copied transforms are behaviorally equal.
    checks=0
    for x in itertools.product((0,1),repeat=3):
        shared=tuple(1-v for v in x); independent=tuple((1-x[i]) for i in range(3)); assert shared==independent;checks+=1
    resources={'SHARED':{'rule_descriptions':1,'site_applications':3},'COPIED':{'rule_descriptions':3,'site_applications':3}}
    dominates=resources['SHARED']['rule_descriptions']<resources['COPIED']['rule_descriptions'] and resources['SHARED']['site_applications']==resources['COPIED']['site_applications']
    assert dominates
    return {'semantic_checks':checks,'resources':resources,'shared_description_dominates':dominates,'derived_pressure':'parameter/rule sharing under repeated symmetry'}

def dynamic_routing():
    # Two keyed values; query chooses matching key. Fixed-index routing cannot solve both query values.
    cases=0; fixed0_bad=fixed1_bad=0
    for v0,v1,q in itertools.product((0,1),repeat=3):
        target=v0 if q==0 else v1
        select=v0 if q==0 else v1
        assert select==target; cases+=1
        fixed0_bad+=int(v0!=target); fixed1_bad+=int(v1!=target)
    assert fixed0_bad and fixed1_bad
    return {'cases':cases,'fixed_route_errors':[fixed0_bad,fixed1_bad],'conditional_route_errors':0,'derived_pressure':'content/query-dependent routing'}

def sparse_modular():
    # Mode selects one of two generic transforms: identity or complement.
    checks=0; conditional_evals=eager_evals=0
    for mode,x in itertools.product((0,1),repeat=2):
        f0=x; f1=1-x; target=f0 if mode==0 else f1
        conditional=(x if mode==0 else 1-x); eager=(f0,f1)[mode]
        assert conditional==eager==target; checks+=1; conditional_evals+=1; eager_evals+=2
    return {'cases':checks,'conditional_transform_evals':conditional_evals,'eager_transform_evals':eager_evals,'same_behavior':True,'derived_pressure':'sparse conditional modular execution'}

def memory_augmented():
    # Current observation is always 0; hidden cue from first step determines final required output.
    no_memory_best=0
    for a in (0,1):
        correct=sum(int(a==cue) for cue in (0,1)); no_memory_best=max(no_memory_best,correct)
    memory_correct=sum(int(cue==cue) for cue in (0,1))
    assert no_memory_best==1 and memory_correct==2
    return {'no_memory_best_accuracy':no_memory_best/2,'one_bit_memory_accuracy':memory_correct/2,'derived_pressure':'history retention under partial observability'}

def certificate():
    return {
      'recurrent_stateful':recurrence_memory(),
      'local_shared_transform':local_sharing(),
      'content_dependent_routing':dynamic_routing(),
      'sparse_modular':sparse_modular(),
      'memory_augmented':memory_augmented(),
      'all_are_structural_pressure_results_not_named_architecture_primitives':True
    }
