import pytest

from pyfacl import FACLTrace


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
def pytest_acls_fixture():
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


def test_facl_trace(pytest_acls_fixture):
    facl_trace = FACLTrace(v=0)

    # test user1
    trace_result = facl_trace._trace(
        path="/home/user1/project",
        acl="user:user1:rwx",
        mode="at_least",
        _pytest_acls=pytest_acls_fixture,
    )

    trace_expected = {
        "/home/user1/project": {"applicable_acl": "user::rwx", "has_permission": True},
        "/home/user1": {"applicable_acl": "user::rwx", "has_permission": True},
        "/home": {"applicable_acl": "user:user1:rwx", "has_permission": True},
        "/": {"applicable_acl": "user:user1:rwx", "has_permission": True},
    }

    # test root 'at_least'
    trace_result = facl_trace._trace(
        path="/home/user1/project",
        acl="user:root:rwx",
        mode="at_least",
        _pytest_acls=pytest_acls_fixture,
    )

    trace_expected = {
        "/home/user1/project": {
            "applicable_acl": "user:root:r-x",
            "has_permission": False,
        },
        "/home/user1": {"applicable_acl": "user:root:r-x", "has_permission": False},
        "/home": {"applicable_acl": "user::rwx", "has_permission": True},
        "/": {"applicable_acl": "user::rwx", "has_permission": True},
    }

    for entry in trace_result:
        expected = trace_expected[entry["path"]]
        assert entry["applicable_acl"]["line"] == expected["applicable_acl"]
        assert entry["has_permission"] is expected["has_permission"]

    # test root 'at_most'
    trace_result = facl_trace._trace(
        path="/home/user1/project",
        acl="user:root:r-x",
        mode="at_most",
        _pytest_acls=pytest_acls_fixture,
    )

    trace_expected = {
        "/home/user1/project": {
            "applicable_acl": "user:root:r-x",
            "has_permission": True,
        },
        "/home/user1": {"applicable_acl": "user:root:r-x", "has_permission": True},
        "/home": {"applicable_acl": "user::rwx", "has_permission": False},
        "/": {"applicable_acl": "user::rwx", "has_permission": False},
    }

    for entry in trace_result:
        expected = trace_expected[entry["path"]]
        assert entry["applicable_acl"]["line"] == expected["applicable_acl"]
        assert entry["has_permission"] is expected["has_permission"]

    # test group2
    trace_result = facl_trace._trace(
        path="/home/user1/project",
        acl="group:group2:r-x",
        mode="at_least",
        _pytest_acls=pytest_acls_fixture,
    )

    trace_expected = {
        "/home/user1/project": {
            "applicable_acl": "group:group2:r-x",
            "has_permission": True,
        },
        "/home/user1": {"applicable_acl": "other::--x", "has_permission": False},
        "/home": {"applicable_acl": "other::--x", "has_permission": False},
        "/": {"applicable_acl": "other::--x", "has_permission": False},
    }

    for entry in trace_result:
        expected = trace_expected[entry["path"]]
        assert entry["applicable_acl"]["line"] == expected["applicable_acl"]
        assert entry["has_permission"] is expected["has_permission"]


def test_facl_trace_permissions(pytest_acls_fixture):
    facl_trace = FACLTrace(v=0)

    # test user1 exact
    assert facl_trace.has_permission(
        path="/home/user1/project",
        acl="user:user1:rwx",
        mode="exact",
        _pytest_acls=pytest_acls_fixture,
    )

    # test user1 exact no match
    assert not facl_trace.has_permission(
        path="/home/user1/project",
        acl="user:user1:r-x",
        mode="exact",
        _pytest_acls=pytest_acls_fixture,
    )

    # test user1 at least
    assert facl_trace.has_permission(
        path="/home/user1/project",
        acl="user:user1:r-x",
        mode="at_least",
        _pytest_acls=pytest_acls_fixture,
    )

    # test user1 at most
    assert not facl_trace.has_permission(
        path="/home/user1/project",
        acl="user:user1:r-x",
        mode="at_most",
        _pytest_acls=pytest_acls_fixture,
    )

    # test group1 exact
    assert facl_trace.has_permission(
        path="/home/user1/project",
        acl="group:group1:r-x",
        mode="exact",
        _pytest_acls=pytest_acls_fixture,
    )

    # test group1 at least
    assert facl_trace.has_permission(
        path="/home/user1/project",
        acl="group:group1:--x",
        mode="at_least",
        _pytest_acls=pytest_acls_fixture,
    )

    # test group2 at least
    assert facl_trace.has_permission(
        path="/home/user1/project",
        acl="group:group2:--x",
        mode="at_least",
        _pytest_acls=pytest_acls_fixture,
    )

    # test group2 at most (no write)
    assert facl_trace.has_permission(
        path="/home/user1/project",
        acl="group:group2:rwx",
        mode="at_most",
        _pytest_acls=pytest_acls_fixture,
    )

    # test group2
    assert not facl_trace.has_permission(
        path="/home/user1/project",
        acl="group:group2:--x",
        mode="at_most",
        _pytest_acls=pytest_acls_fixture,
    )
