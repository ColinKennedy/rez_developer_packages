"""All of the tests for :mod:`rez_build_helper`."""

import os

# Remove any environment variables that could cause tests to fail.
for name in ["TMPDIR", "TEMP", "TMP"]:
    if name in os.environ:
        del os.environ[name]
