# PyFACL

A Python library for parsing and checking POSIX File Access Control Lists (FACL).

## Installation

### From PyPI
```bash
pip install pyfacl
```

## Usage

```python
from pyfacl import FACL

# Initialize and parse FACL for a file/directory
facl = FACL()
facl.parse("/path/to/file")

# Check permissions with different modes
facl.has_permission("user:username:r-x", mode="exact")     # exact match
facl.has_permission("user:username:r--", mode="at_least") # has at least read
facl.has_permission("user:username:rwx", mode="at_most")  # has at most rwx
```

### Permission Modes

- **`exact`**: Permissions must match exactly
- **`at_least`**: Must have at least the specified permissions
- **`at_most`**: Must have at most the specified permissions

## Development

### Setup Development Environment
```bash
pip install -e ".[dev]"
pre-commit install
```

### Run Pre-commit Checks
```bash
pre-commit run --all-files
```
