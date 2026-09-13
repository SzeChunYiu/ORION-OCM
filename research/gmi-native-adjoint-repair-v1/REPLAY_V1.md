# Replay the native-adjoint repair

Use laptop billy and CPython3.12. The standalone primitive replay requires no dependency installation or
ecology/search execution. From this unit directory:

```sh
python3 -I -B -m unittest discover -s . -p 'test_*v1.py'
python3 -O -I -B -m unittest discover -s . -p 'test_*v1.py'
python3 -I -B replay_v1.py
python3 -O -I -B replay_v1.py
```

Whole-unit replay binds every member before and after an isolated checker and
compares its entire receipt bytes. Old native results are checked against their
complete retained state/ledger/tape records, without changing their identity.
The new native results explicitly name their source version. Source loading,
validation overhead, monitoring and physical cost are outside the authored
Machine ledger; no ecology or timing inference follows.

Repository integration additionally requires:

```sh
python3 -I -B verify_active_runtime_v1.py /path/to/ORION-OCM
python3 -I -B ../machine-intelligence-morphogenesis-v1/test_gmi_vm_parameter_adjoint_v1.py
python3 -O -I -B ../machine-intelligence-morphogenesis-v1/test_gmi_vm_parameter_adjoint_v1.py
```

The separate active-runtime binding prevents a portable corrected-source packet
from being mistaken for proof that another live VM contains the fix. Missing
or different active source is an error. All nine live bindings are required:
five changed files plus the four unchanged native import dependencies. The main manifest binds this binding;
it excludes only itself, avoiding a hash cycle. Store generated validation
outputs outside the frozen unit.

The repository's seven affected historical fixtures are explicitly pinned to
the old VM through the source-buffer loader. Their exact pytest node IDs and
commands are recorded in HISTORICAL_REGRESSION_VALIDATION_V1.json; preserve
all existing goldens. The portable unit's
loader tests perform no ecology calls. See HISTORICAL_RUNTIME_CUSTODY_V1.md.
