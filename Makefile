SHELL=/bin/bash

all: deps lint test
	@echo "All dependencies."

deps:
	pip install poetry
	poetry config virtualenvs.create false
	poetry install --no-root --quiet

lint: deps
	poetry run flake8 --quiet

test: deps
	poetry run pytest --quiet
