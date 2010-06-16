# Test the modules in the utils/ subpackage

import unittest

from qel import iso8601

def tostr(dt):
    date = iso8601.parse(dt)
    return iso8601.tostring(date)

class TestISO8601(unittest.TestCase):
    def test_errors(self):
        self.assertRaises(ValueError, tostr, 'bogus')
        self.assertRaises(ValueError, tostr, '1998extrajunk')
        self.assertRaises(ValueError, tostr, '1998-06-32')

    def test_timezone(self):
        self.assertRaises(ValueError, iso8601.parse_timezone, '05:00')
        self.assertRaises(ValueError, iso8601.parse_timezone, '+05:00extra')
        self.assertRaises(ValueError, iso8601.parse_timezone, '+05:75extra')

        self.assertEqual(iso8601.parse_timezone('Z'), 0)
        self.assertEqual(iso8601.parse_timezone('-05:00'), 5*60*60)
        self.assertEqual(iso8601.parse_timezone('-0500'), 5*60*60)
        self.assertEqual(iso8601.parse_timezone('+02:30'), -(2*60*60 + 30*60))

    def test_basic(self):
        self.assertEqual(tostr('1998'), '1998-01-01T00:00Z')
        self.assertEqual(tostr('1998-06'), '1998-06-01T00:00Z')
        self.assertEqual(tostr('1998-06-13'), '1998-06-13T00:00Z')
        self.assertEqual(tostr('1998-06-13T14:12Z'), '1998-06-13T14:12Z')
        self.assertEqual(tostr('1998-06-13T14:12:30Z'), '1998-06-13T14:12:30Z')
        self.assertEqual(tostr('1998-06-13T14:12:30.2Z'), '1998-06-13T14:12:30Z')
        # Test a Julian date
        self.assertEqual(tostr('1998-188'), '1998-07-07T00:00Z')

    def test_tostring(self):
        dt = iso8601.parse('1998-06-13T14:12Z')
        self.assertEqual(iso8601.tostring(dt), '1998-06-13T14:12Z')
        self.assertEqual(iso8601.tostring(dt, 'Z'), '1998-06-13T14:12Z')
        self.assertEqual(iso8601.tostring(dt, '-05:00'), '1998-06-13T09:12-05:00')

if __name__ == "__main__":
    unittest.main()
