"""
qel.quotations -- Contains the classes representing the contents of
                  a QEL-format quotation.
"""

__revision__ = "$Id: quotation.py,v 1.28 2004/12/26 16:24:28 akuchling Exp $"

import string, time, re

import textwrap
from xml.sax.saxutils import escape
from qel import iso8601

def format_paragraph_as_text (paragraph, indent,
                              use_rst=False, use_wiki=False):
    "Format a list of Text instances into a plain text string"

    if len(paragraph) == 0:
        return ""
    output = ""
    for t in paragraph:
        if use_rst:
            output += t.as_rst()
        elif use_wiki:
            output += t.as_wiki()
        else:
            output += t.as_text()
    if not use_wiki:
        wrap = textwrap.TextWrapper(79, initial_indent=indent)
        wrap.wordsep_re = re.compile(r'(\s+)')
        lines = wrap.wrap(output)
        output = '\n'.join(lines) + '\n'
    return output

def format_partial_paragraph_as_xml(paragraph, indent, encoding):
    """Generate pretty-printed XML output for a portion of a paragraph.
    Neither Break nor PreformattedText instances should be in the
    'paragraph' list.
    """
    output = ""
    for t in paragraph:
        output += t.as_xml(encoding)
    wrap = textwrap.TextWrapper(70, initial_indent=indent)
    wrap.wordsep_re = re.compile(r'(\s+)')
    lines = wrap.wrap(output)
    output = '\n'.join(lines) + '\n'
    return output

def format_paragraph_as_xml(paragraph, indent, encoding):
    """Generate pretty-printed XML output for a paragraph.
    It will split the paragraph apart at Break and PreformattedText
    instances.
    """
    output = ""
    start = 0
    for j in range(len(paragraph)):
        t = paragraph[j]
        if isinstance(t, str):
            output += t.encode(encoding)

        elif (t.is_break() or t.is_preformatted()):
            output += format_partial_paragraph_as_xml(paragraph[start:j],
                                                      indent, encoding)
            start = j + 1
            if t.is_break(): output += indent
            output += t.as_xml(encoding) + '\n'

    output += format_partial_paragraph_as_xml(paragraph[start:], indent,
                                              encoding)
    return output


class Collection (list):
    """A collection of quotations.

    """
    def __init__ (self):
        self.title = None
        self.editor = None
        self.description = None
        self.copyright = None
        self.license = None

    def as_xml (self, encoding="UTF-8"):
        from qel import QEL_HEADER, QEL_FOOTER
        s = QEL_HEADER % encoding
        if self.title:
            s += '  <title>%s</title>\n' % escape(self.title).encode(encoding)
        if self.editor:
            s += '  <editor>%s</editor>\n' % escape(self.editor).encode(encoding)
        if self.description:
            s += '  <description>%s</description>\n' % escape(self.description).encode(encoding)
        if self.copyright:
            s += '  <copyright>%s</copyright>\n' % escape(self.copyright).encode(encoding)
        if self.license:
            s += '  <license>'
            for t in self.license:
                if isinstance(t, str):
                    s += escape(t).encode(encoding)
                else:
                    s += t.as_xml(encoding)
            s += '\n  </license>\n'
        for qt in self:
            s += qt.as_xml(encoding)
        s += QEL_FOOTER
        return s

class Author:
    def __init__ (self):
        self.text = None
        self.type = None
        self.uri = None

    def as_text (self):
        v = ""
        for t in self.text:
            if isinstance(v, str):
                v += t
            else:
                v += t.as_text()
        return v

    def as_rst (self):
        v = ""
        for t in self.text:
            if isinstance(v, str):
                v += t
            else:
                v += t.as_rst()
        return v

    def as_wiki (self):
        v = ""
        for t in self.text:
            if isinstance(v, str):
                v += t
            else:
                v += t.as_wiki()
        return v

    def as_xml (self, encoding='UTF-8'):
        s = '<author'
        if self.type:
            s += ' type="%s"' % self.type.encode(encoding)
        if self.uri:
            s += ' rdf:resource="%s"' % self.uri.encode(encoding)
        s += '>'
        for t in self.text:
            s += t.as_xml(encoding)
        s += '</author>'
        return s


