# Official CoNLL18 loader

`conll18_ud_eval.py` is an unmodified copy of the official UFAL evaluator:
https://universaldependencies.org/conll18/conll18_ud_eval.py

SHA256: `1072e02af00b1a56205b5e8216d51dee9b8944a104d80744afaccc78859fcb16`
Bytes: 27,773. Version 1.2 (2018).

Copyright 2017–2018 Institute of Formal and Applied Linguistics (UFAL), Charles
University. Authors Milan Straka and Martin Popel. Mozilla Public License 2.0;
the original notice and source remain intact. License: https://mozilla.org/MPL/2.0/

The G1 host imports only `load_conllu`/`UDError` for structural admission.
External scientific scoring may separately use `evaluate`; no gold input is
provided to the G1 donor or host structural check.
