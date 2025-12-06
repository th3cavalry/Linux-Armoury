PY=python3
PIP=pip

.PHONY: format lint precommit-install test

format:
	$(PY) -m isort src tests || true
	$(PY) -m black . || true

lint:
	$(PY) -m flake8

precommit-install:
	@echo "To enable pre-commit hooks locally, run:\n  pip install -e '.[dev]' && pre-commit install"

test:
	PYTHONPATH=src pytest -q
