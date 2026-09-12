"""RV-377-195: end-to-end frontier sign of two physical carriers against the strongest classical parent on ONE
registered obligation, using ONLY published measured constants (quoted with sources in
GMI_PHYSICAL_CONSTANTS_FROM_PUBLISHED_MEASUREMENTS_RV_377_195.md). Pure arithmetic + Monte Carlo; no hardware is
measured by this programme. Every interval below is propagated from the quoted error bars / quoted mode ranges.

Registered obligation O_B (protected K5 V7, lane C_FEATURE_LEARNING, nonlinear_signal 0.6, receipts under
microscopes/results/k5_bh_v7/): the FIXED_FEATURE realization = linear readout on (1, x0, x1), x uniform on [-1,1]^2,
world label 1[x0 + 0.4 x1 + 1.5 x0 x1 >= 0]; 1600 protected queries; admissible iff test error <= 0.18. The
linear-Bayes floor is 0.0911 (protected measured 0.0907), so the hardware may add at most
EPS_HW = 0.18 - 0.0911 = 0.0889 error per query (counting every hardware flip as an error: conservative).
"""
import json, sys, numpy as np
from math import comb

rng = np.random.default_rng(377195)
N = 400_000
X = rng.uniform(-1, 1, size=(N, 2))
label = (X[:, 0] + 0.4 * X[:, 1] + 1.5 * X[:, 0] * X[:, 1] >= 0)
# the FIXED_FEATURE realization is the logistic readout on (1, x0, x1) trained on the world (K5 core); reproduce it
# by logistic regression on an independent training draw, then normalise so that max |w_1|, |w_2| = 1 (W_MAX)
from sklearn.linear_model import LogisticRegression
Xtr = rng.uniform(-1, 1, size=(20_000, 2)); ytr = (Xtr[:, 0] + 0.4 * Xtr[:, 1] + 1.5 * Xtr[:, 0] * Xtr[:, 1] >= 0).astype(int)
lr = LogisticRegression(C=1e6, max_iter=5000).fit(Xtr, ytr)
w = np.array([lr.intercept_[0], lr.coef_[0, 0], lr.coef_[0, 1]]); w = w / np.max(np.abs(w[1:]))
score = w[0] + w[1] * X[:, 0] + w[2] * X[:, 1]   # fixed-feature decision statistic (parent decision = sign(score))
floor = float(np.mean((score >= 0) != label))    # should reproduce the analytic linear-Bayes floor ~0.091
EPS_HW = 0.18 - floor

# ---------------------------------------------------------------- classical parent (Horowitz ISSCC 2014, 45 nm)
E_INT8_MULT, E_INT8_ADD = 0.2e-12, 0.03e-12       # J
E_INSTR_OVERHEAD = 70e-12                          # J per instruction on a general-purpose core (Horowitz)
E_SRAM32_READ = 5e-12                              # J per 32-bit SRAM read (8 KB)
D_REG = 3                                          # MACs per query in the registered obligation
parent_lo = D_REG * (E_INT8_MULT + E_INT8_ADD)     # fixed-function datapath, weights register-resident
parent_hi = parent_lo + D_REG * E_INSTR_OVERHEAD   # three instructions on a general-purpose in-order core

# ---------------------------------------------------------------- candidate 1: PCM crossbar (IBM HERMES, Le Gallo 2023)
CORES = 64
E_MVM_1PHASE, E_MVM_4PHASE = 0.86e-6, 3.38e-6      # J per all-core MVM command (Table I, MVM at max utilization)
E_core_1p, E_core_4p = E_MVM_1PHASE / CORES, E_MVM_4PHASE / CORES   # one core executes the 3-MAC obligation
E_mac_1p, E_mac_4p = 1 / 9.76e12 * 2, 1 / 2.48e12 * 2               # J per MAC (2 ops per MAC) from TOPS/W
W_MAX = 1.0
Y_MAX = float(np.abs(w[0]) + np.abs(w[1]) + np.abs(w[2]))   # maximum |score| over the input square
# weight precision "between 3-bit and 4-bit" (TDP): uniform quantization std = W_MAX * 2^-b / sqrt(12)
sig_w = {"4bit": W_MAX * 2 ** -4 / np.sqrt(12), "3bit": W_MAX * 2 ** -3 / np.sqrt(12)}
# additive output noise: 0 (measured-precision reading) .. 10 % of max output range (the paper's own hardware-aware
# training noise model, quoted as the pessimistic corner)
sig_out = {"none": 0.0, "10pct": 0.10 * Y_MAX}


