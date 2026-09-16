from __future__ import annotations
import itertools, json
from pathlib import Path

HERE=Path(__file__).resolve().parent
BITS=(0,1)
WORDS=[()]
for n in range(1,4): WORDS.extend(itertools.product(BITS,repeat=n))


def required_trace(word):
    prev=0; out=[]
    for x in word:
        out.append(prev); prev=x
    return tuple(out)


def stateless_candidates():
    return [("Z",outs) for outs in itertools.product(BITS,repeat=2)]


def one_cell_candidates():
    out=[]
    for bits in itertools.product(BITS,repeat=8):
        rows=tuple((bits[2*i],bits[2*i+1]) for i in range(4))
        out.append(("O",rows))
    return out


def run(candidate,word):
    kind,data=candidate; s=0; ys=[]
    if kind=="Z":
        for x in word: ys.append(data[x])
    else:
        for x in word:
            s,y=data[2*s+x]; ys.append(y)
    return tuple(ys)


def exact(candidate):
    return all(run(candidate,w)==required_trace(w) for w in WORDS)


def full_table_enumeration():
    zero=stateless_candidates(); one=one_cell_candidates(); allc=zero+one
    solutions=[c for c in allc if exact(c)]
    return {
      "candidate_count":len(allc),
      "zero_cell_candidates":len(zero),
      "one_cell_candidates":len(one),
      "zero_cell_exact":sum(exact(c) for c in zero),
      "one_cell_exact":sum(exact(c) for c in one),
      "solutions":solutions,
      "transition_checks":len(allc)*sum(len(w) for w in WORDS)
    }


def partial_ok(rows):
    for w in WORDS:
        s=0; target=required_trace(w)
        for step,x in enumerate(w):
            idx=2*s+x
            if idx not in rows: break
            s,y=rows[idx]
            if y!=target[step]: return False
    return True


def constraint_filter_search():
    visited=0; pruned=0; leaves=[]
    def rec(i,rows):
        nonlocal visited,pruned
        visited+=1
        if not partial_ok(rows):
            pruned+=1; return
        if i==4:
            leaves.append(tuple(rows[j] for j in range(4))); return
        for ns in BITS:
            for y in BITS:
                rows[i]=(ns,y); rec(i+1,rows); rows.pop(i)
    rec(0,{})
    zero=[c for c in stateless_candidates() if exact(c)]
    return {"visited_partial_nodes":visited,"pruned_partial_nodes":pruned,"one_cell_leaves":leaves,"zero_cell_solutions":zero}


def pack_rows(rows):
    bits=[]
    for ns,y in rows: bits.extend((ns,y))
    return sum(bit<<i for i,bit in enumerate(bits))


def unpack_rows(value):
    bits=tuple((value>>i)&1 for i in range(8))
    return tuple((bits[2*i],bits[2*i+1]) for i in range(4))


def main():
    a=full_table_enumeration(); b=constraint_filter_search()
    assert a["candidate_count"]==260
    assert a["zero_cell_exact"]==0 and a["one_cell_exact"]==1 and len(a["solutions"])==1
    rows=a["solutions"][0][1]
    assert b["zero_cell_solutions"]==[] and b["one_cell_leaves"]==[rows]
    packed=pack_rows(rows); assert unpack_rows(packed)==rows
    result={
      "schema":"AJ9C_BLIND_TEMPORAL_OUTCOME_V1",
      "status":"SEARCH_COMPLETE",
      "word_count":len(WORDS),
      "tested_steps_per_candidate":sum(len(w) for w in WORDS),
      "search_1":{"id":"FULL_TABLE_ENUMERATION","presentation":"ROW_TABLE","candidate_count":a["candidate_count"],"zero_cell_exact":a["zero_cell_exact"],"one_cell_exact":a["one_cell_exact"],"solution_rows":rows,"transition_checks":a["transition_checks"]},
      "search_2":{"id":"CONSTRAINT_FILTER_SEARCH","presentation":"PACKED_BITSTRING","visited_partial_nodes":b["visited_partial_nodes"],"pruned_partial_nodes":b["pruned_partial_nodes"],"packed_solution":packed,"solution_rows":rows},
      "raw_resource_vector":{"persistent_cells":1,"table_rows":4,"tested_transitions":sum(len(w) for w in WORDS)},
      "registry_data_used":False
    }
    (HERE/"BLIND_OUTCOME_V1.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,sort_keys=True))

if __name__=="__main__": main()
