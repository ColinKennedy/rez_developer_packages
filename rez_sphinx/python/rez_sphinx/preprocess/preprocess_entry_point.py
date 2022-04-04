"""The module needed to add :ref:`rez_sphinx` as a preprocess function.

See Also:
    ref:`adding_rez_sphinx_as_a_preprocess`

"""

# TODO : If I end up going with a release plugin, see if I can reuse the code
# from over there here (or vice versa)

import json
import logging
import os
import subprocess

from rez import exceptions, packages, resolved_context
from rez.config import config
from rez.vendor.schema import schema

REZ_HELP_KEY = "help"
_REZ_SPHINX_PACKAGE_FAMILY_NAME = "rez_sphinx"

_SEEN = set()
_DEFAULT_LABEL = "Home Page"
_LOGGER = logging.getLogger(__name__)


def _already_processed(path):
    """Check if ``path`` has already been preprocessed before.

    This function exists to prevent a cyclic loop which may be a bug. See
    reference for details.

    Reference:
        https://github.com/nerdvegas/rez/issues/1239#issuecomment-1061390415

    Args:
        path (str): The directory to a path on-disk pointing to a Rez package.

    Returns:
        bool: If ``path`` was already processed, return True.

    """
    if path in _SEEN:
        return True

    _SEEN.add(path)

    return False


def _get_configured_rez_sphinx():
    """Find the Rez package pointing to our installation of :ref:`rez_sphinx`.

    Since part of :ref:`adding_rez_sphinx_as_a_preprocess` tells the user to
    add to `package_definition_build_python_paths`_, we **assume** that this is
    defined somewhere.

    Returns:
        :class:`rez.developer_package.DeveloperPackage` or None: The found package.

    """
    for (
        path
    ) in config.package_definition_build_python_paths:  # pylint: disable=no-member
        package = _get_nearest_rez_package(path)

        if package and package.name == _REZ_SPHINX_PACKAGE_FAMILY_NAME:
            return package

    return None


def _get_help_line(text):
    """Find the line within ``text`` that has the JSON content to decode.

    Important:
        This function assumes that the JSON dict in ``text`` does not span
        multiple lines!

    Args:
        text (str): Raw command output to parse.

    Raises:
        RuntimeError: If nothing in ``text`` matches the expected dict line.

    Returns:
        str: The found line.

    """
    for line in reversed(text.split("\n")):
        line = line.strip()

        if line.startswith("{") and line.endswith("}"):
            return line

    raise RuntimeError('Text "{text}" has no expected dict.'.format(text=text))


def _get_nearest_rez_package(path):
    """Find the nearest Rez package starting at ``path``.

    Args:
        path (str):
            The absolute path to a folder on disk. This folder should be
            a sub-folder inside of a Rez package to the root of the Rez package.

    Returns:
        :class:`rez.developer_package.DeveloperPackage` or None: The found package.

    """
    directory = path

    if not os.path.isdir(directory):
        # It could be a Python wheel / egg file or something.
        directory = os.path.dirname(directory)

    previous = None
    original = directory

    if not os.path.isdir(directory):
        directory = os.path.dirname(directory)

    while directory and previous != directory:
        if _already_processed(directory):
            return None

        previous = directory

        try:
            return packages.get_developer_package(directory)
        except (
            # This happens if the package in `directory` is missing required data
            exceptions.PackageMetadataError,
            # This happens if the package in `directory` is written incorrectly
            schema.SchemaError,
        ):
            _LOGGER.debug('Directory "%s" found an invalid Rez package.', directory)

        directory = os.path.dirname(directory)

    _LOGGER.debug(
        'Directory "%s" is either inaccessible or is not part of a Rez package.',
        original,
    )

    return None


