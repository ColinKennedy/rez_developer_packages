import atexit
import functools
import logging
import os
import shutil
import tempfile

from rez.config import config
from six.moves import StringIO
import rpm2cpio
from rez import package_maker

from . import cpio_helper, download_wrap, exception, path_registry, rpm_helper


_LOGGER = logging.getLogger(__name__)


def _create_rez_package_file(rpm, destination):
    with package_maker.make_package(rpm.name, destination) as maker:
        maker.name = rpm.name
        maker.version = rpm.version
        maker.requires = rpm.requires
        # TODO : Add this later
        # maker.help = [["Home Page", rpm.home_page]]
        commands = path_registry.get_package_commands(
            os.path.join(destination, maker.name, maker.version)
        )

        if commands:
            maker.commands = "\n".join(sorted(commands))


def _expand_rpm(rpm, install_folder):
    buffer = StringIO()

    with open(rpm, "r") as handler:
        rpm2cpio.rpm2cpio(stream_in=handler, stream_out=buffer)

    _, path = tempfile.mkstemp(suffix="_rpm_cpio_{rpm}".format(rpm=os.path.splitext(os.path.basename(rpm))[0]))

    buffer.seek(0)

    with open(path, "wb") as handler:
        shutil.copyfileobj(buffer, handler)

    _LOGGER.info('Extracting RPM file "%s" to the "%s" folder.', rpm, install_folder)

    cpio_helper.extract(path, install_folder)


def _install(name, destination, keep_temporary_files=False):
    directory = _make_download_directory(keep_temporary_files=keep_temporary_files)
    rpms = download_wrap.download_all_packages(name, directory)

    if not rpms:
        raise exception.NotFound('No RPMs could be found for package "{name}".'.format(name=name))

    _LOGGER.info('Found "%s" RPM files.', len(rpms))

    output = []

    for rpm in rpms:
        _LOGGER.debug('Processing "%s" RPM.', rpm)
        output.append(rpm_helper.get_details(rpm))

    return output


def _make_download_directory(keep_temporary_files=False):
    directory = tempfile.mkdtemp(suffix="_rez_yum_install_temporary_directory")

    if not keep_temporary_files:
        _LOGGER.debug('Temporary directory "%s" will be removed later.', directory)

        atexit.register(functools.partial(shutil.rmtree, directory))

    return directory


def _make_install_folder(rpm, destination):
    directory = os.path.join(destination, rpm.name, rpm.version)

    if not os.path.isdir(directory):
        os.makedirs(directory)

    return directory


def install(name, destination="", keep_temporary_files=False):
    destination = destination or config.local_packages_path or os.path.expanduser("~", "packages")

    for data in _install(
        name,
        destination=destination,
        keep_temporary_files=keep_temporary_files,
    ):
        install_folder = _make_install_folder(data, destination)
        # For safety's sake, in case anything goes wrong during the install, we
        # will make the RPM files **first** copy the package.py **last** so if
        # RPM extraction fails, we don't give the user a broken Rez package by
        # accident.
        #
        _expand_rpm(data.path, install_folder)
        _create_rez_package_file(data, destination)
