#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The module responsible for implemented un-hashed variants for ``rez_pip_boy``.

Regular ``rez-pip`` API calls hard-code hashed variants. To get
control over variant again, we have to get a bit creative and force
:meth:`rez.package_maker.PackageMaker._get_data` to always return
`False` for "hashed_variants".

"""

import contextlib

from rez import package_maker


def _modified_get_data(function):
    """Modify a Rez API function so that we get un-hashed variants.

    Args:
        function (callable):
            Add :meth:`rez.package_maker.PackageMaker._get_data` to
            this parameter so that any ``rez-pip`` API command installs
            without hashed variants.

    Returns:
        callable: The wrapped command, which creates un-hashed variant Rez pip packages.

    """

    def wrapper(*args, **kwargs):
        output = function(*args, **kwargs)
        output["hashed_variants"] = False

        return output

    return wrapper


@contextlib.contextmanager
def do_nothing():
    """Don't do anything.

    This Python context does nothing. Since ``rez-pip`` defaults to
    using hashed variants, this function is used when a user wants hashed
    variants.

    """
    yield


@contextlib.contextmanager
def force_unhashed_variants():
    """Force ``rez-pip`` API calls to **not** use hashed variants."""
    old_method = package_maker.PackageMaker._get_data
    package_maker.PackageMaker._get_data = _modified_get_data(old_method)

    try:
        yield
    except Exception:
        raise
    finally:
        package_maker.PackageMaker._get_data = old_method
