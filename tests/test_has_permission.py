import pytest

import pyfacl


def test_has_permission_basic(acls_fixture):
    """Basic single-file permission check (trace=False, can_execute=False)."""
    # user1 owns /home/user1/project, so user::rwx applies
    assert pyfacl.has_permission(
        "/home/user1/project",
        "user:user1:r-x",
        mode="at_least",
        _pytest_acls=acls_fixture,
    )
    assert pyfacl.has_permission(
        "/home/user1/project",
        "user:user1:rwx",
        mode="exact",
        _pytest_acls=acls_fixture,
    )
    # root only has r-x at this path, not rwx
    assert not pyfacl.has_permission(
        "/home/user1/project",
        "user:root:rwx",
        mode="at_least",
        _pytest_acls=acls_fixture,
    )
    # at_most: root has r-x, querying rwx → at_most fails (r-x ⊄ rwx is wrong direction)
    # root has r-x, querying r-x at_most passes
    assert pyfacl.has_permission(
        "/home/user1/project",
        "user:root:r-x",
        mode="at_most",
        _pytest_acls=acls_fixture,
    )


def test_has_permission_trace(acls_fixture):
    """Trace mode: permission must be granted at every directory level."""
    # user1 has rwx everywhere in the fixture
    assert pyfacl.has_permission(
        "/home/user1/project",
        "user:user1:r-x",
        mode="at_least",
        trace=True,
        _pytest_acls=acls_fixture,
    )
    # root only has r-x at /home/user1 and /home/user1/project but rwx at
    # /home and / (via user::rwx owner match), so at_least rwx fails
    assert not pyfacl.has_permission(
        "/home/user1/project",
        "user:root:rwx",
        mode="at_least",
        trace=True,
        _pytest_acls=acls_fixture,
    )
    # group2 only has r-x at /home/user1/project; parent dirs fall to other::--x
    assert not pyfacl.has_permission(
        "/home/user1/project",
        "group:group2:r-x",
        mode="at_least",
        trace=True,
        _pytest_acls=acls_fixture,
    )


def test_has_permission_can_execute(acls_fixture):
    """can_execute mode: execute on all parents, specified perm on file only."""
    # user1 can navigate (has --x everywhere) and has rwx on the target
    assert pyfacl.has_permission(
        "/home/user1/project",
        "user:user1:r-x",
        mode="at_least",
        can_execute=True,
        _pytest_acls=acls_fixture,
    )
    # group2 cannot navigate (other::--x on parents only, which gives --x,
    # but FACLHas checks navigate as at_least --x, which passes)
    # group2 has r-x on the target → passes
    assert pyfacl.has_permission(
        "/home/user1/project",
        "group:group2:r-x",
        mode="at_least",
        can_execute=True,
        _pytest_acls=acls_fixture,
    )
    # group2 does NOT have rwx on the target (only r-x)
    assert not pyfacl.has_permission(
        "/home/user1/project",
        "group:group2:rwx",
        mode="at_least",
        can_execute=True,
        _pytest_acls=acls_fixture,
    )


def test_has_permission_both_flags_raises():
    """trace and can_execute cannot both be True."""
    with pytest.raises(ValueError, match="cannot both be True"):
        pyfacl.has_permission(
            "/some/path",
            "user:user1:r-x",
            trace=True,
            can_execute=True,
        )


def test_has_permission_default_mode(acls_fixture):
    """Default mode is at_least."""
    # user1 has rwx, querying r-x with default at_least should pass
    assert pyfacl.has_permission(
        "/home/user1/project",
        "user:user1:r-x",
        _pytest_acls=acls_fixture,
    )
