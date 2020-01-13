#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A series of exceptions for this package to use.

Exceptions are used to find and catch issues with Rez packages. Each of
these exceptions are meant to be caught and returned as a report to the
user. e.g. instead of letting the traceback actually return, the user
might get a report like "my_package_name was skipped because it has no
git repository".

"""


class CoreException(Exception):
    """A base exception for all of the exceptions in this module to inherit from."""

    pass


class InvalidPackage(CoreException):
    """A Rez package that has an issue that causes the code to fail.

    For example, if a Rez package has no find-able path on-disk, that
    would cause issues.

    """

    # TODO : Change this so that path can default to an empty string
    def __init__(self, package, path, message, full_message=""):
        """Store the user's Rez package, the path on-disk to the package, and anything else.

        Args:
            package (:class:`rez.packages_.Package`): The Rez package that caused the exception.
            path (str): An absolute path to the folder where this package lives, on-disk.
            message (str): A summary of the issue. Keep it brief!
            full_message (str, optional): A more detailed message, if you want to write one.

        """
        super(InvalidPackage, self).__init__(message)

        self._package = package
        self._path = path
        self._full_message = full_message

    def get_full_message(self):
        """str: The unabridged error message."""
        return self._full_message

    def get_package(self):
        """:class:`rez.packages_.Package`: The Rez package that caused the exception."""
        return self._package

    def get_path(self):
        """str: An absolute path to the folder where this packge lives, on-disk."""
        return self._path

    def __eq__(self, other):
        """bool: Check if some `other` exception has equivalent data as this instance."""
        return (
            isinstance(other, self.__class__)
            and self.get_package() == other.get_package()
            and self.get_path() == other.get_path()
            and self.get_full_message() == other.get_full_message()
        )

    def __repr__(self):
        """str: Show exactly how to reproduce the current instance of this class."""
        return (
            "{self.__class__.__name__}("
            "{self._package!r}, "
            '"{self._path}", '
            '"{self.message}", '
            'full_message="{self._full_message}"'
            ")".format(self=self)
        )


class MultiplePackageMatches(InvalidPackage):
    """If 2+ Rez packages were found when only one Rez package was expected."""

    pass


class NoGitRepository(InvalidPackage):
    """If a Rez package has no git repository.

    It's not necessarily an "error" for a Rez package to have no
    git repository but if it has no git repository **and** it is an
    installed packagee (e.g. it has no build system) then it causes
    problems for this package.

    This exception exists to catch weird packages like these before they
    cause extra problems later.

    """

    pass


class NoRepositoryRemote(Exception):
    """If a git repository was supposed to have a remote URL but does not."""

    pass


class PackageNotFound(InvalidPackage):
    """If no Rez package was found when at least one Rez package was expected."""

    pass
