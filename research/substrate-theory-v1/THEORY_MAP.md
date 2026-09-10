# Theory Map v1 — dependencies between cognitive mechanics

Nodes are mechanics; edges are "requires". (P) = parent that already owns the mechanism (assimilate, don't rebuild). Status: ● operative / ◐ partial / ○ absent.

```
 ecology
   │  viability gate ◐  (learnability: pairwise-disjoint motifs; recall-ALL admission law)
   │  (P: value-of-history non-derivability check; SYNTH 5.1 recall-constrained MDL)
   ▼
 mining ◐  fragment extraction from history
   │  score function ●support-rank → SWAP to post-application utility (P: Stitch/Babble, SYNTH 2.2)
   │  candidate generation (P: anti-unification w/ warrants, SYNTH 2.2b)
   ▼
 admission ●  recall-ALL law: admitted ⟺ library recovers all motifs
   │  sequential stopping (P: Wald SPRT, SYNTH 8.2); e-graph normal-form gate (P: egg, SYNTH 3.1)
   ▼
 serving ○  ← THE critical path
   │  learned router I/V over library (P: contextual bandits EXP4/Thompson + Bao steering;
   │  P: ACT-R U=PG−C, ARCH 1.1); supervised by amortised-return ledger (RL 1.2)
   │  requires: Z feature map, delayed ecological reward, cost-charged regret
   ▼
 execution ●  φ units, β fallback; divergence-triggered β (P: DreamerV3, RL 2.3)
   ▼
 verification ●  exact independent checker; restart discipline; normal forms
   │  CEGIS adversarial input selection (P: Solar-Lezama; ARCH 4.1)
   ▼
 receipts ●  → ledger C (charging semantics corrected: #353/#359)
   │  failure classes ○ (ResidualKind dead code → wire; + economic-harm class)
   │  physical cost vector ● (P: DATABASE_PARENT_SUFFICIENT lesson)
   ▼
 consolidation ○  ← second critical path
   │  wake-sleep re-mining (P: DreamCoder, ARCH 4.2); retirement/excision (P: Soar utility
   │  problem, ARCH 1.3); capital recycling market (RL 6.3); replay (P: generative replay RL 5.3)
   ▼
 development ◐  amortisation crossing (M1C #360/#361 in flight)
   │  closed form (P: materialized-view economics + cracking, SYNTH 6.1/6.2)
   ▼
 RSI ○  generation ledger: cost-to-verified-improvement slope (parentless — ours alone)
   │  active experiment selection (P: CEGIS Ψ-guided, ARCH 4.1; EIG probes SYNTH 8.1)
   │  typed repair constraints (P: Popper/LFF, ARCH 4.3); Ψ-δ reflection (P: Reflexion, ARCH 4.6)
   ▼
 governance ● (cuts across admission, adoption, ecology)
      authority lattice A + scope S.epoch + certificate κ; E-signed adoption;
      shadow→canary rollout (P: SPIBB, HCOPE/doubly-robust gating, ARCH §c); DGM self-tampering lesson
```

## Critical paths

1. **Serving path** (ecology → mining-score → admission → **learned router** → execution → receipts): closes levels 3→4 of the ladder. Everything except the router is ●/◐.
2. **Consolidation path** (receipts → retirement/wake-sleep → library quality → serving quality): closes library saturation; feeds back into path 1.
3. **RSI path** (failures → typed diagnosis → priced experiments → governed repair → generation ledger): closes level 5; depends on the failure-class wiring (F-1) and on paths 1–2 providing the substrate being improved.

## Non-edges (explicitly NOT dependencies)

- Learned serving does NOT require learned representation first — router features can start as the existing fragment-support vector (RL 1.2 lowest-cost entry).
- RSI does NOT depend on scale arms; the generation ledger is meaningful at current scale (ARCH #7 honest terminal: AMORTIZER_ONLY).
- Development does NOT require consolidation; M2-P1 showed the search prior without any retirement loop. Consolidation extends the regime, not gates entry.
