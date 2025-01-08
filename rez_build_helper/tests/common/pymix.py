"""Miscellaneous functions to make unittests work with between Python versions."""

import platform
import sys


def can_check_links() -> bool:
    """Check if this environment is allowed to check for symlinks."""
    # Python 2 + Windows fails to call os.path.symlink but it's fixed in other
    # operating systems / later Python versions.
    #
    return platform.system() != "Windows" and sys.version_info.major != 2
