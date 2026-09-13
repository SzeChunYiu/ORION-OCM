"""P1a: derive parity-n class costs by formula; validate only against n=3.

No n>3 candidate is compiled or measured here. The formulas are derived from the
registered flat opcode contract and are checked against the three registered
n=3 facts (XOR 11/call, shared-sum net 39/call with 4 unaccounted, lookup
17/call). Measurement of n=4,5,6 happens only after this registration merges.
"""

def unpack(n):            # LOAD_FAST x, UNPACK_SEQUENCE, n * STORE_FAST
    return n + 2

def xor_chain(n):         # unpack + n loads + (n-1) XOR ops + RETURN
    return unpack(n) + n + (n - 1) + 1, 0

def shared_sum_net(n):    # unpack + shared form + n threshold units + output
    shared_form = 2 * n                      # n loads + (n-1) adds + store
    units = 6 * n                            # int(s>=k): global,load,const,cmp,call,store
    output = 2 * n + 4                       # global, r loads, r-1 ops, const, cmp, call, return
    return unpack(n) + shared_form + units + output, n + 1

def lookup_table(n):      # unpack + index arithmetic + const table + subscript
    index = 3 * (n - 1) + 1 + (n - 1)        # shifts for n-1 inputs, last load, n-1 ORs
    return unpack(n) + index + 1 + 1 + 1, 0

def delegating_sum(n):    # sum(x) & 1 -- independent of n
    return 6, 1

FAMILIES = {"WRITTEN_XOR_CHAIN": xor_chain,
            "WRITTEN_SHARED_SUM_NET": shared_sum_net,
            "WRITTEN_LOOKUP_TABLE": lookup_table,
            "DELEGATING_SUM_AND_MASK": delegating_sum}

REGISTERED_N3 = {"WRITTEN_XOR_CHAIN": (11, 0), "WRITTEN_SHARED_SUM_NET": (39, 4),
                 "WRITTEN_LOOKUP_TABLE": (17, 0), "DELEGATING_SUM_AND_MASK": (6, 1)}

print("=== formula validation against the registered n=3 facts")
ok = True
for name, fn in FAMILIES.items():
    got, want = fn(3), REGISTERED_N3[name]
    good = got == want
    ok &= good
    print("  %-24s formula=%-9s registered=%-9s %s" % (name, got, want, "OK" if good else "*** MISMATCH ***"))
print("  all formulas reproduce n=3:", ok)

print("\n=== PREDICTIONS (per full domain sweep, 2^n inputs), n = 4, 5, 6")
print("  %-24s %-4s %-10s %-10s %s" % ("family", "n", "opcodes", "unacc.", "per-call"))
pred = {}
for n in (4, 5, 6):
    sweep = 2 ** n
    for name, fn in FAMILIES.items():
        per_call, unacc_per_call = fn(n)
        pred[(name, n)] = (sweep * per_call, sweep * unacc_per_call)
        print("  %-24s %-4d %-10d %-10d %d" % (name, n, sweep * per_call, sweep * unacc_per_call, per_call))

print("\n=== PREDICTED ORDER (product order: <= in both, < in one)")
def dominates(a, b):
    return a[0] <= b[0] and a[1] <= b[1] and (a[0] < b[0] or a[1] < b[1])
for n in (3, 4, 5, 6):
    sweep = 2 ** n
    rows = {k: (sweep * FAMILIES[k](n)[0], sweep * FAMILIES[k](n)[1]) for k in FAMILIES}
    winner = [k for k in rows if not any(dominates(rows[j], rows[k]) for j in rows if j != k)]
    print("  n=%d undominated: %s" % (n, sorted(winner)))

print("\n=== REGISTERED PREDICTIONS, stated so they can fail")
print("  P1a-1 XOR chain per-call cost is 3n+2 and carries zero unaccounted calls.")
print("  P1a-2 shared-sum threshold net per-call cost is 11n+6 with n+1 unaccounted calls,")
print("        so it is dominated by the XOR chain for every n in {4,5,6}.")
print("  P1a-3 lookup table per-call cost is 5n+2, NOT 2^n: a constant table is one")
print("        LOAD_CONST, so this coordinate does not charge table size at all.")
print("  P1a-4 no crossover occurs in {4,5,6}: the written XOR chain stays undominated,")
print("        and sum(x)&1 stays incomparable at a constant 6 opcodes per call.")
print("  P1a-5 the neural family never wins in this coordinate at any n in {4,5,6};")
print("        a neural win therefore requires a different task (P1b), not a larger n.")