class _CollectionAttribute:
    def __init__ (self):
        self.text = None
        self.type = None
        self.uri = None

    def as_text (self):
        v = ""
        for t in self.text:
            v += t.as_text()
        return v

    def as_rst (self):
        v = ""
        for t in self.text:
            v += t.as_rst()
        return v

    def as_wiki (self):
        v = ""
        for t in self.text:
            v += t.as_wiki()
        return v

    def as_html (self):
        v = "<p class='%s'>" % self.tag_name
        for t in self.text:
            t = t.as_html()
            if isinstance(t, str):
                t = t.encode('iso-8859-1')
            v += t
        return v + '\n'

    def as_xml (self, encoding='UTF-8'):
        s = '<%s' % self.tag_name
        if self.type:
            typ = ','.join(self.type)
            s += ' type="%s"' % typ.encode(encoding)
        if self.uri:
            s += ' rdf:resource="%s"' % self.uri.encode(encoding)
        s += '>'
        for t in self.text:
            s += t.as_xml(encoding)
        s += '</%s>' % self.tag_name
        return s

class Source (_CollectionAttribute):
    tag_name = 'source'

class Author (_CollectionAttribute):
    tag_name = 'author'


class Quotation:
    """Encapsulates a single quotation.

    Attributes:
    id -- a string containing this quotation's ID
    date -- the date of this quotation (another string, in ISO-8601 format)
    type -- list of strings, containing various categories for this quotation

    text -- A list of paragraphs, of minimum length 1.
            A paragraph is just a list of Text() instances, or
            subclasses of Text(), containing the text of the quotation.
    source -- A Source instance (Optional)
    author -- An Author instance (Optional)
    note -- A list of paragraphs, as for the .text attribute.  (Optional)

    Methods:
    as_fortune() -- return the quotation formatted for fortune
    as_html()    -- return an HTML version of the quotation
    as_text()    -- return a plain text version of the quotation
    as_xml()     -- return the QEL version of the quotation
    """

    def __init__(self):
        self.id = self.date = None
        self.text = []
        self.author = self.source = None
        self.note = []
        self.type = None

    def __len__(self):
        "Return the number of bytes in the text of this quotation"
        size = 0
        for p in self.text:
            for t in p:
                size += len(t)
        return size

    def as_text(self, include_date=0, include_note=0):
        """Convert instance into plain text, returning a string.
        If 'include_date' is true, the date will be included on the
        attribution line.  If 'include_note' is true, any notes will
        also be formatted and returned as part of the string.
        """

        # If there's more than one paragraph, each paragraph
        # will be indented by 4 spaces.  Single paragraphs
        # aren't indented at all.
        if len(self.text) > 1: indent = 4 * " "
        else: indent = ""

        output = ""
        for i in range(len(self.text)):
            paragraph = self.text[i]

            start = 0
            for j in range(len(paragraph)):
                t = paragraph[j]
                if (t.is_break() or t.is_preformatted()):
                    output += format_paragraph_as_text(paragraph[start:j],
                                                       indent)
                    output += t.as_text()
                    if t.is_preformatted():
                        output += '\n'
                    start = j + 1

            output += format_paragraph_as_text(paragraph[start:], indent)

        para = ""
        for i in ['author', 'source']:
            value = getattr(self, i)
            if value is not None:
                v = value.as_text()
                if para:
                    para += ', '
                    v = v[:1].lower() + v[1:]
                para += v

        # Add the date
        if include_date and self.date:
            date = iso8601.parse(self.date)
            para += ' ' + time.strftime('(%Y)', time.gmtime(date))

        if para:
            para = "-- " + para
            lines = textwrap.wrap(para, 75,
                                  initial_indent = 6*' ',
                                  subsequent_indent = 9*' ')
            para = '\n'.join(lines) + '\n'
            output += para

        if include_note and self.note:
            output += '\n'
            for paragraph in self.note:
                para = ""
                for t in paragraph:
                    para += t.as_text()
                lines = textwrap.wrap(para, 75)
                output += '\n'.join(lines) + '\n'

        return output


    def as_rst(self):
        """Convert instance into RestructuredText.
        """

        output = ""
        for i in range(len(self.text)):
            paragraph = self.text[i]

            start = 0
            for j in range(len(paragraph)):
                t = paragraph[j]
                if (t.is_break() or t.is_preformatted()):
                    output += format_paragraph_as_text(paragraph[start:j],
                                                       "",
                                                       use_rst=True)
                    output += t.as_rst()
                    if t.is_preformatted():
                        output += '\n'
                    start = j + 1

            output += format_paragraph_as_text(paragraph[start:], "",
                                               use_rst=True)
        return output


    def as_wiki(self):
        """Convert instance into Wiki markup.
        """

        output = ""
        for i in range(len(self.text)):
            paragraph = self.text[i]

            start = 0
            for j in range(len(paragraph)):
                t = paragraph[j]
                if (t.is_break() or t.is_preformatted()):
                    output += format_paragraph_as_text(paragraph[start:j],
                                                       "",
                                                       use_wiki=True)
                    output += t.as_rst()
                    if t.is_preformatted():
                        output += '\n'
                    start = j + 1

            output += '*' + format_paragraph_as_text(paragraph[start:], "",
                                               use_wiki=True) + '\n'

        para = ""
        for i in ['author', 'source']:
            value = getattr(self, i)
            if value is not None:
                v = value.as_wiki()
                if i == 'author':
                    v = '[[en:%s|%s]]' % (v, v)
                if para:
                    para += ', '
                    v = v[:1].lower() + v[1:]
                para += v

        if para:
            para = "**" + para
            lines = textwrap.wrap(para, 75)
            para = '\n'.join(lines) + '\n'
            output = output.rstrip() + '\n' + para

        return output


    def as_fortune(self):
        """Convert instance into plain text and append a '%' character
        as required by the fortune(6) program, returning a string.
        """
        return self.as_text() + '%'

    def as_html(self):
        """Convert instance into a straightforward HTML format.

        This function's output can't be customized in any way.
        If you want different formatting, implement it yourself,
        either by using a Quotation instance or by applying some
        XML-specific transformation to the QEL representation.
        """

        output = ""
        id = ""
        if self.id:
            id = "id='%s'" % str(self.id)
        for paragraph in self.text:
            output += "<p class='quotation' %s>" % id
            id = ""
            for t in paragraph:
                output += t.as_html()
            output += "</p>\n"

        for i in ['author', 'source']:
            value = getattr(self, i)
            if value is not None:
                output += value.as_html()
        return output

    def as_xml(self, encoding='UTF-8'):
        """Convert instance into QEL, pretty-printing it.
        """
        id = date = typ = ""
        if self.id is not None:
            id = ' id="%s"' % escape(self.id.encode(encoding))
        if self.date is not None:
            date = ' date="%s"' % escape(self.date.encode(encoding))
        if self.type is not None:
            typ = ','.join(self.type)
            typ = ' type="%s"' % escape(typ.encode(encoding))

        output = "  <quotation%s%s%s>\n" % (id, date, typ)
        for paragraph in self.text:
            output += "    <p>\n"
            output += format_paragraph_as_xml(paragraph, 6*' ', encoding)
            output += "    </p>\n"

        for i in ['author', 'source']:
            value = getattr(self, i)
            if value is not None:
                output += (6*' ') + value.as_xml(encoding) + '\n'


        if self.note:
            output += "    <note>\n"
            for paragraph in self.note:
                output += "      <p>\n"
                output += format_paragraph_as_xml(paragraph, 8*' ', encoding)
                output += "      </p>\n"
            output += "    </note>\n"

        output += "  </quotation>\n"
        return output

