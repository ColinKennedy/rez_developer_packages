"""Connect :ref:`Sphinx` to :ref:`rez_sphinx`."""

import itertools
import logging
import textwrap
import os
import traceback

from rez_utilities import finder
import six

from . import exception, preference


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
    output = set()

    for request in itertools.chain(
        package.private_build_requires or [],
        package.build_requires or [],
        package.requires or [],
    ):
        if request.is_ephemeral or request.negation:
            _LOGGER.debug('Skipping loading ephemerals from "%s" package.', request)

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


def _get_environment_package(name):
    # TODO : Replace this with a Rez API call
    variable = "REZ_{name}_ROOT".format(name=name.upper())

    try:
        directory = os.environ[variable]
    except KeyError:
        raise ValueError(
            'Rez package "{name}" is not found. Are you sure it is in your '
            "current Rez resolve?".format(name=name)
        )

    package = finder.get_nearest_rez_package(directory)

    if package:
        return package

    raise RuntimeError(
        'Found directory "{directory}" for Rez package "{name}" but no Rez package. '
        "This should not happen.".format(directory=directory, name=name)
    )


def _get_intersphinx_mappings(package):
    # TODO : Add a configuration option here. Default to only consider "requires"
    output = dict()

    for request in _get_intersphinx_candidates(package):
        package = _get_environment_package(request.name)
        path = _get_package_objects_inv(package)

        if not path:
            continue

        raise ValueError()

    return output


def _get_package_objects_inv(package):
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
    # TODO : We need to handle non-semantic versions here
    return "{version.major}.{version.minor}".format(version=version)


def _get_nearest_caller_package():
    stack = traceback.extract_stack(limit=2)
    caller = stack[-1]

    directory = os.path.dirname(caller.path)

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
    package = _get_nearest_caller_package()

    data["intersphinx_mapping"] = _get_intersphinx_mappings(package)
    data["name"] = package.name
    data["release"] = str(package.version)
    data["version"] = _get_major_minor_version(package.version)

    return data
