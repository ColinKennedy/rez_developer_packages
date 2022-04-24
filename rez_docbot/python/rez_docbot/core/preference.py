"""A module for describing all :ref:`rez_docbot` settings."""

# TODO : All preferences need to be unittested. global + reading from a package
import functools

import schema
from rez.config import config as config_

from . import publisher_

_MASTER_KEY = "rez_docbot"
_PUBLISHERS = "publishers"

_REZ_OPTIONVARS = "optionvars"
_PACKAGE_CONFIGURATION_ATTRIBUTE = "rez_docbot_configuration"


def _override_rez_configuration(package):
    """Add the configuration using the contents of ``package``.

    Args:
        package (rez.packages.Package):
            A source / installed Rez package to query values from.

    Returns:
        rez.config.Config: The copied, overwritten configuration.

    """
    overrides = {
        _REZ_OPTIONVARS: {
            _MASTER_KEY: getattr(package, _PACKAGE_CONFIGURATION_ATTRIBUTE)
        }
    }

    config = config_.copy(overrides=overrides)

    raise ValueError(sorted(dir(config)))


def get_base_settings(package):
    """Get the parsed classes for publishing documentation.

    Args:
        package (rez.packages.Package):
            A package which may contain extra configuration overrides.
            Any override not found will be retrieved globally.

    Returns:
        dict[str, object]: The parsed user configuration settings.

    """
    if hasattr(package, _PACKAGE_CONFIGURATION_ATTRIBUTE):
        config = _override_rez_configuration(package)
    else:
        config = config_

    if hasattr(config, "optionvars"):
        rez_user_options = config.optionvars  # pylint: disable=no-member
    else:
        rez_user_options = {}

    data = rez_user_options.get(_MASTER_KEY) or dict()

    if not data:
        return dict()

    publisher_schema = schema.Schema(
        {
            _PUBLISHERS: [
                schema.Use(functools.partial(publisher_.validate_publisher, package))
            ],
        }
    )

    return publisher_schema.validate(data)


def get_all_publishers(package):
    """Get every publish method registered globally and under ``package``.

    Important:
        The returned :class:`.Publisher` classes are not authenticated by
        default.  You need to call :meth:`.Publisher.authenticate` to connect
        them to a remote repository database (like `GitHub`_).

    Args:
        package (rez.packages.Package):
            A package which may contain extra configuration overrides.
            Any override not found will be retrieved globally.

    Returns:
        list[Publisher]: Every registered publish method.

    """
    data = get_base_settings(package)

    if not data:
        return []

    return data[_PUBLISHERS]


def get_first_versioned_view_url(package, allow_optionals=False):
    """Find a URL where published documentation lives.

    Args:
        package (rez.packages.Package, optional):
            A package which may contain extra configuration overrides.
            Any override not found will be retrieved globally.
        allow_optionals (bool, optional):
            In :ref:`rez_docbot`'s configuration, users can mark documentation
            sources as optional (or not). If it's optional, there's a chance
            that the documentation URL points to nothing. If you would rather
            ensure the returned URL definitely has documentation, use the
            default option for this parameter (``False``).

    Raises:
        RuntimeError:
            If no viewing URL could be found.

    Returns:
        str: A recommended, found URL to view the documentation from.

    """
    publishers = get_all_publishers(package=package)

    if not publishers:
        raise RuntimeError(
            'Global configuration + package "{package}" have no publishers.'.format(
                package=package
            )
        )

    optionals = []
    unversioned = []

    for publisher in publishers:
        if not publisher.is_required():
            optionals.append(publisher)

            if not allow_optionals:
                continue

        if not publisher.allow_versioned_publishes():
            continue

        return publisher.get_resolved_view_url()

    if unversioned:
        raise RuntimeError(
            'No required publisher "{unversioned}" supports versioning.'.format(
                unversioned=unversioned
            )
        )

    if optionals:
        raise RuntimeError(
            "No required publishers were found. Optional publishers "
            '"{optionals}" were ignored.'.format(optionals=optionals)
        )

    raise RuntimeError("Unknown error. Cannot continue.")