def _get_resolved_help(context, command):
    """Find and auto-generated a `help`_ attribute for our Rez package.

    Args:
        context (rez.resolved_context.ResolvedContext):
            The context which contains :ref:`rez_sphinx` and :ref:`rez_docbot`.
            (We need :ref:`rez_sphinx` at minimum. But :ref:`rez_docbot` is
            needed for getting network publishing information).

    Returns:
        list[list[str, str]]: The found `help`_ values, if any.

    """
    parent_environment = dict()

    if "REZ_CONFIG_FILE" in os.environ:
        parent_environment["REZ_CONFIG_FILE"] = os.environ["REZ_CONFIG_FILE"]

    # Note: This prevents any cyclic loops which may occur because
    # :ref:`rez_sphinx` calls :func:`rez.developer_package.DeveloperPackage` as
    # part of its work and that function recursively called
    # preprocess_function.
    #
    # Reference: https://github.com/nerdvegas/rez/issues/1239#issuecomment-1061390415
    #
    parent_environment["REZ_PACKAGE_PREPROCESS_FUNCTION"] = ""

    process = context.execute_command(
        command,
        stdout=subprocess.PIPE,
        universal_newlines=True,
        parent_environ=parent_environment,
    )
    stdout, _ = process.communicate()

    _LOGGER.debug('Got raw `help` attribute, "%s".', stdout)

    try:
        stdout = _get_help_line(stdout)
    except RuntimeError:
        return dict()

    return json.loads(stdout)


def _get_sphinx_context():
    """Get a Rez context for ``rez_sphinx``, if possible.

    Returns:
        rez.packages.Package or None:
            If the context cannot be found, cannot be solved, or as some other
            kind of issue, this function returns nothing.

    """
    # TODO : Prevent this from being called recursively, if possible
    package = _get_configured_rez_sphinx()

    if not package:
        # TODO : Consider replacing the log calls in this function with print,
        # since this module is called without logger handlers?
        #
        _LOGGER.warning(
            "Skipping preprocessor because rez_sphinx wasn't set up properly. "
            'Please set "package_definition_build_python_paths" and try again.'
        )

        return None

    # TODO : Also I think we need to detect if docbot is needed and only
    # include it if needed (e.g. have some mechanism so users can build
    # locally, if the explicitly want that)
    #
    request = [
        ".rez_sphinx.feature.docbot_plugin==1",
        "{package.name}=={package.version}".format(  # pylint: disable=missing-format-attribute,line-too-long
            package=package
        ),
    ]

    context = resolved_context.ResolvedContext(request)

    if context.success:
        return context

    _LOGGER.error('Request "%s" failed to resolve. Cannot continue', request)

    return None


def _serialize_help(data):
    """Convert ``data`` to something JSON-friendly.

    Args:
        data (dict[str, list]): The raw Rez package attributes, as a dict.

    Returns:
        str: The JSON text.

    """
    help_ = data.get("help") or []
    help_ = expand_help(help_)

    return json.dumps(help_)


def expand_help(help_):
    """Convert ``help_`` into a list of lists.

    Args:
        help_ (list[str] or str or None): The found Rez package help, if any.

    Returns:
        list[list[str, str]]: Each found label + documentation entry, if any.

    """
    if not help_:
        return []

    if not isinstance(help_, str):
        return help_

    return [[_DEFAULT_LABEL, help_]]


def run(_, data):
    """Replace the `package help`_ in ``data`` with auto-found Sphinx documentation.

    If no :ref:`rez_sphinx tags <rez_sphinx tag>` are found, this function will
    exit early and do nothing.

    Args:
        _ (rez.packages.Package):
            The installed (built) Rez package. This package is mostly read-only.
        data (dict[str, object]):
            The contents of ``this``. Changing this instance will have an
            effect on the Rez package which is written to-disk.

    """
    context = _get_sphinx_context()

    if not context:
        return

    help_ = _serialize_help(data)
    package_source_root = os.getcwd()  # Note: This is **assumed** to be correct

    command = (
        "rez_sphinx suggest preprocess-help '{package_source_root}' '{help_}'".format(
            package_source_root=package_source_root,
            help_=help_,
        )
    )
    _LOGGER.info('Executing command "%s" in the rez_sphinx environment.', command)

    data[REZ_HELP_KEY] = _get_resolved_help(context, command)
