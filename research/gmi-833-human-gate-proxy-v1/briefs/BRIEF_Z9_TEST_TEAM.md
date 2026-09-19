# BRIEF Z9-T — environment/test team (fresh-session model proxy)

You are the environment/test team in a blind prediction protocol. A separate prediction team, which you will never communicate with, claims to have a theory that predicts — from an environment's registered descriptors alone — which class of machine an exhaustive search will choose and at what price the choice flips. YOU DO NOT KNOW THAT THEORY AND MUST NOT TRY TO GUESS IT. Your job is to construct a held-out batch of environments from the family below that is diverse, non-trivial, and independently chosen — the kind of batch a sceptical experimentalist would build to give a theory every chance to fail.

## Rules (binding)

1. Read no file at all. Everything you need is in this brief. Do not run code that enumerates or simulates candidate machines; you may use scratch arithmetic to check that your rationals are well-formed.
2. Your batch is recorded verbatim and will never be edited.
3. Do not include an environment you consider degenerate unless you deliberately mark it as a control.

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

## What to produce

Write EXACTLY ONE file, at the path given to you in the task message (the path is of the form /tmp/claude-501/revive-gates/z9/batch_<b>/ENVIRONMENTS.json), containing a JSON object:

{
  "schema": "GMI_833_Z9_ENVIRONMENT_BATCH_V1",
  "batch": <b>,
  "author_role": "TEST_TEAM",
  "rationale": "<3-6 sentences: how you chose the batch and why it is a fair, hard held-out test>",
  "environments": [
    {"env_id": "B<b>-E01", "L": 3, "target_0": "CUR", "target_1": "PREV", "p": "2/5", "eta": "1", "lambdas": ["1/10", "1/2"], "note": "<why this one>"},
    ...
  ]
}

Requirements: between 10 and 14 environments; use at least 8 distinct menu targets across the batch including at least two of PREV2, XOR2, AND2, OR2, MAJ3; use both L=3 and L=4; use at least four distinct p values including one of "0" or "1"; choose lambdas spanning what you yourself would consider cheap and expensive state; every rational as a reduced fraction string. Then reply with a short summary and the exact block:

VERDICT_BLOCK_BEGIN
row: Z9-2 | verdict: SATISFIED | reason: <one sentence on how the batch was constructed independently>
model_self_report: <the model identifier you believe you are running as, or UNKNOWN>
VERDICT_BLOCK_END
