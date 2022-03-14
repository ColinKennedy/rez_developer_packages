"""A quick module for handling differences between PyPI and Rez versioning syntax."""

from rez import packages


def to_rez_request(text):
    """Convert ``text``, a PyPI request, into a Rez package request.

    Args:
        text (str): Some package request to convert. e.g. ``"some-thing==1.2.3"``.

    Returns:
        str: The equivalent Rez request. e.g. ``"some_thing==1.2.3"``.

    """
    # TODO : Maybe I can re-use code from rez-pip to replace this text
    return text.replace("-", "_")


def is_request_installed(pypi_request):
    """Check if ``pypi_request`` is findable as a Rez package.

    Args:
        pypi_request (str):
            Some package request to convert. e.g. ``"some-thing==1.2.3"``.

    Returns:
        bool: If any package was found.

    """
    rez_request = to_rez_request(pypi_request)

    return packages.get_latest_package_from_string(rez_request) is not None
