"""A collection of :mod:`schema` types for :ref:`rez_sphinx` to use internally."""

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
    """Ensure ``item`` is not an empty object or empty string.

    Args:
        item (object or str): Some object to check.

    Raises:
        TypeError: If ``item`` isn't a string.
        ValueError: If ``item`` is empty.

    Returns:
        str: The original ``item``.

    """
    if not isinstance(item, six.string_types):
        raise TypeError('Item "{item}" is not a string.'.format(item=item))

    if not item:
        raise ValueError("The given item is empty.")

    return item


def _validate_python_dot_path(text):
    """Check that ``text`` is a Python dot-separated import path.

    Args:
        text (str):
            A contiguous, absolute import path such as
            ``"rez_sphinx.core.api_builder"``

    Raises:
        ValueError: If ``text`` is not a correct type or invalid typing.

    Returns:
        str: The original ``text``.

    """
    if not isinstance(text, six.string_types):
        raise ValueError('Item "{text}" is not a string.'.format(text=text))

    if not _DOT_EXPRESSION.match(text):
        raise ValueError(
            'Text "{text}" did not match pattern, "{_DOT_EXPRESSION.pattern}"'.format(
                text=text, _DOT_EXPRESSION=_DOT_EXPRESSION
            )
        )

    return text


def _validate_toctree_line(text):
    """Ensure ``text`` is an expected Sphinx toctree entry.

    Common Sphinx toctree expressions could be just a relative path to a ReST
    file (without its .rst extension) such as. ``"foo/bar"`` or a custom title
    + the same relative path such as ``"Foo Bar Link <foo/bar>"``.

    Args:
        text (str): Some text to check.

    Raises:
        ValueError: If ``text`` is invalid.

    Returns:
        str: The original text.

    """
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
