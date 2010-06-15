# Test the modules in the utils/ subpackage

import unittest

from qel import iso8601

def tostr(dt):
    date = iso8601.parse(dt)
    return iso8601.tostring(date)

class TestISO8601(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(tostr('1998'), '1998-01-01T00:00Z')
        self.assertEqual(tostr('1998-06'), '1998-06-01T00:00Z')
        self.assertEqual(tostr('1998-06-13'), '1998-06-13T00:00Z')
        self.assertEqual(tostr('1998-06-13T14:12Z'), '1998-06-13T14:12Z')
        self.assertEqual(tostr('1998-06-13T14:12:30Z'), '1998-06-13T14:12:30Z')
        self.assertEqual(tostr('1998-06-13T14:12:30.2Z'), '1998-06-13T14:12:30Z')

if __name__ == "__main__":
    unittest.main()
