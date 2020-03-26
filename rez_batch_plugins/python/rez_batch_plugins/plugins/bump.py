#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A tool which specializes in bumping Rez package dependencies."""

import argparse
import collections
import logging
import os
import sys
import tempfile
import textwrap

from python_compatibility import wrapping
from rez import build_process_, build_system, package_search, package_test
from rez.utils import formatting
from rez_batch_process.core import registry
from rez_batch_process.core.plugins import command, conditional
from rez_bump import rez_bump_api
from rez_industry import api
from rez_utilities import creator, inspection

_Configuration = collections.namedtuple(
    "_Configuration", "command token pull_request_name ssl_no_verify results"
)
_LOGGER = logging.getLogger(__name__)
_BUMP_CHOICES = frozenset(("major", "minor", "patch"))
_Results = collections.namedtuple(
    "_Results", "pre_bump_build pre_bump_test post_bump_build post_bump_test"
)


class Bump(command.RezShellCommand):
    """A class that forces downstream Rez packages to accept a new Rez package version."""

    @staticmethod
    def _get_pull_request_body(package, configuration):
        """str: Convert a Rez package into a description for pull requests from this class."""
        template = textwrap.dedent(
            """\
            This PR bumps a Rez package because one-or-more of its
            dependencies have changed.

            Normally, you'd only need to do this when a dependency
            releases a new major version. Which means that the
            dependency's API must have changed in a way that could break
            your code.

            ## Extra Instructions
            {configuration.instructions}

            ## Testing
            ### Pre-Bump
            Does it build? {configuration.results.pre_bump_build}
            Does testing pass? {configuration.results.pre_bump_test}

            ### Post-Bump
            Does it build? **{configuration.results.post_bump_build}**
            Does testing pass? **{configuration.results.post_bump_test}**

            ## Reviewer Expectations
            Please review this PR to ensure

            A. That the code changes look correct
            B. The affected packages build
            C. rez-test still works for said package(s)

            Once that's done, this PR should be good to merge.

            Thanks for your review!
            """
        )

        return template.format(package=package, configuration=configuration)

    @staticmethod
    def _bump(package, increment, new_dependencies):
        return _bump(package, increment, new_dependencies)

    @classmethod
    def _run_command_with_results(cls, package, arguments):
        """Run the main bump command on a Rez package.

        Args:
            package (:class:`rez.developer_package.DeveloperPackage`):
                The Rez package that will be changed. Any command
                run by this function will do so while cd'ed into the
                directory of this package.

                To be clear, this Rez package represents one of the downstream packages
                whose version + dependenc(ies) will be changed.
            arguments (:class:`argparse.Namespace`):
                The user-provided, plug-in specific arguments.
                Specifically, this should bring in

                - The command that the user wants to run, per-package
                - The name of the ticket that will be used for git branches
                - The option to "raise an exception if any error occurs"
                  or whether it's OK to continue.

        Returns:
            str: Any error message that occurred from this command, if any.

        """
        build_path = tempfile.mkdtemp(suffix="_pre_bump_build_path")
        pre_bump_build = True

        try:
            creator.build(package, build_path, packages_path=arguments.additional_paths)
        except RuntimeError:
            pre_bump_build = False

        pre_bump_tests = _run_test(package, paths=arguments.additional_paths)

        error = ""
        post_bump_build = "Not run"
        post_bump_tests = "Not run"

        try:
            package = cls._bump(package, arguments.new, arguments.packages)
        except Exception:  # pylint: disable=broad-except
            error = 'Bumping package "{package.name}" failed.'.format(package=package)
            _LOGGER.warning('Package "%s" bump failed.', package)
        else:
            build_path = tempfile.mkdtemp(suffix="_post_bump_build_path")
            post_bump_build = True

            try:
                creator.build(
                    package, build_path, packages_path=arguments.additional_paths
                )
            except Exception:  # pylint: disable=broad-except
                post_bump_build = False

            post_bump_tests = _run_test(package, paths=arguments.additional_paths)

        results = _Results(
            pre_bump_build, pre_bump_tests, post_bump_build, post_bump_tests
        )

        return error, results

    @classmethod
    def parse_arguments(cls, text):
        """Parse user-provided CLI text into inputs that this class understands.

        Args:
            text (list[str]): The user provided input, separated by spaces.

        Returns:
            :class:`argparse.Namespace`: The parsed output.

        """
        parser = _get_parser()

        return parser.parse_args(text)

    @classmethod
    def run(cls, package, arguments):
        """Run a command on a package and create a pull request.

        Args:
            package (:class:`rez.developer_package.DeveloperPackage`):
                The Rez package that will be used changed. Any command
                run by this function will do so while cd'ed into the
                directory of this package.
            arguments (:class:`argparse.Namespace`):
                The user-provided, plug-in specific arguments.
                Specifically, this should bring in

                - The command that the user wants to run, per-package
                - The name of the ticket that will be used for git branches
                - The option to "raise an exception if any error occurs"
                  or whether it's OK to continue.

        Returns:
            str: Any error message that occurred from this command, if any.

        """
        error, results = cls._run_command_with_results(package, arguments)

        if error:
            return error

        cls._create_pull_request(
            package,
            _Configuration(
                "bump",
                arguments.token,
                arguments.pull_request_name,
                arguments.ssl_no_verify,
                results,
            ),
            cached_users=arguments.cached_users,
            fallback_reviewers=arguments.fallback_reviewers,
            base_url=arguments.base_url,
        )

        return ""


