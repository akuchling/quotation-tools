"""
qel.scripts -- Entry points for the quotation-tools scripts
"""

import re, time
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
