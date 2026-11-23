from kpc_core import parse_text,compare

def test_300_codes_and_duplicate_preservation():
    vals=[f'{i:05d}' for i in range(10000,10300)]
    a=parse_text('A','\n'.join(vals))
    b=parse_text('B','\n'.join(reversed(vals)))
    assert len(a.codes)==300
    assert compare({'A':a,'B':b})['match']
    b=parse_text('B','\n'.join(vals[:-1]+[vals[0]]))
    assert not compare({'A':a,'B':b})['match']
