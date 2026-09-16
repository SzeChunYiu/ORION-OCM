from __future__ import annotations
import json
from collections import deque
from pathlib import Path

HERE=Path(__file__).resolve().parent
START=("N",("N","E","A"),("N","B","E"))
GOAL=("N","A","B")


def local_options(t):
    out=[]
    if not (isinstance(t,tuple) and len(t)==3 and t[0]=="N"):
        return out
    _,left,right=t
    if left=="E": out.append((right,"DROP_LEFT_E"))
    if right=="E": out.append((left,"DROP_RIGHT_E"))
    for nl,tag in local_options(left): out.append((("N",nl,right),"L/"+tag))
    for nr,tag in local_options(right): out.append((("N",left,nr),"R/"+tag))
    return out


def fifo_frontier_search():
    q=deque([(START,[START],[])])
    seen={START}; expanded=0; generated=0; peak=1
    branching_at_start=len(local_options(START))
    while q:
        term,path,tags=q.popleft()
        if term==GOAL:
            return {"path":path,"tags":tags,"expanded_states":expanded,"generated_edges":generated,"peak_frontier":peak,"branching_at_start":branching_at_start}
        expanded+=1
        for nxt,tag in local_options(term):
            generated+=1
            if nxt in seen: continue
            seen.add(nxt); q.append((nxt,path+[nxt],tags+[tag])); peak=max(peak,len(q))
    return None


def to_prefix(t):
    if isinstance(t,tuple):
        return ("N",)+to_prefix(t[1])+to_prefix(t[2])
    return (t,)


def parse_prefix(tokens,i=0):
    tok=tokens[i]
    if tok!="N": return tok,i+1
    left,j=parse_prefix(tokens,i+1); right,k=parse_prefix(tokens,j)
    return ("N",left,right),k


def prefix_options(tokens):
    t,end=parse_prefix(tuple(tokens)); assert end==len(tokens)
    return [(to_prefix(nxt),tag) for nxt,tag in reversed(local_options(t))]


def depth_limited_iteration(max_depth=5):
    start=to_prefix(START); goal=to_prefix(GOAL)
    total_visited=0; total_generated=0
    for limit in range(max_depth+1):
        def dfs(state,depth,path,tags,onpath):
            nonlocal total_visited,total_generated
            total_visited+=1
            if state==goal: return path,tags
            if depth==limit: return None
            for nxt,tag in prefix_options(state):
                total_generated+=1
                if nxt in onpath: continue
                r=dfs(nxt,depth+1,path+[nxt],tags+[tag],onpath|{nxt})
                if r is not None: return r
            return None
        found=dfs(start,0,[start],[],{start})
        if found is not None:
            path,tags=found
            return {"depth_limit":limit,"path":path,"tags":tags,"visited_nodes":total_visited,"generated_edges":total_generated,"branching_at_start":len(prefix_options(start))}
    return None


def jsonable(x):
    if isinstance(x,tuple): return [jsonable(v) for v in x]
    if isinstance(x,list): return [jsonable(v) for v in x]
    if isinstance(x,dict): return {k:jsonable(v) for k,v in x.items()}
    return x


def main():
    a=fifo_frontier_search(); b=depth_limited_iteration()
    assert a is not None and b is not None
    assert len(a["tags"])==2 and b["depth_limit"]==2 and len(b["tags"])==2
    assert a["branching_at_start"]==2 and b["branching_at_start"]==2
    assert a["path"][0]==START and a["path"][-1]==GOAL
    assert parse_prefix(b["path"][-1])[0]==GOAL
    result={"schema":"AJ9F_BLIND_TERM_OUTCOME_V1","status":"SEARCH_COMPLETE",
      "search_1":{"id":"FIFO_FRONTIER_SEARCH","presentation":"NESTED_TUPLE",**a},
      "search_2":{"id":"DEPTH_LIMITED_ITERATION","presentation":"PREFIX_TOKEN_SEQUENCE",**b},
      "raw_resource_vector":{"solution_steps":2,"initial_legal_successors":2,"nested_path_states":len(a["path"]),"prefix_path_states":len(b["path"])},
      "registry_data_used":False}
    result=jsonable(result)
    (HERE/"BLIND_OUTCOME_V1.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,sort_keys=True))
if __name__=="__main__": main()
