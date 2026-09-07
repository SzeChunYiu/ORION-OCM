"""Registered SHA stream; engineering calls only authored choice/construction seams."""
import hashlib,json
from unary_contract import InputRefused,SCHEMA
from unary_rule_contract import count,encoded

MASTER="ocm-unary-causal-v1"
EPISODES=4
SPLITS=("train","development","final")
SIZES=(32,16,32)
MAX_ATTEMPTS=65536
KINDS=("every","no","some","not_every")
NAMES=("P0","P1","P2")

def _index(x,n,reason):
    if type(x) is not int or not 0<=x<n:raise InputRefused(reason)

def coordinates(episode,split,attempt,slot):
    _index(episode,EPISODES,"EPISODE")
    if type(split) is not str or split not in SPLITS:raise InputRefused("SPLIT")
    _index(attempt,MAX_ATTEMPTS,"DRAW_INDEX");_index(slot,SIZES[SPLITS.index(split)],"SLOT")

def expressions(split):
    if type(split) is not str or split not in SPLITS:raise InputRefused("SPLIT")
    atom=lambda i:["pred",NAMES[i]]
    if split=="train":return [atom(i) for i in range(3)]
    return ([atom(i) for i in range(3)]+[["not",atom(i)] for i in range(3)]+
            [[op,atom(i),atom(j)] for op in ("and","or") for i in range(3) for j in range(3)])

def choice(master,episode,split,attempt,tag,pool,*,work):
    if type(master) is not str or not master or type(tag) is not str or not tag:raise InputRefused("CHOICE_FIELD")
    coordinates(episode,split,attempt,0)
    if type(pool) is not list or not pool:raise InputRefused("CHOICE_POOL")
    value=[master,episode,split,attempt,tag];raw=encoded(value,work)
    count(work,"choice_hash_calls");count(work,"bytes_hashed",len(raw))
    hashed=hashlib.sha256(raw).digest()
    return {"input":value,"canonical_input":raw.decode(),"sha256":hashed.hex(),
            "index":int.from_bytes(hashed,"big")%len(pool)}

def build_candidate(episode,split,attempt,slot,choose,*,work):
    """Trusted field-choice callback is an authored seam, never task-supplied code."""
    coordinates(episode,split,attempt,slot);pool=expressions(split);fields=[]
    def take(tag,values):
        result=choose(tag,values)
        if type(result) is not dict:_index(None,len(values),"CHOICE_INDEX")
        index=result.get("index");_index(index,len(values),"CHOICE_INDEX")
        value=json.loads(encoded(values[index],work));count(work,"candidate_fields")
        fields.append({"field":tag,"index":index,"value":value,"choice":json.loads(encoded(result,work))})
        return value
    n=take("premise_count",[2,3] if split=="train" else [4,5,6])
    premises=[{"kind":take(f"premise/{i}/kind",list(KINDS)),
               "left":take(f"premise/{i}/left",pool),"right":take(f"premise/{i}/right",pool)} for i in range(n)]
    task={"schema":SCHEMA,"predicates":list(NAMES),"premises":premises,
          "query":{"kind":KINDS[slot%4],"left":take("query/left",pool),"right":take("query/right",pool)}}
    return {"episode":episode,"split":split,"attempt":attempt,"slot":slot,"fields":fields,
            "task":task,"task_bytes":encoded(task,work).decode()}

def draw(episode,split,attempt,slot,*,work):
    """Fixed registered production choice. Do not invoke during engineering."""
    return build_candidate(episode,split,attempt,slot,
        lambda tag,pool:choice(MASTER,episode,split,attempt,tag,pool,work=work),work=work)
