
from distutils.core import setup

setup(
    name = 'quotation-tools',
    version = "0.0.5",
    description = "Tools for parsing and maintaining quotation collections "
                  "using the QEL format.",
    author = "A.M. Kuchling",
    author_email = "amk@amk.ca",
    url = "http://www.amk.ca/qel/",

    packages = ['qel'],
    scripts = [#'scripts/fortune2qel',
               'scripts/qtformat', 'scripts/qtgrep', 'scripts/qtmerge',
               'scripts/qtgenerateids'],
    data_files = [('/usr/lib/sgml/', ['xml/qel-2.01.dtd',
                                      'xml/quotation-tools.cat',
                                      'xml/ibtwsh6.dtd',
                                      'xml/xhtml-lat1.ent',
                                      'xml/xhtml-special.ent',
                                      'xml/xhtml-symbol.ent'])]
    )


