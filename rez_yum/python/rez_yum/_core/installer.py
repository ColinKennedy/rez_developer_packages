from rez import config

from . import rpm_helper


def _install(name, destination, seen=frozenset()):
    seen = seen or set()
    rpms = rpm_helper.download_installed_rpms(name, destination)
    output = []

    for rpm in rpms:
        data = _get_package_details(rpm)
        full_path = _get_full_qualified_name(data)

        if full_path in seen:
            continue

        seen.add(full_path)

        for requirement in data.all_requirements:
            _install(requirement, destination=destination, seen=seen)

        output.append((rpm, data))


def install(name, destination=""):
    destination = destination or config.local_packages_path

    for rpm, data in _install(name, destination=destination):
        folder = _make_install_folder(rpm, destination)
        _expand_rpm(rpm, folder)
        _create_rez_package_file(data, folder)
