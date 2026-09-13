# Focused verification

From this unit directory, use CPython 3.12 on Linux:

```sh
python3.12 -I -B test_strategic_tom_v1.py -v
python3.12 -I -O -B test_strategic_tom_v1.py -v
```

The test entrypoint compiles its sibling model from source and needs no ambient
Python path or GitHub environment. It generates only exact finite game tables.
