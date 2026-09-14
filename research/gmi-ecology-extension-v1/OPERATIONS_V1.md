# Ecology extension: read first

Theorem + exact finite checks for A2. Extends MIM `ECOLOGY_CONTRACT_V1.json`
+ `ECOLOGY_AXES_V2.json` + `DEFINITIONS_V2_EXACT.md §2` without editing them.

Run from this unit directory:

```sh
python3 -I -B test_ecology_extension_v1.py -v
python3 -I -O -B test_ecology_extension_v1.py -v
```

Sibling source compiled explicitly; exact integer/string checks only,
CPython 3.8 safe.
