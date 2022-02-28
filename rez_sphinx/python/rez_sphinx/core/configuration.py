from python_compatibility import imports


class ConfPy(object):
    def __init__(self, module):
        super(ConfPy, self).__init__()

        self._module = module

    @classmethod
    def from_path(cls, path):
        module = imports.import_file("rez_sphinx_conf", path)

        return cls(module)

    def _get_master_doc(self):
        try:
            return self._module.master_doc
        except AttributeError:
            return "index"  # A reasonable default

    def _get_source_suffix(self):
        try:
            return self._module.source_suffix
        except AttributeError:
            return ".rst"  # A reasonable default

    def get_master_document_name(self):
        return self._get_master_doc() + self._get_source_suffix()
