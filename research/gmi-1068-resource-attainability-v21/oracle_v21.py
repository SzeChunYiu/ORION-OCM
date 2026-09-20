"""Independent literal execution and finite witness images; no production imports."""
from functools import lru_cache
from itertools import product


def words(actions,length):
    return tuple(w for size in range(length+1) for w in product(range(actions),repeat=size))


def execute(observations,rows,start,word,budget=None):
    state=start;spent=0;prefixes=[0];trace=[('OBS',observations[start])]
    for action in word:
        edge=rows[state][action]
        if edge is None:
            trace.append(('ILLEGAL',));return tuple(trace),None,tuple(prefixes)
        output,cost,destination=edge
        spent+=cost;prefixes.append(spent)
        if budget is not None and spent>budget:
            trace.append(('ILLEGAL',));return tuple(trace),None,tuple(prefixes)
        trace.extend((('EDGE',output,cost),('OBS',observations[destination])))
        state=destination
    return tuple(trace),(state,spent),tuple(prefixes)


def machines(actions,outputs,costs):
    for n in (1,2):
        possibilities=(None,)+tuple(product(range(outputs),range(costs),range(n)))
        for observations in product((None,0,1),repeat=n):
            for flat in product(possibilities,repeat=n*actions):
                rows=tuple(tuple(flat[s*actions+a] for a in range(actions)) for s in range(n))
                yield observations,rows


@lru_cache(None)
def preorders(n):
    result=[]
    for flat in product((False,True),repeat=n*n):
        r=tuple(tuple(flat[i*n+j] for j in range(n)) for i in range(n))
        if all(r[i][i] for i in range(n)) and all(not(r[i][j] and r[j][k]) or r[i][k]
                for i,j,k in product(range(n),repeat=3)):result.append(r)
    return tuple(result)


def subsets(values):
    return tuple(tuple(x for i,x in enumerate(values) if mask & (1<<i)) for mask in range(1<<len(values)))


def joint(observations,rows,histories,p,values,selected):
    result=[]
    for h in selected:
        _,execution,_=execute(observations,rows,*histories[h])
        if p[h] and values[h] is not None and execution is not None:
            result.append((h,execution[1],values[h]))
    return tuple(result)


def image(fibers,budget=None):
    return tuple(sorted({value for _,cost,value in fibers if budget is None or cost<=budget}))


def observe(admitted,values,h):
    return ('ILLEGAL',None) if not admitted[h] else ('UNDEFINED',None) if values[h] is None else ('VALUE',values[h])


def resource(kind,x,y):
    if kind in ('nat','signed'):return x+y
    if kind=='peak':return max(x,y)
    if kind=='vector':return tuple(a+b for a,b in zip(x,y))
    if kind=='mixed':return (x[0]+y[0],max(x[1],y[1]))
    raise ValueError(kind)


def below(x,y):
    return all(a<=b for a,b in zip(x,y)) if type(x) is tuple else x<=y


def prefixes(kind,word,initial):
    result=[initial]
    for cost in word:result.append(resource(kind,result[-1],cost))
    return tuple(result)


def matrix_product(a,b):
    return tuple(tuple(sum(a[i][k]*b[k][j] for k in range(3)) for j in range(3)) for i in range(3))
