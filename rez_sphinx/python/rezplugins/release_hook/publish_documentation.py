import inspect
import json
import logging
import os
import subprocess

from rez import exceptions, packages, release_hook, resolved_context
from rez.config import config
from rez.vendor.schema import schema


_REZ_SPHINX_PACKAGE_FAMILY_NAME = "rez_sphinx"

_DEFAULT_LABEL = "Home Page"
_LOGGER = logging.getLogger(__name__)


class PublishDocumentation(release_hook.ReleaseHook):
    @classmethod
    def name(cls):
        return "publish_documentation"

    def pre_release(self, user, install_path, variants=None, **kwargs):
        # TODO : This code is cursed. Find a better way to do this. Seriously.
        # Easily the worst code I've ever written.
        #
        current_frame = inspect.currentframe()
        caller_frame = current_frame.f_back
        filename, lineno, function, code_context, index = inspect.getframeinfo(caller_frame)

        # f_locals is the local namespace seen by the frame
        caller_instance = caller_frame.f_locals['self']

        directory = os.path.dirname(caller_instance.package.filepath)

        if _has_rez_sphinx_documentation(directory):
            replace_help(caller_instance.package)

    def post_release(self, user, install_path, variants, **kwargs):
        # TODO : Make this real
        print('POST RELEASE')


def _get_configured_rez_sphinx():
    """Find the Rez package pointing to our installation of :ref:`rez_sphinx`.

    Since part of :ref:`adding_rez_sphinx_as_a_preprocess` tells the user to
    add to `plugin_path`_, we **assume** that this is defined somewhere.

    Returns:
        :class:`rez.developer_package.DeveloperPackage` or None: The found package.

    """
    for path in config.plugin_path or []:
        package = _get_nearest_rez_package(path)

        if package and package.name == _REZ_SPHINX_PACKAGE_FAMILY_NAME:
            return package

    return None


def _get_nearest_rez_package(path):
    """Assuming that `directory` is on or inside a Rez package, find the nearest Rez package.

    Args:
        directory (str):
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

    process = context.execute_command(
        command,
        stdout=subprocess.PIPE,
        universal_newlines=True,
        parent_environ=parent_environment,
    )
    stdout, _ = process.communicate()

    _LOGGER.debug('Got raw `help` attribute, "%s".', stdout)

    # TODO : Sanitize `stdout` here
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
        # since `foo` is called without logger handlers?
        #
        _LOGGER.warning(
            "Skipping preprocessor because rez_sphinx wasn't set up properly. "
            'Please set "plugin_path" and try again.'
        )

        return None

    # TODO : Also I think we need to detect if docbot is needed and only
    # include it if needed (e.g. have some mechanism so users can build
    # locally, if the explicitly want that)
    #
    request = [
        ".rez_sphinx.feature.docbot_plugin==1",
        "{package.name}=={package.version}".format(package=package),
    ]

    context = resolved_context.ResolvedContext(request)

    if context.success:
        return context

    _LOGGER.error('Request "%s" failed to resolve. Cannot continue', request)

    return None


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


def replace_help(package):
    """Replace the `package help`_ in ``data`` with auto-found Sphinx documentation.

    If no :ref:`rez_sphinx tags <rez_sphinx tag>` are found, this function will
    exit early and do nothing.

    Args:
        package (rez.packages.Package):
            The source Rez package whose `help`_ attribute will be queried and changed.

    """
    context = _get_sphinx_context()

    if not context:
        return

    help_ = json.dumps(expand_help(package.help))

    package_source_root = os.path.dirname(package.filepath)

    command = (
        "rez_sphinx suggest preprocess-help '{package_source_root}' '{help_}'".format(
            package_source_root=package_source_root,
            help_=help_,
        )
    )
    _LOGGER.info('Executing command "%s" in the rez_sphinx environment.', command)

    package.resource._data["help"] = _get_resolved_help(context, command)
    del package.resource.__dict__["help"]


def _has_rez_sphinx_documentation(directory):
    raise NotImplementedError('Need to write this')


def register_plugin():
    return PublishDocumentation
