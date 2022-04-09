"""The module which managers user configuration settings.

Most of these functions are just thin wraps around `rez-config`_ calls.

"""

import itertools
import platform

import schema
import six
from rez import exceptions as rez_exceptions
from rez import plugin_managers
from rez.config import config as config_
from rez.utils import execution
from six.moves import collections_abc

try:
    from functools import lru_cache  # Python 3.2+
except ImportError:
    from backports.functools_lru_cache import lru_cache

from ..core import constant, exception, generic, schema_helper, schema_optional
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
_BUILD_KEY_DEFAULT = "build_documentation"
_CHECK_DEFAULT_FILES = "check_default_files"
_DEFAULT_FILES = "default_files"
_DOCUMENTATION_ROOT_KEY = "documentation_root"
_EXTENSIONS_KEY = "sphinx_extensions"
_INIT_KEY = "init_options"

_ENABLE_APIDOC = "enable_apidoc"
_ALLOW_APIDOC_TEMPLATES = "allow_apidoc_templates"
_APIDOC = "sphinx-apidoc"
_APIDOC_OPTIONS = "arguments"
# TODO : Change sphinx-quickstart to a dict too like sphinx-apidoc, maybe?
_QUICKSTART = "sphinx-quickstart"

_HELP_PARENT_KEY = "auto_help"
_HELP_FILTER = "filter_by"
_HELP_SORT_ORDER = "sort_order"
_MASTER_KEY = "rez_sphinx"
_CONFIG_OVERRIDES = "sphinx_conf_overrides"
_EXTRA_REQUIRES = "extra_requires"

_INTERSPHINX_SETTINGS = "intersphinx_settings"
_PACKAGE_LINK_MAP = "package_link_map"

_KNOWN_DYNAMIC_PREFERENCE_KEYS = frozenset(
    (
        _CONFIG_OVERRIDES,
        _INTERSPHINX_SETTINGS,
        "{_INTERSPHINX_SETTINGS}.{_PACKAGE_LINK_MAP}".format(
            _INTERSPHINX_SETTINGS=_INTERSPHINX_SETTINGS,
            _PACKAGE_LINK_MAP=_PACKAGE_LINK_MAP,
        )
    )
)

_DEFAULT_ENTRIES = list(preference_init.DEFAULT_ENTRIES)

# Reference:
# https://github.com/readthedocs/readthedocs.org/issues/2569#issuecomment-485117471
#
_MASTER_DOC_DEFAULT = "index"
_MASTER_DOC = "master_doc"

_MASTER_SCHEMA = schema.Schema(
    {
        schema.Optional(_BUILD_KEY, default=_BUILD_KEY_DEFAULT): schema.Or(
            schema_helper.NON_NULL_STR, [schema_helper.NON_NULL_STR]
        ),
        schema.Optional(_EXTENSIONS_KEY, default=list(_BASIC_EXTENSIONS)): [
            schema_helper.PYTHON_DOT_PATH
        ],
        schema.Optional(
            _INIT_KEY,
            default={
                _DEFAULT_FILES: _DEFAULT_ENTRIES,
                _CHECK_DEFAULT_FILES: True,
            },
        ): {
            schema.Optional(_DEFAULT_FILES, default=_DEFAULT_ENTRIES): [
                preference_init.FILE_ENTRY
            ],
            schema.Optional(_CHECK_DEFAULT_FILES, default=True): bool,
        },
        schema.Optional(
            _API_TOCTREE_LINE, default="API Documentation <api/modules>"
        ): schema_helper.TOCTREE_LINE,
        schema.Optional(_QUICKSTART, default=[]): [str],
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
        schema.Optional(
            _CONFIG_OVERRIDES,
            default={
                constant.SPHINX_MODULE_VARIABLE: False,
                _MASTER_DOC: _MASTER_DOC_DEFAULT,
            },
        ): {
            schema.Optional(
                _MASTER_DOC, default=_MASTER_DOC_DEFAULT
            ): schema_helper.NON_NULL_STR,
            schema.Optional(constant.SPHINX_MODULE_VARIABLE, default=False): bool,
            schema.Optional(schema_helper.NON_NULL_STR): object,
        },
        schema.Optional(
            _APIDOC,
            default={
                _ALLOW_APIDOC_TEMPLATES: True,
                _ENABLE_APIDOC: True,
            },
        ): {
            schema.Optional(_ALLOW_APIDOC_TEMPLATES, default=True): bool,
            schema.Optional(_APIDOC_OPTIONS): [str],
            schema.Optional(_ENABLE_APIDOC, default=True): bool,
        },
        schema.Optional(
            _DOCUMENTATION_ROOT_KEY, default=_DOCUMENTATION_DEFAULT
        ): schema_helper.NON_NULL_STR,
        schema.Optional(_EXTRA_REQUIRES, default=[]): [
            preference_configuration.REQUEST_STR
        ],
        schema.Optional(_INTERSPHINX_SETTINGS, default={}): {
            _PACKAGE_LINK_MAP: {str: schema_helper.NON_NULL_STR}
        },
    }
)

