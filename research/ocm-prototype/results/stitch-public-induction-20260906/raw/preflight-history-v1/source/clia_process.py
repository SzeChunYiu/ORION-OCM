"""One bounded native child per synthesis/check call; host configuration only."""
import json
import math
from pathlib import Path
import subprocess
import sys
import time

PYTHON = sys.executable
WORKER = Path(__file__).with_name('clia_worker.py')


def invoke(action, payload, *, timeout_ms=5000, deadline_s=15):
    start = time.perf_counter()
    metrics = {'external_deadline_s': deadline_s, 'native_timeout_ms': timeout_ms,
               'worker_cpu_s': None, 'peak_rss_kib': None, 'worker_pid': None,
               'unmeasured': ['energy', 'native internal active bytes', 'installation/pretraining costs']}
    result = {'status': 'CANNOT_CHECK', 'reason': 'invalid or exhausted host bounds',
              'native_invoked': False, 'metrics': metrics}
    if (action not in ('synthesize', 'verify') or type(timeout_ms) is not int or not 1 <= timeout_ms <= 60000
            or not isinstance(deadline_s, (int, float)) or not math.isfinite(deadline_s) or not 0 < deadline_s <= 120):
        metrics['envelope_wall_s'] = time.perf_counter() - start
        return result
    result.pop('reason')  # Valid bounds must not leave a stale failure reason on success.
    request = json.dumps({'action': action, 'payload': payload, 'timeout_ms': timeout_ms})
    metrics['request_bytes'] = len(request.encode())
    try:
        with subprocess.Popen([PYTHON, str(WORKER)], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, text=True) as process:
            result['native_invoked'] = True; metrics['worker_pid'] = process.pid
            try:
                stdout, stderr = process.communicate(request, timeout=deadline_s)
            except subprocess.TimeoutExpired:
                process.kill(); process.communicate()
                result['reason'] = 'EXTERNAL_TIMEOUT'
            else:
                metrics['response_bytes'] = len(stdout.encode())
                if process.returncode:
                    result['reason'] = 'native worker unavailable/failed'
                    result['worker_exit'] = process.returncode
                    result['worker_error'] = stderr[-2000:]
                else:
                    decoded = json.loads(stdout)
                    child_metrics = decoded.pop('metrics', {})
                    result.update(decoded); metrics.update(child_metrics)
    except (OSError, ValueError, TypeError) as exc:
        result['reason'] = f'worker unavailable or malformed response: {type(exc).__name__}'
    metrics['envelope_wall_s'] = time.perf_counter() - start
    result['metrics'] = metrics
    return result
