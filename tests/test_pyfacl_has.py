from pyfacl import FACLHas


def test_facl_has(acls_fixture):
    facl_has = FACLHas(path="/home/user1/project", v=0)

    # test user1
    has_permission = facl_has.has_permission(
        acl="user:user1:r-x",
        mode="at_least",
        _pytest_acls=acls_fixture,
    )
    assert has_permission

    has_permission = facl_has.has_permission(
        acl="user:user1:rwx",
        mode="at_least",
        _pytest_acls=acls_fixture,
    )
    assert has_permission

    # test root 'at_least'
    has_permission = facl_has.has_permission(
        acl="user:root:rwx",
        mode="at_least",
        _pytest_acls=acls_fixture,
    )
    assert not has_permission

    # test group2
    has_permission = facl_has.has_permission(
        acl="group:group2:r-x",
        mode="at_least",
        _pytest_acls=acls_fixture,
    )
    assert has_permission

    # test group2
    has_permission = facl_has.has_permission(
        acl="group:group2:rwx",
        mode="at_least",
        _pytest_acls=acls_fixture,
    )
    assert not has_permission

    # test group2
    has_permission = facl_has.has_permission(
        acl="group:group2:rwx",
        mode="at_most",
        _pytest_acls=acls_fixture,
    )
    assert has_permission

    # test group2
    has_permission = facl_has.has_permission(
        acl="group:group2:--x",
        mode="at_most",
        _pytest_acls=acls_fixture,
    )
    assert not has_permission