_PREFERENCE_DICT_SEPARATOR = "."

_HOOK_DEBUG_KEY = "hook"
_PREPROCESS_DEBUG_KEY = "preprocess"
_PREPROCESS_FUNCTION = "run"
_PREPROCESS_MODULE = "preprocess_entry_point"
_PUBLISH_HOOK_CLASS_NAME = "publish_documentation"

_PACKAGE_CONFIGURATION_ATTRIBUTE = "rez_sphinx_configuration"
_REZ_OPTIONVARS = "optionvars"


def _get_preprocess_import_path():
    """str: Get the module + function needed to call the preprocess hook."""
    return "{_PREPROCESS_MODULE}.{_PREPROCESS_FUNCTION}".format(
        _PREPROCESS_MODULE=_PREPROCESS_MODULE,
        _PREPROCESS_FUNCTION=_PREPROCESS_FUNCTION,
    )


def _get_special_preference_paths(text, package=None):
    """Query the currently-set preference values located at ``text``.

    Args:
        text (str):
            A dot-separated string indicating a :ref:`rez_sphinx` configuration
            setting.  This text usually has dynamic content and is thus
            "special". e.g. ``"intersphinx_settings.package_link_map"``.  See
            also: :func:`get_preference_from_path`
        package (rez.packages.Package, optional):
            A Rez package which may override the global setting.  If the
            package doesn't define an opinion, the global setting / default
            value is used instead.

    Raises:
        NotImplementedError:
            If ``text`` could not be handled. Add support for it, if needed.

    Returns:
        set[str]: Each found preference path, if any.

    """

    def _get_dynamic_dict_keys(path, package=None):
        output = set()

        try:
            keys = get_preference_from_path(text, package=package).keys()
        except exception.ConfigurationError:
            # The user hasn't defined it. Just ignore it.
            return set()

        output.add(path)

        for key in keys:
            output.add("{path}.{key}".format(path=path, key=key))

        return output

    if text in _KNOWN_DYNAMIC_PREFERENCE_KEYS:
        return _get_dynamic_dict_keys(text, package=package)

    raise NotImplementedError(
        'Case "{text}" is unknown. Need to write code for this.'.format(text=text)
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

    if "--sep" not in output:
        output.append("--no-sep")

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
            the :ref:`rez_sphinx init` CLI.

    Raises:
        UserInputError: If there are any found errors.

    """
    if "--output-dir" in options or "-o" in options:
        raise exception.UserInputError(
            'You are not allowed to pass "--output-dir/-o" to sphinx-apidoc.'
        )


def _validate_quick_start_options(settings):
    """Check if the `sphinx-quickstart`_ settings are invalid.

    Raises:
        UserInputError: If ``settings`` contains invalid or missing data.

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
    # TODO : Add doc
    return _MASTER_SCHEMA.validate(data)


def allow_apidoc_templates(package=None):
    """Enable / Disable :ref:`rez_sphinx apidoc templates`.

    Args:
        package (rez.packages.Package, optional):
            A Rez package which may override the global setting.  If the
            package doesn't define an opinion, the global setting / default
            value is used instead.

    Returns:
        bool:
            If True, `sphinx-apidoc`_ runs just before :ref:`rez_sphinx build
            run` is calls `sphinx-build`.

    """
    rez_sphinx_settings = get_base_settings(package=package)
    apidoc = rez_sphinx_settings[_APIDOC]

    return apidoc[_ALLOW_APIDOC_TEMPLATES]


def check_default_files(package=None):
    """If True, :ref:`rez_sphinx build run` checks files for user edits.

    Args:
        package (rez.packages.Package, optional):
            A Rez package which may override the global setting.  If the
            package doesn't define an opinion, the global setting / default
            value is used instead.

    Returns:
        bool: Whether or not checking default files is enabled.

    """
    settings = get_base_settings(package=package)
    options = settings.get(_INIT_KEY) or {}

    return options[_CHECK_DEFAULT_FILES]


def is_api_enabled(package=None):
    """Check if the user will generate `sphinx-apidoc`_ ReST files.

    Args:
        package (rez.packages.Package, optional):
            A Rez package which may override the global setting.  If the
            package doesn't define an opinion, the global setting / default
            value is used instead.

    Returns:
        bool:
            If :ref:`rez_sphinx build run` is meant to auto-generate API
            documentation prior to running, return True.

    """
    rez_sphinx_settings = get_base_settings(package=package)
    apidoc = rez_sphinx_settings[_APIDOC]

    return apidoc[_ENABLE_APIDOC]


def get_api_options(options=tuple(), package=None):
    """Find all arguments to pass to `sphinx-apidoc`_.

    Args:
        options (container[str]):
            User arguments to pass to `sphinx-apidoc`_. These options come from
            :ref:`rez_sphinx build run` CLI and may be valid or invalid.
        package (rez.packages.Package, optional):
            A Rez package which may override the global setting.  If the
            package doesn't define an opinion, the global setting / default
            value is used instead.

    """
    rez_sphinx_settings = get_base_settings(package=package)
    apidoc = rez_sphinx_settings[_APIDOC]
    settings = apidoc.get(_APIDOC_OPTIONS) or ["--separate"]

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


def get_auto_help_methods():
    """list[str]: Find all defined `help`_ methods. See :doc:`auto_append_help_tags`."""
    output = []

    if (
        config_.package_preprocess_function  # pylint: disable=no-member
        == _get_preprocess_import_path()
    ):
        output.append(_PREPROCESS_DEBUG_KEY)

    if _PUBLISH_HOOK_CLASS_NAME in config_.release_hooks:  # pylint: disable=no-member
        output.append(_HOOK_DEBUG_KEY)

    return output


# TODO : Is caching really necessary? Maybe remove it from these functions
@lru_cache()
def get_base_settings(package=None):
    """Get all :ref:`rez_sphinx` specific default settings.

    Args:
        package (rez.packages.Package, optional):
            A Rez package which may override the global setting.  If the
            package doesn't define an opinion, the global setting / default
            value is used instead.

    Returns:
        dict[str, object]: The found :ref:`rez_sphinx` configuration settings.

    """
    if hasattr(package, _PACKAGE_CONFIGURATION_ATTRIBUTE):
        overrides = {
            _REZ_OPTIONVARS: {
                _MASTER_KEY: getattr(package, _PACKAGE_CONFIGURATION_ATTRIBUTE)
            }
        }
        config = config_.copy(overrides=overrides)

        # TODO : Not sure why I need to this for optionvars to "take" properly.
        # Possibly it's a config bug? The `_uncache` method, I expected,
        # should've handled this case
        #
        if _REZ_OPTIONVARS in config.__dict__:
            del config.__dict__[_REZ_OPTIONVARS]
    else:
        config = config_

    rez_user_options = config.optionvars  # pylint: disable=no-member

    data = rez_user_options.get(_MASTER_KEY) or {}

    return _validate_all(data)


def get_build_documentation_keys(package=None):
    """Get the `rez tests attribute`_ key for :ref:`rez_sphinx`.

    Args:
        package (rez.packages.Package, optional):
            A Rez package which may override the global setting.  If the
            package doesn't define an opinion, the global setting / default
            value is used instead.

    Returns:
        list[str]:
            The found, allowed Rez `tests`_ keys. By default, this is
            ``["build_documentation"]``.

    """
    rez_sphinx_settings = get_base_settings(package=package)
    keys = rez_sphinx_settings.get(_BUILD_KEY)

    if not keys:
        return [_BUILD_KEY_DEFAULT]

    if isinstance(keys, six.string_types):
        return [keys]

    return keys


def get_build_documentation_key(package=None):
    """Get the `rez tests attribute`_ key for :ref:`rez_sphinx`.

    Args:
        package (rez.packages.Package, optional):
            A Rez package which may override the global setting.  If the
            package doesn't define an opinion, the global setting / default
            value is used instead.

    Returns:
        str:
            The found, preferred `tests`_ keys. By default, this is
            ``"build_documentation"``.

    """
    return get_build_documentation_keys(package=package)[0]


def get_documentation_root_name(package=None):
    """Get the name of the folder where all documentation-related files will go.

    Args:
        package (rez.packages.Package, optional):
            A Rez package which may override the global setting.  If the
            package doesn't define an opinion, the global setting / default
            value is used instead.

    Returns:
        str: The folder name where documentation will live, e.g. ``"documentation"``.

    """
    settings = get_base_settings(package=package)

    return settings.get(_DOCUMENTATION_ROOT_KEY) or _DOCUMENTATION_DEFAULT


def get_filter_method(package=None):
    """Get a function to process original / auto-generated `package help`_ values.

    Args:
        package (rez.packages.Package, optional):
            A Rez package which may override the global setting.  If the
            package doesn't define an opinion, the global setting / default
            value is used instead.

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
    rez_sphinx_settings = get_base_settings(package=package)
    parent = rez_sphinx_settings[_HELP_PARENT_KEY]

    caller = parent[_HELP_FILTER]

    if caller != preference_help.DEFAULT_FILTER:
        return caller

    return caller._callable  # pylint: disable=protected-access


def get_help_label():
    """str: Get the `help`_ which connects with `intersphinx`_."""
    rez_sphinx_settings = get_base_settings()

    return rez_sphinx_settings.get("help_label") or "rez_sphinx_objects_inv"


def get_initial_files_from_configuration():
    """list[Entry]: File data to write during :ref:`rez_sphinx init`."""
    settings = get_base_settings()
    options = settings.get(_INIT_KEY) or {}

    return options[_DEFAULT_FILES]


def get_init_default_entries():
    """Get the documentation files to auto-generate during :ref:`rez_sphinx init`.

    Returns:
        list[Entry]:
            A description of each file's contents and where it should live,
            on-disk, within the source documentation root.

    """
    settings = get_base_settings()

    return settings[_INIT_KEY][_DEFAULT_FILES]


def get_master_api_documentation_line(package=None):
    """str: Get the line that typically is added to the main `index.rst`_.

    Args:
        package (rez.packages.Package, optional):
            A Rez package which may override the global setting.  If the
            package doesn't define an opinion, the global setting / default
            value is used instead.

    Raises:
        ConfigurationError: If the found configuration value is empty.

    Returns:
        str:
            The found text needed to add the auto-generated API into the master
            Sphinx toctree.

    """
    rez_sphinx_settings = get_base_settings(package=package)

    line = rez_sphinx_settings[_API_TOCTREE_LINE]

    if line:
        return line

    raise exception.ConfigurationError(
        'The "{_API_TOCTREE_LINE}" setting cannot be empty.'.format(
            _API_TOCTREE_LINE=_API_TOCTREE_LINE
        )
    )


def get_master_document_name(package=None):
    """Find the first .rst file `Sphinx`_ should point to.

    Ideally this shouldn't be necessary but it looks like, while building
    :ref:`rez_sphinx` in Python 2 + `sphinx-rtd-theme`_, the name of this file
    gets swapped to "contents.rst".

    So we name it "index.rst", for consistency.

    References:
        https://github.com/readthedocs/readthedocs.org/issues/2569#issuecomment-270577290

    Args:
        package (rez.packages.Package, optional):
            A Rez package which may override the global setting.  If the
            package doesn't define an opinion, the global setting / default
            value is used instead.

    Returns:
        str: The base name, without file extension, of the "entry point" for `Sphinx`_.

    """
    settings = get_sphinx_configuration_overrides(package=package)

    return settings[_MASTER_DOC]


def get_package_link_map(package=None):
    """Each Rez package family name + its root documentation, if any.

    Args:
        package (rez.packages.Package, optional):
            A Rez package which may override the global setting.  If the
            package doesn't define an opinion, the global setting / default
            value is used instead.

    Returns:
        dict[str, str]:
            The Rez package family name and the URL to its viewable Sphinx
            documentation.

    """
    rez_sphinx_settings = get_base_settings(package=package)

    if _INTERSPHINX_SETTINGS not in rez_sphinx_settings:
        return {}

    settings = rez_sphinx_settings[_INTERSPHINX_SETTINGS]

    return settings.get(_PACKAGE_LINK_MAP, {})


def get_preference_from_path(path, package=None):
    """Find the preference value located at ``path``.

    See Also:
        :func:`get_preference_paths` and :ref:`rez_sphinx config show-all`.

    Args:
        path (str):
            Some dot-separated dict key to query. e.g.
            ``"init_options.check_default_files"``
        package (rez.packages.Package, optional):
            If provided, the settings from this package are checked.

    Raises:
        ConfigurationError: If ``path`` isn't a valid setting.

    Returns:
        object: Whatever value ``path`` points to. It could be anything.

    """
    rez_sphinx_settings = get_base_settings(package=package)

    if not path:
        return rez_sphinx_settings

    parts = path.split(_PREFERENCE_DICT_SEPARATOR)
    current = rez_sphinx_settings
    full = ""

    for item in parts:
        if full:
            full += "{_PREFERENCE_DICT_SEPARATOR}{item}".format(
                _PREFERENCE_DICT_SEPARATOR=_PREFERENCE_DICT_SEPARATOR,
                item=item,
            )
        else:
            full = item

        try:
            current = current[item]
        except KeyError:
            text = full

            if not full:
                text = item

            raise exception.ConfigurationError(
                'Path "{text}" was not found. See run `rez_sphinx config show-all` for options.'.format(
                    text=text
                )
            )

    return current


def get_preference_paths(package=None):
    """Find all valid paths for :ref:`rez_sphinx config show`.

    Most of these returned paths are "default" and will always be present.
    But depending the currently-set global / package configuration, dynamic
    keys may also be present in the output.

    Args:
        package (rez.packages.Package, optional):
            A Rez package which may override the global setting.  If the
            package doesn't define an opinion, the global setting / default
            value is used instead.

    Returns:
        set[str]: The "default" + "dynamic" keys.

    """

    def _get_mapping(mapping, context):
        outputs = set()
        exceptional_cases = set()

        for key, value in mapping.items():
            if isinstance(key, schema.Optional):
                key = schema_optional.get_raw_key(key)

            if isinstance(key, schema.Use):
                # We wouldn't really know how to handle this situation. Just ignore it.
                exceptional_cases.add(context)

                continue

            if not isinstance(value, collections_abc.Mapping):
                if not isinstance(key, six.string_types):
                    # We wouldn't really know how to handle this situation.
                    # Just ignore it.
                    #
                    exceptional_cases.add(context)
                else:
                    outputs.add(key)

                continue

            inner_context = key

            if context:
                inner_context = "{context}{_PREFERENCE_DICT_SEPARATOR}{key}".format(
                    context=context,
                    _PREFERENCE_DICT_SEPARATOR=_PREFERENCE_DICT_SEPARATOR,
                    key=key,
                )

            inner_output, extra_cases = _get_mapping(value, inner_context)

            if not inner_output:
                # When this happens, it's because a nested object is empty by
                # default. We still want the context key, in this case.
                #
                # e.g. "intersphinx_settings.package_link_map"
                #
                outputs.add(key)

            exceptional_cases.update(extra_cases)

            for inner_key in inner_output:
                if isinstance(inner_key, schema.Optional):
                    inner_key = schema_optional.get_raw_key(inner_key)

                outputs.add(
                    "{key}{_PREFERENCE_DICT_SEPARATOR}{inner_key}".format(
                        key=key,
                        _PREFERENCE_DICT_SEPARATOR=_PREFERENCE_DICT_SEPARATOR,
                        inner_key=inner_key,
                    )
                )

        return outputs, exceptional_cases

    def _expand_cases(cases):
        """Convert ``["foo.bar.thing"]`` into ``["foo", "foo.bar", "foo.bar.thing"]."""
        output = []

        for case in cases:
            parts = case.split(_PREFERENCE_DICT_SEPARATOR)

            for index in range(1, len(parts) + 1):
                output.append(_PREFERENCE_DICT_SEPARATOR.join(parts[:index]))

        return output

    output, exceptional_cases = _get_mapping(
        _MASTER_SCHEMA._schema,  # pylint: disable=protected-access
        context="",
    )

    if not exceptional_cases:
        return output

    expanded_exceptional_cases = _expand_cases(exceptional_cases)

    output.update(
        path
        for case in expanded_exceptional_cases
        for path in _get_special_preference_paths(case, package=package)
    )

    return output


def get_sort_method(package=None):
    """Get the function which sorts entries in Rez `package help`_.

    Args:
        package (rez.packages.Package, optional):
            A Rez package which may override the global setting.  If the
            package doesn't define an opinion, the global setting / default
            value is used instead.

    Returns:
        callable[list[str], str] -> object: The found, callable function.

    """
    rez_sphinx_settings = get_base_settings(package=package)
    parent = rez_sphinx_settings[_HELP_PARENT_KEY]

    caller = parent[_HELP_SORT_ORDER]

    if caller != preference_help.DEFAULT_SORT:
        return caller

    return caller._callable  # Another schema member pylint: disable=protected-access


def get_sphinx_configuration_overrides(package=None):
    """Get all values to directly set within `Sphinx conf.py`_.

    Args:
        package (rez.packages.Package, optional):
            A Rez package which may override the global setting.  If the
            package doesn't define an opinion, the global setting / default
            value is used instead.

    Returns:
        dict[str, object]: Each `Sphinx conf.py`_ variable name and its value.

    """
    rez_sphinx_settings = get_base_settings(package=package)

    return rez_sphinx_settings[_CONFIG_OVERRIDES]


def get_sphinx_extensions():
    """list[str]: All `Sphinx`_ optional add-ons to include in documentation."""
    rez_sphinx_settings = get_base_settings()

    return rez_sphinx_settings.get(_EXTENSIONS_KEY) or list(_BASIC_EXTENSIONS)


def get_quick_start_options(package, options=tuple()):
    """Get the arguments `sphinx-quickstart`_.

    Args:
        package (rez.packages.Package):
            The Rez package to query from. e.g. "python", "Sphinx", etc.
        options (list[str], optional):
            User-provided arguments to consider while resolving
            `sphinx-quickstart`_ values.

    Raises:
        UserInputError:
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
        package.name,
        "--release",
        "",
        "-v",
        "",
        "--suffix",
        constant.SOURCE_DOCUMENTATION_EXTENSION,  # Sphinx 1.8 needs this (for Python 2)
        "--master",
        "index",  # Sphinx 1.8 needs this (for Python 2)
        "--dot=_",  # Sphinx 1.8 needs this (for Python 2)
    ]

    rez_sphinx_settings = get_base_settings(package=package)
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


