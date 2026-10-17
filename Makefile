MAIN = pac-man.py
CONFIG = config.json
MYPY_FLAGS = --warn-return-any --warn-unused-ignores --ignore-missing-imports \
						 --disallow-untyped-defs --check-untyped-defs


install:
	uv sync

run: install
	uv run $(MAIN) $(CONFIG)


debug: install
	uv run python -m pdb $(MAIN) $(CONFIG)


clean:
	rm -rf .mypy_cache
	rm -rf src/__pycache__
	rm -rf src/logic/__pycache__


lint: install
	uv run flake8 . --extend-exclude=.venv
	uv run mypy . $(MYPY_FLAGS) --exclude '.venv'


lint-strict: install
	uv run flake8 . --extend-exclude=.venv
	uv run mypy . --strict --exclude '.venv'


.PHONY: run install debug lint lint-strict clean
