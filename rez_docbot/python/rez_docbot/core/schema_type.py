import _sre
import re

import schema
import six
from six.moves import urllib_parse


_URL_SUBDIRECTORY = re.compile(r"^[\w/]+$")

# TODO : Make sure I don't need functions for these later. If not, simplify them
DEFAULT_AUTHENTICATION = "raw"
RAW = "raw"
FROM_FILE = "from_file"


def _validate_callable(item):
    if callable(item):
        return item

    raise ValueError('Item "{item}" isn\'t a callable function.'.format(item=item))


def _validate_non_empty_str(item):
    if not isinstance(item, six.string_types):
        raise ValueError('Item "{item!r}" is not a string.'.format(item=item))

    if not item:
        raise ValueError('String cannot be empty.')

    return item


def _validate_regex(item):
    if isinstance(item, _sre.SRE_Pattern):
        return item

    raise ValueError('Item "{item}" must be a compiled regex pattern.'.format(item=item))


def _validate_url(item):
    result = urllib_parse.urlparse(item)

    if all((result.scheme, result.netloc)):
        return item

    raise ValueError('Item "{item}" is not a valid URL.'.format(item=item))


def _validate_url_subdirectory(item):
    if _URL_SUBDIRECTORY.match(item):
        return item

    raise ValueError(
        'Item "{item}" is invalid. It must match "{_URL_SUBDIRECTORY.pattern}".'.format(
            item=item, _URL_SUBDIRECTORY=_URL_SUBDIRECTORY
        )
    )


NON_EMPTY_STR = schema.Use(_validate_non_empty_str)

DEFAULT_PUBLISH_PATTERN = "{package.version.major}.{package.version.minor}"
PUBLISH_PATTERNS = schema.Or(_validate_regex, NON_EMPTY_STR)  # TODO : Consider making these more strict in the future

CALLABLE = schema.Use(_validate_callable)

URL = schema.Use(_validate_url)
URL_SUBDIRECTORY = schema.Use(_validate_url_subdirectory)
# SSH = schema.Use(_validate_ssh)  TODO Add this later
