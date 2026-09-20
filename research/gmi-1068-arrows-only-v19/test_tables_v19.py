"""All finite tables versus independent endpoint reconstruction and actual roundtrips."""
from itertools import permutations,product
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import oracle_v19 as oracle
import partial_v19 as partial
import categories_v19 as category
from responses_v19 import Query,observe
COVERAGE={}


class TableTests(unittest.TestCase):
    def check_responses(self,rows,table,permutation):
        count=0
        for length in range(1,5):
            for arrows in product(range(len(rows)),repeat=length):
                expected=oracle.word(rows,arrows)
                mapped=tuple(permutation[a] for a in arrows)
                expected=None if expected is None else permutation[expected]
                self.assertEqual(observe(table,Query('word',mapped)),expected)
                count+=1
        for anchor in range(len(rows)):
            expected=permutation[anchor] if anchor in oracle.units(rows) else None
            self.assertEqual(observe(table,Query('empty',permutation[anchor])),expected)
            count+=1
        return count

    def test_all_tables_and_operational_roundtrips(self):
        counts={key:0 for key in ('accepted_tables','unit_instances','objects','composable_pairs',
            'base_responses','arrow_permutations','relabel_responses','object_permutations',
            'object_roundtrip_responses','bundled_pair_checks','weak_nonassociative_tables',
            'weak_local_coherent_nonassociative_tables')}
        counts.update({'law_pattern_'+''.join(map(str,bits)):0 for bits in product((0,1),repeat=3)})
        for n in range(4):
            table_count=0
            for rows in oracle.tables(n):
                table=partial.Table(rows)
                associative,local,coherent,weak=oracle.laws(rows)
                expected={'associativity':associative,'local_units':local,'coherence':coherent}
                self.assertEqual(partial.laws(table),expected)
                self.assertEqual(partial.units(table),oracle.units(rows))
                inferred=oracle.typed_reconstruction(rows)
                accepted=associative and local and coherent
                self.assertEqual(inferred is not None,accepted)
                counts['law_pattern_'+''.join(str(int(x)) for x in (associative,local,coherent))]+=1
                counts['weak_nonassociative_tables']+=int(weak and not associative)
                counts['weak_local_coherent_nonassociative_tables']+=int(weak and local and coherent and not associative)
                table_count+=1
                if not accepted:
                    with self.assertRaises(ValueError):partial.validate(table)
                    continue
                partial.validate(table)
                cat=category.reconstruct(table)
                category.validate_category(cat)
                self.assertEqual((cat.identities,cat.source,cat.target),
                                 (inferred['identities'],inferred['source'],inferred['target']))
                self.assertEqual(category.flatten(cat).rows,rows)
                bundles=category.bundles(cat)
                self.assertEqual(bundles,tuple((cat.source[a],cat.target[a],a) for a in range(n)))
                for a,b in product(range(n),repeat=2):
                    value=rows[a][b]
                    expected=None if value is None else bundles[value]
                    self.assertEqual(category.bundled_product(cat,bundles[a],bundles[b]),expected)
                    counts['bundled_pair_checks']+=1
                    counts['composable_pairs']+=int(value is not None)
                counts['accepted_tables']+=1
                counts['unit_instances']+=len(inferred['identities'])
                counts['objects']+=cat.object_count
                counts['base_responses']+=self.check_responses(rows,table,tuple(range(n)))
                for permutation in permutations(range(n)):
                    renamed=partial.relabel(table,permutation)
                    self.assertEqual(renamed.rows,oracle.relabel(rows,permutation))
                    rebuilt=category.reconstruct(renamed)
                    self.assertEqual(category.flatten(rebuilt),renamed)
                    counts['relabel_responses']+=self.check_responses(rows,renamed,permutation)
                    counts['arrow_permutations']+=1
                for object_perm in permutations(range(cat.object_count)):
                    identities=tuple(cat.identities[object_perm.index(i)] for i in range(cat.object_count))
                    variant=category.Typed(cat.object_count,tuple(object_perm[x] for x in cat.source),
                        tuple(object_perm[x] for x in cat.target),identities,table)
                    flat=category.flatten(variant)
                    rebuilt=category.reconstruct(flat)
                    bijection=tuple(rebuilt.identities.index(identity) for identity in variant.identities)
                    self.assertEqual(sorted(bijection),list(range(cat.object_count)))
                    for a in range(n):
                        self.assertEqual((bijection[variant.source[a]],bijection[variant.target[a]]),
                                         (rebuilt.source[a],rebuilt.target[a]))
                        self.assertEqual(rebuilt.identities[bijection[variant.source[a]]],
                                         variant.identities[variant.source[a]])
                    counts['object_roundtrip_responses']+=self.check_responses(rows,flat,tuple(range(n)))
                    counts['object_permutations']+=1
            self.assertEqual(table_count,(n+1)**(n*n))
            counts['tables_size_'+str(n)]=table_count
        self.assertEqual(sum(counts['tables_size_'+str(n)] for n in range(4)),262228)
        self.assertEqual(counts['accepted_tables'],counts['law_pattern_111'])
        self.assertEqual(counts['objects'],counts['unit_instances'])
        COVERAGE.update(counts)


if __name__=='__main__':
    result=unittest.main(exit=False,verbosity=2)
    print(json.dumps(COVERAGE,sort_keys=True))
    raise SystemExit(not result.result.wasSuccessful())
