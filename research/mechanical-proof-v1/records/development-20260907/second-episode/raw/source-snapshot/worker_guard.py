"""Import/dispatch guard for the registered data-only worker source closure.

The external runner pins these bytes and runtime; this is not an arbitrary-Python sandbox.
"""
# copy performs an optional Jython probe in the trusted -I -S stdlib bootstrap.
import copy  # noqa: F401 -- load the trusted optional probe before installing the guard
import os
import sys

APP = os.path.dirname(os.path.realpath(__file__))
STDLIB = os.path.dirname(os.path.realpath(os.__file__))
SOURCE_MODULES = frozenset({'worker', 'worker_guard', 'f0_terms', 'f0_search'})
FORBIDDEN_MODULES = frozenset({'ctypes', '_ctypes', 'socket', '_socket', 'subprocess',
                             '_posixsubprocess', 'multiprocessing', 'site', 'ensurepip'})


class PolicyError(ValueError):
    pass


class Guard:
    def __init__(self):
        self.sealed = False
        self.denied = []
        self.finders = tuple(sys.meta_path)
        if not (sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode):
            raise PolicyError('worker requires -I -S -B')
        self.snapshot()  # Reject an already contaminated module environment.

    def refuse(self, event, detail):
        self.denied.append({'event': event, 'detail': str(detail)[:256]})
        raise PolicyError('prohibited ' + event + ': ' + str(detail)[:256])

    def name_allowed(self, name):
        top = name.split('.')[0]
        return top not in FORBIDDEN_MODULES and (top in sys.stdlib_module_names or name in SOURCE_MODULES)

    def origin_allowed(self, name, origin):
        if name == '__main__':
            return True  # The caller/production argv binds the trusted entrypoint.
        if not self.name_allowed(name):
            return False
        if origin in ('built-in', 'frozen'):
            return name.split('.')[0] in sys.stdlib_module_names
        if not isinstance(origin, str):
            return False
        path = os.path.realpath(origin)
        if name in SOURCE_MODULES:
            return path == os.path.join(APP, name + '.py')
        return (path.startswith(STDLIB + os.sep) and
                not {'site-packages', 'dist-packages'} & set(path.split(os.sep)))

    def snapshot(self):
        records = []
        for name, module in sorted(tuple(sys.modules.items())):
            if module is None:
                continue
            spec = getattr(module, '__spec__', None)
            origin = getattr(spec, 'origin', None)
            if name == '__main__':
                origin = 'trusted-entrypoint'
            if not self.origin_allowed(name, origin):
                self.refuse('module-origin', name + ':' + str(origin))
            records.append({'name': name, 'origin': origin})
        return records

    def find_spec(self, fullname, path=None, target=None):
        if self.sealed or not self.name_allowed(fullname):
            self.refuse('import', fullname)
        for finder in self.finders:
            spec = finder.find_spec(fullname, path, target)
            if spec is not None:
                if not self.origin_allowed(fullname, spec.origin):
                    self.refuse('import-origin', fullname + ':' + str(spec.origin))
                return spec
        self.refuse('import', fullname + ':unresolved')

    def audit(self, event, args):
        if event == 'import':
            name = args[0]
            if not self.name_allowed(name) or (self.sealed and name not in sys.modules):
                self.refuse(event, name)
            if len(args) > 1 and args[1] and not self.origin_allowed(name, args[1]):
                self.refuse('import-origin', name + ':' + str(args[1]))
        forbidden = (event.startswith(('socket.', 'ctypes.', 'subprocess.')) or
                     event in {'os.system', 'os.exec', 'os.posix_spawn', 'os.spawn',
                               'os.fork', 'os.forkpty', 'pty.spawn', 'sys.addaudithook'})
        if forbidden or (self.sealed and event in {'compile', 'exec', 'code.__new__', 'function.__new__'}):
            self.refuse(event, 'dispatch denied')

    def seal(self):
        self.snapshot()
        self.sealed = True

    def report(self):
        return {'schema': 'mechanical-worker-audit-v1', 'guard_sealed': self.sealed,
                'imported_modules': self.snapshot(), 'prohibited_events': list(self.denied)}


def install_guard():
    guard = Guard()
    sys.path[:] = [APP, STDLIB, os.path.join(STDLIB, 'lib-dynload')]
    sys.meta_path[:] = [guard]
    sys.addaudithook(guard.audit)
    return guard

