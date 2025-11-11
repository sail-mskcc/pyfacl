import pytest

from pyfacl import FACL


@pytest.mark.production
def test_production_acl(tempfile_with_acl):

    # setup
    facl = FACL(path=tempfile_with_acl)

    # check 'other' permissions
    assert facl.has_permission("other::r-x", mode="exact")
    assert facl.has_permission("other::--x", mode="at_least")
    assert facl.has_permission("other::r-x", mode="at_most")
    assert not facl.has_permission("other::rwx", mode="at_least")
    assert not facl.has_permission("other::--x", mode="at_most")

    # check unknown user permissions
    assert facl.has_permission("user:unknown_user:r-x", mode="exact")
    assert facl.has_permission("user:unknown_user:--x", mode="at_least")
    assert facl.has_permission("user:unknown_user:r-x", mode="at_most")
    assert not facl.has_permission("user:unknown_user:rwx", mode="at_least")
    assert not facl.has_permission("user:unknown_user:--x", mode="at_most")
