
cov:
	coverage3 run test/test_parse.py
	ls -l .coverage
	coverage3 run -a test/test_iso8601.py
	ls -l .coverage
	coverage3 run -a test/test_quotation.py
	ls -l .coverage
	coverage3 run -a test/test_scripts.py
	ls -l .coverage

	coverage3 annotate -d /tmp/ build/lib/qel/*.py
