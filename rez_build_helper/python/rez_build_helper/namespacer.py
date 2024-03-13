"""Simple "struct-like" objects for dealing with Python package namespaces."""

import collections

PythonPackageItem = collections.namedtuple(
    "PythonPackageItem",
    ["namespace_text", "namespace_parts", "relative_path"],
)
