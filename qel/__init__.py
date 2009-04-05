##     qel -- A package for parsing and manipulating QEL.
##     Copyright (C) 2001 A.M. Kuchling

##     This program is free software; you can redistribute it and/or modify
##     it under the terms of the GNU General Public License as published by
##     the Free Software Foundation; either version 2 of the License, or
##     (at your option) any later version.

##     This program is distributed in the hope that it will be useful,
##     but WITHOUT ANY WARRANTY; without even the implied warranty of
##     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##     GNU General Public License for more details.

##     You should have received a copy of the GNU General Public License
##     along with this program; if not, write to the Free Software
##     Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA


"""
qel -- A package for parsing and manipulating collections of quotations
       in Quotation Exchange Language (QEL) format.

Modules contained in the qel package:
    database -- Storing and indexing QEL files for fast access.
    parse -- Parsing a QEL file into a series of Quotation instances.
    quotations -- Contains the Quotation class, representing a single
                  quotation's contents, and other associated classes.

Constants:
QEL_HEADER -- The XML header to be written at the start of a QEL file.
QEL_FOOTER -- The footer to be written at the end of a QEL file (just
              a closing <quotation> tag, currently.
"""

# QEL package

__revision__ = "$Id: __init__.py,v 1.10 2002/10/02 12:26:11 akuchling Exp $"
__version__ = '0.0.5'

# XML and DTD declaration for QEL files

QEL_HEADER = """<?xml version="1.0" encoding="%s"?>
<?xml-stylesheet href="http://www.amk.ca/qel/qel.css"?>
<quotations
  xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
  xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#">
"""

# Footer of QEL files
QEL_FOOTER = "</quotations>\n"

# Namespaces
QEL_NS = "http://www.amk.ca/qel/"
RDF_NS = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
