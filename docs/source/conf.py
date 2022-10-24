# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join("..", "..")))

import re

# -- Project information -----------------------------------------------------

project = "hikari-flare"
copyright = "2022, Lunarmagpie"
author = "Lunarmagpie"

with open("../../flare/__init__.py") as fp:
    file = fp.read()

if _match := re.search(r"__version__ = \"([^\"]+)", file):
    version = _match.group(1)
    release = version
else:
    raise RuntimeError("Improperly formatted flare/__init__.py file")

master_doc = "index"

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "myst_parser",
    "sphinx_immaterial",
]

autodoc_default_options = {"member-order": "groupwise"}

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "hikari": ("https://hikari-py.github.io/hikari", None),
}

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_immaterial"

# material theme options (see theme.conf for more information)
html_theme_options = {
    "icon": {
        "repo": "fontawesome/brands/github",
    },
    "site_url": "https://lunarmagpie.github.io/hikari-flare/",
    "repo_url": "https://github.com/Lunarmagpie/hikari-flare",
    "repo_name": "hikari-flare",
    "repo_type": "github",
    "features": [
        "navigation.expand",
        "navigation.tabs",
        "toc.integrate",
        "navigation.sections",
        "navigation.instant",
        "header.autohide",
        "navigation.top",
        "navigation.tracking",
        "search.highlight",
        "search.share",
        "toc.follow",
        "toc.sticky",
    ],
    "palette": [
        {
            "media": "(prefers-color-scheme: light)",
            "scheme": "default",
            "primary": "red",
            "accent": "pink",
            "toggle": {
                "icon": "material/lightbulb-outline",
                "name": "Switch to dark mode",
            },
        },
        {
            "media": "(prefers-color-scheme: dark)",
            "scheme": "slate",
            "primary": "red",
            "accent": "pink",
            "toggle": {
                "icon": "material/lightbulb",
                "name": "Switch to light mode",
            },
        },
    ],
    # END: version_dropdown
    "toc_title_is_page_title": True,
}
