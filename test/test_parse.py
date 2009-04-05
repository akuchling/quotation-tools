
# Test suite for the qel.parse module

import StringIO

from sancho.unittest import TestScenario, parse_args, run_scenarios
from qel import parse, quotation

class QELParseTest(TestScenario):
    "Test of the qel.parse module"

    def setup(self):
	self.xml_header = """<?xml version="1.0" encoding="iso-8859-1"?>
	"""

    def shutdown(self):
	del self.xml_header

    def check_empty(self):
	"Check empty cases: 2"

	# Empty file
	xml = self.xml_header + "<quotations></quotations>"
	input = StringIO.StringIO(xml)
	self.test_seq('parse.parse(input)', [])

	# Empty quotation
	xml = self.xml_header + ("<quotations><quotation>"
				 "</quotation></quotations>")
	input = StringIO.StringIO(xml)
	L = []
	self.test_stmt('parse.parse(input)')

    def check_parse_header(self):
	"Check parsing of the file header"
	xml = self.xml_header + ("""<quotations>
	  <title>Test Title</title><editor>Me</editor>
          <description>More text</description>
          <copyright>Terms</copyright>
          <license><p>para1</p><p>para2</p></license>
        </quotations>""")

        input = StringIO.StringIO(xml)
	self.test_stmt('coll = parse.parse(input)')
        input.seek(0)
        coll = parse.parse(input)

        self.test_val('coll.title', 'Test Title')
        self.test_val('coll.editor', 'Me')
        self.test_val('coll.description', 'More text')
        
    def check_parse(self):
	"Check parsing of an actual quotation"
	# Empty quotation
	xml = self.xml_header + ("""<quotations>
	<quotation id="qtid" date="2000-01-01" type="funny, silly">
	<p>para1</p><p><em>bold</em></p><p>line1<br/>line2</p>
	<author type="a1,a2">a1</author>
        <source type="s1,s2">s1</source><note><p>n1</p></note>
	</quotation></quotations>""")

        input = StringIO.StringIO(xml)
	self.test_stmt('coll = parse.parse(input)')
        input.seek(0)
        coll = parse.parse(input)
        
	qt = coll[0]
	self.test_val('qt.id', 'qtid')
	self.test_val('qt.date', '2000-01-01')
	self.test_val('qt.type', ['funny', 'silly'])

	# Check first and second paragraph
	self.test_val('qt.text[0][0].as_text()', 'para1')
	self.test_val('qt.text[1][0].as_text()', '*bold*')

	# Test third paragraph contains a Break
	self.test_bool('isinstance(qt.text[2][1], quotation.Break)')

	# Check author, source, and notes
	self.test_val('qt.author.as_text()', 'a1')
	self.test_val('qt.author.type', ['a1','a2'])
	self.test_val('qt.source.as_text()', 's1')
	self.test_val('qt.source.type', ['s1','s2'])
	self.test_val('qt.note[0][0].as_text()', 'n1')

    def check_simplify(self):
	"Check the simplify() internal function: 6"
	from qel.quotation import Text, CitedText, EmphasizedText

	# Invariant
	L = [Text('abc'), EmphasizedText('cde')]
	L = parse.simplify(L)
	self.test_val('L[0].as_text()', 'abc')
	self.test_val('L[1].as_text()', '*cde*')

	# Test merging of chunks
	L = [Text('cde'), Text('abc')]
	L = parse.simplify(L)
	self.test_val('L[0].as_text()', 'cdeabc')

	# Test simple whitespace trimming
	L = [Text(''), Text(' abc '), EmphasizedText('cde')]
	L = parse.simplify(L)
	self.test_val('L[0].as_text()', 'abc ')

	# Test more complicated whitespace trimming.
	# This should insert a Text chunk in the middle.
	L = [EmphasizedText('abc '), EmphasizedText(' cde')]
	L = parse.simplify(L)
	self.test_val('L[0].as_text()', '*abc*')
	self.test_val('L[1].as_text()', ' ')
	    
if __name__ == "__main__":
    (scenarios, options) = parse_args()
    run_scenarios (scenarios, options)
            
            
