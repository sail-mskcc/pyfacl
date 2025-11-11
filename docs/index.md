# PyFACL Documentation

A Python library for parsing and checking POSIX File Access Control Lists (FACL).

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

### Check one file/folder permission

```python
from pyfacl import FACL

# Parse ACLs for a file
facl = FACL(path="/path/to/file")

# Check permissions
has_read = facl.has_permission("user:alice:r--", mode="at_least")
has_exact = facl.has_permission("user:bob:rwx", mode="exact")
```

### Check trace through directory hierarchy

```python
from pyfacl import FACLTrace

# Initialize FACLTrace for a directory
facl_trace = FACLTrace(path="/path/to/directory", v=1)

# Trace permissions for a specific user
trace_result = facl_trace.has_permission("user:username:r-x", mode="at_least")
```

## CLI Commands

### `pyfacl trace`

Trace permissions through directory hierarchy:

```bash
# Check if user has read permissions
pyfacl trace /path/to/file "user:alice:r--" --mode at_least
```

Example output:
```bash
$ pyfacl trace /data1/collab002/sail/example/permission/folder user:moormana:r-x
0) ✅ other::r-x /
1) ✅ other::r-x /data1
2) ✅ group::rwx /data1/collab002
3) ✅ group::r-x /data1/collab002/sail
4) ✅ group::r-x /data1/collab002/sail/example
5) ❌ user:moormana:--x /data1/collab002/sail/example/permission
6) ✅ group::r-x /data1/collab002/sail/example/permission/folder
```

In this trace, items 0-4 and 6 show ✅ **passing** permissions, while item 5 shows ❌ **failing** permissions where the user only has execute (`--x`) but needs read+execute (`r-x`).

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
