
cov:
	coverage run test/test_parse.py
	coverage annotate -d /tmp/ qel/parse.py
	coverage run test/test_iso8601.py
	coverage annotate -d /tmp/ qel/iso8601.py
	coverage run test/test_quotation.py
	coverage annotate -d /tmp/ qel/quotation.py
