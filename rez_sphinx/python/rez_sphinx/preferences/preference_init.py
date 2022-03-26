r"""Some Sphinx files may be generated during :ref:`rez_sphinx init`.

This module is in charge of describing those files. e.g. what the file name is,
its file content, how will Rez / Sphinx refer to that file, etc.

This module is a companion module for :mod:`.preference`.

Attributes:
    FILE_ENTRY (:class:`schema.Schema`):
        "base_text" (str): "The documentation text body\nto write to this file."
        "path" (str): "inner/folder/some_file_name_without_an_extension"
        "add_tag" (bool, optional): If True, a :ref:`rez_sphinx tag` is added.
        "check_pre_build" (bool, optional): If True, ensure "path" has edits, pre-build.
        "title" (str, optional): "Custom title name if you want"

"""

import io
import os
import re
import textwrap

import schema

from ..core import generic, schema_helper

_BASE_TEXT = textwrap.dedent(
    """\
    This auto-generated file is meant to be written by the developer. Please
    provide anything that could be useful to the reader such as:

    - General Overview
    - A description of who the intended reader is (developers, artists, etc)
    - Tutorials
    - "Cookbook" style tutorials
    - Table Of Contents (toctree) to other Sphinx pages
    """
)
_DEFAULT_TEXT_TEMPLATE = textwrap.dedent(
    """\
    {title}
    {title_suffix}

    {output}"""
)
_TAG_NAME = "rez_sphinx_help"
_TAG_TEMPLATE = "..\n    %s:{title}" % _TAG_NAME
_SPHINX_REF = re.compile(r"^\.\. _(?P<label>[\w ]+):\s*$")
_HAS_INDENT = re.compile(r"^\s+[^\s]*")
_IS_COMMENT = re.compile(r"^\.\.\s*")


class Entry(object):
    """A description for Sphinx files to generate during :ref:`rez_sphinx init`."""

    def __init__(self, data):
        """Store ``data`` for reference, later.

        Args:
            data (dict[str, object]): All content which describes the current instance.

        """
        super(Entry, self).__init__()

        self._data = data

    @classmethod
    def validate_data(cls, data):
        """Check if ``data`` is valid and, if so, create a new instance.

        Args:
            data (dict[str, object]): All content which describes the current instance.

        Returns:
            Entry: The created instance.

        """
        data = _FILE_ENTRY.validate(data)

        return cls(data)

    def _is_tag_enabled(self):
        """If True, add an tag for Rez to generate a `help`_ for later, on-build.

        References:
            :ref:`rez_sphinx auto-help`.

        Returns:
            bool:
                If True, this instance is auto-registered by Rez, pre-build. If
                False, this document is still added to Sphinx but it is not
                auto-discovered by Rez nor appended to the user's package
                `help`_ attribute during `rez-build`_.

        """
        return self._data.get("add_tag") or True

    def _get_file_name(self):
        """str: Get the "on-disk save name" for this instance (no file extension)."""
        path = os.path.basename(self.get_relative_path())

        return os.path.splitext(path)[0]

    def _get_title(self):
        """str: A human-friendly phrase to describe this instance, in documentation."""
        return self._data.get("title") or _make_title(self._get_file_name())

    def check_pre_build(self):
        """If True, make sure users have manually filled out the documentation.

        In short, check if the found documentation on-disk matches
        :meth:`Entry.get_default_text`. If it's the same then we know that the
        user hasn't updated the documentation yet.

        Returns:
            bool: If True, run the check prior to Sphinx builds. If False, don't.

        """
        # TODO : Add a unittest for this functionality
        return self._data.get("check_pre_build") or True

    def get_default_text(self):
        """str: The generated Sphinx documentation text body."""
        output = self._data["base_text"]
        title = self._get_title()

        if self._is_tag_enabled():
            # TODO : Maybe it'd be cool to add a directive to Sphinx called
            # "rez_sphinx_help" and then somehow query those smartly. Or just do a
            # raw text parse. Either way is probably fine.
            #
            # Reference: https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html  pylint: disable=line-too-long
            #
            output = _TAG_TEMPLATE.format(title=title) + "\n\n" + output

        return _DEFAULT_TEXT_TEMPLATE.format(
            title=title,
            title_suffix="=" * len(title),
            output=output,
        )

    def get_toctree_line(self):
        """str: The text to add into a Sphinx toctree which refers to this instance."""
        path = self.get_relative_path()
        normalized = os.path.normcase(path)
        name = os.path.splitext(normalized)[0]

        return name.replace("\\", "/")  # Sphinx uses forward slashes in toctrees

    def get_relative_path(self):
        """str: Get the path to this file, relative to the documentation source root."""
        # TODO : Get this .rst from the user's configuration settings. Don't do this
        return self._data.get("path") + ".rst"

    def write(self, root):
        """Write this instance to disk, starting at ``root``.

        This method may make inner directories as needed.

        Args:
            root (str):
                A directory to start writing the file within. Usually this is
                the documentation source root.

        """
        full = os.path.join(root, self.get_relative_path())
        directory = os.path.dirname(full)

        if not os.path.isdir(directory):
            os.makedirs(directory)

        text = generic.decode(self.get_default_text())

        with io.open(full, "w", encoding="utf-8") as handler:
            handler.write(text)

    def __repr__(self):
        """str: Create a representation of this instance."""
        return "{self.__class__.__name__}({self._data!r})".format(self=self)


