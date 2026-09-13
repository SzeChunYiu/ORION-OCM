# Focused interval verification

From this directory with CPython3.12 on Linux:

```sh
python3.12 -I -B test_parity_n_intervals_v1.py -v
python3.12 -I -O -B test_parity_n_intervals_v1.py -v
```

The tests use exact fractions, fixed formula premises and supplied interval
contracts. They enumerate only arithmetic completions, not parity candidates.
No native measurement, timing campaign, search, or grand replay is invoked.

The scoped repair receipt records the actual interpreter and command outputs,
and binds current source plus the untouched original PR573 archive.
It does not authenticate the original reported measurements.
