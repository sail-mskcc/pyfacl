import logging
import subprocess

from pyfacl import logger


class FACL:
    """
    Represents a POSIX File Access Control List (FACL) for a given file or directory.
    """

    def __init__(self, v: int = 0, _facl: str = ""):
        """
        Initialize the FACL object. Args are used for debugging and testing.
        """
        self.logger = logger.setup_logger(
            __name__, level=logging.INFO if v == 0 else logging.DEBUG
        )
        self.is_init = False
        self.facl = _facl
        self.path = ""
        self.owner = ""
        self.group = ""
        self.flags = ""
        self.acls = []

    def parse(self, path: str):
        """
        Parse the FACL for the given file or directory path.
        Args:
            path (str): The file or directory path.
        """
        self.is_init = True
        self.facl = self._get_facl(path)
        self._parse_metadata()
        self._parse_acls()

    @staticmethod
    def _facl_available():
        """
        Check if the `getfacl` command is available on the system.

        Returns:
            bool: True if `getfacl` is available, False otherwise.
        """
        return (
            subprocess.call(
                ["which", "getfacl"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            == 0
        )

    def _get_facl(self, path: str) -> str:
        """
        Retrieve the FACL for the given path using the `getfacl` command.

        Args:
            path (str): The file or directory path.
        Returns:
            str: The raw FACL output from the `getfacl` command.
        """
        if not self._facl_available():
            self.logger.error("The 'getfacl' command is not available on this system.")
            return ""
        try:
            result = subprocess.run(
                ["getfacl", path], capture_output=True, text=True, check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error retrieving FACL for {path}: {e}")
            return ""

    def _parse_metadata(self):
        """
        Parse metadata, such as path, owner, groups and flags.

        Example:
        ```
        # file: data1/collab002/sail/isabl/datalake/prod/010/collaborators
        # owner: krauset
        # group: grp_hpc_collab002
        # flags: -s-
        ```
        """
        patterns = {
            "path": "# file: ",
            "owner": "# owner: ",
            "group": "# group: ",
            "flags": "# flags: ",
        }
        for key, pattern in patterns.items():
            if pattern not in self.facl:
                self.logger.warning(
                    f"Metadata pattern '{pattern}' not found in FACL output."
                )
                continue
            for line in self.facl.splitlines():
                if line.startswith(pattern):
                    setattr(self, key, line.split(":", 1)[1].strip())

    def _parse_acl(self, acl_line: str):
        """
        Parse a single ACL entry line.
        Example entries:
        ```
        user::rwx
        user:krauset:rwx
        group::r-x
        group:grp_hpc_collab002:r-x
        mask::rwx
        other::r-x
        default:user::rwx
        default:group::r-x
        """

        # parse
        acl_split = acl_line.split(":")
        if len(acl_split) not in [3, 4]:
            msg = (
                f"ACL line does not have the correct number of fields (3 or 4):"
                f"\nLine: {acl_line}\nFields: {acl_split}"
            )
            self.logger.warning(msg)
            return None

        # default
        default = len(acl_split) == 4
        if default:
            if acl_split[0] not in ["d", "default"]:
                msg = (
                    f"Unexpected default ACL prefix '{acl_split[0]}' in line:"
                    f"\n{acl_line}"
                )
                self.logger.warning(msg)
                return None
            acl_split = acl_split[1:]  # remove default prefix

        # type
        type_map = {
            "u": "user",
            "user": "user",
            "g": "group",
            "group": "group",
            "m": "mask",
            "mask": "mask",
            "o": "other",
            "other": "other",
        }
        if acl_split[0] not in type_map:
            self.logger.warning(
                f"Unexpected ACL type '{acl_split[0]}' in line:\n{acl_line}"
            )
            return None
        acl_type = type_map[acl_split[0]]

        # name
        name = acl_split[1]
        if name == "":
            if acl_type == "user":
                if not self.is_init:
                    self.logger.warning("FACL not initialized before parsing ACLs.")
                name = self.owner
            elif acl_type == "group":
                if not self.is_init:
                    self.logger.warning("FACL not initialized before parsing ACLs.")
                name = self.group

        # permissions
        permissions = acl_split[2]
        if not all(c in "rwx-" for c in permissions) or len(permissions) != 3:
            self.logger.warning(
                f"Invalid permissions '{permissions}' in line:\n{acl_line}"
            )
            return None

        # create
        acl_entry = {
            "default": default,
            "type": acl_type,
            "name": name,
            "permissions": permissions,
        }
        return acl_entry

    def _parse_acls(self):
        """
        Parse ACL entries from the FACL output.

        Example entries:
        ```
        user::rwx
        user:krauset:rwx
        group::r-x
        group:grp_hpc_collab002:r-x
        mask::rwx
        other::r-x
        default:user::rwx
        default:group::r-x
        default:other::r-x
        ```
        """
        for line in self.facl.splitlines():
            if line.startswith("#") or line.strip() == "":
                continue
            acl_entry = self._parse_acl(line)
            if acl_entry:
                self.acls.append(acl_entry)

    @staticmethod
    def _permission_match(perm_key: str, perm_query: str, mode: str) -> bool:
        """
        Check if the permission key matches the permission query for three different
        modes:

        Example: rwx vs rx
        - 'exact': both must match exactly
        - 'at_least': perm_key must have at least the permissions in perm_query
        - 'at_most': perm_key must have at most the permissions in perm_query

        Args:
            perm_key (str): The permission key (e.g., 'rwx').
            perm_query (str): The permission query (e.g., 'rx').
            mode (str): The matching mode ('exact', 'at_least', 'at_most').
        """
        if mode == "exact":
            return perm_key == perm_query
        elif mode == "at_least":
            for char_query in perm_query:
                if char_query != "-" and char_query not in perm_key:
                    return False
            return True
        elif mode == "at_most":
            for char_key in perm_key:
                if char_key != "-" and char_key not in perm_query:
                    return False
            return True
        else:
            raise ValueError(
                f"Invalid mode '{mode}'. Choose from 'exact', 'at_least', 'at_most'."
            )

    def _infer_groups(self, user: str) -> list:
        """
        Infer groups for a given user using the `id -Gn` command.

        Args:
            user (str): The username.
        Returns:
            list: List of groups the user belongs to.
        """
        try:
            result = subprocess.run(
                ["id", "-Gn", user], capture_output=True, text=True, check=True
            )
            groups = result.stdout.strip().split()
            return groups
        except subprocess.CalledProcessError as e:
            self.logger.warning(f"Error retrieving groups for user {user}: {e}")
            return []

    def has_permission(self, acl: str, mode: str = "at_least") -> bool:
        """
        Check if a specific user or group has a certain permission.
        Users are checked first, then groups, and finally 'other'.

        Args:
            entity_type (str): 'user' or 'group'.
            name (str): The name of the user or group.
            permission (str): The permission to check ('r', 'w', or 'x').
        """
        # parse acl
        acl_entry = self._parse_acl(acl)
        entity_type = acl_entry["type"]
        name = acl_entry["name"]
        permission = acl_entry["permissions"]

        # check user
        if entity_type in ["user"]:
            for acl in self.acls:
                if acl["default"]:
                    continue
                if acl["type"] == "user" and acl["name"] == name:
                    return self._permission_match(acl["permissions"], permission, mode)
        # check groups
        if entity_type in ["user", "group"]:
            if entity_type == "user":
                groups = self._infer_groups(name)
            else:
                groups = [name]
            for acl in self.acls:
                if acl["default"]:
                    continue
                if acl["type"] == "group" and acl["name"] in groups:
                    return self._permission_match(acl["permissions"], permission, mode)

        # check other
        if entity_type in ["user", "group", "other"]:
            for acl in self.acls:
                if acl["default"]:
                    continue
                if acl["type"] == "other":
                    return self._permission_match(acl["permissions"], permission, mode)
        return False
