"""Independent explicit endpoint-labelled chain/resource arrows and cumulative traversal."""
from itertools import product


def category(objects,arrows):
    src=tuple(objects.index(a[0]) for a in arrows);dst=tuple(objects.index(a[1]) for a in arrows)
    pairs=tuple((a[0],a[1]) for a in arrows)
    rows=tuple(tuple(None if a[1]!=b[0] else pairs.index((a[0],b[1])) for b in arrows) for a in arrows)
    ids=tuple(pairs.index((o,o)) for o in objects)
    return rows,src,dst,ids


def chain():
    arrows=tuple((i,j) for i in range(3) for j in range(i,3))
    return category(tuple(range(3)),arrows),tuple(j-i for i,j in arrows)


def resource(c,costs,maximum):
    rows,src,dst,ids=c;objects=tuple(product(range(len(ids)),range(maximum+1)))
    labels=tuple((f,r) for f in range(len(rows)) for r in range(maximum+1) if costs[f]<=r)
    arrows=tuple(((src[f],r),(dst[f],r-costs[f])) for f,r in labels)
    rs=tuple(objects.index(a) for a,b in arrows);rt=tuple(objects.index(b) for a,b in arrows)
    rrows=tuple(tuple(None if arrows[i][1]!=arrows[j][0] else labels.index((rows[f][g],r))
                      for j,(g,s) in enumerate(labels)) for i,(f,r) in enumerate(labels))
    ri=tuple(labels.index((ids[o],r)) for o,r in objects)
    return (rrows,rs,rt,ri),objects,labels


def lift(c,costs,maximum,request,balance):
    _,src,dst,ids=c;start,word=request;current=start;remaining=balance;out=[]
    labels=tuple((f,r) for f in range(len(src)) for r in range(maximum+1) if costs[f]<=r)
    for f in word:
        if src[f]!=current or remaining<costs[f]:return None
        out.append(labels.index((f,remaining)));remaining-=costs[f];current=dst[f]
    return ((start*(maximum+1)+balance,tuple(out)),remaining)
