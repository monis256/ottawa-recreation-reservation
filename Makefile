.PHONY: run test help

default: help

run:
	pipenv run src/main.py

test:
	flake8 src/
	pylint src/

help:
	@echo "Available options:"
	@echo "  run     : Run the Python application."
	@echo "  test    : Run linters."
	@echo "  help    : Show this help message."