_FILE_ENTRY = schema.Schema(
    {
        "base_text": schema_helper.NON_NULL_STR,
        "path": schema_helper.NON_NULL_STR,
        schema.Optional("add_tag", default=True): bool,
        schema.Optional("check_pre_build", default=True): bool,
        schema.Optional("relative_path"): schema_helper.NON_NULL_STR,
        schema.Optional("title"): schema_helper.NON_NULL_STR,
    }
)
FILE_ENTRY = schema.Use(Entry.validate_data)
DEFAULT_ENTRIES = (
    Entry.validate_data(
        {
            "base_text": _BASE_TEXT,
            "path": "developer_documentation",
            "title": "Developer Documentation",
        }
    ),
    Entry.validate_data(
        {
            "base_text": _BASE_TEXT,
            "path": "user_documentation",
            "title": "User Documentation",
        }
    ),
)


def _get_header_text_at(offset, lines):
    """Find the appropriate header text, starting from ``offset``.

    If a document looks like this:

    ::

        <(1)

        ===============
        Overline Header
        ===============

        <(2)

        More text

        <(3)

        .. A sphinx role / comment

        <(4)

        underline header
        ****************

        <(5)

        Last line

    Imagine each <(1/2/3/4/5) is your cursor position for ``offset``.

    - <(1) returns ``"Overline Header"``.
    - <(2) returns nothing, because it's obstructed by "More text".
    - <(3) returns ``"underline header"`` (it ignores the sphinx comment line)
    - <(4) returns ``"underline header"``, too
    - <(5) returns nothing, because it's at the end of the lines

    Todo:
        Add unittests for all of these situations.

    Args:
        offset (int): A 0-or-more value where we'll start looking for a header.
        lines (list[str]): The ReST source code to look within for the header.

    Returns:
        str: The found header line, if any.

    """

    def _uses_one_character(text):
        return len(set(text)) == 1

    def _get_underline_header_text(index, lines, line_length):
        after_index = index + 1

        if after_index >= line_length:
            return ""

        expected_text = lines[index].rstrip()
        after = lines[after_index].rstrip()

        if _uses_one_character(after) and len(after) == len(expected_text):
            return expected_text

        return ""

    def _get_overline_header_text(index, lines, line_length):
        before_index = index - 1

        if before_index < 0:
            return ""

        after_index = index + 1

        if after_index >= line_length:
            return ""

        before = lines[before_index].rstrip()
        expected_text = lines[index].rstrip()
        after = lines[after_index].rstrip()

        if (
            _uses_one_character(before)
            and before == after
            and len(before) == len(expected_text)
            and len(expected_text) == len(after)
            and len(after) == len(before)
        ):
            return expected_text

        return ""

    line_length = len(lines)

    for index, line in enumerate(lines[offset:]):
        if not line.strip() or _IS_COMMENT.match(line) or _HAS_INDENT.match(line):
            continue

        header = _get_overline_header_text(offset + index, lines, line_length)

        if header:
            return header

        header = _get_underline_header_text(offset + index, lines, line_length)

        if header:
            return header

        return ""

    return ""


def find_tags(lines):
    """Parse ``lines`` for :ref:`rez_sphinx tags <rez_sphinx tag>`.

    An expected tag looks like this:

    ::
        ..
           rez_sphinx_help:My Label Here

    Args:
        lines (list[str]): The source-code lines of some Sphinx ReST file.

    Returns:
        list[list[str, str]]: Each hard-coded label + "destination", if any.

    """
    output = []
    count = len(lines)

    for index, line in enumerate(lines):
        if not _IS_COMMENT.match(line):
            continue

        next_index = index + 1

        if next_index > count:  # `line` is the last line. Skip this.
            continue

        next_line = lines[next_index].strip()

        if not next_line.startswith(_TAG_NAME):
            continue

        _, name = next_line.split(":")
        destination = _get_header_text_at(next_index + 1, lines)

        output.append((name, destination))

    return output


def _make_title(text):
    """Convert some file name into a Human-friendly documentation phrase.

    Args:
        text (str): Some disk file name to convert. e.g. "some_file".

    Returns:
        str: The converted phrase. e.g. "Some File".

    """
    return text.replace("_", " ").title()
