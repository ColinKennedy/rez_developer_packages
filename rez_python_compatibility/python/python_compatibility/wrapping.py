#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Generic-but-still-useful wrappers."""

import cProfile
import contextlib
import functools
import inspect
import os
import pstats
import sys
import tempfile

from six.moves import io


class _Content(object):
    """A thin wrapper to store args, kwargs, and results of called Python objects."""

    def __init__(self, args, kwargs, results):
        """Keep track of the use's call and results.

        Args:
            args (tuple[object]): The positional arguments passed by the user.
            kwargs (tuple[object]): The keyword arguments passed by the user.
            results (object): Whatever the watched callable object's return was.

        """
        super(_Content, self).__init__()

        self._args = args
        self._kwargs = kwargs
        self._results = results

    def get_all_args(self):
        """tuple[object]: The positional arguments passed by the user."""
        return self._args

    def get_all_kwargs(self):
        """tuple[object]: The keyword arguments passed by the user."""
        return self._kwargs

    def get_all_results(self):
        """object: Whatever the watched callable object's return was."""
        return self._results

    def get_all(self):
        """tuple[tuple[object], tuple[object], object]: Everything related to the caller."""
        return (self._args, self._kwargs, self._results)


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


@contextlib.contextmanager
def keep_os_environment():
    """Save the some environment and restore it later."""
    original = os.environ.copy()

    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(original)


@contextlib.contextmanager
def keep_sys_path():
    """Save the current :attr:`sys.path` and restore it later."""
    paths = list(sys.path)

    try:
        yield
    finally:
        sys.path[:] = paths


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


@contextlib.contextmanager
def watch_callable(item):
    """Wrap the execution of `item` but do not prevent its execution.

    Args:
        item (callable): Any Python object that is callable.

    Yields:
        A Python context which gets back every called record.

    """
    container = []

    if inspect.ismethod(item):
        parent = item.im_self
    elif inspect.isfunction(item):
        parent = sys.modules[item.__module__]
    else:
        # TODO : Finish this
        raise NotImplementedError('Need to write this')

    @functools.wraps(item)
    def wrapper(*args, **kwargs):
        result = item(*args, **kwargs)
        container.append(_Content(args, kwargs, result))

    try:
        setattr(parent, item.__name__, wrapper)

        yield container
    finally:
        # Revert the item back to normal
        setattr(parent, item.__name__, item)
