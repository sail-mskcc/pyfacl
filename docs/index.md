# PyFACL Documentation

A Python library for parsing and checking POSIX File Access Control Lists (FACL).

```{toctree}
:maxdepth: 2
:caption: Contents:

index
```

## Overview

PyFACL provides a simple interface to work with POSIX Access Control Lists (ACLs) on Unix-like systems. It allows you to parse, analyze, and check file permissions through both a Python API and command-line interface.

**Key Features:**
- Parse POSIX ACLs
- Query permission against user/group/other
- Automatically handle group memberships
- Trace permissions through directory hierarchies

**Source Code:** [GitHub Repository](https://github.com/sail-mskcc/pyfacl)

## Installation

Install PyFACL from PyPI:

```bash
pip install pyfacl
```

## Python API

```python
from pyfacl import FACL

# Parse ACLs for a file
facl = FACL()
facl.parse("/path/to/file")
facl.parse("/home/krauset")

# Check permissions
has_read = facl.has_permission("user:alice:r--", mode="at_least")
has_exact = facl.has_permission("user:bob:rwx", mode="exact")

# Check trace
from pyfacl import FACLTrace
trace = FACLTrace()
result = trace.has_permission("/deep/path/to/file", "user:alice:rwx")
```

## CLI Commands

### `pyfacl trace`

Trace permissions through directory hierarchy:

```bash
# Check if user has read permissions
pyfacl trace /path/to/file "user:alice:r--" --mode at_least
```

## Permission Modes

PyFACL supports three permission matching modes:

- **`exact`**: Permissions must match exactly
- **`at_least`**: Must have at least the specified permissions
- **`at_most`**: Must have at most the specified permissions

## Development

### Setup Development Environment

```bash
git clone https://github.com/sail-mskcc/pyfacl.git
cd pyfacl
pip install -e ".[dev]"
pre-commit install
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
pre-commit run --all-files
```

## License

MIT License - see the [LICENSE](https://github.com/sail-mskcc/pyfacl/blob/main/LICENSE) file for details.

## Support

- **Issues:** [GitHub Issues](https://github.com/sail-mskcc/pyfacl/issues)
- **Source:** [GitHub Repository](https://github.com/sail-mskcc/pyfacl)
