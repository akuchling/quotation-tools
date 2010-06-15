# Test suite for the Quotation class

import unittest
from qel import quotation 

class QuotationTest(unittest.TestCase):
    "Test of the Quotation class"
    def setUp(self):
	self.qt = quotation.Quotation()

    def tearDown(self):
	del self.qt

    def test_xmlconv(self):
	"Conversion to XML"

	# Empty quotation
	self.assertEquals(self.qt.as_xml(),
			  "  <quotation>\n  </quotation>\n")
	self.assertEquals(self.qt.as_xml("UTF-8"),
			  "  <quotation>\n  </quotation>\n")

	# Add an id and a date
	self.qt.id = "idval" ; self.qt.date = "2000-01-01"
	self.qt.type = ['funny', 'silly']
	self.assertEquals(self.qt.as_xml(),
		       '  <quotation id="idval" date="2000-01-01" type="funny,silly">\n'
		       '  </quotation>\n')
	# Test quoting
	self.qt.id = "&<>" ; self.qt.date = "&<>"
	self.qt.type = None
	self.assertEquals(self.qt.as_xml(),
		       '  <quotation id="&amp;&lt;&gt;" date="&amp;&lt;&gt;">\n'
		       '  </quotation>\n')

	# Test minimal quotatation with 1 paragraph
	self.qt.id = self.qt.date = None
	self.qt.text = [ [quotation.Text('para1')] ]
	self.assertEquals(self.qt.as_xml(),
                           """  <quotation>
    <p>
      para1
    </p>
  </quotation>
""")
	self.assertEquals(self.qt.as_text(),
			  """para1\n""")
        # Test a break
        self.qt.id = self.qt.date = None
        self.qt.text = [ [quotation.Text('line1'), quotation.Break(),
                          quotation.Text('line2')] ]
        self.assertEquals(self.qt.as_xml(),
                           """  <quotation>
    <p>
      line1
      <br />
      line2
    </p>
  </quotation>
""")
        self.assertEquals(self.qt.as_text(),
                       """line1\nline2\n""")

        # Test simple text with 2 paragraphs
        self.qt.id = self.qt.date = None
        self.qt.text = [ [quotation.Text('para1')],
                         [quotation.Text('para2')] ]
        self.assertEquals(self.qt.as_xml(),
                       """  <quotation>
    <p>
      para1
    </p>
    <p>
      para2
    </p>
  </quotation>
""")
        self.assertEquals(self.qt.as_text(),
                       """    para1\n    para2\n""")

        self.qt.author = quotation.Author()
        self.qt.author.text = [quotation.Text('author')]
        self.qt.source = quotation.Source()
        self.qt.source.text = [quotation.CitedText('source')]
        self.qt.note   = [ [quotation.Text('note')] ]
        self.qt.text = [ [quotation.EmphasizedText('1')],
                         [quotation.Text('para2')] ]
        def fix_ws (S):
            return ' '.join(S.split())
        self.assertEquals(fix_ws(self.qt.as_xml()),
                       fix_ws("""  <quotation>
    <p>
      <em>1</em>
    </p>
    <p>
      para2
    </p>
    <author>author</author>
    <source><cite>source</cite></source>
    <note>
      <p>
        note
      </p>
    </note>
  </quotation>
"""))
        self.assertEquals(self.qt.as_text(include_note=1),
                           """    *1*
    para2
      -- author, _source_

note
""")
                             
    def test_text(self):
        "Text class and its subclasses"

        t = quotation.Text('content')
        self.assertEquals(str(t), 'content')
        self.assertEquals(t.as_text(), 'content')
        self.assertEquals(t.as_html(), 'content')
        self.assertEquals(t.as_xml(), 'content')

    def test_text_encoding(self):
        t = quotation.Text(u'Montr\xe9al')
        self.assertEquals(t.as_xml("UTF-8"), 'Montr\xc3\xa9al')
        self.assertEquals(t.as_xml("Latin-1"), 'Montr\xe9al')

    def test_text_quoting(self):
        # Test handling of quoting
        t = quotation.Text('&<>')
        self.assertEquals(t.as_text(), '&<>')
        self.assertEquals(t.as_html(), '&amp;&lt;&gt;')
        self.assertEquals(t.as_xml(), '&amp;&lt;&gt;')

    def test_text_addition(self):
        # Test addition of strings
        t = quotation.Text('&<>')
        t=t+"abc"
        self.assertEquals(t.as_text(), '&<>abc')

    def test_text_subclasses(self):
        # Text subclasses (just the HTML and text forms)
        for klass, text, html in [
            (quotation.Acronym, 'body', '<acronym>body</acronym>'),
            (quotation.CitedText, '_body_', '<cite>body</cite>'),
            ]:
            t = klass('body')
            self.assertEquals(t.as_text(), text)
            self.assertEquals(t.as_html(), html)            
            
if __name__ == "__main__":
    unittest.main()