# Text and Markup and its subclasses are used to hold chunks of text;
# instances know how to display themselves as plain text or as HTML.

class Text:
    """A chunk of plain text."""

    def __init__(self, text=""):
        if isinstance(text, str):
            text = str(text)
        self.text = text

    def __str__(self):
        return self.as_text()

    def __len__ (self):
        return len(self.text)

    def __repr__ (self):
        s = repr(self.as_text())
        if len(s) > 25: s = s[0:15] + '...' + s[-8:]
        return '<%s: %s>' % (self.__class__.__name__, s)

    def as_text(self, encoding='iso-8859-1'):
        return self.text.encode(encoding)

    as_rst = as_wiki = as_text

    def as_html (self):
        return escape(self.text).encode('iso-8859-1')

    def as_xml (self, encoding='UTF-8'):
        return escape(self.text).encode(encoding)

    def is_break(self):        return 0
    def is_plain(self):        return 1
    def is_preformatted(self): return 0

    # We need to allow adding a string to Text instances.
    def __add__(self, val):
        if isinstance(val, str):
            val = str(val, 'iso-8859-1')
        newtext = self.text + val
        return Text(newtext)

    def startswith (self, S):
        return self.text.startswith(S)
    def endswith (self, S):
        return self.text.endswith(S)
    def lstrip (self):
        return Text(self.text.lstrip())
    def rstrip (self):
        return Text(self.text.rstrip())


