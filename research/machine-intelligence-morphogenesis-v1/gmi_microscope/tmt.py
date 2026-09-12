"""Exact / finite microscope checks of the Transformer microfeature theorems TMT-1..TMT-15
(GMI_TRANSFORMER_MICROFEATURE_THEOREMS_V1.md section 16, programme X-TMT1..X-TMT15: the ten checks the section lists, plus X-TMT5, X-TMT7,
X-TMT14 and X-TMT15, which the section names as theorems but did not list as checks).

Every check here is a MATHEMATICAL IMPLEMENTATION CHECK of a theorem on a finite, enumerated scope, executed in exact
rational arithmetic wherever the statement is algebraic (fractions.Fraction) and in floating point with a declared tolerance
where the statement involves exp/log (softmax, entropy, cross-entropy). None of it is empirical neural evidence; the receipt
says so in every entry. Writes GMI_TRANSFORMER_MICROFEATURE_EXACT_RECEIPT_V1.json at the research root.
"""
from __future__ import annotations

import itertools
import json
import math
import os
from fractions import Fraction as Fr

from .core import sha256_of

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
KIND = "MATH_IMPLEMENTATION_CHECK__NOT_EMPIRICAL_NEURAL_EVIDENCE"


# ----------------------------------------------------------------------------------------------------------------------
# X-TMT1: order-information necessity. Finite obligations on binary sequences; permutation-invariant encoders collide on
# quotient-distinct histories, positional encoders do not.
def x_tmt1(n=4):
    seqs = list(itertools.product((0, 1), repeat=n))
    obligations = {"first_token": lambda h: h[0], "is_sorted": lambda h: int(all(h[i] <= h[i + 1] for i in range(n - 1))), "count_ones": lambda h: sum(h)}
    encoders = {"multiset_counts": lambda h: (sum(h),), "sorted_tuple": lambda h: tuple(sorted(h)), "positional_tuple": lambda h: tuple(h)}
    out = {}
    for oname, q in obligations.items():
        for ename, z in encoders.items():
            # pairs (h, g.h) with identical encoder state but different quotient: theorem says no exact realization on both
            collisions = 0; pairs = 0
            for h in seqs:
                for g in itertools.permutations(range(n)):
                    hp = tuple(h[g[i]] for i in range(n))
                    if hp <= h: continue
                    pairs += 1
                    if z(h) == z(hp) and q(h) != q(hp): collisions += 1
            out[f"{oname}|{ename}"] = {"quotient_distinct_permutation_pairs_with_equal_state": collisions, "permutation_pairs": pairs}
    # assertions: order-sensitive obligations collide under invariant encoders and never under the positional encoder;
    # the permutation-invariant obligation (count_ones) never collides with any encoder
    ok = (out["first_token|multiset_counts"]["quotient_distinct_permutation_pairs_with_equal_state"] > 0 and out["is_sorted|sorted_tuple"]["quotient_distinct_permutation_pairs_with_equal_state"] > 0
          and all(v["quotient_distinct_permutation_pairs_with_equal_state"] == 0 for k, v in out.items() if k.endswith("positional_tuple"))
          and all(v["quotient_distinct_permutation_pairs_with_equal_state"] == 0 for k, v in out.items() if k.startswith("count_ones")))
    return {"check": "X-TMT1", "theorem": "TMT-1 order-information necessity", "scope": f"all binary sequences of length {n}, all permutations, 3 obligations x 3 encoders", "kind": KIND, "cells": out, "passed": ok}


# X-TMT2: finite-window impossibility. W-suffix collisions and the exact minimal error of any suffix-only decision.
def x_tmt2():
    out = {}; ok = True
    for W in (1, 2, 3):
        n = W + 2; seqs = list(itertools.product((0, 1), repeat=n)); q = lambda h: h[0]
        by_suffix = {}
        for h in seqs: by_suffix.setdefault(h[-W:], []).append(q(h))
        collisions = sum(1 for v in by_suffix.values() if len(set(v)) > 1)
        # minimal number of errors of ANY decision rule that is a function of the suffix (choose the majority label per suffix)
        min_err = sum(min(v.count(0), v.count(1)) for v in by_suffix.values())
        out[f"W={W}"] = {"n": n, "suffix_classes": len(by_suffix), "classes_with_quotient_collision": collisions, "min_errors_of_any_suffix_only_rule": min_err, "sequences": len(seqs), "min_error_rate": str(Fr(min_err, len(seqs)))}
        ok &= collisions == len(by_suffix) and Fr(min_err, len(seqs)) == Fr(1, 2)
    return {"check": "X-TMT2", "theorem": "TMT-2 finite-window impossibility", "scope": "binary sequences of length W+2, obligation = first token, W in {1,2,3}", "kind": KIND, "cells": out, "passed": ok}


