"""The module which managers user configuration settings.

Most of these functions are just thin wraps around :ref:`rez-config` calls.

"""

import platform

from rez.config import config


_BASIC_EXTENSIONS = (
    "--ext-autodoc",  # Needed for auto-documentation generation later
    "--ext-intersphinx",  # Needed to find + load external Rez package Sphinx data
    "--ext-viewcode",  # Technically optional, but I think it's cool to always have
)


# TODO : Add caching here
def get_build_documentation_key():
    """str: Get the :ref:`rez tests attribute` key which builds via :ref:`rez_sphinx`."""
    rez_sphinx_settings = _get_base_settings()

    return rez_sphinx_settings.get("build_documentation_key") or "build_documentation"


# TODO : Add caching here
def get_help_label():
    """str: Get the :ref:`rez help attribute` which connects with :ref:`intersphinx`."""
    rez_sphinx_settings = _get_base_settings()

    return rez_sphinx_settings.get("help_label") or "rez_sphinx_objects_inv"


def _get_base_settings():
    """dict[str, object]: Get all :ref:`rez_sphinx` specific default settings."""
    return config.optionvars.get("rez_sphinx") or dict()


def _get_quick_start_overridable_options(overrides=tuple()):
    """Get all :ref:`sphinx-quickstart` parameters which the user can modify.

    Args:
        overrides (list[str], optional):
            :ref:`sphinx-quickstart` user settings to prefer over the
            defaults, if any. e.g. ``["--sep"]``.

    Returns:
        list[str]: The resolved "user + :ref:`rez_sphinx`" :ref:`sphinx-quickstart` settings.

    """
    output = list(overrides)

    if "--no-sep" not in output:
        output.append("--sep")  # if specified, separate source and build dirs

    if "--language" not in output and "-l" not in output:
        # Assume English, if no language could be found.
        output.extend(["--language", "en"])

    if "--makefile" not in output and "--no-makefile" not in output:
        output.append("--no-makefile")

    if "--batchfile" not in output and "--no-batchfile" not in output:
        if platform.system() == "Windows":
            output.append("--batchfile")
        else:
            output.append("--no-batchfile")

    return output


def get_quick_start_options(options=tuple()):
    """Get the arguments :ref:`sphinx-quickstart`.

    Args:
        options (list[str], optional):
            User-provided arguments to consider while resolving
            :ref:`sphinx-quickstart` values.

    Raises:
        :class:`.UserInputError:
            If the user attempted to pass settings which may only be
            edited by :ref:`rez_sphinx`, fail this function early.
            Examples of "reserved" parameters are "--project", which are
            meant to be set by the Rez package name.

    Returns:
        list[str]: Any arguments to pass to sphinx-quickstart by default.

    """
    if options:
        raise NotImplementedError('Need to support "{options}" setting.')

    output = [  # These options are required to be part of the output
        "--author",
        "",
        "--ext-intersphinx",
        "--project",
        "",
        "--release",
        "",
        "-v",
        "",
        "--suffix",
        ".rst",  # Sphinx 1.8 needs this (for Python 2)
        "--master",
        "index",  # Sphinx 1.8 needs this (for Python 2)
        "--dot=_",  # Sphinx 1.8 needs this (for Python 2)
    ]

    output.extend(_BASIC_EXTENSIONS)

    rez_sphinx_settings = _get_base_settings()
    settings = rez_sphinx_settings.get("sphinx-quickstart") or []

    if "--author" in settings or "-a" in settings:
        raise exception.UserInputError("Do not provide any authors for rez-sphinx.")

    if "--project" in settings or "-p" in settings:
        raise exception.UserInputError("Do not provide a project name for rez-sphinx.")

    if "--release" in settings or "-r" in settings:
        raise exception.UserInputError(
            "Do not provide a release version for rez-sphinx."
        )

    if "-v" in settings:
        raise exception.UserInputError(
            "Do not provide a project version for rez-sphinx."
        )

    if "--master" in settings:
        raise exception.UserInputError(
            'Do not provide a "--master" argument for rez-sphinx.'
        )

    if "--suffix" in settings:
        raise exception.UserInputError(
            'Do not provide a "--suffix" argument for rez-sphinx.'
        )

    for extension in _BASIC_EXTENSIONS:
        while extension in settings:
            settings.remove(extension)

    output.extend(_get_quick_start_overridable_options(settings))

    return output
