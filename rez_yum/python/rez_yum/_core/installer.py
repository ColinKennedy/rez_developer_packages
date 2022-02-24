import atexit
import functools
import logging
import shutil
import tempfile

from rez.config import config

from . import download_wrap, rpm_helper


_LOGGER = logging.getLogger(__name__)


def _install(name, destination, keep_temporary_files=False):
    directory = tempfile.mkdtemp(suffix="_rez_yum_install_temporary_directory")

    if not keep_temporary_files:
        _LOGGER.debug('Temporary directory "%s" will be removed later.', directory)

        atexit.register(functools.partial(shutil.rmtree, directory))

    rpms = download_wrap.download_all_packages(name, directory)
    output = []

    for rpm in rpms:
        _LOGGER.debug('Processing "%s" RPM.', rpm)
        data = rpm_helper.get_details(rpm)
        output.append((rpm, data))

    return output


def install(name, destination="", keep_temporary_files=False):
    destination = destination or config.local_packages_path or os.path.expanduser("~", "packages")

    for rpm, data in _install(
        name,
        destination=destination,
        keep_temporary_files=keep_temporary_files,
    ):
        folder = _make_install_folder(rpm, destination)
        _expand_rpm(rpm, folder)
        _create_rez_package_file(data, folder)
