#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Generic-but-still-useful wrappers."""

import contextlib
import cProfile
import functools
import inspect
import os
import pstats
import sys
import tempfile

from six.moves import io, mock

from . import imports


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


def _is_method_of_class(original):
    """bool: Check if `original` is some kind of method of a class."""
    if inspect.ismethod(original):
        return True

    if _get_class_that_defined_method(original):
        return True

    return False


def _is_static_method(caller):
    """bool: Check if `caller` is a function defined as a staticmethod."""
    class_ = _get_class_that_defined_method(caller)

    if not class_:
        return False

    binded_value = class_.__dict__[caller.__name__]

    if isinstance(binded_value, staticmethod):
        return True

    return False


def _get_class_that_defined_method(meth):
    # Reference: https://stackoverflow.com/a/25959545/3626104
    if not hasattr(meth, "__qualname__"):
        # This only happens in Python 2. Python 3+ will always have ``__qualname__``
        return None

    if inspect.ismethod(meth) or (
        inspect.isbuiltin(meth)
        and getattr(meth, "__self__", None) is not None
        and getattr(meth.__self__, "__class__", None)
    ):
        for cls in inspect.getmro(meth.__self__.__class__):
            if meth.__name__ in cls.__dict__:
                return cls

        meth = getattr(meth, "__func__", meth)  # fallback to __qualname__ parsing

    if inspect.isfunction(meth):
        cls = getattr(
            inspect.getmodule(meth),
            meth.__qualname__.split(".<locals>", 1)[0].rsplit(".", 1)[0],
            None,
        )
        if isinstance(cls, type):
            return cls

    return getattr(meth, "__objclass__", None)  # handle special descriptor objects


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
def watch_namespace(original, namespace="", implicits=False):
    """Check the inputs and outputs of `original`, any time it is called.

    Reference:
        https://stackoverflow.com/a/61963740/3626104

    Args:
        original (callable):
            The object to keep track of.
        namespace (str, optional):
            The full namespace of `original` to mock. If no namespace is given,
            this function will auto-find the namespace, using `original`. Default: "".
        implicits (bool, optional):
            If True and `original` is a method of a class instance, the
            first argument in args will be the instance (self). Usually,
            we don't want that redundant information, so use False to
            exclude it. Default is False.

    Raises:
        RuntimeError: If no `namespace` was given or could be automatically found.

    Yields:
        list[:class:`_Content`]:
            The found inputs and outputs for each time `container` was called.

    """
    container = []

    if not namespace:
        namespace = imports.get_namespace(original)

    if not namespace:
        raise RuntimeError(
            'No namespace was given and "{original}" has no discoverable namespace.'.format(
                original=original
            )
        )

    is_static = _is_static_method(original)

    @functools.wraps(original)
    def side_effect(*args, **kwargs):
        """Run `original` and store its inputs and outputs into `container`."""
        if inspect.ismethod(original):
            # If it's a bound method, ignore the first argument, since
            # it's always `self` or `cls` and we don't need to pass it twice.
            #
            if not hasattr(original, "im_self"):
                args = args[1:]
            elif original.im_self is not None:
                # Reference: https://stackoverflow.com/a/53322/3626104
                args = args[1:]

        result = original(*args, **kwargs)

        if _is_method_of_class(original) and not implicits:
            if not is_static:
                # Most of the time, we don't want `self` or `cls` included in `args`
                args = args[1:]

        container.append(_Content(args, kwargs, result))

        return result

    if is_static:
        patcher = mock.patch(namespace, autospec=original, side_effect=side_effect)
    else:
        patcher = mock.patch(namespace, autospec=True, side_effect=side_effect)

    patcher.start()

    try:
        yield container
    finally:
        patcher.stop()
