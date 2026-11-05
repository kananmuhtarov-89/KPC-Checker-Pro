from kpc_core import normalize, parse_text, compare
import pytest

@pytest.mark.parametrize('raw,expected', [
    ('KPC018569','18569'), ('KPC 018569','18569'), ('18569','18569'),
    ('KPÇ00023','00023'), ('00000123','00123'), ('0','00000'),
])
def test_normalize(raw, expected):
    assert normalize(raw) == expected

@pytest.mark.parametrize('raw', ['123456', 'KPC0123456', '12a34', 'KPC12-34', '2026/11/05'])
def test_reject(raw):
    with pytest.raises(ValueError): normalize(raw)

def test_match_reordered():
    lists = {'A':parse_text('A','KPC039617, 039623, 39617'),
             'B':parse_text('B','39617 39617 39623'),
             'C':parse_text('C','39623\n39617\n39617')}
    r = compare(lists)
    assert r['match'] and r['duplicates']['A']['39617'] == 2

def test_duplicate_mismatch():
    lists = {x:parse_text(x, txt) for x,txt in [('A','12,12'),('B','12,13'),('C','12,12')]}
    r=compare(lists)
    assert not r['match']
    assert r['differences'] == [
        {'KPC':'00012','A':2,'B':1,'C':2},
        {'KPC':'00013','A':0,'B':1,'C':0}]

def test_invalid_blocks_match():
    lists={x:parse_text(x,txt) for x,txt in [('A','12345,HELLO'),('B','12345'),('C','12345')]}
    r=compare(lists)
    assert not r['ready'] and not r['match'] and r['invalid']['A'] == ['HELLO']

def test_missing_list_blocks_match():
    lists={x:parse_text(x,txt) for x,txt in [('A','12345'),('B','12345'),('C','')]}
    assert not compare(lists)['match']
