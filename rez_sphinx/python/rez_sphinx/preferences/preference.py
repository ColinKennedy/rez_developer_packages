"""The module which managers user configuration settings.

Most of these functions are just thin wraps around `rez-config`_ calls.

"""

import itertools
import platform

import schema
import six
from rez.config import config
from six.moves import collections_abc
from rez import plugin_managers

try:
    from functools import lru_cache  # Python 3.2+
except ImportError:
    from backports.functools_lru_cache import lru_cache

from . import preference_configuration, preference_help, preference_init
from ..core import exception, generic, schema_helper, schema_optional

_DOCUMENTATION_DEFAULT = "documentation"

_BASIC_EXTENSIONS = (
    "sphinx.ext.autodoc",  # Needed for auto-documentation generation later
    "sphinx.ext.intersphinx",  # Needed to find + load external Rez package Sphinx data
    "sphinx.ext.viewcode",  # Technically optional, but I think it's cool to always have
)
SPHINX_SEPARATE_SOURCE_AND_BUILD = "--sep"

_API_TOCTREE_LINE = "api_toctree_line"
_BUILD_KEY = "build_documentation_key"
_CHECK_DEFAULT_FILES = "check_default_files"
_DEFAULT_FILES = "default_files"
_DOCUMENTATION_ROOT_KEY = "documentation_root"
_EXTENSIONS_KEY = "sphinx_extensions"
_INIT_KEY = "init_options"  # TODO : Consider renaming to "init_command"

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


# TODO : Move _SPHINX_MODULE_KEY to a better place
_SPHINX_MODULE_KEY = "add_module_names"

_DEFAULT_ENTRIES = list(preference_init.DEFAULT_ENTRIES)

# Reference: https://github.com/readthedocs/readthedocs.org/issues/2569#issuecomment-485117471
_MASTER_DOC_DEFAULT = "index"
_MASTER_DOC = "master_doc"

