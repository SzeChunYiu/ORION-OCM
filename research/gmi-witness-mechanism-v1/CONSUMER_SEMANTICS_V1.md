# Consumer semantics of the recovered witness

The authoritative parent is the pinned VM implementation in
[vm.py](https://github.com/SzeChunYiu/ORION-OCM/blob/5378c2b7f91f8fbc567764a2ee0c5ff6e256e814/research/machine-intelligence-morphogenesis-v1/gmi_microscope/vm.py),
with primitive meanings in
[core.py](https://github.com/SzeChunYiu/ORION-OCM/blob/5378c2b7f91f8fbc567764a2ee0c5ff6e256e814/research/machine-intelligence-morphogenesis-v1/gmi_microscope/core.py).
These files are also available in the recovery packet's bound source archive.
This is an analysis of that program, not a new general equivalence theorem.

Let G be the original 14-node pruned genotype in CANDIDATES_V1.json and Z the
fixed zero-vector replacement. Consider native B0 execution from init through
any finite sequence of query(x), feedback(x,y), revoke(x), with four-bit
inputs and fixed-point targets, and no external intervention on internal
state or costs. The machine does not stop on a resource charge threshold.

**Claim.** G and Z return the same query values and abstention flags.
The named stores table0_s and evidence0_s agree, including entry order, at
every event boundary. This claim projects away the dense cell, replaced
vector representation, tape, genotype encoding and all resource charges.

Proof. At init both common stores are empty. G additionally allocates a dense
cell at value8 and represents its output as the string list ["dense0_w0"];
Z outputs the one-element value vector [Val(0)] because its input is 0 or16,
NEG is exact negation on these inputs and ReLU(-x)=0. The representations
differ; their one-bit INSERT keys both equal (0,). No GRAD, LINEAR, AFFINE or
other numeric dense-cell consumer occurs in either graph.

The only dense outgoing edges go to EVIDENCE port0 and insert1 port1.
EVIDENCE emits its store identifier without reading either input value.
feedback adds the actual four-bit x and target y directly to that store.
Therefore replacement does not change the evidence-store operation.

On each evaluate pass, both NEAREST nodes read the same pre-update table
when its ordered contents agree, so their fixed-point values agree.
MORPH_RULE emits1; VERIFY has no program bound and emits1. The ABSTAIN gates
therefore return the same nearest0 value. All forward nodes precede all
update nodes in both VMs. The two updates remain insert0 then insert1:
insert0 has depth2; insert1 depth3 in G and depth4 in Z. Thus tie-breaking
cannot reverse the updates. insert0 inserts the same four-bit key and target;
insert1 inserts the same one-bit zero key and pre-update nearest1 value.
Each operation removes existing copies of its own key before appending.
The complete ordered table is consequently equal after each update.

On revoke, both common stores undergo identical key-prefix filtering.
G also writes the dense cell's initial value, but no consumer reads its
number. Both machines replay the same ordered remaining evidence through
the same evaluate/update argument. There is no program or materialization
node in either graph. This proves preservation for each event and hence
for all finite event sequences in the declared model by induction.

The 11-context experiment checks all served traces and every captured
post-INSERT store state, providing finite regression evidence for the
source argument. It does not enumerate all event sequences. Representation
equivalence remains false: string references and Val objects, dense-cell
presence, tape and encoded graphs differ. Although this proof establishes
the common EVIDENCE **store contents**, it does not equate the incoming
EVIDENCE vector representations. Resource equality is explicitly false.

For the varying-key control V, the final NEG yields [Val(input_bit0)].
Its graph and order match Z except for that operation parameter. There is
no active dense gradient or tape consumer. Before the first memory
difference, its only behaviorally read difference is insert1's key.
Actual capture first diverges at the fourth INSERT operation (zero-based
index3), during the second feedback: Z uses (0,), V uses (1,).
The next served row (trace index2) changes from4 to3 at all 16 inputs.
These are native fixed-point integers, not normalized capabilities.

This establishes an effect of the changed key rule on this program's
behavior. V still passes the historical bar, so constant key (0,) is not
necessary for that admissibility criterion. No deletion of the whole
insert1 channel was tested, and no necessity claim for that channel follows.
Both variants use the retained KVSTORE/INSERT/NEAREST memory machinery.
The removed DENSE coefficient is unnecessary for G's observable behavior,
not proof that dense parameters are unnecessary in general.

The presence-based carrier label is therefore not invariant under the
declared query/store projection: G is labelled DENSE and Z is labelled
KVSTORE. This is a concrete representative dependence of that label, not
a claim that their full cost-bearing responses or raw graph encodings agree.
