import typer

from pyfacl import FACLHas, FACLTrace

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
    facl_has = FACLHas(path=path, v=1)
    has_permission = facl_has.has_permission(acl, mode)
    if has_permission:
        typer.echo(f"Permission '{mode}' for ACL '{acl}' is granted on path '{path}'.")
    else:
        typer.echo(
            f"Permission '{mode}' for ACL '{acl}' is NOT granted on path '{path}'."
        )


def main():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
