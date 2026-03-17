.PHONY: help init check-init check-dev-deps install clean lint format build test package

DIST_DIR := dist
SRC_DIR := src
PYTHON ?= python3

help:
	@echo "Available commands:"
	@echo "  make init    - Initialize template values interactively"
	@echo "  make install  - Install project dependencies"
	@echo "  make clean   - Clean build directory"
	@echo "  make build   - Build project"
	@echo "  make package - Build plugin package"

init:
	$(PYTHON) scripts/init-wox-project.py

check-init:
	@$(PYTHON) scripts/init-wox-project.py --check-initialized

check-dev-deps:
	@uv run python -c 'import importlib.util, sys; missing = [name for name in ("ruff", "mypy") if importlib.util.find_spec(name) is None]; missing and (print("Development dependencies are not installed. Run '"'"'make install'"'"' first.", file=sys.stderr), print("Missing packages: " + ", ".join(missing), file=sys.stderr), sys.exit(1))'

install: check-init
	uv sync --all-extras

clean:
	rm -rf $(DIST_DIR)

lint: check-init check-dev-deps
	uv run ruff check src
	uv run mypy src

format: check-init check-dev-deps
	uv run ruff format src

build: lint format
	rm -rf $(DIST_DIR)
	mkdir -p $(DIST_DIR)/dependencies
	uv pip freeze > requirements.txt
	uv pip install -r requirements.txt --target $(DIST_DIR)/dependencies
	rm requirements.txt
	cp -r $(SRC_DIR)/* $(DIST_DIR)/
	find $(DIST_DIR)/dependencies -type d -name "*.dist-info" -o -name "*.egg-info" | xargs rm -rf
	find $(DIST_DIR)/dependencies -type f -name "__editable__*" -o -name ".lock" | xargs rm -f
	rm -rf $(DIST_DIR)/dependencies/*mypy*
	rm -rf $(DIST_DIR)/dependencies/ruff
	rm -rf $(DIST_DIR)/dependencies/bin
	echo 'import os\nimport sys\n\n# Add dependencies directory to Python path\ndeps_dir = os.path.join(os.path.dirname(__file__), "dependencies")\nif deps_dir not in sys.path:\n    sys.path.insert(0, deps_dir)\n\nfrom .main import plugin\n\n__all__ = ["plugin"]' > $(DIST_DIR)/__init__.py
	cp plugin.json $(DIST_DIR)/plugin.json
	mkdir -p $(DIST_DIR)/images
	cp images/* $(DIST_DIR)/images/

test: check-init
	uv run python -m unittest tests/test_friendly_names.py

package: check-init build
	cd $(DIST_DIR) && zip -r "../wox.plugin.{{.Name}}.wox" .
	rm -rf $(DIST_DIR)
