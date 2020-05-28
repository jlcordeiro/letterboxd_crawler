.PHONY: tests

tests:
	@python3 -m coverage run -m unittest discover tests
	@python3 -m coverage report --show-missing --omit=tests/*
