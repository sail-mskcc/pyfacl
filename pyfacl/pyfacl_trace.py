import os

from pyfacl import FACL, logger


class FACLTrace:
    """
    Analyze and trace ACLs through directory hierarchy.
    """

    def __init__(self, path: str = None, v: int = 0) -> None:
        self.logger = logger.logger_basic(__name__, v)
        self.print = logger.logger_print(v)
        self.v = v
        self.path = path

        # catch common error that path and acl are mixed up
        if "/" not in path and ":" in path:
            raise ValueError(
                f"Path looks like an ACL entry. Please check your input:\nPath: {path}"
            )

    def _trace(self, acl: str, mode: str, _pytest_acls: dict = None) -> list:
        """
        Trace and return all applicable ACLs for the given path.

        Args:
            path (str): The file or directory path to trace.
            acl (str): The ACL string to check (e.g., "user:user1:rwx").
            mode (str): The permission mode to check (e.g., "r", "w", "x").
            _pytest_acls (dict, optional): For testing purposes with pre-defined ACLs.

        Returns:
            List[dict]: List of dictionaries with applicable ACLs, path, and permission
        """
        trace = []
        current_path = self.path
        if not current_path.startswith("/"):
            current_path = os.path.abspath(current_path)

        while True:

            # get info (from pytest dict or by parsing)
            if _pytest_acls is None:
                facl = FACL(path=current_path, v=self.v)
            else:
                facl_str = _pytest_acls[current_path]
                facl = FACL(v=self.v, _facl=facl_str)
                facl.is_init = True
                facl._parse_metadata()
                facl._parse_acls()

            # check for applicable ACL
            applicable_acl = facl.get_applicable_acl(acl)
            # Default to False when no applicable ACL exists
            # Only check permission if we have an applicable ACL
            has_permission = False
            if applicable_acl:
                has_permission = facl.has_permission(acl, mode)

            # store info
            trace_entry = {
                "path": current_path,
                "applicable_acl": applicable_acl,
                "has_permission": has_permission,
            }
            trace.append(trace_entry)

            # stop traversing if no applicable ACL found
            if not applicable_acl:
                break

            # move up one directory
            parent_path = os.path.dirname(current_path)
            if parent_path == current_path:
                break
            current_path = parent_path

        # reverse and add index
        trace.reverse()
        for i, entry in enumerate(trace):
            entry["index"] = i
        return trace

    def _print_permission(self, trace_entry: dict) -> None:
        """
        Print the permission trace for a given path.
        """
        color = {
            True: "\033[92m",  # Green for granted
            False: "\033[91m",  # Red for denied
        }[trace_entry["has_permission"]]
        emoji = {
            True: "✅",
            False: "❌",
        }[trace_entry["has_permission"]]

        # Handle case where no applicable ACL was found
        if trace_entry["applicable_acl"] is None:
            acl_info = "NO_ACL"
        else:
            acl_info = trace_entry["applicable_acl"]["line"]

        self.print.info(
            (
                f"{color}{trace_entry['index']}) {emoji} "
                f"{acl_info} "
                f"{trace_entry['path']}\033[0m"
            )
        )

    def has_permission(self, acl: str, mode: str, _pytest_acls: dict = None) -> bool:
        """
        Check if a specific user or group has a certain permission at the given path.
        """

        trace = self._trace(acl, mode, _pytest_acls=_pytest_acls)

        has = True
        for entry in trace:
            if not entry["has_permission"]:
                has = False
            self._print_permission(entry)
        return has
