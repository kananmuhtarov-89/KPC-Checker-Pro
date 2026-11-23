from pathlib import Path
from ocr_engine import extract_image

EXPECTED=[f'{n:05d}' for n in list(range(33788,33798))+list(range(33995,34001))+list(range(34054,34057))]

def test_two_original_problematic_images():
    for filename in ('small.png','large.png'):
        result=extract_image((Path(__file__).parent/'fixtures'/filename).read_bytes())
        assert result['numbers']==EXPECTED, (filename,result)
        assert result['warnings']==[]
        assert result['blank_cells']==1
