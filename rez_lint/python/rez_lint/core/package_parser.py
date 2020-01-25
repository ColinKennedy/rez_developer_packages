#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A module that's dedicated to parsing Rez package definition files."""

import re


def _make_attribute_expressions(attribute):
    return (
        re.compile(r"^{attribute}\s*=".format(attribute=attribute)),  # Python syntax
        re.compile(
            r"^def\s+{attribute}\s*\(".format(attribute=attribute)
        ),  # functional
        re.compile(r"^{attribute}\s*:".format(attribute=attribute)),  # YAML syntax
    )


_EXPRESSIONS = {
    "build_requires": _make_attribute_expressions("build_requires"),
    "help": _make_attribute_expressions("help"),
    "private_build_requires": _make_attribute_expressions("private_build_requires"),
    "requires": _make_attribute_expressions("requires"),
    "version": _make_attribute_expressions("version"),
}


def _get_row_number(path, expressions):
    """Get the first line number that matches an expression in `expressions`.

    Args:
        path (str):
            The path on-disk to an ASCII file that is read and parsed.
        expressions (list[:class:`_sre.compile`]):
            Every Regex pattern used to find some text. The first
            line in `path` that matches any of these patterns will be
            returned.

    Returns:
        int: A 1-based number that indicates the found match.

    """
    matches = set()

    with open(path, "r") as handler:
        for index, line in enumerate(handler.readlines()):
            for expression in expressions:
                if expression.match(line):
                    matches.add(index)

                    break

    return sorted(matches)[-1] + 1


def get_definition_row(path, attribute):
    """Get the line in a Rez package that defines the given attribute.

    Args:
        path (str):
            The path on-disk to an ASCII file that is read and parsed.
        attribute (str):
            The Rez package attribute to query. e.g. "version",
            "requires", etc.

    Raises:
        ValueError: If `attribute` is not a supported option.

    Returns:
        int: A 1-based number that indicates the found match.

    """
    try:
        expressions = _EXPRESSIONS[attribute]
    except KeyError:
        raise ValueError(
            'Value "{attribute}" is not an option. Options are "{_EXPRESSIONS}".'
            "".format(attribute=attribute, _EXPRESSIONS=sorted(_EXPRESSIONS))
        )

    try:
        return _get_row_number(path, expressions)
    except IndexError:
        return 0


def get_line_at_row(path, row):
    """Get the ASCII line of a text file.

    Args:
        path (str): The path on-disk to an ASCII file that is read and parsed.
        row (int): A 1-based index number to get the text of.

    Returns:
        str: The text found at that line.

    """
    with open(path, "r") as handler:
        for index, line in enumerate(handler.readlines()):
            if index + 1 == row:
                return line

    return ""
