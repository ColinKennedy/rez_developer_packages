"""Connect :ref:`Sphinx` to :ref:`rez_sphinx`."""

import itertools
import logging
import os
import textwrap
import traceback

import six
from rez_utilities import finder

from . import exception, path_control, preference

_LOGGER = logging.getLogger(__name__)
_REZ_SPHINX_BOOTSTRAP_LINES = textwrap.dedent(
    """
    # -- rez-sphinx start --
    # -- DO NOT TOUCH --
    #
    # These lines are needed for rez-sphinx to work
    #
    from rez_sphinx import api
    locals().update(api.bootstrap(locals()))
    #
    # If you want to add extra user customizations, please feel free to add any
    # of them BELOW this line.
    #
    # -- rez-sphinx end --
    """
)


def _get_intersphinx_candidates(package):
    """Find every dependeny of ``package`` which will be checked for a :ref:`objects.inv`.

    Args:
        package (:class:`rez.developer_package.DeveloperPackage`):
            A Rez package which the user is attempting to build documentation for.

    Returns:
        set[str]:
            All Rez package family name requests which the user needs in
            order to build their documentation.

    """
    output = set()

    # TODO : Add a configuration option here. Default to only consider "requires"
    for request in itertools.chain(
        package.private_build_requires or [],
        package.build_requires or [],
        package.requires or [],
    ):
        if request.ephemeral:
            _LOGGER.debug('Skipped loading "%s" ephemeral request.', request)

            continue

        if request.conflict:
            _LOGGER.debug('Skipped loading "%s" excluded request.', request)

            continue

        if request.weak and not _in_resolve(request.name):
            _LOGGER.debug('Skipped loading "%s" weak request.', request)

            continue

        if request.name in output:
            # If the user defines a package requirement in more than one
            # place, that's okay because a Rez resolve will only get one
            # single Package version. Just skip the duplicate requirement.
            #
            continue

        output.add(request.name)

    output.update(_get_tests_requires(package))

    return output


def _in_resolve(name):
    """Check if ``name`` is a Rez package family which is in the current resolve.

    Args:
        name (str): A Rez package name. e.g. "python", "Sphinx", etc.

    Returns:
        bool: If ``name`` has a root path.

    """
    try:
        return bool(path_control.get_installed_root(name))
    except EnvironmentError:
        return False


def _get_environment_package(name):
    """Find a Rez package describing ``name``.

    Important:
        This function assumes that ``name`` is in the current Rez resolve.

    Args:
        name (str):
            The Rez package family name to search for. e.g. "rez",
            "Sphinx", "python", etc.

    Raises:
        EnvironmentError:
            If ``name`` is not listed in your Rez environment.
        RuntimeError:
            If for some reason ``name`` exists but has no Rez valid Rez
            package. If this happens, it's almost 100% some kind of Rez
            build / release issue, caused by **user** error.

    Returns:
        :class:`rez.developer_package.DeveloperPackage`: The found package.

    """
    directory = path_control.get_installed_root(name)
    package = finder.get_nearest_rez_package(directory)

    if package:
        return package

    raise RuntimeError(
        'Found directory "{directory}" for Rez package "{name}" but no Rez package. '
        "This should not happen.".format(directory=directory, name=name)
    )


def _get_intersphinx_mappings(package):
    """Find every :ref`:objects.inv` file for each dependency of ``package``.

    The found :ref`:objects.inv` will be used to populate a
    :ref:`intersphinx_mapping` for ``package``. This enables
    cross-linking between external Rez packages, as long as they were
    also built by Sphinx.

    Note:
        The searched Rez packages by default are

        - :ref:`requires`
        - :ref:`build_documentation_key`

        If you want to search for other requests for your package, like
        :ref:`private_build_requires` or :ref:`build_requires`, consider
        setting that using :ref:`rez-config`.

    Args:
        package (:class:`rez.developer_package.DeveloperPackage`):
            A Rez package which the user is attempting to build documentation for.

    Returns:
        dict[str, tuple[str] or str]:
            A suitable :ref:`intersphinx_mapping` for :ref:`Sphinx`.

    """
    output = dict()

    for request in _get_intersphinx_candidates(package):
        package = _get_environment_package(request)
        path = _get_package_objects_inv(package)

        if not path:
            continue

    return output