# X-TMT3: fixed-routing union lower bound on enumerated dependency families (pointer tasks on k tokens).
def x_tmt3(k=4):
    out = {}; ok = True
    # family A: each input requires one source edge per target (a 'pointer' per position): E(x) = {(t, s_t)}
    inputs_a = list(itertools.product(range(k), repeat=k))
    fam = {"pointer_per_position": [frozenset((t, s[t]) for t in range(k)) for s in inputs_a],
           "single_pointer_last_token": [frozenset({(k - 1, s)}) for s in range(k)],
           "local_window_2": [frozenset((t, max(0, t - j)) for t in range(k) for j in (0, 1))],  # input-independent: union = E(x)
           }
    for name, E in fam.items():
        union = frozenset().union(*E); mean = Fr(sum(len(e) for e in E), len(E))
        ok &= all(e <= union for e in E) and len(union) >= mean
        out[name] = {"inputs": len(E), "union_edges": len(union), "mean_required_edges": str(mean), "structural_routing_opportunity_edges": str(len(union) - mean), "union_covers_every_input": all(e <= union for e in E)}
    ok &= Fr(out["local_window_2"]["structural_routing_opportunity_edges"]) == 0 and Fr(out["pointer_per_position"]["structural_routing_opportunity_edges"]) > 0
    return {"check": "X-TMT3", "theorem": "TMT-3 fixed-routing union lower bound", "scope": f"pointer dependency families on {k} tokens ({len(inputs_a)} inputs), a single-pointer family, and an input-independent local window", "kind": KIND, "cells": out, "passed": ok}


# X-TMT4: softmax variational characterization (numerical, float with tolerance).
def x_tmt4():
    def H(p): return -sum(x * math.log(x) for x in p if x > 0)
    out = {}; ok = True; worst = 0.0
    grid_step = 40
    simplex3 = [(i / grid_step, j / grid_step, (grid_step - i - j) / grid_step) for i in range(grid_step + 1) for j in range(grid_step + 1 - i)]
    for s in ((1.0, 2.0, 3.0), (0.0, 0.0, 0.0), (-2.0, 5.0, 1.0), (10.0, -10.0, 0.0)):
        for T in (0.5, 1.0, 2.0):
            m = max(s); e = [math.exp((x - m) / T) for x in s]; Z = sum(e); p = [x / Z for x in e]
            obj = lambda q: sum(qi * si for qi, si in zip(q, s)) + T * H(q)
            best_grid = max(obj(q) for q in simplex3); val = obj(p); lse = T * (math.log(Z) + m / T)
            gap = best_grid - val; worst = max(worst, gap)
            ok &= gap <= 1e-9 and abs(val - lse) <= 1e-9
            out[f"s={s}|T={T}"] = {"softmax": [round(x, 12) for x in p], "objective_at_softmax": round(val, 12), "max_objective_on_simplex_grid": round(best_grid, 12), "T_logsumexp": round(lse, 12)}
    return {"check": "X-TMT4", "theorem": "TMT-4 softmax variational characterization", "scope": "4 score vectors x 3 temperatures; simplex grid of step 1/40 (861 points); float64, tolerance 1e-9", "kind": KIND + "__NUMERICAL", "cells": out, "worst_grid_gap": worst, "passed": ok}


# exact attention primitives in rational arithmetic with a dyadic kernel 2^s (scores are integers) so that softmax-style
# normalization and the online (block-wise) rescaling are exact; plus a float64 version with real exp.
def _attn_exact(Q, K, V, causal=True):
    n = len(Q); out = []
    for i in range(n):
        js = range(i + 1) if causal else range(n)
        s = [sum(Q[i][a] * K[j][a] for a in range(len(Q[i]))) for j in js]
        w = [Fr(2) ** int(x) for x in s]; Z = sum(w)
        out.append([sum(w[t] * V[j][a] for t, j in enumerate(js)) / Z for a in range(len(V[0]))])
    return out


