#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The main classes and attributes used to convert checker messages into lint messages."""

import collections
import os

from . import resource_utilities

Location = collections.namedtuple("Location", "path row column text")


class Description(object):
    """The main class that is used to format and display output lint messages."""

    def __init__(self, summary, location, code, full=None):
        """Add text / context information that will be later output.

        Args:
            summary (list[str]): The lines that will be displayed when
                the user chooses to not print the "verbose" lint message.
            location (:attr:`.Location`): The path, row, and column data that
                can be used to find this instance on-disk.
            code (:attr:`.Code`): The category label + its unique key.
                This value can be used to temporarily disable the check
                and identify the check.
            full (list[str], optional): The message that is displayed
                when the user enables "verbose" lint messages.

        Raises:
            ValueError: If `location` has no file path.

        """
        if not location.path:
            raise ValueError(
                'Location "{location!r}" must have a non-empty file path.'.format(
                    location=location
                )
            )

        super(Description, self).__init__()

        self._code = code
        self._full = full or []
        self._location = location
        self._summary = summary

    def _format_message(self, lines, padding=(0, 0)):
        """Change raw lint menssages into a consistent output message.

        This message is sent directly to ``rez_lint`` and printed.

        Args:
            lines (list[str]):
                The lines that come from a :class:`.BaseChecker` plugin.
                These lines are changed to become "linter-friendly".

        Returns:
            list[str]: The lines to print.

        """
        row = self._location.row
        column = self._location.column

        if padding:
            padding_row_template = "{{:{padding[0]}d}}".format(padding=padding)
            padding_column_template = "{{:{padding[1]}d}}".format(padding=padding)
            row = padding_row_template.format(self._location.row)
            column = padding_column_template.format(self._location.column)

        first_line = [
            "{self._code.short_name}: {row}, {column}: {lines[0]} ({self._code.long_name})".format(
                self=self, row=row, column=column, lines=lines,
            )
        ]
        details = ["    " + line for line in lines[1:]]

        return first_line + details

    def is_location_specific(self):
        """bool: If this instance actually refers to a file on-disk."""
        return os.path.exists(self._location.path)

    def get_code(self):
        """:attr:`.Code`): Get the category label + its unique key."""
        return self._code

    def get_full_text(self):
        """list[str]: Get the "verbose" message for this instance."""
        return self._full

    def get_header(self):
        """str: The group / path that this instance refers to."""
        path = self._location.path
        relative = os.path.relpath(path, os.getcwd())

        if not relative.startswith(".."):
            path = relative

        if path == ".":
            path = os.getcwd()

        return path

    def get_location(self):
        """:attr:`.Location`: Find the path, row, and column data for this instance."""
        return self._location

    def get_location_data(self):
        """str: A "path:row:column:line" syntax that Vim uses load a quickfix buffer."""
        text = str(self._location.text.rstrip())
        text += " ({self._code.long_name})".format(self=self)

        return ":".join(
            [
                self.get_header(),
                str(self._location.row),
                str(self._location.column),
                text,
            ]
        )

    def get_message(self, padding=(0, 0), verbose=False):
        """Get the "lint message" representation of this instance.

        Args:
            padding (list[int, int], optional):
                The row and column text that will be used to adjust lint
                messages. It's basically a formatting option.
            verbose (bool, optional):
                If True, the full, unabridged message is returned. If
                False, only a short snippet of the full message is
                returned. Default is False.

        Returns:
            list[str]: The text that will be used for lint messages.

        """
        if verbose:
            return self._format_message(self._full or self._summary, padding=padding)

        return self._format_message(self._summary, padding=padding)

    def get_padding_row(self):
        """int: Get the number that's needed to pad each row value to keep lint output clean."""
        path = self._location.path

        if os.path.isdir(path):
            return 0

        return len(str(resource_utilities.get_line_count(path)))

    def get_padding_column(self):
        """int: Get the number that's needed to pad each column value to keep lint output clean."""
        return len(str(self._location.column))

    def get_summary(self):
        """str: The first line of this instance that is used for lint messages."""
        return self._summary

    def __eq__(self, other):
        """bool: If one instance of this class is equal to the current instance."""
        return (
            self.get_summary() == other.get_summary()
            and self.get_code() == other.get_code()
            and self.get_location() == other.get_location()
            and self.get_full_text() == other.get_full_text()
        )

    def __lt__(self, other):
        """bool: Check if this instance should come before or after another instance."""
        return self.get_summary() < other.get_summary()

    def __repr__(self):  # pragma: no cover
        """str: Get the code needed to copy or re-create this instance."""
        template = "{self.__class__.__name__}({summary!r}, {location!r}, {code!r}, full={full})"

        return template.format(
            self=self,
            summary=self.get_summary(),
            code=self.get_code(),
            location=self.get_location(),
            full=self.get_full_text(),
        )


def _get_vimgrep_sort(line):  # pragma: no cover
    """Get a sorting priority for some vimgrep-style line of text.

    Args:
        line (str):
            Text such as "package.py:10:0:requires = [".
            (10 is the row number, 0 is the column)

    Returns:
        tuple[str or int]:
            A unique object that can be used by Python's `sorted`
            function as a key.

    """
    items = []

    for item in line.split():
        stripped = item.strip(',:')

        if stripped.isdigit():
            items.append(int(stripped))
        else:
            items.append(item)

    return tuple(items)


def sort_with_vimgrep(lines):
    """Sort some vimrgrep-formatted lines, based on file path and row / column data.

    Args:
        lines (iter[str]):
            Text such as ["package.py:10:0:requires = ["].
            (Where 10 is the row number, 0 is the column)

    Returns:
        list[str]: The sorted text.

    """
    return sorted(lines, key=_get_vimgrep_sort)
