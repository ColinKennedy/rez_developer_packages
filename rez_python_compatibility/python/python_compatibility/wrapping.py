#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Generic-but-still-useful wrappers."""

import contextlib
import cProfile
import functools
import os
import pstats
import sys
import tempfile

from six.moves import io


@contextlib.contextmanager
def capture_pipes():
    """Capture the stdout and stderr of the code that executes within this context.

    Example:
        >>> import sys

        >>> with capture_pipes() as output:
        >>>     print('hello')
        >>>     print('there', file=sys.stderr)

        >>> stdout, stderr = output

    Yields:
        tuple[:class:`io.StringIO`, :class:`io.StringIO`]: The captured stdout and stderr.

    """
    oldout, olderr = sys.stdout, sys.stderr

    try:
        out = [io.StringIO(), io.StringIO()]
        sys.stdout, sys.stderr = out

        yield out
    finally:
        sys.stdout, sys.stderr = oldout, olderr
        out[0] = out[0].getvalue()
        out[1] = out[1].getvalue()


@contextlib.contextmanager
def keep_cwd(directory):
    """After the current Python context exits, cd into the given directory.

    This is useful for when you need to temporarily change the user's directory
    while running some code.

    Example:
        >>> some_folder = os.getcwd()

        >>> with keep_cwd(some_folder):
        >>>     os.chdir('some other folder')

        >>> print(some_folder == os.getcwd())  # This will return True

    Yields:
        The current context. Once this is yielded, the user's working directory
        is set back to `directory`.

    """
    try:
        yield
    finally:
        os.chdir(directory)


def profile_temporary(sort_field="cumulative"):
    """Profile some Python object to get its timing information.

    Example:
        >>> @profile_temporary()
        >>> def something():
        ...     time.sleep(1)

    Args:
        sort_field (str, optional): A potential column of information
            to sort the output data by. The default value is usually
            what you want. Default: "cumulative".

    """

    def actual_profileit(function):
        """Wrap the given function."""

        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            """Pass the function + its arguments here and run it while profiling it."""
            profiler = cProfile.Profile()
            results = profiler.runcall(function, *args, **kwargs)

            with tempfile.NamedTemporaryFile() as handler:
                pass

            profiler.dump_stats(handler.name)
            stats = pstats.Stats(handler.name)
            stats.sort_stats(sort_field)
            stats.print_stats()

            os.remove(handler.name)

            return results

        return wrapper

    return actual_profileit


def run_once(function):
    """Make sure that the given function only ever runs once.

    Reference:
        https://stackoverflow.com/a/4104188/3626104

    Args:
        function (callable): The function that you only ever want to be able to call once.

    Returns:
        callable: The same `function`, but now with logic better controlled.

    """

    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        """Make sure that the wrapped function only gets run once."""
        if not wrapper.has_run:
            wrapper.has_run = True

            return function(*args, **kwargs)

        return None

    wrapper.has_run = False

    return wrapper
