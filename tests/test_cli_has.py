import logging
from io import StringIO

from typer.testing import CliRunner

from pyfacl.cli import app


def test_cli_has(tempfile_with_acl):
    """Test the CLI has command with a temporary file."""

    # Capture logger output from print_logger (not pyfacl_trace)
    log_capture = StringIO()
    log_handler = logging.StreamHandler(log_capture)
    logger = logging.getLogger("print_logger")
    logger.addHandler(log_handler)
    logger.setLevel(logging.INFO)

    runner = CliRunner()

    # Run the CLI command with other::r-x to avoid user lookup issues
    result = runner.invoke(app, ["has", tempfile_with_acl, "other::rwx"])

    # Check that command executed successfully
    assert result.exit_code == 0

    # Get captured log output
    log_output = log_capture.getvalue()

    # Should contain the final permission result message in stdout
    assert "NOT granted" in result.stdout

    # Check that we have trace output in logs
    assert log_output.strip(), f"Expected log output but got: '{log_output}'"

    # Check format of trace output
    log_lines = log_output.strip().split("\n")
    expected = ["✅", "✅", "❌"]

    for i, line in enumerate(log_lines):
        if line.strip() and ("✅" in line or "❌" in line):
            assert "::" in line  # Has ACL format
            assert "/" in line  # Has path
            assert line.split(")")[0].strip()[-1].isdigit()  # Has number) format
            assert (
                expected[i] in line
            ), f"Expected {expected[i]} in line but got: '{line}'"

    # Clean up
    logger.removeHandler(log_handler)


def test_cli_has_succeed(tempfile_with_acl):
    """Test the CLI has command with a temporary file."""

    # Capture logger output from print_logger (not pyfacl_trace)
    log_capture = StringIO()
    log_handler = logging.StreamHandler(log_capture)
    logger = logging.getLogger("print_logger")
    logger.addHandler(log_handler)
    logger.setLevel(logging.INFO)

    runner = CliRunner()

    # Run the CLI command with other::r-x to avoid user lookup issues
    result = runner.invoke(app, ["has", tempfile_with_acl, "other::r-x"])

    # Check that command executed successfully
    assert result.exit_code == 0

    # Get captured log output
    log_output = log_capture.getvalue()

    # Should contain the final permission result message in stdout
    assert "is granted" in result.stdout

    # Check that we have trace output in logs
    assert log_output.strip(), f"Expected log output but got: '{log_output}'"

    # Check format of trace output
    log_lines = log_output.strip().split("\n")
    expected = ["✅", "✅", "✅"]

    for i, line in enumerate(log_lines):
        if line.strip() and ("✅" in line or "❌" in line):
            assert "::" in line  # Has ACL format
            assert "/" in line  # Has path
            assert line.split(")")[0].strip()[-1].isdigit()  # Has number) format
            assert (
                expected[i] in line
            ), f"Expected {expected[i]} in line but got: '{line}'"

    # Clean up
    logger.removeHandler(log_handler)


def test_cli_has_at_most(tempfile_with_acl):
    """Test the CLI has command with a temporary file."""

    # Capture logger output from print_logger (not pyfacl_trace)
    log_capture = StringIO()
    log_handler = logging.StreamHandler(log_capture)
    logger = logging.getLogger("print_logger")
    logger.addHandler(log_handler)
    logger.setLevel(logging.INFO)

    runner = CliRunner()

    # Run the CLI command with other::r-x to avoid user lookup issues
    result = runner.invoke(
        app, ["has", tempfile_with_acl, "other::rwx", "--mode", "at_most"]
    )

    # Check that command executed successfully
    assert result.exit_code == 0

    # Get captured log output
    log_output = log_capture.getvalue()

    # Should contain the final permission result message in stdout
    assert "is granted" in result.stdout

    # Check that we have trace output in logs
    assert log_output.strip(), f"Expected log output but got: '{log_output}'"

    # Check format of trace output
    log_lines = log_output.strip().split("\n")
    expected = ["✅", "✅", "❌"]

    for i, line in enumerate(log_lines):
        if line.strip() and ("✅" in line or "❌" in line):
            assert "::" in line  # Has ACL format
            assert "/" in line  # Has path
            assert line.split(")")[0].strip()[-1].isdigit()  # Has number) format
            assert (
                expected[i] in line
            ), f"Expected {expected[i]} in line but got: '{line}'"

    # Clean up
    logger.removeHandler(log_handler)
