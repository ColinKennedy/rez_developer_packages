"""The functions needed to implement :ref:`build-order --filter`."""

import logging
import os

import six
from rez.config import config
from rez_bump import rez_bump_api
from rez_utilities import finder

from ...core import constant, exception, sphinx_helper
from ...preferences import preference

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


def _is_installed(package, directory, version=None):
    """Check if ``package`` is installed into ``directory``.

    Args:
        package (rez.packages.Package):
            A Rez package to check for.
        directory (str):
            The root folder on-disk where released Rez packages live.
        version (rez.vendor.version.version.Version, optional):
            If included, this version is used instead of ``package.version``.

    Returns:
        bool: If the package is released somewhere.

    """
    version = version or package.version

    if not version:
        # In the rare case that an installed Rez package is unversioned...
        return os.path.isdir(os.path.join(directory, package.name))

    return os.path.isdir(os.path.join(directory, package.name, str(version)))


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
    """Remove from ``packages`` only if has been released with documentation.

    In other words, ``packages`` may be returned even if it already has
    documentation.

    Args:
        packages (list[rez.packages.Package]):
            The source / installed Rez packages to filter. Usually,
            these are source Rez packages.

    Returns:
        list[rez.packages.Package]:
            Every package from ``packages`` which isn't released with
            documentation.

    """
    output = []

    release_path = config.release_packages_path

    if not release_path:
        raise exception.ConfigurationError("No configuration release path was defined.")

    if not os.path.isdir(release_path):
        # If the release path doesn't exist then ``packages`` cannot possibly
        # be released to that location. Though we should warn the user, because
        # it's likely user error if that ever happens.
        #
        _LOGGER.warning('release_packages_path "%s" doesn\'t exist.', release_path)

        return packages

    for package in packages:
        if not _has_documentation(package):
            # :ref:`rez_sphinx init` would bump :attr:`package.version` to its
            # next minor version. So if there's not documentation in `package`
            # then that means we need to check for a release not this package
            # but its **next** version up!
            version = package.version

            if version:
                version = rez_bump_api.bump_version(
                    package.version,
                    minor=1,
                    absolute=False,
                    normalize=True,
                )

            if not _is_installed(package, release_path, version=version):
                output.append(package)
        elif not _is_installed(package, release_path):
            # If ``package`` has documentation then it's assumed that the
            # package's current version is what **would** be released. This
            # typically only happens while re-running batch publish. See
            # :doc:`batch_publish_documentation` for details.
            #
            output.append(package)

    return output


def _no_filter(packages):
    """Don't filter anything.

    Args:
        packages (iter[rez.packages.Packages]): The source / installed Rez packages.

    Returns:
        iter[rez.packages.Packages]: The original, unaltered Rez packages.

    """
    return packages


def get_mode_by_name(name):
    """Find a callable function matching ``name``.

    Args:
        name (str):
            A registered possibility, e.g. ``"none"``, ``"already_released"``,
            ``"already_documented"`` etc.

    Raises:
        ValueError: If ``name`` is not a registered command.

    Returns:
        callable[str] -> list[rez.packages.Package]:
            A function that takes an absolute directory path and then finds all
            Rez packages that it can, underneath the directory.

    """
    try:
        return OPTIONS[name]
    except KeyError:
        raise ValueError(
            'Name "{name}" is invalid. The options were, "{options}".'.format(
                name=name, options=sorted(OPTIONS.keys())
            )
        )


DEFAULT = "none"
OPTIONS = {
    DEFAULT: _no_filter,
    "already_documented": _existing_documentation,
    "already_released": _existing_release,
}
