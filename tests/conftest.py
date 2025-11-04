import os
import tempfile

import pytest


def generate_facl_str(path, owner, group, custom_acls=[]):
    """
    Always default to user::rwx, group::r-x, other::--x plus any custom ACLs.
    """
    facl_lines = [
        f"# file: {path}",
        f"# owner: {owner}",
        f"# group: {group}",
        "# flags: -s-",
        "user::rwx",
        "group::r-x",
        "other::--x",
    ]
    facl_lines.extend(custom_acls)
    return "\n".join(facl_lines) + "\n"


@pytest.fixture
def facl_fixture():
    # rewrite using generate_facl_str
    facl = generate_facl_str(
        "/home/user1/project",
        "user1",
        "group1",
        [
            "d:user::rwx",
            "d:g::r-x",
            "o::r-x",
        ],
    )
    facl = facl.replace("other::--x", "other::r-x")
    return facl


@pytest.fixture
def acls_fixture():
    """
    Create fixture to simulate a directory hierarchy with ACLs for testing FACLTrace
    """
    pytest_acls = {
        "/": generate_facl_str("/", "root", "group1", ["user:user1:rwx"]),
        "/home": generate_facl_str("/home", "root", "group1", ["user:user1:rwx"]),
        "/home/user1": generate_facl_str(
            "/home/user1", "user1", "group1", ["user:root:r-x"]
        ),
        "/home/user1/project": generate_facl_str(
            "/home/user1/project",
            "user1",
            "group1",
            ["user:root:r-x", "group:group2:r-x"],
        ),
    }
    return pytest_acls


@pytest.fixture
def tempfile_with_acl():
    filepath = tempfile.NamedTemporaryFile(delete=False)

    # add 'other' ACL entry
    os.system(f"setfacl -m o::r-x {filepath.name}")
    yield filepath.name

    # cleanup
    os.remove(filepath.name)
