"""Independent finite tables, endpoint assignments, bracket recursion and decoders."""
from functools import lru_cache
from itertools import product


def tables(n):
    for flat in product((None,)+tuple(range(n)),repeat=n*n):
        yield tuple(tuple(flat[i*n:i*n+n]) for i in range(n))


def units(rows):
    n=len(rows)
    return tuple(e for e in range(n) if rows[e][e]==e and all(
        (rows[e][x] is None or rows[e][x]==x) and (rows[x][e] is None or rows[x][e]==x) for x in range(n)))


def laws(rows):
    n=len(rows);es=units(rows);assoc=coherent=True
    for x,y,z in product(range(n),repeat=3):
        xy,yz=rows[x][y],rows[y][z]
        left=None if xy is None else rows[xy][z];right=None if yz is None else rows[x][yz]
        assoc &= left==right
        coherent &= not(xy is not None and yz is not None and left is None)
    local=all(any(rows[e][x]==x for e in es) and any(rows[x][e]==x for e in es) for x in range(n))
    return assoc,local,coherent


@lru_cache(None)
def catalog(n):return tuple(rows for rows in tables(n) if all(laws(rows)))


def endpoints(rows):
    """Enumerate assignments, not production's neutral lookup reconstruction."""
    n=len(rows);es=units(rows);k=len(es);solutions=[]
    for flat in product(range(k),repeat=2*n):
        source,target=flat[:n],flat[n:]
        if any(source[e]!=i or target[e]!=i for i,e in enumerate(es)):continue
        if any(rows[es[source[x]]][x]!=x or rows[x][es[target[x]]]!=x for x in range(n)):continue
        if any((rows[x][y] is not None)!=(target[x]==source[y]) or
               (rows[x][y] is not None and (source[rows[x][y]]!=source[x] or target[rows[x][y]]!=target[y]))
               for x,y in product(range(n),repeat=2)):continue
        if any(rows[rows[x][y]][z]!=rows[x][rows[y][z]] for x,y,z in product(range(n),repeat=3)
               if target[x]==source[y] and target[y]==source[z]):continue
        solutions.append((source,target,es))
    return tuple(solutions)


@lru_cache(None)
def shapes(leaves):
    if leaves==1:return (None,)
    return tuple((a,b) for split in range(1,leaves) for a in shapes(split) for b in shapes(leaves-split))


def fill(shape,labels):
    return next(labels) if shape is None else ('seq',fill(shape[0],labels),fill(shape[1],labels))


@lru_cache(None)
def trees(arrows,empties,maximum):
    alphabet=tuple(('arrow',i) for i in range(arrows))+tuple(('empty',i) for i in range(empties))
    return tuple(fill(shape,iter(labels)) for length in range(1,maximum+1)
                 for shape in shapes(length) for labels in product(alphabet,repeat=length))


def encoding(tree,identity):
    if tree[0]=='seq':return encoding(tree[1],identity)+encoding(tree[2],identity)
    return (tree[1] if tree[0]=='arrow' else identity[tree[1]],)


def typed(rows,source,target,identities,tree):
    if tree[0]!='seq':
        arrow=tree[1] if tree[0]=='arrow' else identities[tree[1]]
        return source[arrow],target[arrow],arrow
    left=typed(rows,source,target,identities,tree[1]);right=typed(rows,source,target,identities,tree[2])
    if left is None or right is None or left[1]!=right[0]:return None
    return left[0],right[1],rows[left[2]][right[2]]


def raw(rows,present,neutral,tree,identity=None):
    if tree[0]=='arrow':return tree[1] if tree[1] in present else None
    if tree[0]=='empty':
        value=tree[1] if identity is None else identity[tree[1]]
        return value if value in neutral else None
    left=raw(rows,present,neutral,tree[1],identity);right=raw(rows,present,neutral,tree[2],identity)
    return None if left is None or right is None else rows[left][right]


def guard(tree,present,neutral):
    if tree[0]=='seq':return guard(tree[1],present,neutral) and guard(tree[2],present,neutral)
    return tree[1] in (present if tree[0]=='arrow' else neutral)


def pad(n,labels,rows):
    lookup={a:i for i,a in enumerate(labels)}
    return tuple(tuple(None if x not in lookup or y not in lookup or rows[lookup[x]][lookup[y]] is None
                       else labels[rows[lookup[x]][lookup[y]]] for y in range(n)) for x in range(n))


def presented(n):
    for mask in range(1<<n):
        labels=tuple(i for i in range(n) if mask>>i&1)
        for rows in catalog(len(labels)):yield labels,rows


def basis(n,k=None):
    empties=n if k is None else k
    return tuple(('arrow',i) for i in range(n))+tuple(('empty',i) for i in range(empties))+tuple(
        ('seq',('arrow',i),('arrow',j)) for i,j in product(range(n),repeat=2))


def decodable(codes,observations):
    image=tuple(sorted(set(codes)));values=tuple(dict.fromkeys(observations))
    for outputs in product(values,repeat=len(image)):
        decoder=dict(zip(image,outputs))
        if all(decoder[code]==value for code,value in zip(codes,observations)):return True
    return False


def exact(a,b):
    if type(a) is not type(b):return False
    if type(a) is tuple:return len(a)==len(b) and all(exact(x,y) for x,y in zip(a,b))
    return a==b


def certify(actual,expected):
    if not exact(actual,expected):raise ValueError('independent observation certificate mismatch')
    return True


def rename(tree,objects,arrows):
    if tree[0]=='seq':return ('seq',rename(tree[1],objects,arrows),rename(tree[2],objects,arrows))
    return tree[0],(arrows if tree[0]=='arrow' else objects)[tree[1]]


def relabel(rows,permutation):
    inverse=tuple(permutation.index(i) for i in range(len(rows)))
    return tuple(tuple(None if rows[inverse[x]][inverse[y]] is None else permutation[rows[inverse[x]][inverse[y]]]
                       for y in range(len(rows))) for x in range(len(rows)))
