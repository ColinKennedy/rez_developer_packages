"""The main module for defining pre-release and post-release behavior.

See :class:`PublishDocumentation` for details.

"""

import inspect
import json
import logging
import os
import subprocess

from rez import exceptions, packages, release_hook, resolved_context
from rez.config import config
from rez.vendor.schema import schema

_REZ_SPHINX_PACKAGE_FAMILY_NAME = "rez_sphinx"

_DEFAULT_LABEL = "Home"  # This label matches Rez's default label text
_LOGGER = logging.getLogger(__name__)

_BUILD_DOCUMENTATION_KEY = "build_documentation"
_DOCUMENTATION_FOLDER = "documentation"
_SPHINX_CONFIGURATION_FILE = "conf.py"


class PublishDocumentation(release_hook.ReleaseHook):
    """The class which runs pre-release / post-release methods.

    - On pre-release: Add help keys (See :ref:`auto_append_help_tags`).
    - On post-release: Publish the documentation to remote (See
      :ref:`rez_sphinx publish run`).

    """

    @classmethod
    def name(cls):
        """str: The name to refer to this plug-in class."""
        return "publish_documentation"

    def __init__(self, source_path):
        super(PublishDocumentation, self).__init__(source_path)

        self._publish_context = None

    def pre_release(self, user, install_path, variants=None, **kwargs):
        """Modify the `help`_ attribute, if needed.

        Args:
            user (str):
                The current user name. e.g. ``$USER``.
            install_str (str):
                The directory on-disk where the package and its variants will
                be released to.
            variants (list[rez.packages.Variant], optional):
                The specific variant(s) to release. If no variant was
                specified, this parameter is passed ``None``, implying that all
                variants will be released.
            **kwargs (dict[str, object], optional):
                Extra options to include in the release, if any.

        """
        package = _get_caller_package()
        directory = os.path.dirname(package.filepath)

        if not _has_rez_sphinx_documentation(directory):
            # If there's no ``rez_sphinx`` documentation, there's nothing to do.
            return

        requires = _get_extra_documentation_requires(package)
        context = _get_sphinx_context(extra_request=[str(request) for request in requires])

        if not context:
            raise RuntimeError("Context could not be resolved. Cannot publish documentation.")

        self._publish_context = context

        replace_help(context, package)

    def post_release(self, user, install_path, variants, **kwargs):
        """Send the built documentation to remote server(s), if needed.

        Args:
            user (str):
                The current user name. e.g. ``$USER``.
            install_str (str):
                The directory on-disk where the installed (released) Rez
                package and its variants were built to.
            variants (list[rez.packages.Variant], optional):
                The specific variant(s) which were released. If no variant was
                specified, this parameter is passed ``None``, implying that all
                variants were released.
            **kwargs (dict[str, object], optional):
                Extra options to include in the release, if any.

        """
        stdout = _run_command(self._publish_context, "rez_sphinx publish run")
        print("Got publish output")
        print(stdout)


def _has_rez_sphinx_documentation(directory):
    # TODO : Need a better way to query this that isn't hard-coded
    configuration = os.path.join(directory, _DOCUMENTATION_FOLDER, _SPHINX_CONFIGURATION_FILE)

    return os.path.isfile(configuration)


def _get_caller_package():
    # TODO : This code is cursed. Find a better way to do this. Seriously.
    # Easily the worst code I've ever written.
    #
    current_frame = inspect.currentframe()
    caller_frame = current_frame.f_back.f_back
    filename, lineno, function, code_context, index = inspect.getframeinfo(
        caller_frame
    )

    # f_locals is the local namespace seen by the frame
    caller_instance = caller_frame.f_locals["self"]

    return caller_instance.package


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


def _get_extra_documentation_requires(package):
    tests = package.tests

    if not tests:
        return set()

    # TODO : Don't hard code this. Get from configuration, somehow
    if _BUILD_DOCUMENTATION_KEY not in tests:
        return set()

    test = tests[_BUILD_DOCUMENTATION_KEY]

    if not hasattr(test, "get"):
        # Not ``"requires"`` was defined
        return set()

    return test.get("requires") or []


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

        if line.startswith("[") and line.endswith("]"):
            return line

    raise RuntimeError('Text "{text}" has no expected dict.'.format(text=text))


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
        command (str):
            The shell command to call.

    Returns:
        list[list[str, str]]: The found `help`_ values, if any.

    """
    stdout = _run_command(context, command)
    _LOGGER.debug('Got raw `help` attribute, "%s".', stdout)

    return json.loads(_get_help_line(stdout))


def _get_sphinx_context(extra_request=frozenset()):
    # """Get a Rez context for ``rez_sphinx``, if possible.
    #
    # Returns:
    #     rez.packages.Package or None:
    #         If the context cannot be found, cannot be solved, or as some other
    #         kind of issue, this function returns nothing.
    #
    # """
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
    request.extend(extra_request)

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


def replace_help(context, package):
    """Replace the `package help`_ in ``data`` with auto-found Sphinx documentation.

    If no :ref:`rez_sphinx tags <rez_sphinx tag>` are found, this function will
    exit early and do nothing.

    Args:
        package (rez.packages.Package):
            The source Rez package whose `help`_ attribute will be queried and changed.

    """
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


def _run_command(context, command):
    parent_environment = dict()

    if "REZ_CONFIG_FILE" in os.environ:
        parent_environment["REZ_CONFIG_FILE"] = os.environ["REZ_CONFIG_FILE"]

    process = context.execute_command(
        command,
        stdout=subprocess.PIPE,
        universal_newlines=True,
        parent_environ=parent_environment,
    )
    stdout, stderr = process.communicate()

    if process.returncode != 0:
        raise RuntimeError(
            'Command "{command}" failed for context "{context}".'.format(command=command, context=context)
        )

    return stdout


def register_plugin():
    """PublishDocumentation: Add this plug-in to Rez."""
    return PublishDocumentation
