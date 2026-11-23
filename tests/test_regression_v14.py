from pathlib import Path
from ocr_engine import extract_image

FIXTURES=Path(__file__).parent/'fixtures'

def test_skewed_three_pairs():
    r=extract_image((FIXTURES/'skewed_3pairs.png').read_bytes())
    assert r['numbers']==['42528','53860','53734','53789','53976','53861','53902','53630','53788','53904','53815','53631','53787']
    assert r['blank_cells']==2 and not r['warnings']

def test_four_pairs_original():
    expected=['33788','33789','33790','33791','33792','33793','33794','33795','33796','33797','33995','33996','33997','33998','33999','34000','34054','34055','34056']
    for f in ('small.png','large.png'):
        r=extract_image((FIXTURES/f).read_bytes())
        assert r['numbers']==expected and not r['warnings']
