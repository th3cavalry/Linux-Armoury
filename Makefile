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

build:
	$(PY) -m build

flatpak-build:
	@echo "Building Flatpak..."
	flatpak-builder --user --install --force-clean build-dir com.github.th3cavalry.linux-armoury.yml

flatpak-run:
	flatpak run com.github.th3cavalry.linux-armoury

clean:
	rm -rf dist/ build/ *.egg-info/ .pytest_cache/ .coverage build-dir/

install:
	$(PIP) install .
