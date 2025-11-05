.PHONY: test lint fix run

test:
	python -m pytest

lint:
	ruff check .

fix:
	ruff check . --fix

run:
	python app.py
