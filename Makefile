.PHONY: all
all: install lint test build

.PHONY: check
check: lint test

.PHONY: install
install:
	poetry install --all-extras --with dev

.PHONY: lint
lint: lint/black lint/ruff lint/mypy

.PHONY: lint/black
lint/black:
	poetry run black --diff --check combadge tests

.PHONY: lint/ruff
lint/ruff:
	poetry run ruff combadge tests

.PHONY: lint/mypy
lint/mypy:
	poetry run mypy combadge tests

.PHONY: format
format: format/black format/ruff

.PHONY: format/black
format/black:
	poetry run black combadge tests

.PHONY: format/ruff
format/ruff:
	poetry run ruff --fix combadge tests

.PHONY: test
test:
	poetry run pytest tests

.PHONY: build
build:
	poetry build
