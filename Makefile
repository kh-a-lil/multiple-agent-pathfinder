install:
	@uv sync
debug:
	@python3 -m pdb src/__main__.py
run:
	@uv run python3 -m src $(MAP)
clean:
	@rm -rf __pycache__ */__pycache__ .mypy_cache */.mypy_cache
lint:
	@uv run  mypy src --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
	@flake8 src
.PHONY: lint clean run debug install
