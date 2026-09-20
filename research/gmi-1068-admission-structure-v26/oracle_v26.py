"""Independent V25-derived table enumeration, endpoint assignments and tree recursion."""
from functools import lru_cache
from itertools import product


def units(rows):
    return tuple(e for e in range(len(rows)) if rows[e][e]==e and all(
        (rows[e][x] is None or rows[e][x]==x) and (rows[x][e] is None or rows[x][e]==x)
        for x in range(len(rows))))


def lawful(rows):
    n=len(rows);es=units(rows)
    if any(not any(rows[e][x]==x for e in es) or not any(rows[x][e]==x for e in es)
           for x in range(n)):return False
    for x,y,z in product(range(n),repeat=3):
        xy,yz=rows[x][y],rows[y][z]
        left=None if xy is None else rows[xy][z];right=None if yz is None else rows[x][yz]
        if left!=right or (xy is not None and yz is not None and left is None):return False
    return True


def endpoint_assignments(rows):
    n=len(rows);ids=units(rows);out=[]
    for flat in product(range(len(ids)),repeat=2*n):
        src,dst=flat[:n],flat[n:]
        if any(src[e]!=i or dst[e]!=i for i,e in enumerate(ids)):continue
        if any(rows[ids[src[x]]][x]!=x or rows[x][ids[dst[x]]]!=x for x in range(n)):continue
        if any((rows[x][y] is not None)!=(dst[x]==src[y]) or
               (rows[x][y] is not None and (src[rows[x][y]]!=src[x] or dst[rows[x][y]]!=dst[y]))
               for x,y in product(range(n),repeat=2)):continue
        if any(rows[rows[x][y]][z]!=rows[x][rows[y][z]] for x,y,z in product(range(n),repeat=3)
               if dst[x]==src[y] and dst[y]==src[z]):continue
        out.append((rows,src,dst,ids))
    return tuple(out)


@lru_cache(None)
def models(n):
    out=[]
    for flat in product((None,)+tuple(range(n)),repeat=n*n):
        rows=tuple(tuple(flat[i*n:i*n+n]) for i in range(n))
        if lawful(rows):
            possibilities=endpoint_assignments(rows)
            if len(possibilities)!=1:raise ValueError('independent endpoint uniqueness failed')
            out.append(possibilities[0])
    return tuple(out)


def functor_failure(c,d,objects,arrows):
    rows,src,dst,ids=c;other,ds,dt,di=d
    if any((ds[arrows[f]],dt[arrows[f]])!=(objects[src[f]],objects[dst[f]])
           for f in range(len(rows))):return 'endpoint'
    if any(arrows[e]!=di[objects[o]] for o,e in enumerate(ids)):return 'identity'
    if any(other[arrows[f]][arrows[g]]!=arrows[rows[f][g]]
           for f,g in product(range(len(rows)),repeat=2) if rows[f][g] is not None):return 'composition'
    return 'accepted'


@lru_cache(None)
def shapes(n):
    if n==1:return (None,)
    return tuple((l,r) for k in range(1,n) for l in shapes(k) for r in shapes(n-k))


def fill(shape,labels):
    return next(labels) if shape is None else ('seq',fill(shape[0],labels),fill(shape[1],labels))


@lru_cache(None)
def trees(n,k):
    alphabet=tuple(('arrow',i) for i in range(n))+tuple(('empty',i) for i in range(k))
    return tuple(fill(s,iter(labels)) for length in range(1,4) for s in shapes(length)
                 for labels in product(alphabet,repeat=length))


def evaluate(c,tree):
    rows,src,dst,ids=c
    if tree[0]!='seq':
        f=tree[1] if tree[0]=='arrow' else ids[tree[1]]
        return src[f],dst[f],f
    left,right=evaluate(c,tree[1]),evaluate(c,tree[2])
    if left is None or right is None or left[1]!=right[0]:return None
    return left[0],right[1],rows[left[2]][right[2]]


def map_tree(tree,objects,arrows):
    if tree[0]=='seq':return ('seq',map_tree(tree[1],objects,arrows),map_tree(tree[2],objects,arrows))
    return tree[0],(arrows if tree[0]=='arrow' else objects)[tree[1]]


def map_response(response,objects,arrows):
    return None if response is None else (objects[response[0]],objects[response[1]],arrows[response[2]])


def path(c,request):
    rows,src,dst,ids=c;start,word=request;current=start;result=ids[start]
    for f in word:
        if src[f]!=current:return None
        result=rows[result][f];current=dst[f]
    return start,current,result


def admission(c,allowed):
    rows,_,_,ids=c
    return (all(e in allowed for e in ids),all(rows[f][g] in allowed for f in allowed for g in allowed
                                            if rows[f][g] is not None))


def restriction(c,allowed):
    rows,src,dst,ids=c;allowed=tuple(sorted(allowed));where={f:i for i,f in enumerate(allowed)}
    return (tuple(tuple(None if rows[f][g] is None else where[rows[f][g]] for g in allowed) for f in allowed),
            tuple(src[f] for f in allowed),tuple(dst[f] for f in allowed),tuple(where[e] for e in ids))


def exact(a,b):
    if type(a) is not type(b):return False
    if type(a) is tuple:return len(a)==len(b) and all(exact(x,y) for x,y in zip(a,b))
    return a==b


def certify(actual,expected):
    if not exact(actual,expected):raise ValueError('independent observation mismatch')
    return True
