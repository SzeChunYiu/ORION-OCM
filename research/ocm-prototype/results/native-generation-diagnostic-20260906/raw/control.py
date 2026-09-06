"""Harmless subprocess controls only. Does not load a proposal or call run()."""
import json
from pathlib import Path
import sys
from capture import capture_one

root = Path(sys.argv[1]); root.mkdir()
commands = {
    'success': [sys.executable,'-c','import sys; print(sys.stdin.read()); print("stderr-ok",file=sys.stderr)'],
    'error': [sys.executable,'-c','import sys; print("intentional",file=sys.stderr); sys.exit(7)'],
    'timeout': ['/usr/bin/timeout','--kill-after=0.1s','0.05s',sys.executable,'-c','import time; time.sleep(2)'],
    'watchdog': [sys.executable,'-c','import time; time.sleep(2)'],
}
results = {}
for name, argv in commands.items():
    result = capture_one(argv, b'PUBLIC_MANUAL_FIXTURE', root/name, root, 0.1 if name == 'watchdog' else 3)
    results[name] = result
assert results['success']['exit_code'] == 0
assert (root/'success/stdout').read_bytes() == b'PUBLIC_MANUAL_FIXTURE\n'
assert (root/'success/stderr').read_bytes() == b'stderr-ok\n'
assert results['error']['exit_code'] == 7 and (root/'error/stderr').read_bytes() == b'intentional\n'
assert results['timeout']['gnu_timeout_exit'] and results['timeout']['exit_code'] == 124
assert results['watchdog']['supervisor_timeout'] and results['watchdog']['exit_code'] == -9
assert all(not Path('/proc/'+str(x['pid'])).exists() for x in results.values())
try:
    capture_one(commands['success'],b'',root/'success',root,3)
except FileExistsError:
    pass
else:
    raise AssertionError('create-only capture overwritten')
(root/'CONTROL.json').write_text(json.dumps({'status':'PASS','control_cases':4,'overwrite_refused':True,
 'actual_actor_calls':0,'commands':commands,'results':results},indent=2)+'\n')
print('4 harmless subprocess cases + create-only refusal PASS; no actor calls')
