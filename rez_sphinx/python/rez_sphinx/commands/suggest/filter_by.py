import os
import logging
import six
from rez_utilities import finder

from ..core import constant, sphinx_helper
from ..preferences import preference


_LOGGER = logging.getLogger(__name__)


# TODO : Combine this logic with initer._check_for_existing_documentation
# We must be using the same function for both!
#
def _has_documentation(package):
    """Determine if ``package`` needs :ref:`rez_sphinx init` ran on it.

    Args:
        package (rez.packages.Package):
            The source Rez package to check for documentation.

    Returns:
        bool: If ``package`` has documentation, return True.

    """
    # Check if ``package`` is an installed, auto-generated package
    if _in_help(constant.REZ_SPHINX_OBJECTS_INV, package.help):
        _LOGGER.debug(
            'Package "%s" will be skipped. It already has an objects.inv.',
            package.name,
        )

        return True

    package_root = finder.get_package_root(package)

    # Check if ``package`` is a source package
    documentation_top = os.path.join(
        package_root,
        preference.get_documentation_root_name(package=package),
    )

    if os.path.isdir(documentation_top):
        _LOGGER.debug(
            'Package "%s" will be skipped. It has a documentation folder.',
            package.name,
        )

        return True

    try:
        configuration = sphinx_helper.find_configuration_path(package_root)
    except RuntimeError:
        pass
    else:
        _LOGGER.debug(
            'Package "%s" will be skipped. It has a conf.py "%s" file.',
            package.name,
            configuration,
        )

        return True

    return False


def _in_help(label, help_):
    """Check if ``label`` is in ``help_``.

    Args:
        label (str):
            A phrase to search with ``help_`` for. e.g. ``"Foo"``.
        help_ (list[list[str, str]] or str or None):
            The defined `help`_, if any. e.g. ``[["Foo", "README.md"]]``

    Returns:
        bool: If ``label`` is in ``help_``, return True.

    """
    if not help_:
        return False

    if isinstance(help_, six.string_types):
        return False

    return any(entry_label == label for entry_label, _ in help_)


def _existing_documentation(packages):
    """Remove any Rez package from ``packages`` which already has documentation.

    This function uses a variety of checks including searching "known"
    documentation locations. As well as guessing where it could be.

    This function searches specifically for `Sphinx`_ documentation only.

    Args:
        packages (list[rez.packages.Package]):
            The source / installed Rez packages to filter. Usually,
            these are source Rez packages.

    Returns:
        list[rez.packages.Package]:
            Every package from ``packages`` which doesn't have documentation.

    """
    return [package for package in packages if not _has_documentation(package)]


def _existing_release(packages):
    output = []

    for package in packages:
        if not _has_documentation(package):
            output.append(package)

    return output


def _no_filter(package):
    raise ValueError()


def get_mode_by_name(name):
    # """Find a callable function matching ``name``.
    #
    # Args:
    #     name (str):
    #         A registered possibility, e.g. ``"none"``, ``"installed"``, or
    #         ``"guess"``.
    #
    # Raises:
    #     ValueError: If ``name`` is not a registered command.
    #
    # Returns:
    #     callable[str] -> list[rez.packages.Package]:
    #         A function that takes an absolute directory path and then finds all
    #         Rez packages that it can, underneath the directory.
    #
    # """
    try:
        return OPTIONS[name]
    except KeyError:
        raise ValueError(
            'Name "{name}" is invalid. The options were, "{options}".'.format(
                name=name, options=sorted(OPTIONS.keys())
            )
        )


_DEFAULT_KEY = "none"
OPTIONS = {
    _DEFAULT_KEY: _no_filter,
    "already_ran": _existing_documentation,
    "already_released": _existing_release,
}
