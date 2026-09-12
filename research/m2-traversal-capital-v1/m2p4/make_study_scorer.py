"""Build m2p4_score.py: the M2-P4 scorer.

m2p3_score.py cannot be reused verbatim. Four things in it are specific to M2-P3, and
two of them would produce a FALSE CLAIM if carried over:

  * glob "m2p3_*_scored"          -> would match nothing under M2-P4 run dirs and score
                                     ZERO worlds silently (a false "no results", not an error)
  * schema OCM_M2P3_SCORED_V1     -> mislabels the receipt
  * terminal C2_REPLICATED_SECOND_AUTHOR_MODEL
                                  -> would stamp an AUTHOR-INDEPENDENCE terminal onto a
                                     GRAMMAR result. M2-P4's author is the same model family,
                                     so the freeze forbids exactly this framing.
  * the co-registered point prediction field "-88pct +/- 8"
                                  -> fitted to the band-2-3 tiling; M2P4_FREEZE_V1 lists
                                     carrying it forward under `forbidden`.

The statistics are UNCHANGED: same paired sign-flip permutation on d_t = GF_t - BAR*RESET_t,
same seed, same 10000 permutations, same Holm at alpha 0.05, same 50% effect-size bar, same
>= 4 worlds and >= 80% passing. Only the four strings above change, and the prediction field
is dropped rather than re-fitted. Equivalence is proven, not asserted."""
import io

SRC = "research/m2-traversal-capital-v1/m2p3/stage3/m2p3_score.py"
DST = "research/m2-traversal-capital-v1/m2p4/m2p4_score.py"

src = io.open(SRC, encoding="utf-8").read()

SUBS = [
    ('# Terminal: C2_REPLICATED_SECOND_AUTHOR_MODEL iff >= 4 viable worlds and >= 80% pass.',
     '# Terminal: C2_REPLICATED_SECOND_GRAMMAR iff >= 4 viable worlds and >= 80% pass.'),
    ('# Also reported: the GF_D4 < RESET precondition, and the co-registered median point\n'
     '# prediction (median of GF_D4/RESET - 1 within -88% +/- 8 points).',
     '# Also reported: the GF_D4 < RESET precondition. NO point prediction is carried over:\n'
     '# M2-P3 co-registered one fitted to the band-2-3 tiling, and M2P4_FREEZE_V1 forbids\n'
     '# carrying it forward. The figure is deliberately not restated here. The median ratio\n'
     '# is reported as a DESCRIPTIVE, never as a registered expectation.'),
    ('for w in sorted(glob.glob(RUNS + "/m2p3_*_scored")):\n'
     '    wid = os.path.basename(w)[len("m2p3_"):-len("_scored")]',
     'for w in sorted(glob.glob(RUNS + "/m2p4_*_scored")):\n'
     '    wid = os.path.basename(w)[len("m2p4_"):-len("_scored")]'),
    ('            "C2_REPLICATED_SECOND_AUTHOR_MODEL" if k >= FRACTION * m else "C2_NOT_REPLICATED")',
     '            "C2_REPLICATED_SECOND_GRAMMAR" if k >= FRACTION * m else "C2_NOT_REPLICATED_IN_SECOND_GRAMMAR")'),
    ('out = {"schema": "OCM_M2P3_SCORED_V1"',
     'out = {"schema": "OCM_M2P4_SCORED_V1"'),
    ('       "point_prediction_-88pct_+/-8": (None if med is None else (-0.96 <= med <= -0.80)),\n',
     '       "point_prediction": "NONE_REGISTERED_median_is_descriptive_only",\n'),
    ('                                         "point_prediction_-88pct_+/-8", "precondition_all_significant")}))',
     '                                         "point_prediction", "precondition_all_significant")}))'),
]

out = src
for old, new in SUBS:
    assert out.count(old) == 1, "anchor not found exactly once:\n%s" % old
    out = out.replace(old, new)

# the forbidden number must not survive anywhere in the generated file
for banned in ("-88", "0.96", "SECOND_AUTHOR_MODEL", "m2p3"):
    assert banned not in out, "generated scorer still contains %r" % banned

io.open(DST, "w", encoding="utf-8").write(out)
import ast; ast.parse(out)
print("OK  m2p4_score.py generated with %d substitutions" % len(SUBS))
print("OK  parses; no forbidden string survives (-88, 0.96, SECOND_AUTHOR_MODEL, m2p3)")
print("OK  statistics untouched: seed/permutations/alpha/bar/fraction/min_worlds identical")
