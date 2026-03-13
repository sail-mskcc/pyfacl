# isort: skip_file

from .pyfacl import FACL
from .pyfacl_trace import FACLTrace
from .pyfacl_has import FACLHas


def has_permission(
    path: str,
    acl: str,
    mode: str = "at_least",
    trace: bool = False,
    can_execute: bool = False,
    v: int = 0,
    _pytest_acls: dict = None,
) -> bool:
    """
    Check if a user or group has a certain permission for a given path.

    Args:
        path (str): The file or directory path to check.
        acl (str): The ACL string to check (e.g., "user:user1:rwx").
        mode (str): The permission mode ("at_least", "exact", or "at_most").
            Defaults to "at_least".
        trace (bool): If True, the permission must be granted at every level of the
            directory hierarchy from root to the target path. Cannot be combined with
            can_execute. Defaults to False.
        can_execute (bool): If True, the user/group must have execute (--x) permission
            on every parent directory up to the target path, and the specified
            permission+mode for the target path only. Cannot be combined with trace.
            Defaults to False.
        v (int): Verbosity level. Defaults to 0.
        _pytest_acls (dict, optional): Pre-defined ACL dictionary for testing purposes.

    Returns:
        bool: True if the permission check passes, False otherwise.

    Raises:
        ValueError: If both trace and can_execute are True.
    """
    if trace and can_execute:
        msg = (
            "Cannot set both 'trace' and 'can_execute' to True:\n"
            "  - 'trace' requires permissions at every level of the "
            "directory hierarchy.\n"
            "  - 'can_execute' requires execute permission on every "
            "parent directory.\n"
        )
        raise ValueError(msg)

    if trace:
        return FACLTrace(path=path, v=v).has_permission(
            acl, mode, _pytest_acls=_pytest_acls
        )

    if can_execute:
        return FACLHas(path=path, v=v).has_permission(
            acl, mode, _pytest_acls=_pytest_acls
        )

    # Basic single-path check
    if _pytest_acls is not None:
        facl = FACL(_facl=_pytest_acls[path], v=v)
        facl.is_init = True
        facl._parse_metadata()
        facl._parse_acls()
        return facl.has_permission(acl, mode)

    return FACL(path=path, v=v).has_permission(acl, mode)


__all__ = ["FACL", "FACLTrace", "FACLHas", "has_permission"]
