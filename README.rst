quotation-tools
===============

This is a Python package containing scripts for parsing and
maintaining quotation collections using the Quotation Exchange
Language, or QEL, format.  The scripts making up the toolkit are:

* **qtformat**: For converting QEL to various other formats (text,HTML,more)
* **qtgenerateids**:   Adds a unique ID to each quotation in a file.
* **qtgrep**: For searching through a collection
* **qtmerge**: For merging a number of QEL files
* **fortune2qel**: Reads a fortune(6) file and outputs QEL for as many
  quotations as possible.

The QEL home page is http://quotations.amk.ca/qel/ ; the latest
version of this software is available there.

Suggestions, bug reports, and patches are welcome; please e-mail them
to me at amk@amk.ca, or post a pull request on github.com. The master
repository is at https://github.com/akuchling/quotation-tools.


Requirements
------------

You will need Python 3.3 or greater.


Installation
------------

The quotation-tools use the Distutils for installation.  Run:

	python setup.py install

to build and install them.

The QEL 2.0 DTD and some additional XML declaration files required by
the DTD are installed into /usr/lib/sgml/.  Run 'install-catalog
--install quotation-tools' to add the installed DTDs to the master
catalog.  (On Debian, use 'install-sgmlcatalog' as the script name
instead.)


License
-------

All the code in this package is free software; you can redistribute it
and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2 of
the License, or (at your option) any later version.

The QEL DTD is under a modified version of the W3C's software license,
though the copyright is held by me.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.


| Andrew M. Kuchling
| amk@amk.ca
| http://www.amk.ca