def crossbar_flip(sw, so, draws=64):
    flips = []
    for _ in range(draws):
        dw = rng.normal(0, sw, size=3)   # absolute weight programming error, std relative to W_MAX = 1
        s_hw = (w[0] + dw[0]) + (w[1] + dw[1]) * X[:, 0] + (w[2] + dw[2]) * X[:, 1] + rng.normal(0, so, size=N)
        flips.append(np.mean((s_hw >= 0) != (score >= 0)))
    return float(np.mean(flips))


cross = {}
for wk, sw in sig_w.items():
    for ok, so in sig_out.items():
        cross[f"{wk}|{ok}"] = crossbar_flip(sw, so)
cross_flip_lo, cross_flip_hi = min(cross.values()), max(cross.values())
# drift (Joshi 2020: nu ~ 0.06): after time t the conductances scale by (t/t0)^-nu; with global drift compensation the
# scale is removed and the residual is the device-to-device spread of nu; charged as a re-programming/calibration
# burden per obligation lifetime, not per query. Not needed for the sign; recorded.
E_cross_lo, E_cross_hi = E_core_1p, E_core_4p
# native saving vs parent MAC (register-resident weights) at d = 3
S_lo, S_hi = D_REG * (E_INT8_MULT + E_INT8_ADD - E_mac_4p), D_REG * (E_INT8_MULT + E_INT8_ADD - E_mac_1p)
# crossover dimension d* where the digital parent's per-MAC cost (with SRAM weight fetch, or register-resident)
# exceeds the per-command crossbar cost
e_dig_fetch = E_INT8_MULT + E_INT8_ADD + E_SRAM32_READ / 4
d_star = {"1phase|sram_fetch": E_core_1p / e_dig_fetch, "4phase|sram_fetch": E_core_4p / e_dig_fetch,
          "1phase|register": E_core_1p / (E_INT8_MULT + E_INT8_ADD), "4phase|register": E_core_4p / (E_INT8_MULT + E_INT8_ADD)}

# ---------------------------------------------------------------- candidate 2: superconducting processor (Willow)
eps_1q = (0.00035, 0.00029); eps_cz = (0.0033, 0.0018); eps_ro = (0.0077, 0.0021)   # mean ± (spec sheet)
T1 = (68.0, 13.0); t_cycle = 1.1e-6                                                     # us, s
idle_c = 0.9e-2                                                                          # Table S4 (per qubit per cycle)
N_1Q, N_CZ, N_Q = 6, 2, 2   # minimal 2-qubit linear-form circuit: 6 single-qubit gates, 2 CZ, 2 qubits idle, 1 readout


def p_fail(sign):
    e1 = eps_1q[0] + sign * eps_1q[1]; ecz = eps_cz[0] + sign * eps_cz[1]; ero = eps_ro[0] + sign * eps_ro[1]
    idle = idle_c * T1[0] / (T1[0] - sign * T1[1])
    return N_1Q * max(e1, 0) + N_CZ * ecz + N_Q * idle + ero


pf_lo, pf_hi = p_fail(-1), p_fail(+1)
z = np.abs(score) / Y_MAX                           # single-shot bias: P(correct) = 1/2 + z(1-2 p_fail)/2


