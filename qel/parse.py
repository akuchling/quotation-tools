"""
qel.parse -- Parse a document in the QEL DTD,
             converting it to a list of Quotation objects.
"""

import io, codecs, sys, string, re
from xml.dom import pulldom

from qel import QEL_NS, RDF_NS
from qel import quotation

__all__ = ['ParseError', 'parse']

class ParseError (Exception):
    pass

def _split_type(S):
    """(str): [str]

    Given a string containing comma-separated types, return a list of the types.
    """
    if S is None:
        return None
    return [typ.strip() for typ in S.split(',')]

def simplify(text_list, trim_ends = True):
    "Apply various simplifications to a list of Text instances"
    # Merge consecutive Text objects
    for i in range(1, len(text_list)):
        t1 = text_list[i-1]
        t2 = text_list[i]
        if isinstance(t1, quotation.Text) and isinstance(t2, quotation.Text):
            t2.text = t1.text + t2.text
            text_list[i-1] = None
            i += 1

    # Remove Nones
    text_list = [obj for obj in text_list if obj is not None]

    # Translate all whitespace to spaces, and condense runs of whitespace
    # down to a single space.
    for i in range(len(text_list)):
        t = text_list[i]
        if isinstance(t, quotation.Text):
            text_list[i] = quotation.Text(re.sub('\s+', ' ', t.text))
        elif t.is_break() or t.is_preformatted():
            continue
        else:
            t.children = simplify(t.children, trim_ends=False)

    # Remove redundant whitespace between chunks.
    for i in range(len(text_list)-2, -1, -1):
        left, right = text_list[i:i+2]
        if (left.is_break() or right.is_break() or
            left.is_preformatted() or right.is_preformatted()):
            continue
        if (left.endswith(' ') and right.startswith(' ')):
            if left.is_plain():
                if len(right) > 1:
                    text_list[i+1] = right = right.lstrip()
            elif right.is_plain():
                if len(left) > 1:
                    text_list[i] = left = left.rstrip()
            else:
                # Both chunks are something formatted.  This is likely to
                # be an error, so we'll insert a Text chunk between them.
                text_list[i] = left = left.rstrip()
                text_list[i+1] = right = right.lstrip()
                text_list.insert( i+1, quotation.Text(' '))

    # Remove leading whitespace from the first Text instance,
    # and trailing whitespace from the last one.
    changed = True
    while trim_ends and len(text_list) and changed:
        changed = False
        first = text_list[0]
        if not (first.is_preformatted() or first.is_break()):
            text_list[0] = first = first.lstrip()
            if len(first) == 0:
                del text_list[0]
                changed = True

    changed = True
    while trim_ends and len(text_list) and changed:
        changed = False
        last = text_list[-1]
        if not (last.is_preformatted() or last.is_break() ):
            text_list[-1] = last = last.rstrip()
            if len(last) == 0:
                del text_list[-1]
                changed = True

    if text_list and trim_ends:
        assert not text_list[0].startswith(' ')

    return text_list

def _ignore_text (stream):
    """_ignore_text(DOMStream) : (str,Node)
    Discard text, until an element is encountered.
    """
    while 1:
        token, node = next(stream)
        if token in [pulldom.START_ELEMENT, pulldom.END_ELEMENT,
                     pulldom.END_DOCUMENT]:
            return token, node

def _collect_text (stream, end_tag):
    """_collect_text(DOMStream, str) : string
    Accumulate the plain text up until the specified end tag.
    """
    text = ""
    while 1:
        token, node = next(stream)
        if token == pulldom.CHARACTERS:
            text += node.nodeValue
        elif token == pulldom.END_ELEMENT:
            if node.tagName == end_tag:
                return text
            else:
                raise ParseError("Unexpected end tag: </%s>" % node.tagName)
        elif token == pulldom.START_ELEMENT:
            raise ParseError("Unexpected start tag: <%s>" % node.tagName)