def _attn_online_blocks(Q, K, V, block=2):
    """Flash-style: process keys in blocks with running max and rescaling; exact with the dyadic kernel."""
    n = len(Q); out = []
    for i in range(n):
        m = None; l = Fr(0); acc = [Fr(0)] * len(V[0])
        for b0 in range(0, i + 1, block):
            js = list(range(b0, min(b0 + block, i + 1)))
            s = [sum(Q[i][a] * K[j][a] for a in range(len(Q[i]))) for j in js]
            m_new = max(s) if m is None else max(m, max(s))
            scale = Fr(2) ** int(m - m_new) if m is not None else Fr(1)
            l = l * scale; acc = [x * scale for x in acc]
            for t, j in enumerate(js):
                w = Fr(2) ** int(s[t] - m_new); l += w; acc = [acc[a] + w * V[j][a] for a in range(len(V[0]))]
            m = m_new
        out.append([x / l for x in acc])
    return out


def _tiny_inputs(n=5, d=2):
    Q = [[Fr((i * 3 + a) % 3 - 1) for a in range(d)] for i in range(n)]
    K = [[Fr((i * 5 + 2 * a) % 3 - 1) for a in range(d)] for i in range(n)]
    V = [[Fr((i * 7 + a) % 5 - 2) for a in range(d)] for i in range(n)]
    return Q, K, V


# X-TMT5: causal-mask legality (exact): with the causal mask, output i does not depend on tokens > i; without it, it does.
def x_tmt5():
    Q, K, V = _tiny_inputs(); n = len(Q)
    base_c = _attn_exact(Q, K, V, causal=True); base_f = _attn_exact(Q, K, V, causal=False)
    K2 = [row[:] for row in K]; V2 = [row[:] for row in V]; K2[-1] = [x + 1 for x in K2[-1]]; V2[-1] = [x + 3 for x in V2[-1]]  # perturb the LAST token only
    pert_c = _attn_exact(Q, K2, V2, causal=True); pert_f = _attn_exact(Q, K2, V2, causal=False)
    causal_prefix_unchanged = all(base_c[i] == pert_c[i] for i in range(n - 1)); full_changed = any(base_f[i] != pert_f[i] for i in range(n - 1))
    return {"check": "X-TMT5", "theorem": "TMT-5 causal information legality", "scope": f"exact dyadic-kernel attention on {n} tokens; perturb the last token; compare outputs at positions < {n-1}", "kind": KIND,
            "cells": {"causal_mask_outputs_before_last_position_unchanged": causal_prefix_unchanged, "unmasked_outputs_before_last_position_changed": full_changed}, "passed": causal_prefix_unchanged and full_changed}


# X-TMT6: exact cache substitution: recompute K,V at every step vs cache them; identical outputs; op counts.
def x_tmt6():
    n = 6; d = 2; Wk = [[Fr(1), Fr(-1)], [Fr(2), Fr(1)]]; Wv = [[Fr(1), Fr(1)], [Fr(0), Fr(-1)]]
    xs = [[Fr((t * 3 + a) % 3 - 1) for a in range(d)] for t in range(n)]
    def proj(W, x): return [sum(W[a][b] * x[b] for b in range(d)) for a in range(d)]
    # (a) recompute all K,V for the prefix at every step
    ops_recompute = 0; outs_a = []
    for t in range(n):
        K = [proj(Wk, x) for x in xs[: t + 1]]; V = [proj(Wv, x) for x in xs[: t + 1]]; ops_recompute += 2 * (t + 1) * d * d
        outs_a.append(_attn_exact(xs[: t + 1], K, V, causal=True)[t])
    # (b) cache
    ops_cache = 0; Kc = []; Vc = []; outs_b = []
    for t in range(n):
        Kc.append(proj(Wk, xs[t])); Vc.append(proj(Wv, xs[t])); ops_cache += 2 * d * d
        outs_b.append(_attn_exact(xs[: t + 1], Kc, Vc, causal=True)[t])
    same = outs_a == outs_b
    return {"check": "X-TMT6", "theorem": "TMT-6 exact cache substitution", "scope": f"{n}-step autoregressive continuation, d = {d}, exact rational projections and dyadic-kernel attention", "kind": KIND,
            "cells": {"outputs_identical": same, "projection_mults_recompute": ops_recompute, "projection_mults_cached": ops_cache, "ratio": str(Fr(ops_recompute, ops_cache))}, "passed": same and ops_cache < ops_recompute}


