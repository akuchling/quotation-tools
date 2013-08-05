"""
qel.scripts -- Entry points for the quotation-tools scripts
"""

import re, time
from . import quotation

def generate_ids(qtcoll):
    """Loop over the quotations in the collection, assigning new IDs to entries that lack one.
    """
    # List existing IDs
    ids = set(qt.id for qt in qtcoll if qt.id is not None)

    # Determine the maximum ID in the file
    id_pat = re.compile('q\d+$')
    existing_ids = [id for id in ids if id_pat.match(id)]
    if existing_ids:
        newid = max(int(id[1:]) for id in existing_ids)
    else:
        newid = 1

    # Add IDs to quotes that lack one
    changed = False
    for qt in qtcoll:
        if qt.id is not None:
            continue
        while ('q' + str(newid)) in ids:
            newid += 1
        qt.id = 'q' + str(newid)
        ids.add(qt.id)
        changed = True

    return changed

class DuplicateIDException(Exception):
    pass

def merge(*collections, strict=True):
    """Merge two collections into a single collection.

    If 'strict' is true, a DuplicateIDException will be raised.
    If it's false, the second occurrence of the ID will be given
    a new ID.
    """
    newcoll = quotation.Collection()
    ids = set()
    for coll in collections:
        for qt in coll:
            newcoll.append(qt)
            if qt.id is not None:
                if qt.id in ids:
                    if strict:
                        raise DuplicateIDException('Duplicated ID %r' % qt.id)

                    else:
                        # We're in non-strict mode, so we need to generate
                        # a new unique ID for this quotation.
                        while True:
                            new_id = 'q' + str(int(time.time()*10))
                            if new_id not in ids:
                                break
                            time.sleep(0.1)

                        qt.id = new_id

                ids.add(qt.id)

    return newcoll