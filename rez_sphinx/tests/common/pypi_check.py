from rez import packages


def to_rez_request(text):
    # TODO : Maybe I can re-use code from rez-pip to replace this text
    return text.replace("-", "_")


def is_request_installed(pypi_request):
    rez_request = to_rez_request(pypi_request)

    return packages.get_latest_package_from_string(rez_request) is not None
