# GitHub Copilot Instructions for PyFACL

## Project Overview

PyFACL is a Python library for parsing and checking POSIX File Access Control Lists (FACL). It provides both a CLI tool and a Python API for analyzing file permissions through directory hierarchies.

## Tech Stack

- **Language**: Python 3.12+
- **CLI Framework**: Typer (>=0.15.0)
- **Testing**: pytest
- **Code Formatting**: Black (line-length: 88)
- **Import Sorting**: isort (profile: black)
- **Linting**: flake8 (max-line-length: 88, extend-ignore: E203)
- **Build System**: poetry-core (>=2.0.0)
- **Pre-commit**: Configured with hooks for trailing whitespace, end-of-file-fixer, flake8, black, isort, and pytest

## Code Style and Conventions

### Python Style
- Follow Black formatting with 88 character line length
- Use isort with Black profile for import ordering
- Target Python 3.12+ syntax and features
- Adhere to flake8 linting rules (ignore E203 for Black compatibility)

### Import Organization
- Use `# isort: skip_file` comment when import order must be preserved (e.g., in `__init__.py`)
- Standard library imports first, then third-party, then local imports
- Absolute imports preferred over relative imports where appropriate

### Code Structure
- Keep CLI commands in `pyfacl/cli.py` using Typer decorators
- Core FACL logic in `pyfacl/pyfacl.py`
- Trace functionality in `pyfacl/pyfacl_trace.py`
- Permission checking in `pyfacl/pyfacl_has.py`
- Logging utilities in `pyfacl/logger.py`

### Docstrings and Comments
- Use docstrings for functions and classes
- Keep comments minimal and meaningful
- Document complex permission logic and ACL parsing

## Development Workflow

### Setup
```bash
pip install -e ".[dev]"
pre-commit install
```

### Pre-commit Checks
All changes must pass pre-commit hooks before committing:
```bash
pre-commit run --all-files
```

This runs:
- Trailing whitespace removal
- End-of-file fixer
- Large file checker
- Merge conflict checker
- Debug statement checker
- Docstring-first checker
- flake8 linting
- Black formatting
- isort import sorting
- pytest test suite

### Testing
- Run tests with: `pytest`
- All tests must pass before submitting changes
- Test files are located in `tests/` directory
- Use fixtures defined in `tests/conftest.py`
- Write tests for new features and bug fixes

### Building
- Uses poetry-core as build backend
- Entry point: `pyfacl = "pyfacl.cli:main"`

## Project Structure

```
pyfacl/
├── pyfacl/           # Main package
│   ├── __init__.py   # Package exports (FACL, FACLTrace, FACLHas)
│   ├── cli.py        # CLI commands (trace, has)
│   ├── logger.py     # Logging configuration
│   ├── pyfacl.py     # Core FACL class
│   ├── pyfacl_trace.py   # FACLTrace class
│   └── pyfacl_has.py     # FACLHas class
├── tests/            # Test suite
├── docs/             # Documentation
└── pyproject.toml    # Project configuration
```

## Key Concepts

### Permission Modes
The library supports three permission checking modes:
- `exact`: Permissions must match exactly
- `at_least`: Must have at least the specified permissions
- `at_most`: Must have at most the specified permissions

### ACL Format
ACL strings follow POSIX format: `user:username:rwx` or `group:groupname:rwx`

### Trace vs Has
- `trace`: Checks permissions through entire directory hierarchy from root to target
- `has`: Checks if user/group can navigate to path and if specified ACL is granted

## Best Practices

1. **Always run pre-commit hooks** before committing changes
2. **Write tests** for new functionality in the `tests/` directory
3. **Follow Black formatting** - let Black handle all formatting decisions
4. **Keep CLI simple** - complex logic belongs in the library classes, not CLI commands
5. **Maintain Python 3.12+ compatibility** - this is the minimum required version
6. **Document permission logic** - ACL checking can be complex, document the reasoning
7. **Use type hints** where appropriate to improve code clarity
8. **Keep dependencies minimal** - only add new dependencies if absolutely necessary

## Common Tasks

### Adding a New CLI Command
1. Add command function to `pyfacl/cli.py` with `@app.command()` decorator
2. Use Typer's argument and option types for parameters
3. Import necessary classes from `pyfacl` package
4. Add corresponding tests in `tests/test_cli_*.py`

### Adding Core Functionality
1. Implement in appropriate module (`pyfacl.py`, `pyfacl_trace.py`, or `pyfacl_has.py`)
2. Update `__init__.py` if adding new public classes
3. Write comprehensive tests in `tests/test_*.py`
4. Ensure all pre-commit hooks pass

### Fixing Bugs
1. Write a failing test that reproduces the bug
2. Fix the bug
3. Ensure the test passes
4. Run full test suite to catch regressions
5. Update documentation if behavior changes

## Documentation

- Main documentation is hosted on ReadTheDocs: https://pyfacl.readthedocs.io/
- Configuration in `.readthedocs.yaml`
- Documentation source in `docs/` directory
- README.md contains quick start guide and examples
