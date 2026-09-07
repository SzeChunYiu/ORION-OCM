"""Validate the entire historical metadata population; assignment uses identities only."""
import re
from corpus_contract import key_identity
from env_inputs import canonical, digest, relative_name, valid_hash

PREFIX = b'ocm.f1.semantic-coverage.v1\x00'


def require(condition, reason):
    if not condition: raise ValueError(reason)


def fields(value, names, reason):
    require(type(value) is dict and set(value) == set(names.split()), reason)


def validate_population(source, graph, solutions, expected_count):
    fields(source, 'commit tree identity files verified_tree_objects', 'source schema')
    require(source['identity'] == 'PINNED_GIT_BLOBS', 'source authority')
    require(all(type(source[k]) is str and re.fullmatch('[0-9a-f]{40}', source[k])
                for k in ('commit', 'tree')), 'source commit/tree')
    require(type(source['verified_tree_objects']) is dict, 'tree metadata map')
    for oid, binding in source['verified_tree_objects'].items():
        require(type(oid) is str and re.fullmatch('[0-9a-f]{40}', oid), 'tree oid')
        fields(binding, 'bytes sha256', 'tree binding')
        require(type(binding['bytes']) is int and binding['bytes'] >= 0, 'tree size')
        valid_hash(binding['sha256'])
    require(type(expected_count) is int and expected_count > 0, 'population count')
    require(type(source['files']) is dict and type(solutions) is dict, 'metadata maps')
    files = source['files']
    for path, row in files.items():
        relative_name(path)
        if path.startswith('Theorems/') and path.endswith('.lean'):
            require(re.fullmatch(r"Theorems/Thm_([A-Za-z0-9_']+)\.lean", path), 'wrapper path')
        if path.startswith('P2M/Sol/') and path.endswith('.lean'):
            require(re.fullmatch(r"P2M/Sol/S_([A-Za-z0-9_']+)\.lean", path), 'solution path')
        fields(row, 'bytes mode oid path sha256 state', 'file schema')
        require(row['path'] == path and row['state'] == 'ACCEPTED' and row['mode'] == '100644', 'file identity')
        require(type(row['bytes']) is int and row['bytes'] >= 0, 'file size')
        require(type(row['oid']) is str and re.fullmatch('[0-9a-f]{40}', row['oid']), 'blob oid')
        valid_hash(row['sha256'])
    fields(graph, 'edge_count graph_kind graph_sha256 node_count nodes semantic_dependencies_verified topological_order', 'graph schema')
    require(graph['graph_kind'] == 'LEXICAL_THEOREM_IMPORT_GRAPH' and
            graph['semantic_dependencies_verified'] is False, 'graph scope')
    nodes = graph['nodes']; require(type(nodes) is dict, 'node map'); node_keys = set(nodes)
    require(type(graph['node_count']) is int and graph['node_count'] == len(nodes) == expected_count, 'node count')
    require(node_keys == set(solutions), 'solution keyset')
    wrappers = {p[len('Theorems/Thm_'):-5] for p in files if p.startswith('Theorems/Thm_') and p.endswith('.lean')}
    solkeys = {p[len('P2M/Sol/S_'):-5] for p in files if p.startswith('P2M/Sol/S_') and p.endswith('.lean')}
    require(node_keys == wrappers == solkeys, 'source pair keyset')
    order = graph['topological_order']
    require(type(order) is list and all(type(k) is str for k in order) and len(order) == len(nodes) and
            set(order) == node_keys, 'topological keyset')
    rank = {k: i for i, k in enumerate(order)}; edges = 0; population = []
    for key, node in nodes.items():
        key_identity(key)
        fields(node, 'dependencies wrapper_sha256 solution_sha256', 'node schema')
        deps = node['dependencies']
        require(type(deps) is list and all(type(d) is str for d in deps) and
                len(deps) == len(set(deps)) and set(deps) <= node_keys, 'dependency keyset')
        require(all(rank[d] < rank[key] for d in deps), 'dependency order')
        solution = solutions[key]
        fields(solution, 'bytes imports mode oid path sha256 solution_bytes solution_id solution_sha256 state', 'solution schema')
        imports = solution['imports']
        require(type(imports) is list and all(type(x) is str for x in imports), 'import list')
        inferred = {x[len('Theorems.Thm_'):] for x in imports if x.startswith('Theorems.Thm_')}
        require(set(deps) == inferred, 'import dependency mismatch')
        wp, sp = 'Theorems/Thm_' + key + '.lean', 'P2M/Sol/S_' + key + '.lean'
        require(all(solution[k] == files[sp][k] and type(solution[k]) is type(files[sp][k])
                    for k in ('bytes', 'mode', 'oid', 'path', 'sha256', 'state')), 'solution source identity')
        require(solution['solution_id'] == 'P2M.Sol.S_' + key and
                solution['solution_sha256'] == solution['sha256'] == node['solution_sha256'] and
                type(solution['solution_bytes']) is int and solution['solution_bytes'] == solution['bytes'], 'solution duplicate identity')
        require(files[wp]['sha256'] == node['wrapper_sha256'], 'wrapper hash')
        population.append({'key': key, 'wrapper': files[wp], 'solution': files[sp]})
        edges += len(deps)
    require(type(graph['edge_count']) is int and graph['edge_count'] == edges, 'edge count')
    require(graph['graph_sha256'] == digest(canonical(nodes)), 'internal graph digest')
    return population


def ordered_population(population, commit):
    require(type(commit) is str and re.fullmatch('[0-9a-f]{40}', commit), 'commit identity')
    require(type(population) is list and population, 'population list')
    keys = [row['key'] for row in population]
    require(len(keys) == len(set(keys)), 'duplicate population key')
    for key in keys: key_identity(key)
    rows = [dict(row, assignment_digest=digest(PREFIX + commit.encode('ascii') + b'\x00' + row['key'].encode('utf-8')))
            for row in population]
    return sorted(rows, key=lambda row: (bytes.fromhex(row['assignment_digest']), row['key'].encode('utf-8')))
