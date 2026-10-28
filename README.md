> For developer

    Please run `make init` to initialize the project.

# {{.Name}}

A Python plugin for Wox 2.4.8 or newer.

## Development

Install Python 3.10 or newer, [uv](https://docs.astral.sh/uv/) and GNU Make. Clone this template, then run:

```sh
make init     # Enter the plugin name, description, trigger keywords and metadata
make install  # Install runtime and development dependencies
make test     # Run the tests
make lint     # Run Ruff and mypy
make package  # Create a .wox package in the project directory
```

`plugin.json` contains a JSON array placeholder until `make init` or the Wox scaffolder replaces it. After initialization, edit `src/main.py` to implement your plugin. Double-click the resulting `.wox` file to install it in Wox.

## Install

```
wpm install {{.Name}}
```