# X-TMT7: implementation invariance of exact attention: naive vs block-wise online normalization (exact) and float64 real-exp.
def x_tmt7():
    Q, K, V = _tiny_inputs(n=6)
    naive = _attn_exact(Q, K, V); online = _attn_online_blocks(Q, K, V, block=2); online3 = _attn_online_blocks(Q, K, V, block=3)
    exact_equal = naive == online == online3
    # float version with real exp
    Qf = [[float(x) for x in r] for r in Q]; Kf = [[float(x) for x in r] for r in K]; Vf = [[float(x) for x in r] for r in V]; n = len(Qf)
    def naive_f(i):
        s = [sum(Qf[i][a] * Kf[j][a] for a in range(2)) for j in range(i + 1)]; m = max(s); w = [math.exp(x - m) for x in s]; Z = sum(w)
        return [sum(w[j] * Vf[j][a] for j in range(i + 1)) / Z for a in range(2)]
    def online_f(i, block=2):
        m = -math.inf; l = 0.0; acc = [0.0, 0.0]
        for b0 in range(0, i + 1, block):
            js = list(range(b0, min(b0 + block, i + 1))); s = [sum(Qf[i][a] * Kf[j][a] for a in range(2)) for j in js]
            m_new = max(m, max(s)); scale = math.exp(m - m_new) if m > -math.inf else 0.0; l *= scale; acc = [x * scale for x in acc]
            for t, j in enumerate(js):
                w = math.exp(s[t] - m_new); l += w; acc = [acc[a] + w * Vf[j][a] for a in range(2)]
            m = m_new
        return [x / l for x in acc]
    maxdiff = max(abs(naive_f(i)[a] - online_f(i)[a]) for i in range(n) for a in range(2))
    return {"check": "X-TMT7", "theorem": "TMT-7 implementation invariance of exact attention", "scope": "6 tokens; naive vs online block-wise (blocks 2 and 3) normalization; exact with the dyadic kernel, float64 with real exp", "kind": KIND,
            "cells": {"exact_dyadic_kernel_outputs_identical": exact_equal, "float64_max_abs_difference": maxdiff}, "passed": exact_equal and maxdiff <= 1e-12}


# X-TMT8: tied-parameter function-class inclusion on enumerated tiny two-layer families.
def x_tmt8():
    vals = (-1, 0, 1); inputs = list(itertools.product(vals, repeat=2))
    def relu(v): return [max(0, x) for x in v]
    def f(W1, W2, x): h = relu([sum(W1[a][b] * x[b] for b in range(2)) for a in range(2)]); return tuple(sum(W2[a][b] * h[b] for b in range(2)) for a in range(2))
    mats = [((m[0], m[1]), (m[2], m[3])) for m in itertools.product(vals, repeat=4)]
    untied = set(); tied = set()
    for W1 in mats:
        for W2 in mats:
            untied.add(tuple(f(W1, W2, x) for x in inputs))
        W2t = ((W1[0][0], W1[1][0]), (W1[0][1], W1[1][1]))  # tied: W2 = W1^T (tied input/output embeddings)
        tied.add(tuple(f(W1, W2t, x) for x in inputs))
    return {"check": "X-TMT8", "theorem": "TMT-8 tied-parameter function-class inclusion", "scope": "y = W2 relu(W1 x), W in {-1,0,1}^(2x2), inputs {-1,0,1}^2; tied = (W2 = W1^T)", "kind": KIND,
            "cells": {"distinct_functions_untied": len(untied), "distinct_functions_tied": len(tied), "tied_subset_of_untied": tied <= untied, "strict": len(tied) < len(untied)}, "passed": tied <= untied and len(tied) < len(untied)}


# X-TMT9: residual Jacobian identity, exact rational matrices; residual vs plain products across depth.
def x_tmt9():
    def matmul(A, B): return [[sum(A[i][k] * B[k][j] for k in range(2)) for j in range(2)] for i in range(2)]
    def add(A, B): return [[A[i][j] + B[i][j] for j in range(2)] for i in range(2)]
    I = [[Fr(1), Fr(0)], [Fr(0), Fr(1)]]
    layers = [[[Fr(-1, 4), Fr(1, 8)], [Fr(0), Fr(-1, 2)]], [[Fr(1, 3), Fr(0)], [Fr(-1, 6), Fr(1, 4)]], [[Fr(-1, 2), Fr(1, 4)], [Fr(1, 8), Fr(-1, 3)]]]
    # exact Jacobian of y = x + f(x) with f linear (J_f = A) via exact finite differences (linear => exact)
    def f_lin(A, x): return [sum(A[i][j] * x[j] for j in range(2)) for i in range(2)]
    x0 = [Fr(1, 3), Fr(-2, 5)]; ok = True; cells = {}
    for li, A in enumerate(layers):
        J = [[(f_lin(A, [x0[0] + (1 if j == 0 else 0), x0[1] + (1 if j == 1 else 0)])[i] + [x0[0] + (1 if j == 0 else 0), x0[1] + (1 if j == 1 else 0)][i]) - (f_lin(A, x0)[i] + x0[i]) for j in range(2)] for i in range(2)]
        ok &= J == add(I, A); cells[f"layer{li}_J_equals_I_plus_Jf"] = J == add(I, A)
    P_res = I; P_plain = I
    for A in layers: P_res = matmul(add(I, A), P_res); P_plain = matmul(A, P_plain)
    dist = lambda M: max(abs(M[i][j] - I[i][j]) for i in range(2) for j in range(2))
    cells["end_to_end_residual_jacobian"] = [[str(x) for x in r] for r in P_res]; cells["end_to_end_plain_jacobian"] = [[str(x) for x in r] for r in P_plain]
    cells["max_entry_distance_from_identity_residual"] = str(dist(P_res)); cells["max_entry_norm_plain"] = str(max(abs(x) for r in P_plain for x in r))
    ok &= P_res == matmul(add(I, layers[2]), matmul(add(I, layers[1]), add(I, layers[0])))
    return {"check": "X-TMT9", "theorem": "TMT-9 residual Jacobian identity", "scope": "three exact rational 2x2 linear blocks; finite-difference Jacobians (exact for linear maps); end-to-end products", "kind": KIND, "cells": cells, "passed": ok}