def serialize_default_settings():
    """Get all :ref:`rez_sphinx` default values.

    This function can be very long. :func:`serialize_default_sparse_settings`
    shows a briefer (but still valid) set of default settings.

    Returns:
        dict[str, object]: A simple key / value pair dict.

    """
    output = {}

    for key in _MASTER_SCHEMA.schema.keys():
        if schema_optional.has_default(key):
            output[key.key] = key.default
        else:
            raise NotImplementedError(
                'Key "{key}" needs to be supported.'.format(key=key)
            )

    return output


def serialize_default_sparse_settings():
    """Get the default settings for :ref:`rez_sphinx`.

    These settings ignore nested content and just shows the simple, top-level data.

    See Also:
        :func:`serialize_default_settings`

    Returns:
        dict[str, object]: A simple key / value pair dict.

    """
    required = {
        key
        for key in _MASTER_SCHEMA.schema.keys()
        if not isinstance(key, schema.Optional)
    }

    output = {}

    for key, value in serialize_default_settings().items():
        if not generic.is_iterable(value):
            output[key] = value
        elif key in required:
            output[key] = value
        else:
            output[key] = value.__class__()  # Probably not the best way to do this

    return output


def serialize_override_settings():
    """Get all user-set values, without any default schema values.

    Returns:
        dict[str, object]: The values, stripped of all default data.

    """
    settings = get_base_settings()

    return schema_optional.serialize_sparsely(settings, _MASTER_SCHEMA)


