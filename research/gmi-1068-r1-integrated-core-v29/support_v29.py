"""Production loading and fixture construction, separate from expected semantics."""
from pathlib import Path
import sys
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import oracle_v29 as oracle
import core_v29 as core
import presentation_v29 as presentation
import named_v29 as named
import information_v29 as information


def chain():
    n, source, target, identities, rows = oracle.chain_data()
    return core.categories.Typed(n, source, target, identities, core.partial.Table(rows))


def fixture():
    category = chain()
    mapping = presentation.GeneratorMap((3, oracle.EDGES), category, (1, 4, 2))
    return category, mapping


def adapter(category=None):
    return named.NamedAdapter(chain() if category is None else category,
                              7, oracle.LABELS, oracle.OBJECTS)


def exact(test, actual, expected):
    test.assertEqual(oracle.exact(actual), oracle.exact(expected))


def check_report(test, source, target, query_map, output_map, codes):
    result = information.transport_report(source,target,query_map,output_map,codes)
    truth = oracle.report_truth(source.responses,target.responses,query_map,output_map,codes)
    for key,value in truth.items():exact(test,result[key],value)
    expected_keys = set(truth) | {'source_recovery','restricted_target_recovery','full_target_recovery'}
    test.assertEqual(set(result),expected_keys)
    observations = (source.responses,tuple(tuple(row[i] for i in query_map)
                    for row in target.responses),target.responses)
    for key,rows in zip(('source_recovery','restricted_target_recovery','full_target_recovery'),observations):
        recovery = result[key]
        test.assertEqual(set(recovery),{'code_labels','response_codebook','response_labels','decoder','recoverable'})
        exact(test,recovery['code_labels'],codes)
        codebook = tuple(dict.fromkeys(rows))
        exact(test,recovery['response_codebook'],codebook)
        exact(test,recovery['response_labels'],tuple(codebook.index(row) for row in rows))
        decoders = oracle.attained_decoders(codes,rows)
        exact(test,recovery['recoverable'],bool(decoders))
        decoder = recovery['decoder']
        if not decoders:test.assertIsNone(decoder)
        else:
            test.assertIs(type(decoder),dict)
            test.assertEqual(set(decoder),set(codes))
            for a,b in decoder.items():
                test.assertIs(type(a),int);test.assertIs(type(b),int)
                test.assertTrue(0 <= b < len(codebook))
            exposed = {oracle.exact(k):oracle.exact(codebook[v]) for k,v in decoder.items()}
            test.assertIn(exposed,decoders)
    test.assertTrue(information.verify_transport_report(source,target,query_map,output_map,codes,result))
    return result