horiz_tags = {}
for klass in (quotation.Abbreviation, quotation.Acronym,
              quotation.CitedText, quotation.CodeFormattedText,
              quotation.EmphasizedText, quotation.ForeignText,
              quotation.PreformattedText,
              quotation.QuotedText):
    horiz_tags[ klass.xml_tag ] = klass

def _process_text (nodelist, do_simplify=True):
    L = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            L.append(quotation.Text(node.nodeValue))
        elif node.nodeType == node.ELEMENT_NODE:
            name = node.tagName
            if name in horiz_tags:
                klass = horiz_tags[name]
                inst = klass()
                do_s = not isinstance(inst, quotation.PreformattedText)
                inst.children = _process_text(node.childNodes, do_s)
                L.append(inst)
            elif name == 'br':
                L.append(quotation.Break())
            else:
                raise ParseError("Unexpected element: <%s>" % name)
        else:
            # Skip comments, PIs, and other junk
            pass

    if do_simplify:
        L = simplify(L)
    return L

def _make_para (node):
    assert node.tagName == 'p', "Paragraph tag expected"
    return _process_text(node.childNodes)

def _parse_quotation (stream, token, node):
    while 1:
        #print token, node
        if token == pulldom.START_ELEMENT and node.tagName == 'quotation':
            break
        elif token == pulldom.END_ELEMENT and node.tagName == 'quotations':
            return None

        try:
            token, node = next(stream)
        except StopIteration:
            return None

    stream.expandNode(node)

    qt = quotation.Quotation()
    qt.id = node.getAttributeNS(None, 'id') or None
    qt.date = node.getAttributeNS(None, 'date') or None
    qt.type = node.getAttributeNS(None, 'type') or None
    if qt.type is not None:
        qt.type = _split_type(qt.type)

    for c in node.childNodes:
        if c.nodeType == c.ELEMENT_NODE:
            name = c.tagName
            if name == 'p':
                qt.text.append(_make_para(c))

            elif name == 'author':
                qt.author = a = quotation.Author()
                a.type = c.getAttributeNS(None, 'type') or None
                if a.type is not None:
                    a.type = _split_type(a.type)
                a.uri = c.getAttributeNS(RDF_NS, 'resource') or None
                a.text = _process_text(c.childNodes)

            elif name == 'source':
                qt.source = s = quotation.Source()
                s.type = c.getAttributeNS(None, 'type') or None
                if s.type is not None:
                    s.type = _split_type(s.type)
                s.uri = c.getAttributeNS(RDF_NS, 'resource') or None
                s.text = _process_text(c.childNodes)

            elif name == 'note':
                for c2 in c.childNodes:
                    if (c2.nodeType == c2.ELEMENT_NODE):
                        qt.note.append(_make_para(c2))

    return qt


def parse(input):
    """Parse 'input' as a QEL file, returning a QuotationCollection
    object.  'input' can be either a file object or a string.  If
    'input' is a file object, it is not closed when parsing is
    complete."""

    coll = quotation.Collection()
    stream = pulldom.parse(input)

    # Scan for top-level 'quotations' element
    while 1:
        token, node = next(stream)
        if (token == pulldom.START_ELEMENT and
            node.tagName == 'quotations'):
            break

    # Parse the headers
    while 1:
        token, node = _ignore_text(stream)
        if token != pulldom.START_ELEMENT:
            break
        else:
            if node.tagName in ['title', 'editor',
                                'description', 'copyright']:
                text = _collect_text(stream, node.tagName)
                setattr(coll, node.tagName, text)

            elif node.tagName == 'license':
                coll.license = []
                while 1:
                    token, node = _ignore_text(stream)
                    if token == pulldom.START_ELEMENT and node.tagName == 'p':
                        #print repr(node)
                        #print node.__dict__
                        #print stream.pulldom.firstEvent
                        stream.expandNode(node)
                        coll.license.append(_make_para(node))
                    else:
                        break

            else:
                break

    # Parse a quotation
    while 1:
        qt = _parse_quotation(stream, token, node)
        if qt is None:
            break
        coll.append(qt)
        token, node = next(stream)

    return coll
