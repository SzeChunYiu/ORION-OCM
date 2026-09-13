"""Independent enumeration of actual adequate selectors and finite protocols."""
from itertools import product


def selector_optimum(rows):
    """Enumerate every legal output assignment, without cover masks or solver calls."""
    best = None
    count = 0
    for outputs in product(*rows):
        count += 1
        size = len(set(outputs))
        if best is None or size < best[0]:
            best = size, outputs
    if best is None:
        raise ValueError("empty adequate selector class")
    return dict(width=best[0], outputs=best[1], selectors=count)


def joint_selector_optimum(left_rows, right_rows):
    """Output labels remain pairs, independent of the production flattening."""
    rows = tuple(tuple(product(a, b)) for a in left_rows for b in right_rows)
    return selector_optimum(rows)


def direct_protocol_optimum(rows, actions):
    """Exhaust smaller alphabets, then stop at the first adequate table witness."""
    tried = 0
    for size in range(1, actions+1):
        for decoder in product(range(actions), repeat=size):
            for encoder in product(range(size), repeat=len(rows)):
                tried += 1
                if all(decoder[encoder[x]] in row for x, row in enumerate(rows)):
                    return dict(width=size, encoder=encoder, decoder=decoder, tables=tried)
    raise ValueError("infeasible relation")


def verify_pair_protocol(left_rows, right_rows, encoder, decoder):
    """Execute every original input pair; never consult flattened relation or masks."""
    n2 = len(right_rows)
    if len(encoder) != len(left_rows)*n2:
        raise ValueError("missing pair inputs")
    records = []
    for x, row in enumerate(left_rows):
        for y, other in enumerate(right_rows):
            z = encoder[x*n2+y]
            if type(z) is not int or not 0 <= z < len(decoder):
                raise ValueError("bad message index")
            a, b = decoder[z]
            if a not in row or b not in other:
                raise ValueError("inadequate paired output")
            records.append(dict(input=(x, y), message=z, output=(a, b)))
    return records


def product_selector_minimum(left_rows, right_rows):
    """Enumerate all pairs of local selectors and actual joint output images."""
    best = None
    count = 0
    for a, b in product(product(*left_rows), product(*right_rows)):
        count += 1
        image = {(x, y) for x in a for y in b}
        if best is None or len(image) < best:
            best = len(image)
    return dict(width=best, local_selector_pairs=count)