# X-TMT10: autoregressive chain factorization, exact rational distributions.
def x_tmt10():
    n = 3; seqs = list(itertools.product((0, 1), repeat=n)); raw = {s: Fr(1 + sum(s) + 2 * s[0] + s[-1] * 3, 1) for s in seqs}; Z = sum(raw.values()); p = {s: v / Z for s, v in raw.items()}
    def marg(prefix): return sum(v for s, v in p.items() if s[: len(prefix)] == prefix)
    ok = True
    for s in seqs:
        prod = Fr(1)
        for t in range(n): prod *= marg(s[: t + 1]) / marg(s[:t])
        ok &= prod == p[s]
    return {"check": "X-TMT10", "theorem": "TMT-10 autoregressive chain factorization", "scope": f"exact rational distribution over binary sequences of length {n} (8 sequences)", "kind": KIND, "cells": {"all_sequences_factor_exactly": ok}, "passed": ok}


# X-TMT11: population cross-entropy decomposition CE = H(Y|X) + E KL, and optimum at q = p (float with tolerance).
def x_tmt11():
    px = [Fr(1, 4), Fr(1, 2), Fr(1, 4)]; p = [[Fr(1, 2), Fr(1, 2)], [Fr(1, 4), Fr(3, 4)], [Fr(9, 10), Fr(1, 10)]]
    qs = {"q=p": p, "q_uniform": [[Fr(1, 2), Fr(1, 2)]] * 3, "q_skewed": [[Fr(1, 5), Fr(4, 5)], [Fr(1, 3), Fr(2, 3)], [Fr(1, 2), Fr(1, 2)]]}
    Hc = sum(float(px[x]) * -sum(float(p[x][y]) * math.log(float(p[x][y])) for y in range(2)) for x in range(3)); cells = {}; ok = True; ce_p = None
    for name, q in qs.items():
        ce = sum(float(px[x]) * -sum(float(p[x][y]) * math.log(float(q[x][y])) for y in range(2)) for x in range(3))
        kl = sum(float(px[x]) * sum(float(p[x][y]) * math.log(float(p[x][y]) / float(q[x][y])) for y in range(2)) for x in range(3))
        ok &= abs(ce - (Hc + kl)) <= 1e-12; cells[name] = {"cross_entropy": ce, "H_Y_given_X": Hc, "E_KL": kl, "identity_gap": ce - (Hc + kl)}
        if name == "q=p": ce_p = ce
    ok &= all(cells[n]["cross_entropy"] >= ce_p - 1e-12 for n in cells) and abs(cells["q=p"]["E_KL"]) <= 1e-12
    return {"check": "X-TMT11", "theorem": "TMT-11 population cross-entropy optimum", "scope": "3 contexts x 2 outcomes, exact rational p and three candidate q; float64 logs, tolerance 1e-12", "kind": KIND + "__NUMERICAL", "cells": cells, "passed": ok}


