import unittest
from kpc_core import normalize, parse_text, compare

class KpcAuditTest(unittest.TestCase):
    def test_normalize(self):
        for s in ['KPC018569','18569','KPC 018569','KPÇ 018569','00018569']:
            self.assertEqual(normalize(s),'18569')
    def test_reject(self):
        for s in ['123456','KPC123456','12A34','39671a','']:
            with self.assertRaises(ValueError): normalize(s)
    def test_two_sides(self):
        inputs={'A':parse_text('A','39617,39618'),'C':parse_text('C','KPC039618,KPC039617')}
        r=compare(inputs)
        self.assertTrue(r['match']);self.assertEqual(r['names'],['A','C'])
    def test_three_sides(self):
        x={k:parse_text(k,'39617 39618 39619') for k in 'ABC'}
        self.assertTrue(compare(x)['match'])
    def test_multiplicity(self):
        x={'A':parse_text('A','39617,39617'),'B':parse_text('B','39617,39618')}
        r=compare(x)
        self.assertFalse(r['match']);self.assertEqual(len(r['differences']),2)
    def test_invalid_blocks(self):
        x={'A':parse_text('A','39617,abc'),'B':parse_text('B','39617')}
        self.assertFalse(compare(x)['match'])
    def test_too_few(self):
        with self.assertRaises(ValueError):compare({'A':parse_text('A','39617')})
    def test_markdown(self):
        x=parse_text('A','| 39617 |\n| ----- |\n| 39618 |')
        self.assertEqual(x.codes,['39617','39618'])

if __name__=='__main__': unittest.main()
