"""Sphinx documentation configuration file."""

# cSpell:disable

import os
from datetime import datetime
import sys
from pathlib import Path

from ansys_sphinx_theme import (
    ansys_favicon,
    get_version_match,
)

src = Path(__file__).parents[2] / "src"
if not src.exists():
    raise Exception(f"Cannot find sources: {src}")
sys.path.append(str(src))

from ansys.scadeone.core import __version__, version_info  # noqa
from ansys.scadeone.core.common.versioning import FormatVersions  # noqa

# Project information
project = "PyScadeOne"
copyright = f"(c) {datetime.now().year} ANSYS, Inc. All rights reserved"
author = "ANSYS, Inc."
version = f"{version_info.major}.{version_info.minor}"
release = f"{version}{' - Prerelease' if version_info.pre_release else ''}"

# Selection of documentation parts
config = {}
config["clock"] = False
config["clock_exclude"] = ["api/language/clock.rst"]

# PyScadeOne service versions
supported_versions = Path(__file__).parent / "getting_started/versions.rst"
supported_versions.write_text(FormatVersions.get_versions())


# Copy button customization ---------------------------------------------------
# exclude traditional Python prompts from the copied code
copybutton_prompt_text = r">>> ?|\.\.\. "
copybutton_prompt_is_regexp = True

# Sphinx extensions

extensions = [
    "numpydoc",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.intersphinx",
    "sphinx_copybutton",
    "sphinx.ext.inheritance_diagram",
    "sphinx_design",
    "sphinx_jinja",
]


exclude_patterns = [
    "changelog.rst",
]

if not config["clock"]:
    exclude_patterns.extend(config["clock_exclude"])

# Make sure the target is unique for auto label
# see: https://docs.readthedocs.io/en/stable/guides/cross-referencing-with-sphinx.html
autosectionlabel_prefix_document = True
suppress_warnings = [
    "autosectionlabel.*",
]

# Intersphinx mapping
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    # kept here as an example
    # "scipy": ("https://docs.scipy.org/doc/scipy/reference", None),
    # "numpy": ("https://numpy.org/devdocs", None),
    # "matplotlib": ("https://matplotlib.org/stable", None),
    # "pandas": ("https://pandas.pydata.org/pandas-docs/stable", None),
    # "pyvista": ("https://docs.pyvista.org/", None),
    # "grpc": ("https://grpc.github.io/grpc/python/", None),
}

## numpydoc configuration
# Note: this is key for autosummary, else it fails.
numpydoc_show_class_members = False
numpydoc_xref_param_type = True
#

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix(es) of source filenames.
source_suffix = {".rst": "restructuredtext", ".md": "markdown"}

# The master toctree document.
master_doc = "index"

inherited_members = True

toc_object_entries = False

# use the default pyansys logo
html_favicon = ansys_favicon
html_theme = "ansys_sphinx_theme"
html_short_title = html_title = "PyScadeOne"

# multi-version documentation
cname = os.getenv("DOCUMENTATION_CNAME", default="scadeone.docs.pyansys.com")
"""The canonical name of the webpage hosting the documentation."""

# specify the location of your github repo
html_theme_options = {
    "github_url": "https://github.com/ansys/pyscadeone",
    "show_prev_next": False,
    "show_breadcrumbs": True,
    "additional_breadcrumbs": [
        ("PyAnsys", "https://docs.pyansys.com/"),
    ],
    "switcher": {
        "json_url": f"https://{cname}/versions.json",
        "version_match": get_version_match(__version__),
    },
    "check_switcher": True,
    "logo": "pyansys",
    "ansys_sphinx_theme_autoapi": {
        "project": project,
        "own_page_level": "function",
        "class_content": "both",  # documentation in https://sphinxdocs.ansys.com/version/stable/user-guide/autoapi.html
    },
}

# TODO: uncomment when we have static files
# html_static_path = ["_static"]

# These paths are either relative to html_static_path
# or fully qualified paths (eg. https://...)
html_css_files = []

autodoc_default_options = {
    "members": True,
    "member-order": "groupwise",
    # 'undoc-members': True,
    """_summary_
    """
    "exclude-members": "__weakref__",
    "inherited-members": True,
    "show-inheritance": True,
}

# Jinja context for documentation
jinja_contexts = {
    "clock_ctx": {"clock": config["clock"]},
}

# FIXME: to be removed when the documentation is published
# For now, we ignore the following links when checking for broken links
linkcheck_ignore = [
    "https://scadeone.docs.pyansys.com/*",
    "https://github.com/ansys/pyscadeone/*",
    "https://www.ansys.com/*",
]
linkcheck_exclude_documents = ["changelog.rst"]