_MASTER_SCHEMA = schema.Schema(
    {
        schema.Optional(_BUILD_KEY, default="build_documentation"): schema.Or(
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
        schema.Optional(
            _CONFIG_OVERRIDES,
            default={
                _SPHINX_MODULE_KEY: False,
                _MASTER_DOC: _MASTER_DOC_DEFAULT,
            },
        ): {
            schema.Optional(
                _MASTER_DOC, default=_MASTER_DOC_DEFAULT
            ): schema_helper.NON_NULL_STR,
            schema.Optional(_SPHINX_MODULE_KEY, default=False): bool,
            schema_helper.NON_NULL_STR: object,
        },
        schema.Optional(
            _APIDOC,
            default={
                _ALLOW_APIDOC_TEMPLATES: True,
                _ENABLE_APIDOC: True,
            },
        ): {
            schema.Optional(_ALLOW_APIDOC_TEMPLATES, default=True): bool,
            schema.Optional(_APIDOC_OPTIONS): [],
            schema.Optional(_ENABLE_APIDOC, default=True): bool,
        },
        schema.Optional(
            _DOCUMENTATION_ROOT_KEY, default=_DOCUMENTATION_DEFAULT
        ): schema_helper.NON_NULL_STR,
        schema.Optional(_EXTRA_REQUIRES, default=[]): [
            preference_configuration.REQUEST_STR
        ],
        schema.Optional(_INTERSPHINX_SETTINGS, default=dict()): {
            _PACKAGE_LINK_MAP: {str: schema_helper.NON_NULL_STR}
        },
    }
)

_PREFERENCE_DICT_SEPARATOR = "."

_PUBLISH_HOOK_CLASS_NAME = "publish_documentation"
_HOOK_DEBUG_KEY = "hook"
_PREPROCESS_DEBUG_KEY = "preprocess"


def get_auto_help_methods():
    output = []

    if config.package_preprocess_function == "preprocess_entry_point.run":
        output.append(_PREPROCESS_DEBUG_KEY)

    if _PUBLISH_HOOK_CLASS_NAME in config.release_hooks:
        output.append(_HOOK_DEBUG_KEY)

    return output


def get_package_link_map():
    """dict[str, str]: Each Rez package family name + its root documentation, if any."""
    rez_sphinx_settings = get_base_settings()

    if _INTERSPHINX_SETTINGS not in rez_sphinx_settings:
        return dict()

    settings = rez_sphinx_settings[_INTERSPHINX_SETTINGS]

    return settings.get(_PACKAGE_LINK_MAP, dict())


def _get_special_preference_paths(text):
    """Query the currently-set preference values located at ``text``.

    Args:
        text (str):
            A dot-separated string indicating a :ref:`rez_sphinx` configuration
            setting.  This text usually has dynamic content and is thus
            "special". e.g. ``"intersphinx_settings.package_link_map"``.  See
            also: :func:`get_preference_from_path`

    Raises:
        NotImplementedError:
            If ``text`` could not be handled. Add support for it, if needed.

    Returns:
        set[str]: Each found preference path, if any.

    """

    def _get_dynamic_dict_keys(path):
        output = set()

        try:
            keys = get_preference_from_path(text).keys()
        except exception.ConfigurationError:
            # The user hasn't defined it. Just ignore it.
            return set()

        output.add(path)

        for key in keys:
            output.add("{path}.{key}".format(path=path, key=key))

        return output

    output = set()

    if text == "sphinx_conf_overrides":
        output.update(_get_dynamic_dict_keys("sphinx_conf_overrides"))

        return output

    if text == "intersphinx_settings.package_link_map":
        output.update(_get_dynamic_dict_keys("intersphinx_settings.package_link_map"))

        return output

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
    return _MASTER_SCHEMA.validate(data)


def allow_apidoc_templates():
    """bool: Enable / Disable :ref:`rez_sphinx apidoc templates`."""
    rez_sphinx_settings = get_base_settings()
    apidoc = rez_sphinx_settings[_APIDOC]

    return apidoc[_ALLOW_APIDOC_TEMPLATES]


def check_default_files():
    """bool: If True, :ref:`rez_sphinx build run` checks files for user edits."""
    settings = get_base_settings()
    options = settings.get(_INIT_KEY) or dict()

    return options[_CHECK_DEFAULT_FILES]


def is_api_enabled():
    """bool: Check if the user will generate `sphinx-apidoc`_ ReST files."""
    rez_sphinx_settings = get_base_settings()
    apidoc = rez_sphinx_settings[_APIDOC]

    return apidoc[_ENABLE_APIDOC]


def get_api_options(options=tuple()):
    """Find all arguments to pass to `sphinx-apidoc`_.

    Args:
        options (container[str]):
            User arguments to pass to `sphinx-apidoc`_. These options come from
            :ref:`rez_sphinx build run` CLI and may be valid or invalid.

    """
    rez_sphinx_settings = get_base_settings()
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


# TODO : Is caching really necessary? Maybe remove it from these functions
@lru_cache()
def get_base_settings(package=None):
    """dict[str, object]: Get all :ref:`rez_sphinx` specific default settings."""
    # TODO : Incorporate ``package`` with unittests
    # Once this is done, make sure to update all get_base_settings to include package contents

    rez_user_options = config.optionvars  # pylint: disable=no-member

    data = rez_user_options.get(_MASTER_KEY) or dict()

    return _validate_all(data)


def get_build_documentation_keys():
    """list[str]: Get the `rez tests attribute`_ key for :ref:`rez_sphinx`."""
    rez_sphinx_settings = get_base_settings()
    keys = rez_sphinx_settings.get(_BUILD_KEY)

    if not keys:
        return ["build_documentation"]

    if isinstance(keys, six.string_types):
        return [keys]

    return keys


def get_build_documentation_key():
    """str: Get the `rez tests attribute`_ key for :ref:`rez_sphinx`."""
    return get_build_documentation_keys()[0]


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

    return caller._callable  # pylint: disable=protected-access


def get_help_label():
    """str: Get the `help`_ which connects with `intersphinx`_."""
    rez_sphinx_settings = get_base_settings()

    return rez_sphinx_settings.get("help_label") or "rez_sphinx_objects_inv"


def get_initial_files_from_configuration():
    """list[Entry]: File data to write during :ref:`rez_sphinx init`."""
    settings = get_base_settings()
    options = settings.get(_INIT_KEY) or dict()

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


def get_master_api_documentation_line():
    """str: Get the line that typically is added to the main `index.rst`_."""
    rez_sphinx_settings = get_base_settings()

    return rez_sphinx_settings[_API_TOCTREE_LINE]


def get_master_document_name():
    """Find the first .rst file `Sphinx`_ should point to.

    Ideally this shouldn't be necessary but it looks like, while building
    :ref:`rez_sphinx` in Python 2 + `sphinx-rtd-theme`_, the name of this file
    gets swapped to "contents.rst".

    So we name it "index.rst", for consistency.

    References:
        https://github.com/readthedocs/readthedocs.org/issues/2569#issuecomment-270577290

    Returns:
        str: The base name, without file extension, of the "entry point" for `Sphinx`_.

    """
    settings = get_sphinx_configuration_overrides()

    return settings[_MASTER_DOC]


def get_preference_from_path(path, package=None):
    """Find the dict value located at ``path``.

    See Also:
        :func:`get_preference_paths` and :ref:`rez_sphinx config show --list-all`.

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
                'Path "{text}" was not found. See --list-all for options.'.format(
                    text=text
                )
            )

    return current


def get_preference_paths():
    """set[str]: All valid paths for :ref:`rez_sphinx config show`."""

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

    output, exceptional_cases = _get_mapping(
        _MASTER_SCHEMA._schema,  # pylint: disable=protected-access
        context="",
    )

    if not exceptional_cases:
        return output

    output.update(
        path
        for case in exceptional_cases
        for path in _get_special_preference_paths(case)
    )

    return output


def get_sort_method():
    """callable[list[str], str] -> object: The sort function for `package help`_."""
    rez_sphinx_settings = get_base_settings()
    parent = rez_sphinx_settings[_HELP_PARENT_KEY]

    caller = parent[_HELP_SORT_ORDER]

    # TODO : Consider simplifying this section
    if caller != preference_help.DEFAULT_SORT:
        return caller

    return caller._callable  # Another schema member pylint: disable=protected-access


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


def serialize_default_settings():
    """Get all :ref:`rez_sphinx` default values.

    This function can be very long. :func:`serialize_default_sparse_settings`
    shows a briefer (but still valid) set of default settings.

    Returns:
        dict[str, object]: A simple key / value pair dict.

    """
    output = dict()

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

    output = dict()

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


def validate_base_settings():
    """Check if the user's settings won't cause :ref:`rez_sphinx` to break.

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
    # TODO : Finish

    def _validate_preprocess(package):
        if not package:
            return None

        if config.package_preprocess_mode != "override":
            # All package modes other than "override" account for the global
            # preprocess function.
            #
            return None

        if not hasattr(package, "preprocess"):
            # The package didn't define a preprocess function. Ignore it.
            return None

        return exception.BadPackage(
            'Package "{package.name} / {package.version}" overwrites the global '
            'preproces function.'.format(package=package)
        )

    def _validate_release_hook(package):
        class_ = plugin_managers.plugin_manager.get_plugin_class("release_hook", _PUBLISH_HOOK_CLASS_NAME)

        if not class_:
            return exception.ConfigurationError('Release hook "{_PUBLISH_HOOK_CLASS_NAME}" could not be loaded by Rez.'.format(_PUBLISH_HOOK_CLASS_NAME=_PUBLISH_HOOK_CLASS_NAME))

        return None

    found_methods = get_auto_help_methods()

    preprocess_issue = None

    if _PREPROCESS_DEBUG_KEY in found_methods:
        preprocess_issue = _validate_preprocess(package)

    hook_issue = None

    if _HOOK_DEBUG_KEY in found_methods:
        hook_issue = _validate_release_hook(package)

    return list(filter(None, (preprocess_issue, hook_issue)))
