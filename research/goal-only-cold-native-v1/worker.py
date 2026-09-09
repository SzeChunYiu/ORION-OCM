"""One fresh process: restore data, solve an issued goal, check the full native proof."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import resource
import sys
import sysconfig
import time

# -I alone still permits system site packages. Use only this adapter and the stdlib
# before custody adds the hash-checked bridge and archived parser runtime.
HERE = Path(__file__).resolve().parent
stdlib = Path(sysconfig.get_path('stdlib')).resolve()
sys.path[:] = [str(HERE), str(stdlib), str(stdlib / 'lib-dynload')]
from custody import (Refusal, checked_read, encoded, identity, load_bridge, parse,
                     raw_id, read_bundle, require, store, validate_request, write_bundle,
                     adapter_sources, execution_identity)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument('operation', choices=('produce-authored', 'solve', 'revoke', 'reinstate'))
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--request', type=Path)
    p.add_argument('--request-sha256')
    p.add_argument('--bundle', type=Path)
    p.add_argument('--state', type=Path)
    p.add_argument('--state-binding', type=Path)
    args = p.parse_args()
    started = time.perf_counter()
    before = resource.getrusage(resource.RUSAGE_SELF)
    out = args.output.resolve()
    out.mkdir(exist_ok=False)
    record = {'schema': 'ordinary.cold-native.observation.v1', 'terminal': 'CANNOT_CHECK',
              'pid': os.getpid(), 'parent_pid': os.getppid(), 'operation': args.operation,
              'python': {'version': sys.version, 'executable': sys.executable,
                         'binary': raw_id(Path(sys.executable).read_bytes())}, 'native_calls': 0}
    try:
        GL, GS, GN, F, manifest = load_bridge(out / 'runtime', include_fixture=args.operation == 'produce-authored')
        adapter_before = adapter_sources()
        source_pin = execution_identity(manifest)
        record['source_manifest'] = source_pin
        record['adapter_sources'] = adapter_before
        if args.operation == 'produce-authored':
            b = F.bundle()
            pins = write_bundle(out / 'bundle', b)
            import ocm_route
            binding = ocm_route.produce(out / 'state', pins, source_pin)
            store(out / 'state-binding.json', encoded(binding))
            record.update(state_binding=raw_id(encoded(binding)), lease=binding['initial_lease'])
            record.update(terminal='AUTHORED_BUNDLE_PERSISTED', bundle=pins,
                          task=F.task(), scope='Synthetic development fixture, not acquired OCM knowledge.')
        else:
            require(args.request is not None and args.bundle is not None, 'MISSING_REQUEST_OR_BUNDLE')
            require(args.request.stat().st_size <= 1_000_000, 'REQUEST_TOO_LARGE')
            raw = args.request.read_bytes()
            require(hashlib.sha256(raw).hexdigest() == args.request_sha256, 'ISSUED_REQUEST_PIN')
            request = parse(raw)
            validate_request(request)
            record.update(request=raw_id(raw), nonce=request['nonce'], mode=request['mode'])
            library = read_bundle(args.bundle, request['bundle'], GL)
            def generate():
                return GS.solve(request['task'], library, request['mode'])
            def check(result):
                source = Path(GN.__file__).parent / 'vendor'
                sources = {key: {'path': str(source / name), **raw_id((source / name).read_bytes())}
                           for key, name in {'index': 'trace_source.py', 'adapter': 'trace_adapter.py',
                                             'verifier': 'mmverify.py'}.items()}
                native = GN.execute(request['task'], result, GL.identity(result), library,
                    request['label'], request['holes'], args.bundle / 'joined.mm', out / 'native', sources)
                from custody import checked_sources
                require(execution_identity(checked_sources()) == source_pin, 'PRE_COMMIT_SOURCE_DRIFT')
                return native
            if request['route'] == 'ocm':
                require(args.state is not None and args.state_binding is not None, 'MISSING_OCM_STATE')
                import ocm_route
                binding = parse(checked_read(args.state_binding, request['state']['binding']))
                if args.operation in ('revoke', 'reinstate'):
                    revision = ocm_route.revise(args.state, binding, request['bundle'], source_pin,
                                               request['state']['lease'], args.operation)
                    record.update(terminal='OCM_REVISION_PERSISTED', ocm=revision)
                else:
                    routed = ocm_route.solve(args.state, binding, request, library, source_pin, generate, check)
                    record.update(ocm=routed, solver=routed['solver'], native=routed['native'])
                    record['native_calls'] = (routed['native'] or {}).get('native_calls', 0)
                    record['terminal'] = 'OCM_GOAL_NATIVE_COMMITTED' if routed['committed'] else 'CANNOT_CHECK'
            else:
                require(args.operation == 'solve', 'ORDINARY_REVISION_FORBIDDEN')
                result = generate()
                record['solver'] = result
                if result['terminal'] == 'GENERATED_PROOF_PENDING_NATIVE':
                    checked = check(result)
                    record.update(terminal=checked['terminal'], native=checked, native_calls=checked['native_calls'])
                else:
                    record['terminal'] = result['terminal']
            record['library_costs'] = library.costs
        # Drift while executing never grants a successful result.
        from custody import checked_sources
        require(checked_sources() == manifest and adapter_sources() == adapter_before, 'POST_SOURCE_DRIFT')
    except Exception as exc:
        record.update(terminal='CANNOT_CHECK', error={'type': type(exc).__name__, 'reason': str(exc)})
    finally:
        after = resource.getrusage(resource.RUSAGE_SELF)
        record['process_cost'] = {'wall_s': time.perf_counter() - started,
            'user_s': after.ru_utime - before.ru_utime, 'system_s': after.ru_stime - before.ru_stime,
            'peak_rss_kib_linux': after.ru_maxrss}
        record['file_imports'] = {name: {'path': str(Path(m.__file__).resolve()),
            **raw_id(Path(m.__file__).read_bytes())} for name, m in sorted(sys.modules.items())
            if getattr(m, '__file__', None) and Path(m.__file__).is_file()}
        store(out / 'observation.json', encoded(record) + b'\n')
    print(json.dumps({'terminal': record['terminal'], 'native_calls': record['native_calls']}))
    return 0 if record['terminal'] != 'CANNOT_CHECK' else 2

if __name__ == '__main__':
    raise SystemExit(main())
