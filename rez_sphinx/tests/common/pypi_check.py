"""A quick module for handling differences between PyPI and Rez versioning syntax."""

from rez.utils import pip
from rez import packages


def is_request_installed(pypi_request):
    """Check if ``pypi_request`` is findable as a Rez package.

    Args:
        pypi_request (str):
            Some package request to convert. e.g. ``"some-thing==1.2.3"``.

    Returns:
        bool: If any package was found.

    """
    rez_request = pip.pip_to_rez_package_name(pypi_request)

    return packages.get_latest_package_from_string(rez_request) is not None
