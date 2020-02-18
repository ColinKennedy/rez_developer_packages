#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The main module responsible for plugin-specific abstract classes.

There are 2 types, :class:`BaseCommand` and :class:`BaseCondition`.

:class:`BaseCommand` -
    Used to do "something" to a Rez package in a repository.
    e.g. Add Python documentation

:class:`BaseCondition` -
    These plug-in classes are responsible for filtering down which Rez
    packages are processed by the command. For example, if the command
    is to add Python documentation, obviously you don't want to add
    documentation to a Rez package that doesn't define a Python package.

    These plug-ins are in charge of making sure only valid input gets
    sent to the command.

"""

import abc
import argparse

import six


@six.add_metaclass(abc.ABCMeta)
class BaseCommand(object):
    """The main class that is does an operation on a Rez package.

    What operation, exactly? That's for you to decide. Simply sub-class
    this class and implement :meth:`BaseCommand.run`. The method can do
    whatever you want.

    The only restriction is that this class is meant to be run on
    a "source" Rez package, which should always be inside of a git
    repository or similar VCS.

    """

    @staticmethod
    def parse_arguments(text):
        """Split the user's command-line input to get whatever this class requires to run.

        This method is your opportunity to request extra information
        from the user before running your command. This parser is meant
        to operate on whatever the main CLI parser doesn't pick up.

        Important:
            This main CLI parser checks for all known arguments. The
            rest of the arguments that could not get parsed are passed
            to this class. That means that this method should aim to
            capture 100% of its input. Because the input should always
            be "plug-in specific" arguments.

        Args:
            text (list[str]):
                The user-provided arguments that this function must process.

        Returns:
            :class:`argparse.Namespace`: The found, plug-in specific arguments.

        """
        parser = argparse.ArgumentParser(
            description="An empty parser. Does basically nothing!"
        )

        return parser.parse_args(text)

    @staticmethod
    @abc.abstractmethod
    def run(package, arguments):
        """Run the action on a given Rez package, whatever it does.

        Args:
            package (:class:`rez.packages_.Package`):
                Some Rez package to process.
            arguments (:class:`argparse.Namespace`):
                The plug-in specific arguments that were given by the
                user to help this function do its work.

        Returns:
            str: If any error was found while the function was executed.

        """
        raise NotImplementedError("Implement the run logic in a sub-class")
