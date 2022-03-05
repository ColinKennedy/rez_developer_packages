import textwrap
import os

import schema

from ..core import schema_helper


_BASE_TEXT = textwrap.dedent(
    """\
    This auto-generated file is meant to be written by the developer. Please
    provide anything that could be useful to the reader such as:

    - General Overview
    - A description of who the intended audience is (developers, artists, etc)
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
_TAG_TEMPLATE = textwrap.dedent(
    """\
    ..
        rez_sphinx_help:{title}"""
)


class Entry(object):
    def __init__(self, data):
        super(Entry, self).__init__()

        self._data = data

    @classmethod
    def validate_data(cls, data):
        data = _FILE_ENTRY.validate(data)

        return cls(data)

    def _is_tag_enabled(self):
        return self._data.get("add_tag") or True

    def _get_file_name(self):
        return self._data["file_name"]

    def _get_sphinx_title(self):
        return self._data.get("sphinx_title") or _make_title(self._get_file_name())

    def check_pre_build(self):
        return self._data.get("check_pre_build") or True

    def get_default_text(self):
        output = self._data["base_text"]
        title = self._get_sphinx_title()

        if self._is_tag_enabled():
            # TODO : Maybe it'd be cool to add a directive to Sphinx called
            # "rez_sphinx_help" and then somehow query those smartly. Or just do a
            # raw text parse. Either way is probably fine.
            #
            # Reference: https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html
            #
            output = _TAG_TEMPLATE.format(title=title) + "\n\n" + output

        return _DEFAULT_TEXT_TEMPLATE.format(
            title=title,
            title_suffix="=" * len(title),
            output=output,
        )

    def get_toctree_line(self):
        path = self.get_relative_path()

        return os.path.splitext(path)[0]

    def get_full_file_name(self):
        # TODO : Get this .rst from the user's configuration settings
        return self._get_file_name() + ".rst"

    def get_relative_path(self):
        return self._data.get("relative_path") or self.get_full_file_name()


_FILE_ENTRY = schema.Schema({
    "base_text": schema_helper.NON_NULL_STR,
    "file_name": schema_helper.NON_NULL_STR,
    schema.Optional("add_tag", default=True): bool,
    schema.Optional("check_pre_build", default=True): bool,
    schema.Optional("relative_path"): schema_helper.NON_NULL_STR,
    schema.Optional("sphinx_title"): schema_helper.NON_NULL_STR,
})
FILE_ENTRY = schema.Use(Entry.validate_data)
DEFAULT_ENTRIES = (
    Entry.validate_data(
        {
            "base_text": _BASE_TEXT,
            "file_name": "developer_documentation",
            "sphinx_title": "Developer Documentation",
        }
    ),
    Entry.validate_data(
        {
            "base_text": _BASE_TEXT,
            "file_name": "user_documentation",
            "sphinx_title": "User Documentation",
        }
    ),
)


def _make_title(text):
    return text.replace("_", " ").title()
