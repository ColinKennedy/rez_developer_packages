import _sre

import schema
import six


def _validate_non_empty_str(item):
    if not isinstance(item, six.string_types):
        raise ValueError('Item "{item!r}" is not a string.'.format(item=item))

    if not item:
        raise ValueError('String cannot be empty.')

    return item


def _validate_regex(item):
    if not isinstance(item, _sre.SRE_Pattern):
        raise ValueError('Item "{item}" must be a compiled regex pattern.')

    return item


NON_EMPTY_STR = schema.Use(_validate_non_empty_str)
DEFAULT_PUBLISH_PATTERN = "{package.version.major}{package.version.minor}"
PUBLISH_PATTERNS = schema.Or(_validate_regex, NON_EMPTY_STR)  # TODO : Consider making these more strict in the future
