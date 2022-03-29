# TODO : Rename this module later

import logging
import json
import os
import subprocess

from rez import exceptions, packages
from rez import resolved_context
from rez.config import config
from rez.vendor.schema import schema


REZ_HELP_KEY = "help"

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
    for path in config.package_definition_build_python_paths:
        package = _get_nearest_rez_package(path)

        if package:
            return package

    return None


def _get_nearest_rez_package(path):
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
            # TODO : Add reference to that cyclic loop issue from before
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
    # TODO : Do I need this parent environment? Maybe not?
    parent_environment = dict()

    if "REZ_CONFIG_FILE" in os.environ:
        parent_environment["REZ_CONFIG_FILE"] = os.environ["REZ_CONFIG_FILE"]

    # Note: This prevents any cyclic loops which may occur because
    # :ref:`rez_sphinx` calls :func:`rez.developer_package.DeveloperPackage` as
    # part of its work and that function recursively called
    # preprocess_function.
    #
    # TODO Add issue number to refer to this
    #
    parent_environment["REZ_PACKAGE_PREPROCESS_FUNCTION"] = ""

    process = context.execute_command(
        command,
        stdout=subprocess.PIPE,
        universal_newlines=True,
        parent_environ=parent_environment,
    )
    stdout, _ = process.communicate()
    # TODO : double-check the output of this. It looks messed up
    _LOGGER.debug('Got raw `help` attribute, "%s".', stdout)

    # TODO : Sanitize `stdout` here
    return json.loads(stdout)


def _get_sphinx_context():
    package = _get_configured_rez_sphinx()

    if not package:
        # TODO : Consider replacing the log calls in this function with print,
        # since `foo` is called without logger handlers?
        #
        _LOGGER.warning(
            'Skipping preprocessor because rez_sphinx wasn\'t set up properly. '
            'Please set "package_definition_build_python_paths" and try again.'
        )

        return None

    # TODO : Check if I can convert that package to a request using an API method
    request = [
        ".rez_sphinx.feature.docbot_plugin==1",
        "{package.name}=={package.version}".format(package=package),
    ]

    context = resolved_context.ResolvedContext(request)

    if context.success:
        return context

    _LOGGER.error('Request "%s" failed to resolve. Cannot continue', request)

    return None


def _serialize_help(data):
    help_ = data.get("help") or []
    help_ = expand_help(help_)

    return json.dumps(help_)


def expand_help(help_):
    """Convert ``help_`` into a list of lists.

    Args:
        help_ (list[str] or str or NoneType): The found Rez package help, if any.

    Returns:
        list[list[str, str]]: Each found label + documentation entry, if any.

    """
    if not help_:
        return []

    if not isinstance(help_, str):
        return help_

    return [[_DEFAULT_LABEL, help_]]


def thing(this, data):
    context = _get_sphinx_context()

    if not context:
        return

    help_ = _serialize_help(data)
    package_source_root = os.getcwd()  # Note: This is **assumed** to be correct

    command = "rez_sphinx suggest preprocess-help '{package_source_root}' '{help_}'".format(
        package_source_root=package_source_root,
        help_=help_,
    )
    _LOGGER.info('Executing command "%s" in the rez_sphinx environment.', command)

    data[REZ_HELP_KEY] = _get_resolved_help(context, command)
