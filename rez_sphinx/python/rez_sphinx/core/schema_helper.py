import re

import schema
import six

_DOT_EXPRESSION = re.compile(r"[a-zA-Z][\w\.]*[\w]")
_SPHINX_MODULE = r"[a-zA-Z0-9\.\ /]"
_TOCTREE_LINE_EXPRESSION = re.compile(
    r"""
    (?:
        {_SPHINX_MODULE}
        |
        .+\s+<{_SPHINX_MODULE}>
    )
    """.format(
        _SPHINX_MODULE=_SPHINX_MODULE
    ),
    re.VERBOSE,
)


def _validate_non_empty_str(item):
    if not item:
        raise ValueError("The given item is empty.")

    if not isinstance(item, six.string_types):
        raise ValueError('Item "{item}" is not a string.'.format(item=item))

    return item


def _validate_python_dot_path(text):
    if not isinstance(text, six.string_types):
        raise ValueError('Item "{text}" is not a string.'.format(text=text))

    return _DOT_EXPRESSION.match(text)


def _validate_toctree_line(text):
    match = _TOCTREE_LINE_EXPRESSION.match(text)

    if match:
        return text

    raise ValueError(
        'Text "{text}" is not a valid toctree entry. '
        'It must match "{_TOCTREE_LINE_EXPRESSION.pattern}".'.format(
            text=text, _TOCTREE_LINE_EXPRESSION=_TOCTREE_LINE_EXPRESSION
        )
    )


NON_NULL_STR = schema.Use(_validate_non_empty_str)
PYTHON_DOT_PATH = schema.Use(_validate_python_dot_path)
TOCTREE_LINE = schema.Use(_validate_toctree_line)
