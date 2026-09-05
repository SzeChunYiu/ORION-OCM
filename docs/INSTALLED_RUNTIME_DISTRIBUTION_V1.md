# Installed runtime distribution

The wheel now supports persistent bounded-world chat outside the repository. The
previous source checkout hid two distribution defects: runtime modules imported
M3 test fixtures, and the default knowledge manifest was resolved from a research
directory absent from installed packages.

## Executable routes

After installing a wheel, either route uses the same session implementation:

```sh
ocm chat --state ./my_state
python -m ocm.chat --state ./my_state
```

Both support the existing `--script`, `--knowledge-manifest`, `--diagnostic`, and
demo options. `ocm --help` explains the distinction between installed chat and
historical M0 repository audits. `ocm status` and `ocm demo` still require the
original repository custody tree; when it is absent, the console entrypoint emits
`CANNOT_CHECK_REPOSITORY_CUSTODY` with exit 2, rather than an uncaught exception or
a false runtime failure. The package does not ship protected evaluation corpora
or the entire historical reference tree.

## Vocabulary and resource custody

`ocm.language.bootstrap` owns the executable seed lexicons. Its function bodies
were copied from the registered M3 fixtures; only public names, return type
annotations, and an unused parameter changed. Historical fixture files remain
unchanged. Runtime chat, the matched parent, and M3/M4/M5 evaluation bootstraps now
import these runtime functions. No `src/ocm` module imports `tests`.

The packaged `ocm.data/KNOWLEDGE_MANIFEST_V1.json` is byte-identical to
`research/ocm-m6/KNOWLEDGE_MANIFEST_V1.json`, SHA-256
`dea32b88defcd56ef659e27c67ef359dbe5043cdb0dd6bb68a962788b80f85c6`.
The loader checks this digest before exposing the default manifest and before
seeding each new default session. Missing or
modified packaged data cannot silently produce an empty bootstrap. The adjacent
`RESOURCE_CUSTODY_V1.json` records the original source paths, source hashes, and
parent commit. The selected custom manifest supplies its own lexical labels.

The resource loader supports ordinary wheel installation, which extracts package
resources to disk. Importing a wheel directly as a ZIP file is outside the
path-based knowledge-loader contract. Resource identity is an integrity check
within this distribution; it is not an independent scientific certification.

## Verification

Five distribution checks were captured failing before the repair. The verification
builds a wheel from a temporary copy containing `src`, project metadata, and
licence files, with no research directory or tests. It installs that wheel with
`--no-index --no-deps` in a fresh virtual environment and removes `PYTHONPATH` and
`PYTHONHOME` before execution from an empty working directory.

The clean-wheel tests verify that no `tests` module is available; start module
chat; query registered knowledge; teach a word; use it compositionally; restart
through the console command; and recover the learned word and dialogue record.
They also instantiate the matched parent and M3/M4/M5 evaluation bootstraps from
the installed package. Additional checks compare seed lexemes and morphology
against the unchanged historical functions, validate source hashes, reject
missing/tampered resources, exercise CLI help and typed absent-custody results,
check custom-manifest vocabulary, and detect a default package-file change after
module import. The last case was added after independent runtime review found
that an import-time digest check alone would become stale in a long-lived process.

Commands:

```sh
python -m pytest -q tests/test_distribution.py
python -m pytest -q tests/m3/test_microworld.py tests/m6/test_chat_alpha.py tests/m7/test_batch3_obligations.py
```

The second command passed all 10 existing regression tests after extraction.
The distribution command passed all 12 checks, including custom-manifest
vocabulary and per-session default-resource custody after the constructor was
wired to the selected manifest.
Local offline wheel construction used the already installed primary runtime
setuptools 84.0.0 and wheel 0.48.0. The isolated execution runtime was Python
3.12.13. CI installs the project's pinned setuptools 75.8.0 and wheel 0.45.1 and
runs the same distribution checks in `.github/workflows/distribution.yml`.

These checks establish installation and bounded runtime integration. They do not
constitute a fresh protected evaluation or reopen any scientific terminal by
themselves.
