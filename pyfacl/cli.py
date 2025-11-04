import typer

from pyfacl import FACLTrace

app = typer.Typer(help="pyfacl: A tool to manage and analyze POSIX file ACLs.")


@app.command()
def permission_trace(
    path: str = typer.Argument(..., help="The file or directory path to trace."),
    acl: str = typer.Argument(
        ..., help="The ACL string to check (e.g., 'user:user1:rwx')."
    ),
    mode: str = typer.Argument(
        ...,
        help="The mode, must be 'exact', 'at_least', 'at_most'.",
    ),
):
    """
    Trace and analyze ACL permissions through a directory hierarchy.
    """
    facl_trace = FACLTrace(v=1)
    has_permission = facl_trace.has_permission(path, acl, mode)
    if has_permission:
        typer.echo(f"Permission '{mode}' for ACL '{acl}' is granted on path '{path}'.")
    else:
        typer.echo(
            f"Permission '{mode}' for ACL '{acl}' is NOT granted on path '{path}'."
        )


if __name__ == "__main__":
    app()
