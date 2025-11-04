from pyfacl import FACLTrace


def test_facl_trace(acls_fixture):
    facl_trace = FACLTrace(v=0)

    # test user1
    trace_result = facl_trace._trace(
        path="/home/user1/project",
        acl="user:user1:rwx",
        mode="at_least",
        _pytest_acls=acls_fixture,
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
        _pytest_acls=acls_fixture,
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
        _pytest_acls=acls_fixture,
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
        _pytest_acls=acls_fixture,
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


def test_facl_trace_permissions(acls_fixture):
    facl_trace = FACLTrace(v=0)

    # test user1 exact
    assert facl_trace.has_permission(
        path="/home/user1/project",
        acl="user:user1:rwx",
        mode="exact",
        _pytest_acls=acls_fixture,
    )

    # test user1 exact no match
    assert not facl_trace.has_permission(
        path="/home/user1/project",
        acl="user:user1:r-x",
        mode="exact",
        _pytest_acls=acls_fixture,
    )

    # test user1 at least
    assert facl_trace.has_permission(
        path="/home/user1/project",
        acl="user:user1:r-x",
        mode="at_least",
        _pytest_acls=acls_fixture,
    )

    # test user1 at most
    assert not facl_trace.has_permission(
        path="/home/user1/project",
        acl="user:user1:r-x",
        mode="at_most",
        _pytest_acls=acls_fixture,
    )

    # test group1 exact
    assert facl_trace.has_permission(
        path="/home/user1/project",
        acl="group:group1:r-x",
        mode="exact",
        _pytest_acls=acls_fixture,
    )

    # test group1 at least
    assert facl_trace.has_permission(
        path="/home/user1/project",
        acl="group:group1:--x",
        mode="at_least",
        _pytest_acls=acls_fixture,
    )

    # test group2 at least
    assert facl_trace.has_permission(
        path="/home/user1/project",
        acl="group:group2:--x",
        mode="at_least",
        _pytest_acls=acls_fixture,
    )

    # test group2 at most (no write)
    assert facl_trace.has_permission(
        path="/home/user1/project",
        acl="group:group2:rwx",
        mode="at_most",
        _pytest_acls=acls_fixture,
    )

    # test group2
    assert not facl_trace.has_permission(
        path="/home/user1/project",
        acl="group:group2:--x",
        mode="at_most",
        _pytest_acls=acls_fixture,
    )
