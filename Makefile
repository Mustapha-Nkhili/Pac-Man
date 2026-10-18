MAIN = pac-man.py
CONFIG = config.json
VENV = .venv
MYPY_FLAGS = --warn-return-any --warn-unused-ignores --ignore-missing-imports \
						 --disallow-untyped-defs --check-untyped-defs

run: $(VENV)
	uv run $(MAIN) $(CONFIG)

$(VENV): pyproject.toml uv.lock
	uv sync
	@touch $(VENV)


install: $(VENV)


debug: $(VENV)
	uv run python -m pdb $(MAIN) $(CONFIG)


clean:
	rm -rf .mypy_cache
	rm -rf src/__pycache__
	rm -rf src/logic/__pycache__


lint: $(VENV)
	uv run flake8 . --extend-exclude=$(VENV)
	uv run mypy . $(MYPY_FLAGS) --exclude '$(VENV)'


lint-strict: $(VENV)
	uv run flake8 . --extend-exclude=$(VENV)
	uv run mypy . --strict --exclude '$(VENV)'


.PHONY: run install debug lint lint-strict clean