# X-TMT12: quantization collision no-go on enumerated authority states.
def x_tmt12():
    states = list(itertools.product(range(8), repeat=2)); q_O = lambda z: (z[0] + z[1]) % 2  # obligation: parity of the sum
    quantizers = {"drop_low_bit": lambda z: (z[0] >> 1, z[1] >> 1), "keep_parity_side_channel": lambda z: (z[0] >> 1, z[1] >> 1, (z[0] + z[1]) % 2), "identity": lambda z: z}
    cells = {}; ok = True
    for name, Q in quantizers.items():
        groups = {}
        for z in states: groups.setdefault(Q(z), set()).add(q_O(z))
        colliding = sum(1 for v in groups.values() if len(v) > 1)
        cells[name] = {"serving_states": len(groups), "serving_states_merging_quotient_distinct_authority_states": colliding, "exact_on_all_states_possible": colliding == 0}
    ok = cells["drop_low_bit"]["serving_states_merging_quotient_distinct_authority_states"] > 0 and cells["keep_parity_side_channel"]["exact_on_all_states_possible"] and cells["identity"]["exact_on_all_states_possible"]
    return {"check": "X-TMT12", "theorem": "TMT-12 quantization collision no-go", "scope": "64 authority states in {0..7}^2, obligation = parity of the sum, three quantizers", "kind": KIND, "cells": cells, "passed": ok}