class Markup (object):
    """A chunk of marked-up text, the base class for all markup classes.

    Instance attributes:
      .children : [ Text | Markup]
        List of children making up this chunk of text.
    """

    text_char = ""
    wiki_delim = ""
    xml_tag = html_tag = ""

    def __init__(self, text=None):
        self.children = []
        if text:
            self.children.append(Text(text))

    def __str__(self):
        return self.as_text()

    def __len__ (self):
        size = 0
        for c in self.children:
            size += len(c)
        return size

    def __repr__ (self):
        s = repr(self.as_text())
        if len(s) > 25: s = s[0:15] + '...' + s[-8:]
        return '<%s: %s>' % (self.__class__.__name__, s)

    def as_text (self, encoding='iso-8859-1'):
        text = ""
        for t in self.children:
            text += t.as_text(encoding)
        return self.text_char + text + self.text_char

    def as_rst (self, encoding='iso-8859-1'):
        text = ""
        for t in self.children:
            text += t.as_rst(encoding)
        text = '`%s`' % text
        if self.xml_tag:
            text = ':%s:%s' % (self.xml_tag, text)
        return text

    def as_wiki (self, encoding='iso-8859-1'):
        text = ""
        for t in self.children:
            text += t.as_wiki(encoding)
        if text:
            if isinstance(self.wiki_delim, tuple):
                start, end = self.wiki_delim
            else:
                start = end = self.wiki_delim
            text = '%s%s%s' % (start, text, end)
        return text

    def as_html (self):
        text = ""
        for t in self.children:
            text += t.as_html()

        if self.html_tag:
            text = "<%s>%s</%s>" % (self.html_tag, text, self.html_tag)
        return text

    def as_xml (self, encoding='utf-8'):
        for t in self.children:
            text = t.as_xml(encoding)

        if self.xml_tag:
            text = "<%s>%s</%s>" % (self.xml_tag, text, self.xml_tag)
        return text

    def is_break(self):        return 0
    def is_plain(self):        return 1
    def is_preformatted(self): return 0

    def startswith (self, S):
        return self.children[0].startswith(S)
    def endswith (self, S):
        return self.children[-1].endswith(S)
    def lstrip (self):
        c2 = [ self.children[0].lstrip() ] + self.children[1:]
        inst = self.__class__()
        inst.children = c2
        return inst
    def rstrip (self):
        c2 = self.children[:-1] + [ self.children[-1].rstrip() ]
        inst = self.__class__()
        inst.children = c2
        return inst

class Abbreviation (Markup):
    text_char = ""
    wiki_delim = ""
    xml_tag = html_tag  = "abbr"

class Acronym (Markup):
    text_char = ""
    wiki_delim = ""
    xml_tag = html_tag = "acronym"

class CitedText (Markup):
    "Text inside <cite>...</cite>"

    text_char = "_"
    wiki_delim = ("''", "''")
    xml_tag = html_tag  = "cite"

    def is_plain(self):        return 0

class CodeFormattedText (Markup):
    "Text inside <code>...</code>"

    text_char = ""
    wiki_delim = ("<nowiki>", "</nowiki>")
    xml_tag = html_tag  = "code"

class EmphasizedText (Markup):
    "Text inside <em>...</em>"
    text_char = "*"
    wiki_delim = "''"
    xml_tag = html_tag  = "em"

    def is_plain(self):        return 0
    as_rst = Markup.as_text

class ForeignText (Markup):
    "Foreign words, from Latin or French or whatever."

    text_char = "_"
    wiki_delim = ("<i>", "</i>")
    html_tag  = "i"
    xml_tag = "foreign"

    def is_plain(self):        return 0

class PreformattedText (Markup):
    "Text inside <pre>...</pre>"

    text_char = ""
    xml_tag = html_tag  = "pre"
    wiki_delim = ("<nowiki>", "</nowiki>")

    def is_preformatted(self): return 1

    def as_text (self, encoding='iso-8859-1'):
        text = super(PreformattedText, self).as_text(encoding)
        text = text.strip()
        return text

    def as_rst (self, encoding='iso-8859-1'):
        text = super(PreformattedText, self).as_text(encoding)
        text = text.strip()
        text = '\n\n::\n'+ text.replace('\n', '\n    ') + '\n\n'
        return text


class QuotedText (Markup):
    text_char = '"'
    wiki_delim = '"'
    xml_tag = html_tag = 'q'

    def is_plain(self):        return 0


class Break (Markup):
    text = ""
    children = ()

    def __repr__(self):
        return '<%s>' % (self.__class__.__name__)

    def as_text(self): return ""
    as_rst = as_wiki = as_text

    def as_html(self): return "<br />"
    def as_xml(self, encoding):
        return "<br />"

    def is_break(self):        return 1
    def is_plain(self):        return 0
    def is_preformatted(self): return 0
