import logging
import os
import subprocess


_LOGGER = logging.getLogger(__name__)


def download_all_packages(name, directory):
    # TODO : Replace this with a Python call later
    _LOGGER.debug('Downloading to directory: "%s"', directory)

    command = [
        "yumdownloader",
        name,
        "--downloadonly",
        # Important: Do not escape the directory path here in --downloaddir or --destdir. It will not work
        "--destdir={directory}".format(directory=directory),
        "--downloaddir={directory}".format(directory=directory),
        "--resolve",
    ]

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )

    stdout, stderr = process.communicate()

    _LOGGER.debug('yumdownloader stdout: "%s".', stdout)
    _LOGGER.debug('yumdownloader stderr: "%s".', stderr)

    return [os.path.join(directory, name) for name in os.listdir(directory)]
