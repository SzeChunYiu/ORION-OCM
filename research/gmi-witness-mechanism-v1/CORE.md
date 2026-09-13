# Witness mechanism ablation

[Result](RESULT_V1.md): DENSE removed with all served traces preserved;
varying-key control changes behavior and still passes the historical bar.

- [Consumer semantics proof](CONSUMER_SEMANTICS_V1.md)
- [Protocol](PROTOCOL_V1.md) and [registration](REGISTRATION_V1.json)
- [Exact three graphs](CANDIDATES_V1.json)
- [Complete native outputs and capture](evidence/RECEIPT_V1.json.gz)
- [Whole-process timing](evidence/PROCESS_TIME_V1.txt)
- [Record checker](check_mechanism_record.py), [tests](test_mechanism_record.py)
- [Witness recovery and source archive](../gmi-witness-recovery-v1/CORE.md)

Run check_mechanism_record.py with Python 3.11 or 3.12 and -I -B to validate
the retained result without new ecology calls. run_mechanism_ablation.py
repeats the registered 33 calls only if explicitly invoked with a new output
directory. The completed run is retained; no repeat is needed to inspect it.
