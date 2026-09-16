from __future__ import annotations
import itertools, json
from collections import Counter
from pathlib import Path

HERE=Path(__file__).resolve().parent
BITS=(0,1)

def stateless_candidates():
    return [("S",outs) for outs in itertools.product(BITS, repeat=2)]

def stateful_candidates():
    out=[]
    for bits in itertools.product(BITS, repeat=8):
        rows=tuple((bits[2*i],bits[2*i+1]) for i in range(4))
        out.append(("M",rows))
    return out

def as_transducer(c):
    typ,data=c
    if typ=="S":
        return 1,{(0,0):(0,data[0]),(0,1):(0,data[1])}
    return 2,{(0,0):data[0],(0,1):data[1],(1,0):data[2],(1,1):data[3]}

def run(c,word,initial=0):
    _,t=as_transducer(c); s=initial; ys=[]
    for x in word:
        s,y=t[(s,x)]; ys.append(y)
    return tuple(ys)

def equivalent_all_words(a,b):
    _,ta=as_transducer(a); _,tb=as_transducer(b)
    stack=[(0,0)]; seen=set()
    while stack:
        sa,sb=stack.pop()
        if (sa,sb) in seen: continue
        seen.add((sa,sb))
        for x in BITS:
            na,ya=ta[(sa,x)]; nb,yb=tb[(sb,x)]
            if ya!=yb: return False
            stack.append((na,nb))
    return True

def words_upto(h):
    out=[()]
    for n in range(1,h+1): out.extend(itertools.product(BITS,repeat=n))
    return out

def finite_signature(c,h=4):
    return tuple(run(c,w) for w in words_upto(h))

def delay1(c):
    for w in words_upto(4):
        prev=0; target=[]
        for x in w: target.append(prev); prev=x
        if run(c,w)!=tuple(target): return False
    return True

def mux_from_gates(c,a,b):
    NOT=lambda x:1-x
    AND=lambda x,y:x & y
    OR=lambda x,y:x | y
    return OR(AND(NOT(c),a),AND(c,b))

def register_step(state):
    pc,r=state
    if pc==0: return (1,(r+1)%3)
    if pc==1:
        if r==0: return (2,r)
        return (1,r-1)
    return (2,r)

def main():
    stateless=stateless_candidates(); stateful=stateful_candidates(); allc=stateless+stateful
    assert len(stateless)==4 and len(stateful)==256 and len(allc)==260

    pair_checks=0; equivalent_pairs=0; h4_disagreements=0
    parent=list(range(len(allc)))
    def find(x):
        while parent[x]!=x:
            parent[x]=parent[parent[x]]; x=parent[x]
        return x
    def union(a,b):
        a,b=find(a),find(b)
        if a!=b: parent[b]=a
    for i in range(len(allc)):
        for j in range(i+1,len(allc)):
            eq=equivalent_all_words(allc[i],allc[j])
            h4=(finite_signature(allc[i])==finite_signature(allc[j]))
            pair_checks += 1
            equivalent_pairs += int(eq)
            h4_disagreements += int(eq!=h4)
            if eq: union(i,j)
    groups={}
    for i in range(len(allc)): groups.setdefault(find(i),[]).append(i)
    size_hist=Counter(len(v) for v in groups.values())

    # Circuit special case and conditional routing from lower Boolean gates.
    mux_checks=0
    for c,a,b in itertools.product(BITS,repeat=3):
        assert mux_from_gates(c,a,b)==(b if c else a); mux_checks+=1

    # Feedback/delay special cases.
    delayed=[c for c in allc if delay1(c)]
    assert len(delayed)==1
    persist=("M",((0,0),(0,0),(1,1),(1,1)))
    assert run(persist,(0,1,0,1),initial=1)==(1,1,1,1)
    toggle=("M",((1,0),(1,0),(0,1),(0,1)))
    assert run(toggle,(0,0,0,0),initial=0)==(0,1,0,1)

    # Bounded register-control organization: step process + recurrent (pc,register) carrier.
    rs=(0,0); trace=[]
    for _ in range(4):
        rs=register_step(rs); trace.append(rs)
    assert trace==[(1,1),(1,0),(2,0),(2,0)]

    # Lifecycle raw resources: no scalar magic-IQ cost.
    resources={
      "STATELESS":{"state_cells":0,"truth_rows":2,"feedback_edges":0,"step_process_evals":1},
      "ONE_BIT_FEEDBACK":{"state_cells":1,"truth_rows":4,"feedback_edges":1,"step_process_evals":1}
    }

    # Five-stage distinction witness.
    expressible=set(range(260))
    realizable_no_delay=set(range(4))
    realizable_delay=set(range(260))
    seed=0 # constant-zero stateless response 00
    reachable={i for i,c in enumerate(allc[:4]) if sum(a!=b for a,b in zip(allc[seed][1],c[1]))<=1}
    identity_idx=stateless.index(("S",(0,1)))
    selected={i for i in reachable if all(run(allc[i],(x,))==(x,) for x in BITS)}
    assert len(reachable)==3 and selected=={identity_idx}
    assert realizable_no_delay < expressible and reachable < realizable_delay and selected < reachable

    result={
      "status":"GREEN",
      "finite_machine_space":{"budget":"state_cells<=1; frozen binary step-process family","stateless":4,"one_bit_feedback":256,"total":260},
      "all_word_equivalence_pair_checks":pair_checks,
      "equivalent_unordered_pairs":equivalent_pairs,
      "operational_quotient_classes":len(groups),
      "quotient_class_size_histogram":{str(k):size_hist[k] for k in sorted(size_hist)},
      "horizon4_vs_all_word_equivalence_disagreements":h4_disagreements,
      "mux_gate_composition_checks":mux_checks,
      "unique_delay1_organization":len(delayed),
      "persistence_witness":"PASS",
      "recurrence_toggle_witness":"PASS",
      "bounded_register_trace":trace,
      "raw_resource_vectors":resources,
      "stage_distinction_witness":{"process_roles":["BOOL_STEP","DELAY_WHEN_SUBSTRATE_ADMITS"],"organization_expressible":len(expressible),"machine_realizable_without_delay":len(realizable_no_delay),"machine_realizable_with_delay":len(realizable_delay),"reachable_under_one_edit_law":len(reachable),"selected_under_identity_requirement":len(selected)},
      "delay_status":"SUBSTRATE_CAPABILITY_REQUIRED_AT_SCOPE",
      "forbidden_promotions":["FEEDBACK_FROM_STATIC_WIRING_WITHOUT_TEMPORAL_SUBSTRATE","UNBOUNDED_MACHINE_SPACE_ENUMERATED","ALL_MACHINE_MODELS_REDUCED","REACHABLE_EQUALS_EXPRESSIBLE","SELECTED_EQUALS_GLOBALLY_POSSIBLE"],
      "claim_ceiling":"AJ4_FINITE_PROCESS_ORGANIZATION_AND_MACHINE_SPACE_AT_REGISTERED_BINARY_SCOPE"
    }
    (HERE/"RESULT_V1.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,sort_keys=True))
if __name__=="__main__": main()