def _get_package_objects_inv(package):
    """Find the path to a Rez package's :ref:`objects.inv` file.

    The package may have a locally installed :ref:`objects.inv` or it
    may be pointing to an Internet URL.  Either way, return the string
    there.

    Args:
        package (:class:`rez.developer_package.DeveloperPackage`):
            A Rez package which we assume may have built
            :ref:`rez_sphinx` documentation and thus also has a
            :ref:`objects.inv` file.

    Returns:
        str:
            The Internet URL or the absolute path for a directory
            containing the "objects.inv" file.

    """
    help_ = package.help or []
    help_label = preference.get_help_label()

    if not help_:
        _LOGGER.warning(
            'Package "%s" has no help. No "%s" help found.',
            package.name,
            help_label,
        )

        return ""

    if isinstance(help_, six.string_types):
        _LOGGER.warning(
            'Package "%s" has single-line help. No "%s" help found.',
            package.name,
            help_label,
        )

        return ""

    for label, path in help_:
        if label == help_label:
            _LOGGER.info(
                'Found: Package "%s" has "%s" defined.', package.name, help_label
            )

            return path

    _LOGGER.info(
        'Package "%s" has tests but no "%s" is defined.', package.name, help_label
    )

    return ""


def _get_tests_requires(package):
    """Find every requested requirement of ``package``.

    Args:
        package (:class:`rez.developer_package.DeveloperPackage`):
            The Rez package which the user is trying to generate Sphinx
            documentation for.

    Returns:
        set[str]:
            All requests which the user needs in order to build their
            documentation.

    """
    tests = package.tests or dict()

    if not tests:
        return set()

    test = tests.get(preference.get_build_documentation_key())

    if not test:
        return set()

    if isinstance(test, six.string_types):
        # It's a rez-test like ``tests = {"build_documentation": "bar"}``.
        # It defines no extra requirements so we can skip it.
        #
        return set()

    return {request.name for request in test.get("requires") or []}


def _get_major_minor_version(version):
    """Convert ``version`` into a "major.minor" string.

    Args:
        version (:class:`rez.vendor.version.version.Version`): The object to convert.

    Returns:
        str: The major + minor.

    """
    # TODO : We need to handle non-semantic versions here
    return "{version.major}.{version.minor}".format(version=version)


def _get_nearest_caller_package():
    """Find the Rez package which called this function.

    Important:
        This function is fragile. Don't use it outside of the context of
        :func:`bootstrap`.

    Raises:
        :class:`.NoPackageFound`: If no Rez package could be found.

    Returns:
        :class:`rez.developer_package.DeveloperPackage`: The found package.

    """
    stack = traceback.extract_stack(limit=3)
    frame = stack[0]
    caller_path = frame.filename

    _LOGGER.debug('Found caller "%s" file path.', caller_path)

    directory = os.path.dirname(caller_path)

    package = finder.get_nearest_rez_package(directory)

    if package:
        return package

    raise exception.NoPackageFound(
        'Directory "{directory}" has no Rez package. '
        "This exception is almost certainly a bug. "
        "Please contact rez_sphinx maintainers.".format(directory=directory),
    )


def append_bootstrap_lines(path):
    """Append :ref:`rez_sphinx` specific commands to a :ref:`Sphinx` conf.py file.

    Args:
        path (str):
            The absolute path to a conf.py which :ref:`Sphinx` uses to source
            and build the user's documentation.

    """
    with open(path, "a") as handler:
        handler.write("\n\n" + _REZ_SPHINX_BOOTSTRAP_LINES)


def bootstrap(data):
    """Gather Rez package information for :ref:`Sphinx`.

    This data is returned and used to auto-fill-out the values for
    :ref:`Sphinx conf.py`.

    Returns:
        dict[str, object]: All Rez data to send to the :ref:`Sphinx conf.py`.

    """
    package = _get_nearest_caller_package()

    data["intersphinx_mapping"] = _get_intersphinx_mappings(package)
    data["name"] = package.name
    data["release"] = str(package.version)
    data["version"] = _get_major_minor_version(package.version)

    return data
