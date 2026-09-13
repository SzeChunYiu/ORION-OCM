# Compositional Language Parent Subtraction V1

Status: **PARENT BOUNDARY EXPLICIT**  
Date: 2026-09-12

## Parent-owned content

Grand GMI does not claim invention of compositionality, systematic recombination, emergent communication, lexicon/utterance tradeoffs or compositional neural representations.

Relevant parents include:

- classical linguistic/symbolic work on compositional semantics;
- coding and communication theory for finite-message distinguishability and variable resource tradeoffs;
- Chaabouni et al. (ACL 2020), showing that emergent languages can generalize to novel combinations while compositionality itself is not universally correlated with generalization, and reporting a transmission/learnability advantage for more compositional languages;
- Kharitonov and Baroni (BlackboxNLP 2020), giving explicit cases where noncompositional languages match or outperform compositional ones on acquisition/generalization;
- Galke, Ram and Raviv (Nature Communications 2024), finding systematic-learning/generalization advantages from more compositional language structure for humans and neural learners in their experimental regime;
- Riveland, Pouget and Driscoll (Nature Neuroscience 2026), explicitly framing compositional mechanisms as a continuum rather than a binary property.

## Grand-GMI residual

The tranche derives a **partition-lattice morphology law** from obligation-relative semantic factorization plus counted resources.

For every partition `pi` of semantic roles,

\[
A(\pi)=\sum_{B\in\pi}\prod_{i\in B} n_i,
\qquad L(\pi)=|\pi|,
\]

and under the declared scalar resource contract

\[
C_\pi=\lambda A(\pi)+cL(\pi).
\]

This yields:

1. exact holistic, partially compositional and fully compositional resource profiles;
2. exact phase boundaries among them;
3. the monotone-chunking theorem as transmission price rises relative to lexical price;
4. a precise productive-recombination guarantee for the block-separable lookup class.

The contribution is therefore not the statement “composition is good.” It is a falsifiable condition for **when and how much composition is resource-selected**, including regimes in which holism is optimal and intermediate chunking is the unique block-count phase.