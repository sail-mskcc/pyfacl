import typer

from pyfacl import FACLTrace

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


@app.command("show")
def permission_show():
    """
    Show command placeholder.
    """
    typer.echo("Show command is not yet implemented.")


def main():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
