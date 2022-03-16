"""The module which managers user configuration settings.

Most of these functions are just thin wraps around `rez-config`_ calls.

"""

import itertools
import platform

import schema
from rez.config import config

try:
    from functools import lru_cache  # Python 3.2+
except ImportError:
    from backports.functools_lru_cache import lru_cache

from ..core import exception, schema_helper
from . import preference_configuration, preference_help, preference_init

_DOCUMENTATION_DEFAULT = "documentation"

_BASIC_EXTENSIONS = (
    "sphinx.ext.autodoc",  # Needed for auto-documentation generation later
    "sphinx.ext.intersphinx",  # Needed to find + load external Rez package Sphinx data
    "sphinx.ext.viewcode",  # Technically optional, but I think it's cool to always have
)
SPHINX_SEPARATE_SOURCE_AND_BUILD = "--sep"

_API_TOCTREE_LINE = "api_toctree_line"
_BUILD_KEY = "build_documentation_key"
_DEFAULT_FILES = "default_files"
_DOCUMENTATION_ROOT_KEY = "documentation_root"
_EXTENSIONS_KEY = "sphinx_extensions"
_INIT_KEY = "init_options"

_ENABLE_APIDOC = "enable_apidoc"
_APIDOC = "sphinx-apidoc"
_QUICKSTART = "sphinx-quickstart"

_HELP_PARENT_KEY = "auto_help"
_HELP_FILTER = "filter_by"
_HELP_SORT_ORDER = "sort_order"
_MASTER_KEY = "rez_sphinx"
_CONFIG_OVERRIDES = "sphinx_conf_overrides"
_EXTRA_REQUIRES = "extra_requires"

_MASTER_SCHEMA = schema.Schema(
    {
        schema.Optional(
            _BUILD_KEY, default="build_documentation"
        ): schema_helper.NON_NULL_STR,
        schema.Optional(_EXTENSIONS_KEY, default=list(_BASIC_EXTENSIONS)): [
            schema_helper.PYTHON_DOT_PATH
        ],
        schema.Optional(_INIT_KEY): {
            schema.Optional(_DEFAULT_FILES, default=[]): [preference_init.FILE_ENTRY]
        },
        schema.Optional(
            _API_TOCTREE_LINE, default="API Documentation <api/modules>"
        ): schema_helper.TOCTREE_LINE,
        schema.Optional(_QUICKSTART, default=[]): [],
        schema.Optional(
            _HELP_PARENT_KEY,
            default={
                _HELP_FILTER: preference_help.DEFAULT_FILTER,
                _HELP_SORT_ORDER: preference_help.DEFAULT_SORT,
            },
        ): {
            schema.Optional(
                _HELP_FILTER, default=preference_help.DEFAULT_FILTER
            ): schema.Use(preference_help.validate_filter),
            schema.Optional(
                _HELP_SORT_ORDER, default=preference_help.DEFAULT_SORT
            ): schema.Use(preference_help.validate_sort),
        },
        schema.Optional(_ENABLE_APIDOC, default=True): bool,
        schema.Optional(_CONFIG_OVERRIDES, default=dict()): {
            schema_helper.NON_NULL_STR: object,
        },
        schema.Optional(_APIDOC, default=[]): [],
        schema.Optional(
            _DOCUMENTATION_ROOT_KEY, default=_DOCUMENTATION_DEFAULT
        ): schema_helper.NON_NULL_STR,
        schema.Optional(_EXTRA_REQUIRES, default=[]): [
            preference_configuration.REQUEST_STR
        ],
    }
)


def _get_quick_start_overridable_options(overrides=tuple()):
    """Get all `sphinx-quickstart`_ parameters which the user can modify.

    Args:
        overrides (list[str], optional):
            `sphinx-quickstart`_ user settings to prefer over the
            defaults, if any. e.g. ``["--sep"]``.

    Returns:
        list[str]:
            The resolved "user + :ref:`rez_sphinx`" settings for `sphinx-quickstart`_.

    """
    output = list(overrides)

    if "--no-sep" not in output:
        output.append(
            SPHINX_SEPARATE_SOURCE_AND_BUILD
        )  # if specified, separate source and build dirs

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

    if "--quiet" not in output and "-q" not in output:
        # Note: This is purely optional. Sphinx tends to spit out a lot of
        # content and we just don't need to see any of it unless there's errors.
        #
        output.append("--quiet")

    return output


def _validate_api_options(options):
    """Check ``options`` for issues which prevents `sphinx-apidoc`_ from running.

    Args:
        options (container[str]):
            User arguments to pass to `sphinx-apidoc`_. This could
            be a combination of automated arguments or arguments which
            the user manually provided, via `rez-config`_ or from
            the :doc:`init_command` CLI.

    Raises:
        :class:`.UserInputError`: If there are any found errors.

    """
    if "--output-dir" in options or "-o" in options:
        raise exception.UserInputError(
            'You are not allowed to pass "--output-dir/-o" to sphinx-apidoc.'
        )


def _validate_quick_start_options(settings):
    """Check if the `sphinx-quickstart`_ settings are invalid.

    Raises:
        :class:`.UserInputError`: If ``settings`` contains invalid or missing data.

    """
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


def _validate_all(data):
    return _MASTER_SCHEMA.validate(data)


def is_api_enabled():
    """bool: Check if the user will generate `sphinx-apidoc`_ ReST files."""
    rez_sphinx_settings = get_base_settings()

    if _ENABLE_APIDOC in rez_sphinx_settings:
        return rez_sphinx_settings[_ENABLE_APIDOC]

    # TODO : Be smarter about accessing default values from the schema
    return True


