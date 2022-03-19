import logging
import os
from rez_utilities import finder
import six

from ..core import constant, sphinx_helper
from ..preferences import preference


_LOGGER = logging.getLogger(__name__)


def _in_help(label, help_):
    if not help_:
        return False

    if isinstance(help_, six.string_types):
        return False

    return any(entry_label == label for entry_label, _ in help_)


def collect_packages(directories, searcher):
    packages = []
    found_names = set()
    found_uuids = dict()
    invalids = set()

    for directory in directories:
        for package in searcher(directory):
            if package.uuid:
                if package.uuid in found_uuids:
                    invalids.add(package)

                    continue

                found_uuids[package.uuid] = package.name

            if package.name in found_names:
                invalids.add(package)

                continue

            found_names.add(package.name)
            packages.append(package)

    return packages


def filter_existing_documentation(packages):
    output = []

    for package in packages:
        # Check if ``package`` is an installed, auto-generated package
        if _in_help(constant.REZ_SPHINX_OBJECTS_INV, package.help):
            _LOGGER.debug(
                'Package "%s" will be skipped. It already has an objects.inv.',
                package.name,
            )

            continue

        package_root = finder.get_package_root(package)

        # Check if ``package`` is a source package
        documentation_top = os.path.join(
            package_root,
            preference.get_documentation_root_name(),
        )

        if os.path.isdir(documentation_top):
            _LOGGER.debug(
                'Package "%s" will be skipped. It has a documentation folder.',
                package.name,
            )

            continue

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

            continue

        output.append(package)

    return output
