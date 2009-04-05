# Test the modules in the utils/ subpackage

from qel import iso8601

for dt in ['1998', '1998-06', '1998-06-13',
           '1998-06-13T14:12Z',
           '1998-06-13T14:12:30Z',
           '1998-06-13T14:12:30.2Z'
           ]:
    date = iso8601.parse( dt )
    print iso8601.tostring( date )
