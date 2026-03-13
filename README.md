# PyFACL

[![PyPI version](https://badge.fury.io/py/pyfacl.svg)](https://badge.fury.io/py/pyfacl)
[![Python](https://img.shields.io/pypi/pyversions/pyfacl.svg)](https://pypi.org/project/pyfacl/)
[![Documentation Status](https://readthedocs.org/projects/pyfacl/badge/?version=latest)](https://pyfacl.readthedocs.io/en/latest/?badge=latest)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python library for parsing and checking POSIX File Access Control Lists (FACL).

**Documentation:** [https://pyfacl.readthedocs.io/en/latest/](https://pyfacl.readthedocs.io/en/latest/)

## Installation

### From PyPI
```bash
pip install pyfacl
```

## Usage

### Python

The simplest way to check permissions is with the top-level `pyfacl.has_permission` function:

```python
import pyfacl

# Case 1 — check a single file/directory (default)
pyfacl.has_permission("/path/to/file", "user:user2:r-x")

# Case 2 — trace through entire directory hierarchy (trace=True)
#   The permission must be granted at every level from / down to the target path.
pyfacl.has_permission("/path/to/file", "user:user2:r-x", trace=True)

# Case 3 — can-execute check (can_execute=True)
#   The user/group must have execute (--x) on every parent directory up to the path,
#   and the specified permission+mode for the target path only.
pyfacl.has_permission("/path/to/file", "user:user2:r-x", can_execute=True)
```

All three cases accept the same optional arguments:

| Argument | Default | Description |
|----------|---------|-------------|
| `mode` | `"at_least"` | `"exact"`, `"at_least"`, or `"at_most"` |
| `trace` | `False` | Check every directory level |
| `can_execute` | `False` | Check execute on parents, specified perm on target |
| `v` | `0` | Verbosity level |

> **Note:** `trace=True` and `can_execute=True` cannot be used together.

#### Permission Modes

- **`exact`**: Permissions must match exactly
- **`at_least`**: Must have at least the specified permissions
- **`at_most`**: Must have at most the specified permissions

---

### CLI

The CLI tool checks permissions through the entire directory hierarchy, checks whether the permissions are met and identifies which permission rule applies at each level.

```bash
pyfacl trace /path/to/file user:<user2>:r-x --mode exact
```

Example output:
```bash
$ pyfacl trace /data1/collab002/sail/example/permission/folder user:user2:r-x
0) ✅ other::r-x /
1) ✅ other::r-x /data1
2) ✅ group::rwx /data1/collab002
3) ✅ group::r-x /data1/collab002/sail
4) ✅ group::r-x /data1/collab002/sail/example
5) ❌ user:user2:--x /data1/collab002/sail/example/permission
6) ✅ group::r-x /data1/collab002/sail/example/permission/folder
```

In this trace, items 0-4 and 6 show ✅ **passing** permissions, while item 5 shows ❌ **failing** permissions where the user only has execute (`--x`) but needs read+execute (`r-x`).

However, often we only care about if the user has the required permission for the final file/directory, not the full trace. For that, we can use the `has` command:

```bash
$ pyfacl has /path/to/file user:<user2>:r-x --mode exact
0) ✅ other::r-x /
1) ✅ other::r-x /data1
2) ✅ group::rwx /data1/collab002
3) ✅ group::r-x /data1/collab002/sail
4) ✅ group::r-x /data1/collab002/sail/example
5) ✅ user:user2:--x /data1/collab002/sail/example/permission
6) ✅ group::r-x /data1/collab002/sail/example/permission/folder
```

---

### Python (class-based API)

The lower-level class-based API gives more control and is useful when you need the
detailed trace output or want to reuse a parsed FACL object.

#### Check one file/folder permission

```python
from pyfacl import FACL

# Initialize and parse FACL for a file/directory
facl = FACL(path="/path/to/file")

# Check permissions with different modes
facl.has_permission("user:user2:r-x", mode="exact")     # exact match
facl.has_permission("user:user2:r--", mode="at_least") # has at least read
facl.has_permission("user:user2:rwx", mode="at_most")  # has at most rwx
```

#### Check trace through directory hierarchy

```python
from pyfacl import FACLTrace

# Initialize FACLTrace for a directory
facl_trace = FACLTrace(path="/path/to/directory", v=1)

# Trace permissions for a specific user
trace_result = facl_trace.has_permission("user:user2:r-x", mode="at_least")
```

#### Check if user/group can navigate to and has permission for a file/directory

```python
from pyfacl import FACLHas

# Initialize FACLHas for a file/directory
facl_has = FACLHas(path="/path/to/file")

# Check if user/group has execute on all parents and the specified perm on the target
has_permission = facl_has.has_permission("user:user2:r-x", mode="at_least")
```

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