def majority_error(gamma, m):
    p = 0.5 + gamma
    return sum(comb(m, k) * p ** k * (1 - p) ** (m - k) for k in range(0, m // 2 + 1))


def quantum_flip(pf, m):
    g = z * (1 - 2 * pf) / 2
    # integrate majority error over the input distribution (binning gamma for speed)
    bins = np.linspace(0, 0.5, 501); idx = np.clip(np.digitize(g, bins) - 1, 0, 499)
    errs = np.array([majority_error(0.5 * (bins[i] + bins[i + 1]), m) for i in range(500)])
    return float(np.mean(errs[idx]))


def min_shots(pf):
    m = 1
    while True:
        f = quantum_flip(pf, m)
        if f <= EPS_HW:
            return m, f
        m += 2
        if m > 20001:
            return None, f


m_lo, f_lo = min_shots(pf_lo); m_hi, f_hi = min_shots(pf_hi)
single_shot_flip = {"p_fail_lo": quantum_flip(pf_lo, 1), "p_fail_hi": quantum_flip(pf_hi, 1)}
P_SYS = 26e3                                        # W (Sycamore SI: 26 kW total, independent of workload)
E_shot_floor = P_SYS * t_cycle                      # J, physical cycle floor
E_shot_meas = 5e6 / 1e6                             # J, Sycamore SI: ~5e6 J for 1M samples
E_q_lo, E_q_hi = m_lo * E_shot_floor, m_hi * E_shot_meas
# NC-2 sufficiency bound for reference (gamma = mean single-shot bias): m >= ln(1/delta) / (2 gamma^2)
gamma_mean = float(np.mean(z) * (1 - 2 * pf_lo) / 2)
nc2_m = float(np.log(1 / EPS_HW) / (2 * gamma_mean ** 2))

out = {
    "revival_id": "RV-377-195",
    "obligation": "K5 V7 C_FEATURE_LEARNING s=0.6 FIXED_FEATURE readout: sign(w0 + w1 x0 + w2 x1) on 1600 protected queries, error<=0.18",
    "fixed_readout_w_normalised": w.tolist(), "y_max": Y_MAX,
    "linear_bayes_floor_mc": floor, "eps_hw_budget": EPS_HW,
    "parent_J_per_query": {"lo_fixed_function": parent_lo, "hi_general_core": parent_hi},
    "crossbar": {"E_J_per_query": {"lo_1phase": E_cross_lo, "hi_4phase": E_cross_hi},
                 "E_per_MAC_J": {"1phase": E_mac_1p, "4phase": E_mac_4p, "digital_int8": E_INT8_MULT + E_INT8_ADD},
                 "native_saving_S_J_at_d3": {"lo": S_lo, "hi": S_hi},
                 "flip_rate": cross, "flip_lo": cross_flip_lo, "flip_hi": cross_flip_hi,
                 "admissible": {k: (v <= EPS_HW) for k, v in cross.items()},
                 "burden_ratio_candidate_over_parent": {"most_favourable": E_cross_lo / parent_hi, "least_favourable": E_cross_hi / parent_lo},
                 "sign": "PARENT" if E_cross_lo > parent_hi else "UNRESOLVED",
                 "crossover_dimension_d_star_MACs": d_star},
    "quantum": {"p_fail_per_shot": {"lo": pf_lo, "hi": pf_hi}, "single_shot_flip": single_shot_flip,
                "min_shots_for_eps_hw": {"lo": m_lo, "hi": m_hi, "flip_at_min": {"lo": f_lo, "hi": f_hi}},
                "nc2_sufficiency_shots_at_mean_gamma": nc2_m, "gamma_mean": gamma_mean,
                "E_shot_J": {"floor_26kW_x_1.1us": E_shot_floor, "measured_sycamore": E_shot_meas},
                "E_J_per_query": {"lo": E_q_lo, "hi": E_q_hi},
                "native_saving_S_J": 0.0,
                "burden_ratio_candidate_over_parent": {"most_favourable": E_q_lo / parent_hi, "least_favourable": E_q_hi / parent_lo},
                "sign": "PARENT" if E_q_lo > parent_hi else "UNRESOLVED"},
    "terminal": "PHYSICAL_FRONTIER_SIGN_FROM_PUBLISHED_CONSTANTS__NOT_MEASURED_IN_PROGRAMME",
    "mc_draws": N,
}
json.dump(out, open(sys.argv[1], "w"), indent=1, sort_keys=True)
print(json.dumps(out, indent=1, sort_keys=True))
