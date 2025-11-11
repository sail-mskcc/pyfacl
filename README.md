# PyFACL

A Python library for parsing and checking POSIX File Access Control Lists (FACL).

## Installation

### From PyPI
```bash
pip install pyfacl
```

## Usage

### CLI

The CLI tool checks permissions through the entire directory hierarchy, checks whether the permissions are met and identifies which permission rule applies at each level.

```bash
pyfacl trace /path/to/file user:<username>:r-x --mode exact
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

### Python

#### Check one file/folder permission

```python
from pyfacl import FACL

# Initialize and parse FACL for a file/directory
facl = FACL(path="/path/to/file")

# Check permissions with different modes
facl.has_permission("user:username:r-x", mode="exact")     # exact match
facl.has_permission("user:username:r--", mode="at_least") # has at least read
facl.has_permission("user:username:rwx", mode="at_most")  # has at most rwx
```

#### Check trace through directory hierarchy

```python
from pyfacl import FACLTrace

# Initialize FACLTrace for a directory
facl_trace = FACLTrace(path="/path/to/directory", v=1)

# Trace permissions for a specific user
trace_result = facl_trace.has_permission("user:username:r-x", mode="at_least")
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
