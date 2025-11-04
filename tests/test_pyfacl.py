import pytest

from pyfacl import FACL


@pytest.fixture
def facl_fixture():
    facl = """
# file: testfile
# owner: user1
# group: group1
# flags: -s-
user::rwx
group::r-x
other::r-x
d:user::rwx
d:g::r-x
o::r-x
"""
    return facl


def test_parse_acl(facl_fixture):

    facl = FACL(v=1, _facl=facl_fixture)

    acl_entry = facl._parse_acl("default:user::rwx")
    assert acl_entry["default"] is True
    assert acl_entry["type"] == "user"
    assert acl_entry["name"] == ""
    assert acl_entry["permissions"] == "rwx"

    acl_entry = facl._parse_acl("d:u:krauset:rwx")
    assert acl_entry["default"] is True
    assert acl_entry["type"] == "user"
    assert acl_entry["name"] == "krauset"
    assert acl_entry["permissions"] == "rwx"

    acl_entry = facl._parse_acl("group:grp_hpc_collab002:r-x")
    assert acl_entry["default"] is False
    assert acl_entry["type"] == "group"
    assert acl_entry["name"] == "grp_hpc_collab002"
    assert acl_entry["permissions"] == "r-x"

    acl_entry = facl._parse_acl("g:grp_hpc_collab002:r-x")
    assert acl_entry["default"] is False
    assert acl_entry["type"] == "group"
    assert acl_entry["name"] == "grp_hpc_collab002"
    assert acl_entry["permissions"] == "r-x"

    acl_entry = facl._parse_acl("other::r-x")
    assert acl_entry["default"] is False
    assert acl_entry["type"] == "other"
    assert acl_entry["name"] == ""
    assert acl_entry["permissions"] == "r-x"


def test_permission_match(facl_fixture):
    facl = FACL(v=1, _facl=facl_fixture)

    # exact
    assert facl._permission_match("rwx", "rwx", "exact")
    assert facl._permission_match("---", "---", "exact")
    assert not facl._permission_match("rwx", "rx", "exact")
    assert not facl._permission_match("r--", "rwx", "exact")

    # at least
    assert facl._permission_match("rwx", "rx", "at_least")
    assert facl._permission_match("r--", "r--", "at_least")
    assert facl._permission_match("rwx", "---", "at_least")
    assert facl._permission_match("rwx", "w", "at_least")
    assert facl._permission_match("rwx", "x", "at_least")
    assert facl._permission_match("rwx", "rw", "at_least")
    assert not facl._permission_match("r-x", "rwx", "at_least")
    assert not facl._permission_match("r--", "w", "at_least")

    # at most
    assert facl._permission_match("r-x", "rx", "at_most")
    assert facl._permission_match("---", "---", "at_most")
    assert facl._permission_match("rwx", "rwx", "at_most")
    assert facl._permission_match("r--", "rwx", "at_most")
    assert facl._permission_match("w--", "rwx", "at_most")
    assert not facl._permission_match("rwx", "rx", "at_most")
    assert not facl._permission_match("rwx", "w", "at_most")
    assert not facl._permission_match("rwx", "---", "at_most")


def test_parse_metadata(facl_fixture):
    facl = FACL(v=1, _facl=facl_fixture)

    facl._parse_metadata()
    assert facl.path == "testfile"
    assert facl.owner == "user1"
    assert facl.group == "group1"
    assert facl.flags == "-s-"


def test_parse_acls(facl_fixture):
    facl = FACL(v=1, _facl=facl_fixture)

    facl._parse_metadata()
    facl._parse_acls()
    assert len(facl.acls) == 6

    expected_acls = [
        {"default": False, "type": "user", "name": "user1", "permissions": "rwx"},
        {"default": False, "type": "group", "name": "group1", "permissions": "r-x"},
        {"default": False, "type": "other", "name": "", "permissions": "r-x"},
        {"default": True, "type": "user", "name": "user1", "permissions": "rwx"},
        {"default": True, "type": "group", "name": "group1", "permissions": "r-x"},
        {"default": False, "type": "other", "name": "", "permissions": "r-x"},
    ]

    for acl, expected in zip(facl.acls, expected_acls):
        assert acl == expected


def test_has_permission(facl_fixture):
    facl = FACL(v=1, _facl=facl_fixture)

    facl._parse_metadata()
    facl._parse_acls()

    # user1 permissions
    assert facl.has_permission("user:user1:rwx", mode="exact")
    assert facl.has_permission("user:user1:r-x", mode="at_least")
    assert facl.has_permission("user:user1:rw-", mode="at_least")
    assert facl.has_permission("user:user1:rwx", mode="at_most")
    assert not facl.has_permission("user:user1:r-x", mode="at_most")

    # group1 permissions
    assert facl.has_permission("group:group1:r-x", mode="exact")
    assert facl.has_permission("group:group1:--x", mode="at_least")
    assert facl.has_permission("group:group1:r-x", mode="at_most")
    assert facl.has_permission("group:group1:rwx", mode="at_most")
    assert not facl.has_permission("group:group1:rwx", mode="at_least")

    # other permissions
    assert facl.has_permission("other::r-x", mode="exact")
    assert facl.has_permission("other::--x", mode="at_least")
    assert facl.has_permission("other::r-x", mode="at_most")
    assert facl.has_permission("other::rwx", mode="at_most")
    assert not facl.has_permission("other::rwx", mode="at_least")

    # unknown user fallback to other
    assert facl.has_permission("user:unknown_user:r-x", mode="exact")
    assert facl.has_permission("user:unknown_user:--x", mode="at_least")
    assert facl.has_permission("user:unknown_user:r-x", mode="at_most")
    assert facl.has_permission("user:unknown_user:rwx", mode="at_most")
    assert not facl.has_permission("user:unknown_user:rwx", mode="at_least")

    # unknown group fallback to other
    assert facl.has_permission("group:unknown_group:r-x", mode="exact")
    assert facl.has_permission("group:unknown_group:--x", mode="at_least")
    assert facl.has_permission("group:unknown_group:r-x", mode="at_most")
    assert facl.has_permission("group:unknown_group:rwx", mode="at_most")
    assert not facl.has_permission("group:unknown_group:rwx", mode="at_least")
