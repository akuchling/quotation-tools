"""
qel.scripts -- Entry points for the quotation-tools scripts
"""

import os, re, time
from . import quotation

class DuplicateIDException(Exception):
    pass

def merge(*collections, strict=True, generate=False):
    """Merge two collections into a single collection.

    If 'strict' is true, a DuplicateIDException will be raised.
    If it's false, the second occurrence of the ID will be given
    a new ID.

    If 'generate' is true, quotations without an ID will be assigned one.
    """
    # Determine the maximum ID in the file of the form 'qNNNN'.
    # We ignore any collisions here.
    id_pat = re.compile('q\d+$')
    existing_ids = set(qt.id
                       for qtcoll in collections
                       for qt in qtcoll
                       if (qt.id is not None and
                           id_pat.match(qt.id))
                       )
    if existing_ids:
        new_id = 1 + max(int(id[1:]) for id in existing_ids)
    else:
        new_id = 1
    del existing_ids

    # Loop over all of the collections
    newcoll = quotation.Collection()
    ids = set()

    for coll in collections:
        for qt in coll:
            newcoll.append(qt)
            if qt.id is None:
                if generate:
                    qt.id = 'q' + str(new_id)
                    new_id += 1
            else:
                # qt.id is not None
                if qt.id in ids:
                    if strict:
                        raise DuplicateIDException('Duplicated ID %r' % qt.id)

                    else:
                        # We're in non-strict mode, so we need to generate
                        # a new unique ID for this quotation.
                        qt.id = 'q' + str(new_id)
                        new_id += 1

            if qt.id is not None:
                ids.add(qt.id)

    return newcoll


def _divide_into_columns(qtcoll):
    # Group the quotations into a set of columns of roughly equal length.
    # We'll count the number of characters in the HTML as an estimator of
    # its length.
    quote_list = [qt.as_html() for qt in qtcoll]
    quote_list = [(len(html), html) for html in quote_list]

    # Figure out the total size; we'll try to have 5K of material per column.
    total_size = sum(size for (size, html) in quote_list)
    target_column_size = 5 * 1024 # Size of 10K

    # Divide the quotes up into lists of columns.
    current_size = 0
    column_list = [ [] ]
    for size, html in quote_list:
        column_list[-1].append(html)
        current_size += size
        if current_size > target_column_size:
            current_size = 0
            column_list.append( [] )

    # If last column is empty, remove it.
    if len(column_list[-1]) == 0:
        del column_list[-1]

    # Ensure there is always an even number of column lists.
    if (len(column_list) % 2) == 1:
        column_list.append([])

    return column_list

def write_html_dir(dir, qtcoll):
    """Export a quotation file as a set of HTML pages, using a fancy template.
    """
    from qel.data import HTML_TEMPLATE

    column_list = _divide_into_columns(qtcoll)

    page_num = 1
    while len(column_list):
        if page_num == 1:
            fn = 'index.html'
        else:
            fn = '{}.html'.format(page_num)
        path = os.path.join(dir, fn)

        last_attr = ('data-last=""' if len(column_list) == 0 else '')

        col1 = column_list.pop(0)
        col2 = column_list.pop(0)

        page = HTML_TEMPLATE.format(page_num=page_num,
                                    last_attr=last_attr,
                                    col1='\n'.join(col1),
                                    col2='\n'.join(col2),
                                    title="Quotation Collection",
                                )

        with open(path, 'wt', encoding='latin-1') as f:
            f.write(page)

        page_num += 1

    print(page_num-1, 'pages written')
