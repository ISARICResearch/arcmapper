tests: lint install
	uv run pytest

install-uv:
	curl -LsSf https://astral.sh/uv/0.4.27/install.sh | sh

install:
	uv sync --all-extras --dev

lint:
	uvx ruff check src
	uvx ruff check tests

.PHONY: install-uv install lint tests
