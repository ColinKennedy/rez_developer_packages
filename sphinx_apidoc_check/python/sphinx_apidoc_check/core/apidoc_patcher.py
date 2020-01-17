#!/usr/bin/env python
# -*- coding: utf-8 -*-


_CREATION_TEXT = 'Would create file '
_SKIPPING_TEXT = ' already exists, skipping.'


def parse(text):
    added = set()
    updated = set()

    for line in text.splitlines():
        if text.startswith(_CREATION_TEXT):
            added.add(line[len(_CREATION_TEXT):-1])
        elif text.endswith(_SKIPPING_TEXT):
            # The full message is 'File %s already exists, skipping.' so we
            # need to clip the front and back of the found text.
            #
            updated.add(line[len("File "):len(_SKIPPING_TEXT)])

    return added, updated


# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# import functools
#
# from python_compatibility import wrapping
# from sphinx.ext import apidoc
#
#
# class FileCollector(object):
#     def __init__(self):
#         super(FileCollector, self).__init__()
#
#         self._added = set()
#         self._updated = set()
#
#     def get_added(self):
#         return list(self._added)
#
#     def get_updated(self):
#         return list(self._updated)
#
#     def add_to_added(self, path):
#         self._added.add(path)
#
#     def add_to_updated(self, path):
#         self._updated.add(path)
#
#
# _COLLECTOR = FileCollector()
#
#
# def _write_file_and_log_path(function):
#     @functools.wraps(function)
#     def wrapper(name, text, opts):
#         with wrapping.capture_pipes() as (stdout, _):
#             output = function(name, text, opts)
#
#         text = stdout.getvalue().strip()
#         _CREATION_TEXT = 'Would create file '
#         _SKIPPING_TEXT = ' already exists, skipping.'
#
#         if text.startswith(_CREATION_TEXT):
#             _COLLECTOR.add_to_added(text[len(_CREATION_TEXT):])
#         elif text.endswith(_SKIPPING_TEXT):
#             # The full message is 'File %s already exists, skipping.'
#             # so we need to get just the front
#             _COLLECTOR.add_to_updated(text[len("File "):len(_SKIPPING_TEXT)])
#
#         return output
#
#     return wrapper
#
#
# def get_collector():
#     return _COLLECTOR
#
#
# @wrapping.run_once
# def patch_sphinx_apidoc():
#     apidoc.write_file = _write_file_and_log_path(apidoc.write_file)
