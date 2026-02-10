import os

import typer

from pyfacl import FACL, FACLTrace

app = typer.Typer(
    help="pyfacl: A tool to manage and analyze POSIX file ACLs.", no_args_is_help=True
)


@app.command("trace")
def permission_trace(
    path: str = typer.Argument(..., help="The file or directory path to trace."),
    acl: str = typer.Argument(
        ..., help="The ACL string to check (e.g., 'user:user1:rwx')."
    ),
    mode: str = typer.Option(
        "at_least",
        help="The mode, must be 'exact', 'at_least', 'at_most'.",
    ),
):
    """
    Trace and analyze ACL permissions through a directory hierarchy.
    """
    facl_trace = FACLTrace(path=path, v=1)
    has_permission = facl_trace.has_permission(acl, mode)
    if has_permission:
        typer.echo(f"Permission '{mode}' for ACL '{acl}' is granted on path '{path}'.")
    else:
        typer.echo(
            f"Permission '{mode}' for ACL '{acl}' is NOT granted on path '{path}'."
        )


@app.command("has")
def permission_has(
    path: str = typer.Argument(..., help="The file or directory path to get ACL from."),
    acl: str = typer.Argument(
        ..., help="The ACL string to check (e.g., 'user:user1:rwx')."
    ),
    mode: str = typer.Option(
        "at_least", help="The mode, must be 'exact', 'at_least', 'at_most'."
    ),
):
    """
    Check if user/group can navigate to path (--x), and specified ACL granted.
    """
    # get trace and final paths
    facl_trace = FACLTrace(path=os.path.dirname(path), v=1)
    facl_path = FACL(path=path, v=1)

    # replace acl with --x for navigation check
    acl_nav = ":".join(acl.split(":")[:-1] + ["--x"])
    can_navigate = facl_trace.has_permission(acl_nav, "at_least")
    has_permission = facl_path.has_permission(acl, mode)
    if can_navigate and has_permission:
        msg = (
            f"User/group can navigate to '{path}'\n"
            f"User/group has '{mode}' permission for ACL '{acl}'."
        )
    elif not can_navigate and has_permission:
        msg = (
            f"User/group cannot navigate to '{path}'\n"
            f"User/group has '{mode}' permission for ACL '{acl}'."
        )
    elif can_navigate and not has_permission:
        msg = (
            f"User/group can navigate to '{path}'\n"
            f"User/group does NOT have '{mode}' permission for ACL '{acl}'."
        )
    else:
        msg = (
            f"User/group cannot navigate to '{path}'\n"
            f"User/group does NOT have '{mode}' permission for ACL '{acl}'."
        )
    typer.echo(msg)


def main():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
