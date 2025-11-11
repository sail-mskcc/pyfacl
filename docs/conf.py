import os
import sys

sys.path.insert(0, os.path.abspath(".."))

# Configuration file for the Sphinx documentation builder.
project = "PyFACL"
copyright = "2025, tobiaspk"
author = "tobiaspk"
release = "1.2.0"

# -- General configuration ---------------------------------------------------
extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output ------------------------------------------------
html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

# -- MyST configuration -----------------------------------------------------
myst_enable_extensions = [
    "colon_fence",
    "deflist",
]

# Source file suffixes
source_suffix = {
    ".rst": None,
    ".md": "myst_parser",
}