def validate_base_settings(package=None):
    """Check if the user's settings won't cause :ref:`rez_sphinx` to break.

    Args:
        package (rez.packages.Package, optional):
            A Rez package which may override the global setting.  If the
            package doesn't define an opinion, the global setting / default
            value is used instead.

    Raises:
        ConfigurationError: Raised if a configuration-related issue is found.

    """
    try:
        get_base_settings()
    except schema.SchemaError as error:
        raise exception.ConfigurationError(
            "Invalid rez-config settings were found. "
            "See ``rez_sphinx config check`` for details. "
            'Summary here: "{error!s}".'.format(
                error=error,
            )
        )


def validate_help_settings(package=None):
    """Ensure ``package`` is compatible with existing global `help`_ settings.

    Args:
        package (rez.packages.Package, optional):
            A Rez package which may override the global setting.  If the
            package doesn't define an opinion, the global setting / default
            value is used instead.

    Returns:
        exception.Base or None:
            If there is some kind of problem, return an exception which the
            caller can choose to raise. If there's nothin wrong, return
            nothing.

    """

    def _validate_preprocess(package):
        if not package:
            return None

        with execution.add_sys_paths(
            config_.package_definition_build_python_paths  # pylint: disable=no-member
        ):
            try:
                module = __import__(_PREPROCESS_MODULE)
            except ImportError:
                caller = _get_preprocess_import_path()

                raise exception.ConfigurationError(
                    'Preprocess caller "{caller}" is defined but '  # pylint: disable=missing-format-attribute,line-too-long
                    "package_definition_build_python_paths cannot import it. "
                    'Got "{config_.package_definition_build_python_paths}". '
                    "Please fix.".format(
                        caller=caller,
                        config_=config_,
                    ),
                )

            if not hasattr(module, _PREPROCESS_FUNCTION):
                raise exception.RezSphinxException(
                    'Expected function "{_PREPROCESS_FUNCTION}" in module. '
                    "Send a ticket to rez_sphinx maintainers to fix.".format(
                        _PREPROCESS_FUNCTION=_PREPROCESS_FUNCTION,
                    )
                )

        if config_.package_preprocess_mode != "override":  # pylint: disable=no-member
            # All package modes other than "override" account for the global
            # preprocess function.
            #
            return None

        if not hasattr(package, "preprocess"):
            # The package didn't define a preprocess function. Ignore it.
            return None

        return exception.BadPackage(
            'Package "{package.name} / {package.version}" overwrites the global '
            "preproces function.".format(package=package)
        )

    def _validate_release_hook():
        try:
            plugin_managers.plugin_manager.get_plugin_class(
                "release_hook",
                _PUBLISH_HOOK_CLASS_NAME,
            )
        except rez_exceptions.RezPluginError:
            return exception.ConfigurationError(
                'Release hook "{_PUBLISH_HOOK_CLASS_NAME}" could not be loaded by Rez.'
                "".format(_PUBLISH_HOOK_CLASS_NAME=_PUBLISH_HOOK_CLASS_NAME)
            )

        return None

    found_methods = get_auto_help_methods()

    preprocess_issue = None

    if _PREPROCESS_DEBUG_KEY in found_methods:
        preprocess_issue = _validate_preprocess(package)

    hook_issue = None

    if _HOOK_DEBUG_KEY in found_methods:
        hook_issue = _validate_release_hook()

    return list(filter(None, (preprocess_issue, hook_issue)))
