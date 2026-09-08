"""Pure cached posting contents; each adapter retains its own current-state guard."""
from unary_contract import InputRefused
import unary_method_plain as D

def contents(store,token,work):
    saved=getattr(store,"_posting_cache",None)
    if saved is not None and saved[0]==token:
        D.bump(work,"posting_cache_hits")
        return saved[1],list(saved[2])
    D.bump(work,"posting_cache_misses");postings={"every":[],"no":[]};refusals=[]
    for mid in store.method_ids:
        D.bump(work,"cold_entries_visited");item=store.read(mid)
        if not item["eligible"]:
            refusals.append({"method_id":mid,"correctness":item["correctness"],"selection":item["selection"]})
        else:
            # Both universal surface kinds have exact clause views.
            for kind in ("every","no"):
                postings[kind].append(mid);D.bump(work,"postings_built")
    postings={k:tuple(v) for k,v in postings.items()}
    store._posting_cache=(token,postings,tuple(refusals))
    return postings,refusals

def select(index,kind):
    index.validate()
    if type(kind) is not str or kind not in index.postings:raise InputRefused("INDEX_KIND")
    D.bump(index.work,"index_probes");ids=index.postings[kind]
    D.bump(index.work,"postings_examined",len(ids));return list(ids)
