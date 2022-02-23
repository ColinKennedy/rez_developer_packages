import logging

from rez import config

from . import rpm_helper


_LOGGER = logging.getLogger(__name__)


def _install(name, destination, seen=frozenset()):
    seen = seen or set()
    rpms = rpm_helper.download_installed_rpms(name, destination)
    output = []

    for rpm in rpms:
        _LOGGER.debug('Processing "%s" RPM.', rpm)

        data = rpm_helper.get_details(rpm)

        if data.name in seen:
            continue

        seen.add(data.name)

        for requirement in data.requires:
            output.extend(_install(requirement, destination=destination, seen=seen))

        output.append((rpm, data))

    return output


def install(name, destination=""):
    destination = destination or config.local_packages_path

    for rpm, data in _install(name, destination=destination):
        folder = _make_install_folder(rpm, destination)
        _expand_rpm(rpm, folder)
        _create_rez_package_file(data, folder)
