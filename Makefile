run:
	@uv run python3 -m src $(MAP)
clean:
	@rm -rf __pycache__ */__pycache__ .mypy_cache */.mypy_cache
lint:
	@uv run mypy .
	@flake8 src
.PHONY: lint clean run