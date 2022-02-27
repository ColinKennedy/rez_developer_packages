"""Miscellaneous functions which make working with file paths easier."""

import os
import shutil
import textwrap


def add_gitignore(directory):
    """Add a .gitignore into ``directory`` which ignores all folder contents.

    No matter what files or folders are added under ``directory``, they
    will be ignored by git.

    Args:
        directory (str): An absolute or relative path to a directory on-disk.

    """
    with open(os.path.join(directory, ".gitignore"), "w") as handler:
        handler.write(
            textwrap.dedent(
                """\
                *
                **/
                !.gitignore
                """
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
