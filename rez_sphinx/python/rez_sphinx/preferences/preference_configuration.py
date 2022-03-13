import schema
from rez.utils import formatting


def _validate_request(text):
    formatting.PackageRequest(text)

    return text


REQUEST_STR = schema.Use(_validate_request)
