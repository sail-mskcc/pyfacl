from pyfacl import FACLTrace


def test_facl_trace(acls_fixture):
    facl_trace = FACLTrace(path="/home/user1/project", v=0)

    # test user1
    trace_result = facl_trace._trace(
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
    facl_trace = FACLTrace(path="/home/user1/project", v=0)

    # test user1 exact
    assert facl_trace.has_permission(
        acl="user:user1:rwx",
        mode="exact",
        _pytest_acls=acls_fixture,
    )

    # test user1 exact no match
    assert not facl_trace.has_permission(
        acl="user:user1:r-x",
        mode="exact",
        _pytest_acls=acls_fixture,
    )

    # test user1 at least
    assert facl_trace.has_permission(
        acl="user:user1:r-x",
        mode="at_least",
        _pytest_acls=acls_fixture,
    )

    # test user1 at most
    assert not facl_trace.has_permission(
        acl="user:user1:r-x",
        mode="at_most",
        _pytest_acls=acls_fixture,
    )

    # test group1 exact
    assert facl_trace.has_permission(
        acl="group:group1:r-x",
        mode="exact",
        _pytest_acls=acls_fixture,
    )

    # test group1 at least
    assert facl_trace.has_permission(
        acl="group:group1:--x",
        mode="at_least",
        _pytest_acls=acls_fixture,
    )

    # test group2 at least
    assert facl_trace.has_permission(
        acl="group:group2:--x",
        mode="at_least",
        _pytest_acls=acls_fixture,
    )

    # test group2 at most (no write)
    assert facl_trace.has_permission(
        acl="group:group2:rwx",
        mode="at_most",
        _pytest_acls=acls_fixture,
    )

    # test group2
    assert not facl_trace.has_permission(
        acl="group:group2:--x",
        mode="at_most",
        _pytest_acls=acls_fixture,
    )


def test_facl_trace_file_without_applicable_acl(acls_fixture_with_file):
    """
    Test that a file without an applicable ACL is still included in the trace.
    This is the bug fix: previously, if the file had no applicable ACL
    (e.g., getfacl failed or returned empty), it would break immediately
    and not include the file in the trace.
    """
    facl_trace = FACLTrace(path="/home/user1/file.txt", v=0)

    # test user2 - the file has empty ACL (simulating getfacl failure)
    trace_result = facl_trace._trace(
        acl="user:user2:rwx",
        mode="at_least",
        _pytest_acls=acls_fixture_with_file,
    )

    # The file should be included even though it has no ACLs
    trace_paths = [entry["path"] for entry in trace_result]

    # Assert that the file is in the trace (this would fail before the fix)
    assert (
        "/home/user1/file.txt" in trace_paths
    ), "File should be included in trace even without ACLs"

    # Verify that we have exactly one entry (the file)
    # The trace stops after encountering a file with no applicable ACL
    assert (
        len(trace_result) == 1
    ), "Trace should contain only the file since no applicable ACL was found"

    # Verify the file entry has no applicable ACL
    file_entry = trace_result[0]
    assert file_entry["path"] == "/home/user1/file.txt"
    assert (
        file_entry["applicable_acl"] is None
    ), "File with no ACLs should have None as applicable_acl"
    assert (
        file_entry["has_permission"] is False
    ), "File with no ACLs should have False for has_permission"