# X-TMT13: key/value cache element accounting for MHA / GQA / MQA.
def x_tmt13():
    L, n, d, H = 4, 16, 8, 8; cells = {}; ok = True
    for name, Hkv in (("MHA", H), ("GQA_g4", H // 4), ("MQA", 1)):
        stored = 0
        for layer in range(L):
            for t in range(n):
                for h in range(Hkv): stored += 2 * d  # one key and one value vector per kv head per token per layer
        cells[name] = {"H_kv": Hkv, "stored_elements": stored, "formula_2LndHkv": 2 * L * n * d * Hkv}; ok &= stored == 2 * L * n * d * Hkv
    ok &= cells["MHA"]["stored_elements"] == 4 * cells["GQA_g4"]["stored_elements"] == 8 * cells["MQA"]["stored_elements"]
    return {"check": "X-TMT13", "theorem": "TMT-13 key/value cache state scaling", "scope": f"L={L}, n={n}, d={d}, H={H}; explicit element count vs 2 L n d H_kv", "kind": KIND, "cells": cells, "passed": ok}


# ----------------------------------------------------------------------------------------------------------------------
# X-TMT14: fixed-window / cache distinction. Combines the X-TMT2 collision construction (a W-window model merges
# quotient-distinct histories) with the X-TMT6 cache trace (recompute vs exact cache). An exact KV cache is added to the
# SAME W-window model: op counts fall, but the induced partition of histories -- the set of histories the model can
# distinguish -- is bit-identical, and still merges the quotient-distinct pairs X-TMT2 enumerates. Cache efficiency is
# therefore not context capacity.
def x_tmt14(W=2, extra=2):
    n = W + extra; d = 2
    Wk = [[Fr(1), Fr(-1)], [Fr(2), Fr(1)]]; Wv = [[Fr(1), Fr(1)], [Fr(0), Fr(-1)]]
    def proj(M, x): return [sum(M[a][b] * x[b] for b in range(d)) for a in range(d)]
    def embed(tok, t): return [Fr(tok), Fr(t % 2)]          # token embedding + a 2-periodic positional feature
    q_O = lambda h: h[0]                                     # the obligation of X-TMT2: the FIRST token
    histories = list(itertools.product((0, 1), repeat=n))

    def run(h, cached):
        """Windowed decoder over history h. Returns (final output, projection-multiplication count).
        The window is the LAST W positions at every step; the cache stores exact per-token K/V projections."""
        ops = 0; Kc = []; Vc = []; out = None
        for t in range(n):
            xs = [embed(h[u], u) for u in range(t + 1)]
            lo = max(0, t - W + 1)                            # the model's legal window at step t
            if cached:
                Kc.append(proj(Wk, xs[t])); Vc.append(proj(Wv, xs[t])); ops += 2 * d * d
                K = Kc[lo:t + 1]; V = Vc[lo:t + 1]
            else:                                             # recompute every in-window K/V at every step
                K = [proj(Wk, x) for x in xs[lo:t + 1]]; V = [proj(Wv, x) for x in xs[lo:t + 1]]; ops += 2 * (t + 1 - lo) * d * d
            Qw = xs[lo:t + 1]
            out = _attn_exact(Qw, K, V, causal=True)[-1]
            # NOTE: the cache stores K/V for ALL tokens, but the window still only admits the last W of them.
        return out, ops

    sig_recompute = {}; sig_cached = {}; ops_r = 0; ops_c = 0; identical = True
    for h in histories:
        (o_r, a) = run(h, False); (o_c, b) = run(h, True); ops_r += a; ops_c += b
        identical &= (o_r == o_c)
        sig_recompute.setdefault(tuple(str(x) for x in o_r), []).append(h)
        sig_cached.setdefault(tuple(str(x) for x in o_c), []).append(h)
    # the induced partitions of the history set (what the model can distinguish)
    part_r = sorted(sorted(v) for v in sig_recompute.values()); part_c = sorted(sorted(v) for v in sig_cached.values())
    # quotient-distinct pairs merged by each variant
    def merged(part): return sum(1 for cls in part for i in range(len(cls)) for j in range(i + 1, len(cls)) if q_O(cls[i]) != q_O(cls[j]))
    m_r, m_c = merged(part_r), merged(part_c)
    # the W-suffix reference partition of X-TMT2 and the quotient-distinct pairs it merges
    suf = {}
    for h in histories: suf.setdefault(h[-W:], []).append(h)
    part_suf = sorted(sorted(v) for v in suf.values()); m_suf = merged(part_suf)
    ok = (identical and part_r == part_c and m_c == m_r > 0 and ops_c < ops_r and m_suf > 0)
    return {"check": "X-TMT14", "theorem": "TMT-14 fixed-window / cache distinction",
            "scope": f"all {len(histories)} binary histories of length {n}; a W={W} windowed exact decoder run twice (recompute vs exact per-token K/V cache); obligation = first token (the X-TMT2 obligation)",
            "kind": KIND,
            "cells": {"outputs_identical_recompute_vs_cached": identical,
                      "projection_mults_recompute": ops_r, "projection_mults_cached": ops_c,
                      "op_ratio": str(Fr(ops_r, ops_c)),
                      "distinguishable_history_classes_recompute": len(part_r), "distinguishable_history_classes_cached": len(part_c),
                      "induced_partition_identical": part_r == part_c,
                      "quotient_distinct_pairs_merged_recompute": m_r, "quotient_distinct_pairs_merged_cached": m_c,
                      "reference_W_suffix_classes": len(part_suf), "quotient_distinct_pairs_merged_by_W_suffix": m_suf,
                      "reading": "the cache changed the op count and changed NOTHING about which histories are distinguishable; the window, not the cache, bounds context capacity"},
            "passed": ok}


# X-TMT15: decoding policy / model distribution distinction. ONE exact rational p_theta over a depth-3 binary token tree
# is decoded by greedy / temperature (deterministic inverse-CDF against a DECLARED fixed quantile sequence -- no RNG) /
# top-k / top-p / beam. The emitted sequences differ across policies while the distribution object is bit-identical
# (same sha over the conditional table), so a reported improvement must name which object improved.
def x_tmt15():
    n = 3; V = (0, 1)
    # exact conditional table p_theta(x_t | x_<t): a declared rational tree, deliberately NOT greedy-optimal at the root
    P = {(): (Fr(11, 20), Fr(9, 20)),
         (0,): (Fr(1, 2), Fr(1, 2)), (1,): (Fr(9, 10), Fr(1, 10)),
         (0, 0): (Fr(1, 2), Fr(1, 2)), (0, 1): (Fr(1, 2), Fr(1, 2)),
         (1, 0): (Fr(9, 10), Fr(1, 10)), (1, 1): (Fr(1, 2), Fr(1, 2))}
    theta_sha = sha256_of({str(k): [str(x) for x in v] for k, v in sorted(P.items())})
    seqs = list(itertools.product(V, repeat=n))
    def pseq(s):
        p = Fr(1)
        for t in range(n): p *= P[s[:t]][s[t]]
        return p

    def greedy():
        s = []
        for t in range(n): s.append(0 if P[tuple(s)][0] >= P[tuple(s)][1] else 1)
        return tuple(s)

    QUANTILES = (Fr(7, 10), Fr(1, 4), Fr(19, 20))   # DECLARED fixed quantile sequence; inverse-CDF, no RNG anywhere
    def sample(T, k=None, top_p=None):
        """Deterministic inverse-CDF emission under temperature T with optional top-k / top-p truncation.
        Temperature is applied exactly by taking p^(1/T) and renormalizing (exact for rational p and integer 1/T)."""
        s = []
        for t in range(n):
            p = list(P[tuple(s)])
            if T != 1:
                inv = Fr(1) / Fr(T)
                assert inv.denominator == 1, "declared scope: 1/T integral so p^(1/T) stays rational"
                p = [x ** int(inv) for x in p]; Z = sum(p); p = [x / Z for x in p]
            order = sorted(range(len(V)), key=lambda i: (-p[i], i))
            keep = set(order)
            if k is not None: keep = set(order[:k])
            if top_p is not None:
                keep = set(); acc = Fr(0)
                for i in order:
                    keep.add(i); acc += p[i]
                    if acc >= top_p: break
            q = [p[i] if i in keep else Fr(0) for i in range(len(V))]; Z = sum(q); q = [x / Z for x in q]
            u = QUANTILES[t]; acc = Fr(0); pick = len(V) - 1
            for i in range(len(V)):
                acc += q[i]
                if u < acc: pick = i; break
            s.append(pick)
        return tuple(s)

    def beam(B):
        beams = [((), Fr(1))]
        for t in range(n):
            cand = [(s + (v,), p * P[s][v]) for s, p in beams for v in V]
            cand.sort(key=lambda sp: (-sp[1], sp[0])); beams = cand[:B]
        return beams[0][0]

    policies = {"greedy": greedy(), "temperature_T=1": sample(1), "temperature_T=1/2": sample(Fr(1, 2)),
                "top_k=1": sample(1, k=1), "top_p=0.6": sample(1, top_p=Fr(3, 5)), "beam_B=2": beam(2), "beam_B=4": beam(4),
                "argmax_sequence": max(seqs, key=lambda s: (pseq(s), tuple(-x for x in s)))}
    cells = {name: {"emitted": list(s), "p_theta_of_emitted": str(pseq(s))} for name, s in policies.items()}
    distinct = {tuple(s) for s in policies.values()}
    # the claims: theta is untouched by any policy; the policies disagree; greedy is NOT the sequence argmax; beam finds it
    ok = (len(distinct) >= 3 and policies["greedy"] != policies["argmax_sequence"]
          and policies["beam_B=4"] == policies["argmax_sequence"]
          and pseq(policies["argmax_sequence"]) > pseq(policies["greedy"])
          and policies["top_k=1"] == policies["greedy"]
          and theta_sha == sha256_of({str(k): [str(x) for x in v] for k, v in sorted(P.items())}))
    cells["p_theta_conditional_table_sha256"] = theta_sha
    cells["distinct_emitted_sequences"] = len(distinct)
    cells["reading"] = "one p_theta, eight decoders, " + str(len(distinct)) + " distinct emissions; an evaluation that moves must name whether it moved p_theta or the decoder"
    return {"check": "X-TMT15", "theorem": "TMT-15 decoding policy / model distribution distinction",
            "scope": "one exact rational p_theta over binary sequences of length 3 (7 conditionals); greedy, temperature T in {1, 1/2} by deterministic inverse-CDF against a declared quantile sequence (7/10, 1/4, 19/20), top-k=1, top-p=0.6, beam B in {2,4}, and the exact sequence argmax; no randomness anywhere",
            "kind": KIND, "cells": cells, "passed": ok}


CHECKS = [x_tmt1, x_tmt2, x_tmt3, x_tmt4, x_tmt5, x_tmt6, x_tmt7, x_tmt8, x_tmt9, x_tmt10, x_tmt11, x_tmt12, x_tmt13, x_tmt14, x_tmt15]
NOT_CHECKED = {}  # X-TMT14 and X-TMT15 now carry finite checks; the section 16 programme is fully implemented at X-TMT1..X-TMT15.


def main(path=None):
    results = [c() for c in CHECKS]
    receipt = {"schema": "GMI_TRANSFORMER_MICROFEATURE_EXACT_V1", "issue": [377, 422], "source_theorems": "GMI_TRANSFORMER_MICROFEATURE_THEOREMS_V1.md (TMT-1..15), programme section 16 (complete: every TMT-1..15 statement has a finite check)",
               "evidence_kind": KIND, "checks": results, "not_checked": NOT_CHECKED, "n_passed": sum(r["passed"] for r in results), "n_checks": len(results),
               "status": "GREEN" if all(r["passed"] for r in results) else "RED",
               "claim_ceiling": "exact/numerical implementation checks of the theorem statements on enumerated finite scopes; establishes nothing about trained neural networks (section 17 of the theorems document remains empirical)"}
    receipt["receipt_sha256"] = sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    json.dump(receipt, open(path or os.path.join(ROOT, "GMI_TRANSFORMER_MICROFEATURE_EXACT_RECEIPT_V1.json"), "w"), indent=1, sort_keys=True, default=str)
    return receipt


if __name__ == "__main__":
    r = main()
    for c in r["checks"]: print(("PASS " if c["passed"] else "FAIL "), c["theorem"])
    print(r["status"], r["n_passed"], "/", r["n_checks"], r["receipt_sha256"][:16])
