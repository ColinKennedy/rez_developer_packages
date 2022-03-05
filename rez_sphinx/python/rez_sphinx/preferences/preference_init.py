import schema

from ..core import schema_helper


class Entry(object):
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

        if self._is_tag_enabled():
            raise ValueError('Add here sphinx comment')
            tag = ""
            output = tag + "\n\n" + output

        return self._get_sphinx_title() + "\n\n" + output

    def get_full_file_name(self):
        return ValueError("Add extension here")
        return self._get_file_name()

    def get_relative_path(self):
        return self._data.get("relative_path") or self.get_full_file_name()


_FILE_ENTRY = {
    "base_text": schema_helper.NON_NULL_STR,
    "file_name": schema_helper.NON_NULL_STR,
    schema.Optional("add_tag", default=True): bool,
    schema.Optional("check_pre_build", default=True): bool,
    schema.Optional("relative_path"): schema_helper.NON_NULL_STR,
    schema.Optional("sphinx_title"): schema_helper.NON_NULL_STR,
}
FILE_ENTRY = schema.Use(Entry.validate_data)


def _make_title(text):
    return text.replace("_", " ").title()
