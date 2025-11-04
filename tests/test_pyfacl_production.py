import os
import tempfile

import pytest

from pyfacl import FACL


@pytest.fixture
def tempfile_with_acl():
    filepath = tempfile.NamedTemporaryFile(delete=False)

    # add 'other' ACL entry
    os.system(f"setfacl -m o::r-x {filepath.name}")
    yield filepath.name

    # cleanup
    os.remove(filepath.name)


@pytest.mark.production
def test_production_acl(tempfile_with_acl):

    # setup
    facl = FACL()
    facl.parse(tempfile_with_acl)

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
