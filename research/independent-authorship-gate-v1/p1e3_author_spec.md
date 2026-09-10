# Authoring task: families of finite combinatorial objects (Implication Systems)

You are an independent task author. You will design a collection of puzzle families.
No knowledge of any existing project, framework, benchmark, or codebase is assumed or
wanted; use only your own vocabulary. If any term below collides with something you
happen to know, ignore that knowledge — this task is self-contained.

## What you author

At least **10 distinct families**. A family is a coherent kind of combinatorial object
with its own construction, its own name, its own description, and a difficulty
gradient across members. Each family has at least **5 instances** (so at least 50
instances in total). More families and more instances are welcome; the floors are
minimums, not targets.

## The formal core every instance compiles into

Every instance, whatever its surface story, must carry a machine-readable formal core
with EXACTLY these keys (these key names are fixed interface; everything else you add
uses your own naming):

```json
"core": {
  "elements": ["...", "..."],
  "implications": [ {"if": ["..."], "then": ["..."]} ],
  "base": ["..."],
  "excluded": ["..."],
  "weights": {"...": 3},
  "goals": ["..."]
}
```

Semantics (public, frozen, and the ONLY thing downstream tooling interprets):

- `elements` is a finite set of named atoms (strings). Everything referenced below
  must be an element.
- `implications` is a list of rules. A rule `{"if": A, "then": B}` fires when every
  atom in `A` holds; firing makes every atom in `B` hold. Rules are monotone: nothing
  ever becomes false.
- `base` is the set of atoms that hold initially.
- The **closure** of the core is the smallest set containing `base` and closed under
  the rules (unique regardless of rule order).
- `excluded` are atoms that are forbidden. A closure containing any excluded atom is
  disqualifying wherever exclusion matters (see the seed question).
- `weights` optionally gives each element a positive integer cost (1..99). Any
  element absent from `weights` costs 1.
- `goals` are the atoms one wants to hold.

Three questions are asked of every instance, each answerable by exact enumeration:

1. **Closure**: which atoms hold in the closure?
2. **Reachable goals**: which `goals` atoms hold in the closure?
3. **Minimum seed**: consider adding some set S of currently-unreachable atoms
   (atoms in the closure of `base` are NOT addable) to the start, where S must not
   include any `excluded` atom. Which minimum-total-cost S makes every `goals` atom
   hold in the closure of `base ∪ S`, while that closure contains no `excluded`
   atom? If no such S exists, the answer is IMPOSSIBLE.

## Hard bounds (instances outside them will be discarded, not fixed)

- `|elements|` <= 24
- `|implications|` <= 64
- `|base|` <= 24
- `|excluded|` <= 12
- `|goals|` <= 8
- the set of addable atoms (elements minus closure(base)) must have size <= 16
- every weight in 1..99

## Package layout you produce

```
families/
  __init__.py            # exposes FAMILIES = [<module names>] and total counts
  fam_<your_short_name>.py   # one module per family (you choose each short name)
AUTHOR_NOTES.md          # your own description of every family, in your words
emit_all.py              # runs every family emitter; writes instances.jsonl
instances.jsonl          # one JSON object per line (generated, deterministic)
```

Each family module must expose:

```python
FAMILY_NAME = "..."        # your name for the family
FAMILY_BLURB = "..."       # one-paragraph description in your own words

def emit(seed: int) -> list[dict]:
    """Deterministic in `seed`; returns >= 5 instance dicts."""
```

Each instance dict must contain:

- `"family"`: your family name
- `"instance_id"`: your stable id, unique across the whole package
- `"core"`: the formal core above
- `"surface"`: ANY additional descriptive fields you want (story, layout, hints,
  your own classification of the instance) — free-form, your naming
- `"intent"`: an object with your OWN expected answers, e.g. your expected closure
  size, which goals you believe are reachable, your expected minimum-seed cost, and
  any note you want to record. Clearly label it: `"intent_role": "audit_only"`.
  Your expected answers may be right or wrong; they are recorded, never checked by
  you against anything.

## Generation rules

- Deterministic: same seed, same instances. Use a fixed seed per family (document it
  in the module) so `emit_all.py` reproduces `instances.jsonl` byte-identically.
- No network, no filesystem access, no environment reads, no threads: emitters are
  pure Python computation over the seed.
- Standard library only.
- Instances within a family should differ non-trivially (do not emit 5 copies of
  the same core).
- Families must differ from each other in construction and in what varies across
  members, not just in name.

## What "distinct" means

Two families that only rename each other's atoms do not count as distinct. Aim for
genuinely different combinatorial structure (chains, layered systems, overlapping
clusters, threshold-like gating, resource-like costing, dead ends, near-miss goals,
...). The surface narrative is yours; the structure is the substance.

## Report

When you finish, list in AUTHOR_NOTES.md: each family name, how many instances it
emits, what varies across its members, and anything you found hard. Do not attempt
to verify your instances with external tools; your own reasoning is enough.
