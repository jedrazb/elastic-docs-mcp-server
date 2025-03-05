VENV = .venv
PYTHON = $(VENV)/bin/python

$(VENV)/bin/activate: pyproject.toml
	uv venv $(VENV)

run: $(VENV)/bin/activate
	uv run $(PYTHON) server.py

add-claude-config: $(VENV)/bin/activate
	uv run mcp install server.py --with elasticsearch

lint:
	uv run black .

clean:
	rm -rf $(VENV) __pycache__

dev: check-nvm
	uv run mcp dev server.py
