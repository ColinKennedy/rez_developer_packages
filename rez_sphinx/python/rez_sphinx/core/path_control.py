"""Miscellaneous functions which make working with file paths easier."""

import io
import os
import shutil
import textwrap

from . import generic


def add_gitignore(directory):
    """Add a .gitignore into ``directory`` which ignores all folder contents.

    No matter what files or folders are added under ``directory``, they
    will be ignored by git.

    Args:
        directory (str): An absolute or relative path to a directory on-disk.

    """
    with io.open(
        os.path.join(directory, ".gitignore"), "w", encoding="utf-8"
    ) as handler:
        handler.write(
            generic.decode(
                textwrap.dedent(
                    """\
                    *
                    **/
                    !.gitignore
                    """
                )
            )
        )


def clear_directory(directory):
    """Delete the contents of ``directory`` without deleting ``directory`` itself.

    Args:
        directory (str): An absolute or relative path to a directory on-disk.

    Raises:
        IOError: If ``directory`` does not exist.

    """
    if not os.path.isdir(directory):
        raise IOError(
            'Directory "{directory}" does not exist.'.format(directory=directory)
        )

    for name in os.listdir(directory):
        full = os.path.join(directory, name)

        if os.path.isdir(full):
            shutil.rmtree(full)
        elif os.path.isfile(full) or os.path.islink(full):
            os.remove(full)


def expand_path(path):
    """Convert ``path`` from a relative, possibly symlinked location to a real path.

    Note:
        ``path`` does not need to exist as a file on-disk.

    Args:
        path (str):
            It could be ".", indicating the current directory. Or "../" meaning
            the parent directory, or an already absolute path.

    Returns:
        str: The expanded path.

    """
    return os.path.normpath(os.path.realpath(path))


def get_installed_root(name):
    """Find the path on-disk where the resolved ``name`` Rez package lives.

    Args:
        name (str): A Rez package name. e.g. "python", "Sphinx", etc.

    Raises:
        EnvironmentError: If ``name`` has no registered directory.

    Returns:
        str: Some directory on-disk.

    """
    # TODO : Add issue to make this function a proper REZ API method
    # Reference: ``pkg.name.upper().replace('.', '_')``
    #
    variable = "REZ_{name}_ROOT".format(name=name.upper().replace(".", "_"))

    try:
        return os.environ[variable]
    except KeyError:
        raise EnvironmentError(
            'Rez package "{name}" is not found. Are you sure it is in your '
            "current Rez resolve?".format(name=name)
        )
