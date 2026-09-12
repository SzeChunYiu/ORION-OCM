import itertools
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
RECEIPT=json.loads((HERE/"GMI_TARGET_INFORMATION_EXACT_RECEIPT_V1.json").read_text())


def test_fixed_null_uniform_success_bound():
    for k in range(1,9):
        worlds=list(itertools.product((0,1),repeat=k))
        guess=(0,)*k
        success=sum(w==guess for w in worlds)/len(worlds)
        assert success==2**(-k)


def test_split_information_exact_iff_all_bits_covered():
    cells=possible=impossible=0
    for k in range(1,9):
        for r in range(k+1):
            for d in range(k-r+1):
                cells+=1;cls=2**(k-r-d);exact=cls==1
                possible+=int(exact);impossible+=int(not exact)
                assert exact==(r+d==k)
    rec=RECEIPT["cases"]["split_information"]
    assert (cells,possible,impossible)==(rec["cells"],rec["exact_possible"],rec["exact_impossible"])


def test_query_and_development_complete_reconstruction_counts_match_receipt():
    qc=dc=split=0
    for k in range(1,9):
        for w in itertools.product((0,1),repeat=k):
            qc+=1;dc+=1
            for r in range(k+1):
                assert tuple(w[:r])+tuple(w[r:])==w
                split+=1
    assert qc==RECEIPT["cases"]["query_complete"]["world_checks"]
    assert dc==RECEIPT["cases"]["development_complete"]["world_checks"]
    assert split==RECEIPT["cases"]["all_prefix_suffix_splits"]["reconstruction_checks"]
