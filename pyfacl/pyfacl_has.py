import os

from pyfacl import FACL, FACLTrace, logger


class FACLHas:
    """
    Check if user/group can navigate to path (--x), and specified ACL granted.
    """

    def __init__(self, path: str = None, v: int = 0) -> None:
        self.logger = logger.logger_basic(__name__, v)
        self.print = logger.logger_print(v)
        self.v = v
        self.path = path

    def has_permission(self, acl: str, mode: str, _pytest_acls: dict = None) -> bool:
        """
        Check if user/group can navigate to path (--x), and specified ACL granted.

        Args:
            path (str): The file or directory path to check.
            acl (str): The ACL string to check (e.g., "user:user1:rwx").
            mode (str): The permission mode (e.g., "at_least", "exact", "at_most").
            _pytest_acls (dict, optional): A dictionary of ACLs for testing purposes.

        Returns:
            bool: True if user/group can navigate and has ACL permission.
        """
        # get trace and final paths
        facl_trace = FACLTrace(path=os.path.dirname(self.path), v=self.v)
        if _pytest_acls is None:
            facl_path = FACL(path=self.path, v=self.v)
        else:
            facl_path = FACL(_facl=_pytest_acls[self.path], v=self.v)
            facl_path.is_init = True
            facl_path._parse_metadata()
            facl_path._parse_acls()

        # replace acl with --x for navigation check
        acl_nav = ":".join(acl.split(":")[:-1] + ["--x"])
        can_navigate = facl_trace.has_permission(
            acl_nav, "at_least", _pytest_acls=_pytest_acls
        )
        has_permission = facl_path.has_permission(acl, mode)
        return can_navigate and has_permission
