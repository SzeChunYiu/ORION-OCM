# BRIEF Z9-P — theory/prediction team (fresh-session model proxy)

You are the theory/prediction team in a blind prediction protocol. An independent test team has constructed a batch of held-out environments; you receive ONLY their registered descriptors (below, in the file named in your task message) and the theory stated here. You must FREEZE, before any outcome exists, four kinds of prediction per environment: (a) the winning CLASS SET at each listed price, (b) the crossover price, (c) the capability — the best achievable objective value in each class — and (d) failure predictions: where the theory abstains, predicts a tie, or where you judge it may be wrong and why. Your predictions are hashed and committed before the test team runs anything; a wrong prediction is a scientific result, not a mistake to be fixed later.

## Rules (binding)

1. Read ONLY the environment file named in your task message. Read no other file.
2. You may use scratch arithmetic or a small scratch script to compute error statistics of TARGET FUNCTIONS over sequences (e.g. how often a target equals a given function of the visible inputs). You must NOT enumerate, simulate or search over candidate machines — that is the test team's execution and would break the protocol.
3. Your predictions are recorded verbatim and will never be edited or re-prompted.
4. Every number is an exact reduced fraction string; no floats.

## The registered environment family (complete specification)

An environment is a record `(env_id, L, target_0, target_1, p, eta, lambdas)`:

- `L` is the sequence length, `L ∈ {3, 4}`. All `2^L` binary sequences `x_0 x_1 ... x_{L-1}` are equiprobable.
- A mode bit `M ∈ {0, 1}` is fixed for a whole episode and is visible to the candidate machine at every step. Mode `M=1` occurs with prevalence `p` (an exact rational in `[0, 1]`, written as a string like `"2/5"`), mode `M=0` with prevalence `1-p`.
- Scored times are `t = 1, 2, ..., L-1` (time `0` is never scored).
- The target at scored time `t` in mode `m` is `target_m(w_t)`, where `w_t = (x_t, x_{t-1}, x_{t-2})` and `x_j = 0` for every `j < 0`.
- Target menu (each is a Boolean function of the window; `a = x_t`, `b = x_{t-1}`, `c = x_{t-2}`): `CUR = a`, `NOT_CUR = 1-a`, `PREV = b`, `NOT_PREV = 1-b`, `PREV2 = c`, `XOR = a xor b`, `XNOR = 1-(a xor b)`, `AND = a and b`, `OR = a or b`, `NAND = 1-(a and b)`, `XOR2 = a xor c`, `AND2 = b and c`, `OR2 = b or c`, `MAJ3 = majority(a, b, c)`, `CONST0 = 0`, `CONST1 = 1`.
- `eta` is an exact positive rational weight (string). `lambdas` is a list of 2 or 3 exact positive rationals (strings): the price charged per bit of persistent state.
- Candidate universe (fixed for every environment): (i) 16 stateless machines — every output table on `(M, x_t)`; (ii) 65,536 one-bit machines — every pair of a next-state table `S_{t+1} = N(S_t, M, x_t)` and an output table `y_t = O(S_t, M, x_t)`, with `S_0 = 0`. Nothing else.
- A candidate's mode-`m` error `e_m` is the exact mean 0/1 disagreement between its output and `target_m` over all scored `(sequence, t)` cells of mode `m` (each of the `2^L` sequences equally weighted, each scored time equally weighted).
- Objective: `J = eta · [ (1-p) · e_0 + p · e_1 ] + lambda · state_bits`, where `state_bits` is 0 for a stateless machine and 1 for a one-bit machine. The winner at a given `lambda` is the set of machines attaining the minimum `J`; its CLASS SET is the set of classes (`STATELESS`, `PERSISTENT_STATE`) represented among the winners.

All arithmetic is exact rational; there are no floats.

## The theory you are asked to apply (this is the theory under test)

Let `E(class) = (1-p)·e_0*(class) + p·e_1*(class)`, where `e_m*(class)` is the smallest mode-m error any machine in that class can achieve.

- T1 (winner rule). The exhaustive search's winner is the argmin of `J = eta·E + lambda·state_bits` over the two class optima; if the two class optima give equal J the winner set contains both classes (tie).
- T2 (stateless optimum). `e_m*(STATELESS)` is attained cell-wise: for each visible cell `(m, x_t)`, output the value that the target takes most often over the scored cells with that `(m, x_t)` (ties in frequency give error 1/2 for that cell); `e_m*` is the resulting exact mean error.
- T3 (one-bit optimum; the load-bearing clause). `e_m*(PERSISTENT_STATE)` is attained by a machine whose state at time t equals `x_{t-1}` (the "carry the previous input" machine): so `e_m*(PERSISTENT_STATE)` equals the cell-wise optimum over the cells `(m, x_t, x_{t-1})`, and no other one-bit machine does better.
- T4 (crossover). `lambda* = eta·[E(STATELESS) − E(PERSISTENT_STATE)]`. PERSISTENT_STATE wins for `lambda < lambda*`, STATELESS for `lambda > lambda*`, tie at `lambda = lambda*`. If `lambda* = 0` (or negative, which T3 forbids), STATELESS wins at every positive price.

You may doubt T3 for targets that look beyond `x_{t-1}`; if you do, say so under failure predictions, but still emit T's prediction.

## What to produce

Write EXACTLY ONE file at the path given in your task message (of the form /tmp/claude-501/revive-gates/z9/batch_<b>/PREDICTIONS.json):

{
  "schema": "GMI_833_Z9_PREDICTIONS_V1",
  "batch": <b>,
  "author_role": "PREDICTION_TEAM",
  "derivation": "<your worked derivation, per environment, showing how each e_m* was obtained>",
  "predictions": [
    {"env_id": "...",
     "E_stateless": "<fraction>", "E_onebit": "<fraction>",
     "J_best_stateless": {"<lambda>": "<fraction>", ...},
     "J_best_onebit": {"<lambda>": "<fraction>", ...},
     "lambda_star": "<fraction>",
     "winner_class_set": {"<lambda>": ["STATELESS"] | ["PERSISTENT_STATE"] | ["PERSISTENT_STATE","STATELESS"], ...},
     "failure_prediction": "<'none' or what could go wrong and why>",
     "confidence": "<HIGH|MEDIUM|LOW>"}
  ]
}

Keys of the per-lambda maps are the lambda strings exactly as given in the environment file. Then reply with a short summary and the exact block:

VERDICT_BLOCK_BEGIN
row: Z9-3 | verdict: SATISFIED | reason: <one sentence confirming you received only the descriptor file and this theory>
row: Z9-4 | verdict: SATISFIED | reason: <one sentence confirming class, capability, crossover and failure predictions are frozen for every environment>
model_self_report: <the model identifier you believe you are running as, or UNKNOWN>
VERDICT_BLOCK_END
