"""Independent partial-operation and typed-endpoint criteria on finite carriers."""
from itertools import product


def tables(n):
    for flat in product((None,)+tuple(range(n)),repeat=n*n):
        yield tuple(tuple(flat[i*n+j] for j in range(n)) for i in range(n))


def units(rows):
    return tuple(e for e in range(len(rows)) if rows[e][e]==e
                 and all(rows[e][x] in (None,x) and rows[x][e] in (None,x)
                         for x in range(len(rows))))


def laws(rows):
    n=len(rows)
    neutral=units(rows)
    associative=coherent=weak=True
    for x,y,z in product(range(n),repeat=3):
        xy,yz=rows[x][y],rows[y][z]
        left=None if xy is None else rows[xy][z]
        right=None if yz is None else rows[x][yz]
        associative = associative and left==right
        coherent = coherent and not(xy is not None and yz is not None and left is None)
        weak = weak and not(left is not None and right is not None and left!=right)
    local=all(any(rows[e][x]==x for e in neutral) and any(rows[x][e]==x for e in neutral)
              for x in range(n))
    return associative,local,coherent,weak


def typed_reconstruction(rows):
    n=len(rows)
    identities=units(rows)
    source=[]
    target=[]
    for arrow in range(n):
        left=[i for i,e in enumerate(identities) if rows[e][arrow]==arrow]
        right=[i for i,e in enumerate(identities) if rows[arrow][e]==arrow]
        if len(left)!=1 or len(right)!=1:
            return None
        source.append(left[0]);target.append(right[0])
    for f,g in product(range(n),repeat=2):
        h=rows[f][g]
        if (h is not None)!=(target[f]==source[g]):
            return None
        if h is not None and (source[h]!=source[f] or target[h]!=target[g]):
            return None
    for f,g,h in product(range(n),repeat=3):
        if target[f]==source[g] and target[g]==source[h]:
            if rows[rows[f][g]][h]!=rows[f][rows[g][h]]:
                return None
    return {'identities':identities,'source':tuple(source),'target':tuple(target)}


def word(rows,arrows):
    state=arrows[0]
    for arrow in arrows[1:]:
        if state is None:
            return None
        state=rows[state][arrow]
    return state


def response_vector(rows,max_length=4):
    n=len(rows)
    anchors=tuple(e if e in units(rows) else None for e in range(n))
    words=tuple(word(rows,w) for length in range(1,max_length+1)
                for w in product(range(n),repeat=length))
    return anchors+words


def relabel(rows,permutation):
    inverse=tuple(permutation.index(i) for i in range(len(rows)))
    return tuple(tuple(None if rows[inverse[i]][inverse[j]] is None
                       else permutation[rows[inverse[i]][inverse[j]]]
                       for j in range(len(rows))) for i in range(len(rows)))


def recoverable(codes,observations):
    """Enumerate decoders on the two-code space rather than call a fiber checker."""
    values=tuple(dict.fromkeys(observations))
    return any(all(decoder[codes[i]]==observations[i] for i in range(len(codes)))
               for decoder in product(values,repeat=2))
