
# Test suite for qel.scripts module

import unittest
from qel import scripts
from qel.quotation import Collection, Quotation

class GenerateIdsTest(unittest.TestCase):
    def test_empty(self):
        # Should run silently and not raise an exception.
        qtcoll = Collection()
        self.assertFalse(scripts.generate_ids(qtcoll))

    def test_ids_added(self):
        qt1 = Quotation()
        qt2 = Quotation()
        qtcoll = Collection()
        qtcoll.extend([qt1, qt2])
        self.assertTrue(scripts.generate_ids(qtcoll))
        self.assertEqual(qt1.id, 'q1')
        self.assertEqual(qt2.id, 'q2')

    def test_maximum_id_found(self):
        qt1 = Quotation()
        qt1.id = 'q45'
        qt2 = Quotation()
        qtcoll = Collection()
        qtcoll.extend([qt1, qt2])
        self.assertTrue(scripts.generate_ids(qtcoll))
        self.assertEqual(qt1.id, 'q45')
        self.assertEqual(qt2.id, 'q46')


class MergeTests(unittest.TestCase):
    def test_empty(self):
        # Should run silently and not raise an exception.
        qtcoll = Collection()
        newcoll = scripts.merge(qtcoll, qtcoll)
        self.assertTrue(len(newcoll) == 0)

    def test_loose_collision(self):
        c1 = Collection()
        c2 = Collection()
        q1 = Quotation()
        q1.id = 'q1'
        q2 = Quotation()
        q2.id = 'q1'
        c1.append(q1)
        c2.append(q2)

        newcoll = scripts.merge(c1, c2, strict=False)
        self.assertEqual(len(newcoll), 2)
        self.assertFalse(q1.id == q2.id)

    def test_strict_collision(self):
        c1 = Collection()
        q1 = Quotation()
        q1.id = 'q1'
        c1.append(q1)

        self.assertRaises(scripts.DuplicateIDException,
                          scripts.merge, c1, c1, strict=True)

if __name__ == '__main__':
    unittest.main()