def get_api_options(options=tuple()):
    """Find all arguments to pass to `sphinx-apidoc`_.

    Args:
        options (container[str]):
            User arguments to pass to `sphinx-apidoc`_. These
            options come from :doc:`build_command` CLI and may be
            valid or invalid.

    """
    rez_sphinx_settings = get_base_settings()
    settings = rez_sphinx_settings.get(_APIDOC) or ["--separate"]

    try:
        _validate_api_options(settings)
    except exception.UserInputError as error:
        raise exception.UserInputError(
            "Error from rez-config: {error}".format(error=error)
        )

    try:
        _validate_api_options(options)
    except exception.UserInputError as error:
        raise exception.UserInputError(
            "Error from the terminal: {error}".format(error=error)
        )

    return list(itertools.chain(options, settings))


# TODO : Is caching really necessary? Maybe remove it from these functions
@lru_cache()
def get_base_settings():
    """dict[str, object]: Get all :ref:`rez_sphinx` specific default settings."""
    rez_user_options = config.optionvars  # pylint: disable=no-member

    data = rez_user_options.get(_MASTER_KEY) or dict()

    return _validate_all(data)


def get_build_documentation_key():
    """str: Get the `rez tests attribute`_ key for :ref:`rez_sphinx`."""
    rez_sphinx_settings = get_base_settings()

    return rez_sphinx_settings.get(_BUILD_KEY) or "build_documentation"


def get_help_label():
    """str: Get the `rez help attribute`_ which connects with `intersphinx`_."""
    rez_sphinx_settings = get_base_settings()

    return rez_sphinx_settings.get("help_label") or "rez_sphinx_objects_inv"


def get_documentation_root_name():
    """str: The name of the folder where all documentation-related files will go."""
    settings = get_base_settings()

    return settings.get(_DOCUMENTATION_ROOT_KEY) or _DOCUMENTATION_DEFAULT


def get_filter_method():
    """Get a function to process original / auto-generated `package help`_ values.

    Returns:
        callable[
            list[list[str, str]],
            list[list[str, str]]
        ] -> tuple[
            list[list[str, str]],
            list[list[str, str]]
        ]:
            A function that takes two `package help`_ lists and may return
            unique results from either of them.

    """
    rez_sphinx_settings = get_base_settings()
    parent = rez_sphinx_settings[_HELP_PARENT_KEY]

    caller = parent[_HELP_FILTER]

    # TODO : Consider simplifying this section
    if caller != preference_help.DEFAULT_FILTER:
        return caller

    return caller._callable


def get_initial_files_from_configuration():
    """list[:class:`.Entry`]: File data to write during :doc:`init_command`."""
    settings = get_base_settings()
    options = settings.get(_INIT_KEY) or dict()

    if _DEFAULT_FILES in options:
        return options[_DEFAULT_FILES]

    return list(preference_init.DEFAULT_ENTRIES)


def get_master_api_documentation_line():
    """str: Get the line that typically is added to the main `index.rst`_."""
    rez_sphinx_settings = get_base_settings()

    return rez_sphinx_settings[_API_TOCTREE_LINE]


def get_sort_method():
    """callable[list[str], str] -> object: The sort function for `package help`_."""
    rez_sphinx_settings = get_base_settings()
    parent = rez_sphinx_settings[_HELP_PARENT_KEY]

    caller = parent[_HELP_SORT_ORDER]

    # TODO : Consider simplifying this section
    if caller != preference_help.DEFAULT_SORT:
        return caller

    return caller._callable


def get_sphinx_configuration_overrides():
    """dict[str, object]: Get all values to directly set within `Sphinx conf.py`_."""
    rez_sphinx_settings = get_base_settings()

    return rez_sphinx_settings[_CONFIG_OVERRIDES]


def get_sphinx_extensions():
    """list[str]: All `Sphinx`_ optional add-ons to include in documentation."""
    rez_sphinx_settings = get_base_settings()

    return rez_sphinx_settings.get(_EXTENSIONS_KEY) or list(_BASIC_EXTENSIONS)


def get_quick_start_options(package, options=tuple()):
    """Get the arguments `sphinx-quickstart`_.

    Args:
        package (str):
            The name of the Rez package family. e.g. "python", "Sphinx", etc.
        options (list[str], optional):
            User-provided arguments to consider while resolving
            `sphinx-quickstart`_ values.

    Raises:
        :class:`.UserInputError`:
            If the user attempted to pass settings which may only be
            edited by :ref:`rez_sphinx`, fail this function early.
            Examples of "reserved" parameters are "--project", which are
            meant to be set by the Rez package name.

    Returns:
        list[str]: Any arguments to pass to sphinx-quickstart by default.

    """
    output = [  # These options are required to be part of the output
        "--author",
        "",
        "--ext-intersphinx",
        "--project",
        package,
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

    rez_sphinx_settings = get_base_settings()
    settings = rez_sphinx_settings.get(_QUICKSTART) or []

    try:
        _validate_quick_start_options(options)
    except exception.UserInputError as error:
        raise exception.UserInputError(
            "Error from the terminal: {error}".format(error=error)
        )

    try:
        _validate_quick_start_options(settings)
    except exception.UserInputError as error:
        raise exception.UserInputError(
            "Error from the rez-config: {error}".format(error=error)
        )

    output.extend(_get_quick_start_overridable_options(settings))
    output.extend(options)

    return output


def validate_base_settings():
    """Check if the user's settings won't cause :ref:`rez_sphinx` to break.

    Raises:
        :class:`.ConfigurationError`: Raised if a configuration-related issue is found.

    """
    try:
        get_base_settings()
    except schema.SchemaError as error:
        raise exception.ConfigurationError(
            'Invalid rez-config settings were found. '
            'See `rez_sphinx config check` for details. Summary here "{error!s}".'.format(
                error=error,
            )
        )
