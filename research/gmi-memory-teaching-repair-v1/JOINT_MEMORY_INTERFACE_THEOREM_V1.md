# Joint memory interfaces and controlled lesions

This is an application of CSR-1/2, finite query reconstruction, and explicit
machine semantics. It repairs the inference from independently assigned resource
numbers to a causal four-memory partition. It introduces no universal ontology.

## MTR-1: sufficient state and an exact lower bound

Fix nonempty finite histories H, finite queries Q, and required outputs f(h,q).
The entire information about h available at service is an encoded state e(h);
the decoder also receives q and a fixed program. Exact adequacy means
d(e(h),q)=f(h,q) for every promised pair. Consequently, if two histories have
different response vectors, their states differ. Conversely a table of response
vectors constructs an adequate encoder and decoder. The minimum state alphabet
is the number N of distinct vectors, requiring ceil(log2 N) fixed data bits.
This does not price the encoder, decoder, acquisition, workspace, or service.

For H={0,1}^t and coordinate queries, N=2^t: exact semantic data and a raw bit
record both grow as t. Distinct functional descriptions need not have distinct
growth rates. Under a correlated promise, N and the sufficient encoding change.
Roles can share physical state; they are not automatically separate components.

## MTR-2: an executable joint representation

The new witness uses H={0,1}^2 and queries x, y, x XOR y.
The raw image stores (x,y,x XOR y) and three two-token load/emit programs.
The compact image stores (x,y); its third program loads both slots, XORs, emits.
Both are adequate by direct evaluation of all four histories.

The eight-token ISA is L0,L1,L2,XOR,EMIT,EMIT0,EMIT1,NOP.
An image contains a two-bit data-length field, three three-bit program lengths,
three bits per token, and its data bits. Lengths and operations are validated;
there is no trailing payload. Raw and compact images use 32 and 37 bits.
Their data fields use three and two bits, respectively. Compression of data
therefore does not imply compression of code plus data.

A common evaluator reservation B and its installation cost are supplied and
charged equally. These are explicit abstract machine reservations, not measured
Python memory. Setup reads both history bits, computes the extra raw XOR when
needed, and writes the complete image: 35 versus 39 core operations.
Installation also checks each encoded bit and token; these additional 38 versus
45 validation operations are included, giving 73 versus 84 in the full ledger.
At one token-operation per executed instruction, serving each query once costs
6 versus 8. Input/query selection, program counter, stack, and output storage
are named separately in the workspace ledger. The lifetime event vector also
charges runtime installation/release, image/runtime bit-time retention, image
release, and clearing the reserved controller bits at each service. They are not erased by calling
the stack alone “working memory.” No minimum over all encodings is claimed.

## MTR-3: interface conditions for a lesion contrast

A service call initializes a fresh controller and uses only its supplied image.
A data lesion zeroes a chosen physical slot. A code lesion replaces the third
program by a valid load-first-slot/emit program. Neither silently alters an
abstract capability label. A sham performs an exact image round trip.
Restoration reloads the saved complete image and initializes the same controller.

For queries 0 and 1, replacing only program 2 preserves outputs AND instruction
traces: their selected programs and accessed data are identical. Induction over
the selected instruction sequence proves this. It does not preserve total image
size. In contrast, zeroing shared slot 0 can alter queries 0 and 2 together.
Thus independence is proved from this interface; shared state refutes an
unqualified modular-independence inference.

A snapshot reads and writes every image bit and retains a full additional image.
Each lesion or restoration reads the old and writes the resulting complete
image. The separate six-epoch schedule records intact, sham, code lesion, restore,
shared-slot lesion, and restore. Each edit also pays validation; each service
pays controller reset. Snapshot reads, bit-time retention and release, both
restorations, and every arm's service are included. Restoration is not free.
The saved image is experiment state and is unavailable to the service decoder. Fresh service controller state is reset equally in every arm.

Over the full promise, an EMIT0 substitute for query 2 is wrong on two histories.
Over the correlated promise {(0,0),(1,1)}, it is adequate. Lesion interpretation
therefore depends on the declared task and promise, not the component's name.
A direct EMIT0 instruction also shows that clearing operand-stack capacity alone
need not prevent all serving; some controller state still exists.

## MTR-4: what the contrast warrants

Enumerating all finite inputs verifies this registered machine and its surgical
image edits. Equality under sham and restore is a positive control. A changed
output under a lesion establishes a dependence within this executable model.
It is not a biological dissociation, an independently executed learner campaign,
a growth law for all memory, or evidence that real systems implement this code.
A same-query trace comparison does not license equality of acquisition,
retention, intervention, or whole-lifetime costs.

Independent tests compare decoded truth tables with direct Boolean functions,
exercise shared-slot and correlated-promise countercases, and check exact
serialized representations. The preserved PR597 scripts are not rerun.
