"""
Test to verify CI environment has necessary ACL tools.
This test ensures that GitHub Actions runners have the required
system dependencies (getfacl, setfacl) installed.
"""

import shutil
import subprocess

import pytest


def test_getfacl_available():
    """Test that getfacl command is available in the system."""
    assert (
        shutil.which("getfacl") is not None
    ), "getfacl command not found in PATH"


def test_setfacl_available():
    """Test that setfacl command is available in the system."""
    assert (
        shutil.which("setfacl") is not None
    ), "setfacl command not found in PATH"


def test_getfacl_version():
    """Test that getfacl can be executed and returns version info."""
    try:
        result = subprocess.run(
            ["getfacl", "--version"],
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        )
        assert result.returncode == 0
        assert len(result.stdout) > 0 or len(result.stderr) > 0
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        pytest.fail(f"getfacl --version failed: {e}")


def test_setfacl_version():
    """Test that setfacl can be executed and returns version info."""
    try:
        result = subprocess.run(
            ["setfacl", "--version"],
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        )
        assert result.returncode == 0
        assert len(result.stdout) > 0 or len(result.stderr) > 0
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        pytest.fail(f"setfacl --version failed: {e}")
