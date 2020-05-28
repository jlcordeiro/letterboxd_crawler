.PHONY: tests pep8

pep8:
	@python3 -m autopep8 --in-place --aggressive --aggressive lmatch/*.py
	@python3 -m pycodestyle lmatch/*.py

tests:
	@python3 -m coverage run -m unittest discover tests
	@python3 -m coverage report --skip-covered --show-missing --omit=tests/*
