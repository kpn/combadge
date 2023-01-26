.PHONY: all
all: install lint unittests build

.PHONY: check
check: lint unittests

.PHONY: install
install:
	poetry install --with dev

.PHONY: lint
lint: lint/black lint/flake8 lint/isort lint/mypy

.PHONY: lint/flake8
lint/flake8:
	poetry run flake8 combadge tests

.PHONY: lint/isort
lint/isort:
	poetry run isort --diff --check combadge tests

.PHONY: lint/black
lint/black:
	poetry run black --diff --check combadge tests

.PHONY: lint/mypy
lint/mypy:
	poetry run mypy combadge tests

.PHONY: format
format: format/isort format/black

.PHONY: format/isort
format/isort:
	poetry run isort combadge tests

.PHONY: format/black
format/black:
	poetry run black combadge tests

.PHONY: unittests
unittests:
	poetry run pytest --cov=./ --cov-report=xml tests

.PHONY: build
build:
	poetry build
