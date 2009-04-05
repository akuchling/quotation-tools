# Test suite for the Quotation class

from sancho.unittest import TestScenario, parse_args, run_scenarios
from qel import quotation 

class QuotationTest(TestScenario):
        "Test of the Quotation class"
        def setup(self):
            self.qt = quotation.Quotation()
            
        def shutdown(self):
            del self.qt

        def check_xmlconv(self):
            "Conversion to XML"
            
            # Empty quotation
            self.test_val( 'self.qt.as_xml()',
                           "  <quotation>\n  </quotation>\n")
            self.test_val( 'self.qt.as_xml("UTF-8")',
                           "  <quotation>\n  </quotation>\n")

            # Add an id and a date
            self.qt.id = "idval" ; self.qt.date = "2000-01-01"
	    self.qt.type = ['funny', 'silly']
            self.test_val( 'self.qt.as_xml()',
			   '  <quotation id="idval" date="2000-01-01" type="funny,silly">\n'
			   '  </quotation>\n')
            # Test quoting
            self.qt.id = "&<>" ; self.qt.date = "&<>"
	    self.qt.type = None
            self.test_val( 'self.qt.as_xml()',
                           '  <quotation id="&amp;&lt;&gt;" date="&amp;&lt;&gt;">\n'
			   '  </quotation>\n')

            # Test minimal quotatation with 1 paragraph
            self.qt.id = self.qt.date = None
            self.qt.text = [ [quotation.Text('para1')] ]
            self.test_val( 'self.qt.as_xml()',
                           """  <quotation>
    <p>
      para1
    </p>
  </quotation>
""")
            self.test_val( 'self.qt.as_text()',
                           """para1\n""")

            # Test a break
            self.qt.id = self.qt.date = None
            self.qt.text = [ [quotation.Text('line1'), quotation.Break(),
			      quotation.Text('line2')] ]
            self.test_val( 'self.qt.as_xml()',
                           """  <quotation>
    <p>
      line1
      <br />
      line2
    </p>
  </quotation>
""")
            self.test_val( 'self.qt.as_text()',
                           """line1\nline2\n""")

            # Test simple text with 2 paragraphs
            self.qt.id = self.qt.date = None
            self.qt.text = [ [quotation.Text('para1')],
                             [quotation.Text('para2')] ]
            self.test_val( 'self.qt.as_xml()',
                           """  <quotation>
    <p>
      para1
    </p>
    <p>
      para2
    </p>
  </quotation>
""")
            self.test_val( 'self.qt.as_text()',
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
            self.test_val( 'fix_ws(self.qt.as_xml())',
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
            self.test_val( 'self.qt.as_text(include_note=1)',
                           """    *1*
    para2
      -- author, _source_

note
""")
                             
        def check_text(self):
            "Text class and its subclasses"

            t = quotation.Text('content')
            self.test_val('str(t)', 'content')
            self.test_val('t.as_text()', 'content')
            self.test_val('t.as_html()', 'content')
            self.test_val('t.as_xml()', 'content')

            t = quotation.Text(u'Montr\xe9al')
            self.test_val('t.as_xml("UTF-8")', 'Montr\xc3\xa9al')
            self.test_val('t.as_xml("Latin-1")', 'Montr\xe9al')
	    
            # Test handling of quoting
            t = quotation.Text('&<>')
            self.test_val('t.as_text()', '&<>')
            self.test_val('t.as_html()', '&amp;&lt;&gt;')
            self.test_val('t.as_xml()', '&amp;&lt;&gt;')

            # Test addition of strings
            self.test_stmt('t=t+"abc"')
            t=t+"abc"
            self.test_val('t.as_text()', '&<>abc')

            # Text subclasses (just the HTML and text forms)
            for klass, text, html in [
                (quotation.Acronym, 'body', '<acronym>body</acronym>'),
                (quotation.CitedText, '_body_', '<cite>body</cite>'),
                ]:
                t = klass('body')
                self.test_val('t.as_text()', text)
                self.test_val('t.as_html()', html)
                
if __name__ == "__main__":
    (scenarios, options) = parse_args()
    run_scenarios (scenarios, options)
            
            
