VENV = .venv
PYTHON = $(VENV)/bin/python

$(VENV)/bin/activate: pyproject.toml
	uv venv $(VENV)

run: $(VENV)/bin/activate
	uv run $(PYTHON) server.py

install-claude-config:
	uv run mcp install server.py --with elasticsearch

lint:
	uv run black .

clean:
	rm -rf $(VENV) __pycache__

dev:
	uv run mcp dev server.py