def _get_user_provided_packages():
    """set[str]: Every package/version whose downstream dependencies must be bumped."""
    parser = _get_parser()
    arguments, _ = parser.parse_known_args(sys.argv[1:])

    return {formatting.PackageRequest(package) for package in arguments.packages}


def _get_packages_which_must_be_changed(paths=None):
    """Get every Rez package that has dependencies to replace.

    The user may have provided 1+ packages at once. Each package will
    be used as the "root" and downstream packages that depend on this
    package will be searched and returned, here.

    Args:
        paths (list[str], optional):
            The directories to search for Rez package families,
            Default: :attr:`rez.config.config.packages_path`.

    Returns:
        tuple[:class:`rez.packages_.Package`, list, list]:
            All of the found Rez packages and a list of any Rez package
            that was considered invalid or any Rez packages that were
            valid but must be skipped, for some reason.

    """
    packages, invalids, skips = conditional.get_default_latest_packages(paths=paths)
    downstream = set()

    for package in _get_user_provided_packages():
        downstream_package_names, _ = package_search.get_reverse_dependency_tree(
            package_name=package.name, depth=1, paths=paths,
        )

        # According to the documenatation in
        # :func:`rez.package_search.get_reverse_dependency_tree` The
        # first list always contains `package` by itself. We don't need
        # this so we discard it here and just get the "depth 1" packages.
        #
        downstream_package_names = downstream_package_names[1]

        downstream.update(downstream_package_names)

    packages_to_change = [package for package in packages if package.name in downstream]

    return packages_to_change, invalids, skips


def _get_parser():
    parser = argparse.ArgumentParser(
        description="Find downstream packages affected by a new package's version."
    )
    parser.add_argument(
        "-n",
        "--new",
        required=True,
        help="Specify whether to bump with a new major, minor, or patch.",
        choices=_BUMP_CHOICES,
    )
    parser.add_argument(
        "-p",
        "--packages",
        required=True,
        nargs="+",
        help="The name of the package/version that will be bumped in all downstream packages.",
    )
    parser.add_argument(
        "-i",
        "--instructions",
        required=True,
        help="Explain any other special notes that you want PR reviewers to know.",
    )
    parser.add_argument(
        "-a",
        "--additional-paths",
        help="An optional set of paths to include while resolving Rez packages.",
    )

    command.add_git_arguments(parser)

    return parser


def _run_build(package, paths=None):
    # TODO : Figure out where to put `paths`
    root = inspection.get_package_root(package)

    system = build_system.create_build_system(root, package=package, verbose=True)

    # create and execute build process
    builder = build_process_.create_build_process(
        "local",  # See :func:`rez.build_process_.get_build_process_types` for possible values
        root,
        build_system=system,
        verbose=True,
    )

    try:
        builder.build(clean=True, install=True)
    except Exception:  # pylint: disable=broad-except
        return False

    return True


def _run_rez_test(package, paths=None):
    # """Build and run the tests for every given Rez package.
    #
    # Args:
    #     packages (:class:`rez.developer_package.DeveloperPackage`):
    #         The Rez package whose tests will be run.
    #     paths (list[str], optional):
    #         All paths to search for Rez packages. Default is
    #         :attr:`rez.config.packages_path`.
    #
    # Returns:
    #     dict[str, int]: The name of each test that ran and its test results.
    #
    # """
    # `package_request` is given an empty string and later defined, below
    runner = package_test.PackageTestRunner(
        package_request="", package_paths=paths, verbose=True,
    )
    runner.package = package

    # TODO : Once this issue is merged and closed, this may need to account for "run_on"
    #
    # Reference: https://github.com/nerdvegas/rez/issues/665
    #
    tests = runner.get_test_names()

    if not tests:
        uri = runner.get_package().uri
        _LOGGER.warning('No tests found "%s".', uri)

        return "No tests were found"

    status = "Succeeded"

    for name in tests:
        test_status = runner.run_test(name)

        if test_status:
            status = "Has fails"

            break  # No need to keep testing since we know there's at least one failure

    return status


def _run_test(package, paths=None):
    with wrapping.keep_cwd(os.getcwd()):
        # Many Rez tests are run assuming that the user is cd'ed
        # into the Rez package so we need to change directory here.
        #
        return _run_rez_test(package, paths=paths)


def _bump(package, increment, new_dependencies):
    rez_bump_api.bump(package, **{increment: 1})

    with open(package.filepath, "r") as handler:
        code = handler.read()

    new_code = api.add_to_attribute("requires", new_dependencies, code)

    with open(package.filepath, "w") as handler:
        handler.write(new_code)

    root = inspection.get_package_root(package)

    return inspection.get_nearest_rez_package(root)


def main():
    """Add :class:`Bump` to ``rez_batch_process``."""
    registry.register_plugin("bump", _get_packages_which_must_be_changed)
    registry.register_command("bump", Bump)
