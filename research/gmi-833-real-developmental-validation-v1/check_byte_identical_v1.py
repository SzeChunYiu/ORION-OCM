"""Byte-compare two files; exit non-zero with a diagnostic if they differ.

Used by CI to assert a committed receipt is reproduced byte-for-byte.
Usage: python3 -I -B check_byte_identical_v1.py <committed> <regenerated>
"""
import sys


def main():
    a, b = sys.argv[1], sys.argv[2]
    with open(a, "rb") as f:
        x = f.read()
    with open(b, "rb") as f:
        y = f.read()
    if x == y:
        print("byte-identical: %s == %s (%d bytes)" % (a, b, len(x)))
        return
    sys.stderr.write("RECEIPT_NOT_REPRODUCED: %s (%d bytes) != %s (%d bytes)\n"
                     % (a, len(x), b, len(y)))
    for i in range(min(len(x), len(y))):
        if x[i] != y[i]:
            lo = max(0, i - 60)
            sys.stderr.write("first difference at byte %d\n" % i)
            sys.stderr.write("  committed:   %r\n" % x[lo:i + 60])
            sys.stderr.write("  regenerated: %r\n" % y[lo:i + 60])
            break
    sys.exit(1)


if __name__ == "__main__":
    main()
