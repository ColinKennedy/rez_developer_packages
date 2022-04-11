"""The entry point for :ref:`rez_sphinx` on the terminal."""

from __future__ import print_function

import argparse
import json
import logging
import operator
import os
import pprint
import shlex
import sys

from python_compatibility import iterbot
from rez.cli import _complete_util
from rez.config import config as config_
from rez_utilities import finder

from .commands import build_orderer, initer, publish_run
from .commands.builder import inspector
from .commands.builder import runner as build_run
from .commands.suggest import build_display, search_mode, suggestion_mode
from .core import api_builder, environment, exception, path_control, print_format
from .preferences import preference
from .preprocess import hook

_LOGGER = logging.getLogger(__name__)


class _HelpPrinter(argparse.ArgumentParser):
    """Show the full help if the user forgets a positional argument.

    Without this class, ``rez_sphinx view`` prints:

    ::

        usage: __main__.py view [-h] {sphinx-conf,view-url} ...
        __main__.py view: error: the following arguments are required: command

    With this class, ``rez_sphinx view`` prints:

    ::

        __main__.py view: error: the following arguments are required: command
        usage: __main__.py view [-h] {sphinx-conf,view-url} ...

        positional arguments:
          {sphinx-conf,view-url}
            sphinx-conf         Show your documentation's Sphinx conf.py settings.
                                Useful for debugging!
            view-url         Show where this documentation will be published to.

        optional arguments:
          -h, --help            show this help message and exit

    I'd expect that to be the default behavior, but it isn't.

    """

    def error(self, message):
        """Print ``message`` as an error."""
        try:
            super(_HelpPrinter, self).error(message)
        finally:
            self.print_help()


def _add_directory_argument(parser):
    """Make ``parser`` include a positional argument pointing to a file path on-disk.

    Args:
        parser (argparse.ArgumentParser): The instance to modify.

    """
    parser.add_argument(
        "directory",
        nargs="?",
        default=os.getcwd(),
        help="The folder to search for a Rez package. "
        "Defaults to the current working directory.",
    )


def _add_remainder_argument(parser):
    """Tell ``parser`` to collect all text into a single namespace parameter.

    Args:
        parser (argparse.ArgumentParser):
            The parser to extend with the new parameter.

    """
    remainder = parser.add_argument(
        "remainder",
        nargs="*",
        help=argparse.SUPPRESS,
    )
    remainder.completer = _complete_util.SequencedCompleter(
        "remainder",
        _complete_util.ExecutablesCompleter,
        _complete_util.FilesCompleter(),
    )


def _build_runner(namespace):
    """Build Sphinx documentation, using details from ``namespace``.

    Args:
        namespace (argparse.Namespace):
            The parsed user content. It contains all of the necessary
            attributes to generate Sphinx documentation.

    Raises:
        UserInputError:
            If the user passes `sphinx-apidoc`_ arguments but also
            specified that they don't want to build API documentation.

    """
    _split_build_arguments(namespace)

    if namespace.no_api_doc and namespace.api_doc_arguments:
        raise exception.UserInputError(
            'You cannot specify --apidoc-arguments "{namespace.api_doc_arguments}" '
            "while also --no-apidoc.".format(namespace=namespace)
        )

    build_run.build(
        namespace.directory,
        api_mode=namespace.api_documentation,
        api_options=namespace.api_doc_arguments,
        no_api_doc=namespace.no_api_doc,
    )


def _build_order(namespace):
    """Show the user the order which documentation must be built.

    Args:
        namespace (argparse.Namespace):
            The parsed user content. It contains all of the necessary
            attributes to generate Sphinx documentation.

    """
    normalized = [path_control.expand_path(path) for path in namespace.directories]
    normalized = iterbot.uniquify(normalized)

    _LOGGER.info('Searching within "%s" for Rez packages.', normalized)

    searcher = search_mode.get_mode_by_name(namespace.search_mode)
    packages = build_orderer.collect_packages(normalized, searcher)

    if not namespace.include_existing:
        packages = build_orderer.filter_existing_documentation(packages)

    # TODO : Add allow_cyclic support. Here or wherever makes the most sense
    suggestion_caller = suggestion_mode.get_mode_by_name(namespace.suggestion_mode)
    ordered = suggestion_caller(packages)

    display_using = build_display.get_mode_by_name(namespace.display_as)
    display_using(ordered)


def _check(namespace):
    """Make sure :doc:`configuring_rez_sphinx` are valid, in/outside ``namespace``.

    Args:
        namespace (argparse.Namespace):
            The parsed user content. It contains all of the necessary
            attributes to generate Sphinx documentation.

    Raises:
        UserInputError:
            If the user passes `sphinx-apidoc`_ arguments but also
            specified that they don't want to build API documentation.

    """
    directory = os.path.normpath(namespace.directory)
    _LOGGER.debug('Found "%s" directory.', directory)

    package = finder.get_nearest_rez_package(directory)
    _validate_base_settings(package=package)

    print("All rez_sphinx settings are valid!")


def _init(namespace):
    """Create a Sphinx project, rooted at ``namespace``.

    Args:
        namespace (argparse.Namespace):
            The parsed user content. It contains all of the necessary
            attributes to generate Sphinx documentation.

    Raises:
        NoPackageFound: If there's no Rez package in ``namespace.directory``.
        BadPackage: If the found Rez package isn't a ``package.py`` file.

    """
    _split_init_arguments(namespace)

    directory = os.path.normpath(namespace.directory)
    _validate_readable(directory)
    _LOGGER.debug('Found "%s" directory.', directory)
    package = finder.get_nearest_rez_package(directory)

    preference.validate_base_settings(package=package)

    if not package:
        raise exception.NoPackageFound(
            'Directory "{directory}" is not in a Rez package. Cannot continue.'.format(
                directory=directory
            )
        )

    if not os.path.isfile(os.path.join(directory, "package.py")):
        raise exception.BadPackage(
            'Package "{package.name}" is not a package.py file. '
            "This command requires a Rez package.py.".format(package=package)
        )

    _LOGGER.debug('Found "%s" Rez package.', package.name)

    initer.init(package, quick_start_options=namespace.quick_start_arguments)


def _list_default(namespace):
    """Print default :ref:`rez_sphinx` configuration settings.

    The default will show everything. ``--sparse`` will only print the simplest
    arguments.

    Args:
        namespace (argparse.Namespace):
            The parsed user content. It contains all of the necessary
            attributes to query preference settings.

    """
    if namespace.sparse:
        data = preference.serialize_default_sparse_settings()
    else:
        data = preference.serialize_default_settings()

    caller = print_format.get_format_caller(namespace.format)
    caller(data)


def _list_overrides(namespace):
    """Print any :ref:`rez_sphinx config` settings the user has changed.

    The default will show everything, the default settings along with their
    overrides. ``--sparse`` will only print the overrides and nothing else.

    Args:
        namespace (argparse.Namespace):
            The parsed user content. It contains all of the necessary
            attributes to query preference settings.

    """
    _LOGGER.debug('Found "%s" directory.', namespace.directory)
    package = finder.get_nearest_rez_package(namespace.directory)

    if not namespace.sparse:
        data = preference.get_base_settings(package=package)
    else:
        data = preference.serialize_override_settings(package=package)

    caller = print_format.get_format_caller(namespace.format)
    caller(data)


def _publish_run(namespace):
    """Build and publish documentation in ``namespace``.

    Args:
        namespace (argparse.Namespace):
            The parsed user content. It contains all of the necessary
            attributes to build + query documentation to publish.

    Raises:
        MissingPlugIn:
            If :ref:`rez_docbot <rez_docbot>` isn't loaded. See
            :ref:`loading_rez_docbot` for details.
        UserInputError:
            If the given / found directory isn't in a Rez package.

    """
    if not environment.is_publishing_enabled():
        raise exception.MissingPlugIn(
            "Must must include .rez_sphinx.feature.docbot_plugin==1 "
            "in your resolve to use this command."
        )

    directory = os.path.normpath(namespace.directory)
    _LOGGER.debug('Found "%s" directory.', directory)

    package = finder.get_nearest_rez_package(directory)

    if not package:
        raise exception.UserInputError(
            'Directory "{namespace.directory}" has no Rez package.'.format(
                namespace=namespace
            )
        )

    publishers = publish_run.get_all_publishers(package)

    built_documentation = publish_run.build_documentation(package)

    for documentation in built_documentation:
        _LOGGER.info('Publishing "%s" documentation.', documentation)

        for publisher in publishers:
            _LOGGER.debug('Publishing with publisher "%s".', publisher)
            publisher.quick_publish(documentation)


def _preprocess_help(namespace):
    """Recommend (Print) A `help`_ attribute for ``namespace``.

    Args:
        namespace (argparse.Namespace):
            The parsed user content. It contains the path to a source Rez
            package and and its initial `help`_ atttribute. That will be used
            to find the remaining `help`_ contents, if any.

    """
    raw_help = " ".join(namespace.initial_help)
    help_ = json.loads(raw_help)
    full_help = hook.preprocess_help(namespace.package_source_root, help_)

    print(json.dumps(full_help))


def _set_up_build(sub_parsers):
    """Add :ref:`rez_sphinx build run` CLI parameters.

    Args:
        sub_parsers (argparse._SubParsersAction):
            A collection of parsers which the :ref:`rez_sphinx build` will be
            appended onto.

    """

    def _add_build_run_parser(command):
        description = "Generates documentation from your .rst files."

        build_runner = command.add_parser(
            "run",
            description=description,
            help=description,
        )
        _add_directory_argument(build_runner)
        choices = sorted(api_builder.MODES, key=operator.attrgetter("label"))
        build_runner.add_argument(
            "--no-apidoc",
            dest="no_api_doc",
            action="store_true",
            help="Disable API .rst file generation.",
        )
        build_runner.add_argument(
            "--apidoc-arguments",
            dest="api_doc_arguments",
            help='Anything you\'d like to send for sphinx-apidoc. e.g. "--private"',
        )
        build_runner.add_argument(
            "--api-documentation",
            choices=[mode.label for mode in choices],
            default=api_builder.FULL_AUTO.label,
            help="When building, API .rst files can be generated for your Python files."
            "\n\n"
            + "\n".join(
                "{mode.label}: {mode.description}".format(mode=mode) for mode in choices
            ),
        )
        build_runner.set_defaults(execute=_build_runner)

        _add_remainder_argument(build_runner)

    description = "Compile Sphinx documentation from a Rez package."
    build = sub_parsers.add_parser("build", description=description, help=description)
    command = build.add_subparsers(dest="command")
    command.required = True
    _add_build_run_parser(command)


def _set_up_config(sub_parsers):
    """Add :doc:`config_command` CLI parameters.

    Args:
        sub_parsers (argparse._SubParsersAction):
            A collection of parsers which the :doc:`config_command` will be
            appended onto.

    """

    def _add_format_argument(parser):
        """Allow the user to choose :ref:`rez_sphinx config` output (`yaml`_)."""
        parser.add_argument(
            "--format",
            choices=sorted(print_format.get_choices().keys()),
            default=print_format.PYTHON_FORMAT,
            help="Change the printed output, at will.",
        )

    def _set_up_list_default(inner_parser):
        """Define the parser for :ref:`rez_sphinx config list-defaults`."""
        description = "Show the rez_sphinx's default settings."
        list_default = inner_parser.add_parser(
            "list-defaults",
            description=description,
            help=description,
        )
        _add_format_argument(list_default)
        list_default.add_argument(
            "--sparse",
            action="store_true",
            help="If included, the reported config will only show top-level items.",
        )
        list_default.set_defaults(execute=_list_default)

    def _set_up_list_overrides(inner_parser):
        """Define the parser for :ref:`rez_sphinx config list-overrides`."""
        description = "Show non-default rez_sphinx's settings."

        list_overrides = inner_parser.add_parser(
            "list-overrides",
            description=description,
            help=description,
        )
        _add_directory_argument(list_overrides)
        _add_format_argument(list_overrides)
        list_overrides.add_argument(
            "--sparse",
            action="store_true",
            help="If included, the reported config shows overrides, only.",
        )
        list_overrides.set_defaults(execute=_list_overrides)

    description = "All commands related to rez_sphinx configuration settings."
    config = sub_parsers.add_parser(
        "config",
        description=description,
        help=description,
    )
    inner_parser = config.add_subparsers(dest="command")
    inner_parser.required = True

    description = "Report if the current user's settings are valid."

    check = inner_parser.add_parser(
        "check",
        description=description,
        help=description,
    )
    _add_directory_argument(check)
    check.set_defaults(execute=_check)

    description = "Print the value of any configuration attribute."

    show = inner_parser.add_parser(
        "show",
        description=description,
        help=description,
    )
    show.add_argument(
        "names",
        nargs="+",
        help="Configuration attributes to check for. Specify inner dicts using "
        '"foo.bar" syntax. Use --list to show all possible values.',
    )
    _add_directory_argument(show)
    show.set_defaults(execute=_show)

    description = "Print every possible configuration attribute."

    show_all = inner_parser.add_parser(
        "show-all",
        description=description,
        help=description,
    )
    _add_directory_argument(show_all)
    show_all.set_defaults(execute=_show_all)

    _set_up_list_default(inner_parser)
    _set_up_list_overrides(inner_parser)


def _set_up_init(sub_parsers):
    """Add :ref:`rez_sphinx init` CLI parameters.

    Args:
        sub_parsers (argparse._SubParsersAction):
            A collection of parsers which the :ref:`rez_sphinx init` will be
            appended onto.

    """
    description = "Set up a Sphinx project in a Rez package."

    init = sub_parsers.add_parser("init", description=description, help=description)
    init.add_argument(
        "--quickstart-arguments",
        dest="quick_start_arguments",
        help="Anything you'd like to send for sphinx-quickstart. "
        'e.g. "--ext-coverage"',
    )
    init.set_defaults(execute=_init)
    _add_directory_argument(init)
    _add_remainder_argument(init)


def _set_up_publish(sub_parsers):
    """Add :ref:`rez_sphinx publish` CLI parameters.

    Args:
        sub_parsers (argparse._SubParsersAction):
            A collection of parsers which the :ref:`rez_sphinx publish` will be
            appended onto.

    """
    description = (
        "Build & Send your documentation to the network. Requires rez_docbot to function.",
    )

    publish = sub_parsers.add_parser(
        "publish",
        help=description,
        description=description,
    )
    inner_parsers = publish.add_subparsers(dest="command")
    inner_parsers.required = True

    description = "Builds + publishs your documentation."
    publish_runner = inner_parsers.add_parser(
        "run",
        description=description,
        help=description,
    )
    _add_directory_argument(publish_runner)
    publish_runner.set_defaults(execute=_publish_run)


def _set_up_suggest(sub_parsers):
    """Add :doc:`suggest_command` CLI parameters.

    Args:
        sub_parsers (argparse._SubParsersAction):
            A collection of parsers which the :doc:`suggest_command` will be
            appended onto.

    """

    def _set_up_build_order(inner_parsers):
        description = (
            "Find and print the Rez packages that need rez_sphinx documentation."
        )
        build_order = inner_parsers.add_parser(
            "build-order",
            description=description,
            help=description,
        )
        build_order.add_argument(
            "directories",
            default=config_.packages_path,  # pylint: disable=no-member
            help="The folders to search within for **source** Rez packages.",
            nargs="+",
        )
        build_order.add_argument(
            "--allow-cyclic",
            action="store_true",
            default=False,
            help="If packages recursively depend on each other, "
            "fail early unless this flag is added.",
        )
        build_order.add_argument(
            "--display-as",
            choices=build_display.CHOICES,
            default=build_display.DEFAULT,
            help="Choose the printed output. "
            '"names" resembles ``rez-depends``. '
            '"directories" points to the path on-disk to the Rez package.',
        )
        build_order.add_argument(
            "--include-existing",
            action="store_true",
            default=False,
            help="Packages which have documentation will be included in the results.",
        )
        build_order.add_argument(
            "--search-mode",
            choices=sorted(search_mode.CHOICES.keys()),
            default=search_mode.DEFAULT,
            help="Define how to search for the source Rez packages. "
            '"source" searches the first folder down. '
            '"installed" searches the every 2 folders down. '
            '"recursive" searches everywhere for valid Rez packages.',
        )
        build_order.add_argument(
            "--suggestion-mode",
            choices=sorted(suggestion_mode.CHOICES.keys()),
            default=suggestion_mode.DEFAULT,
            help="Determines the way package dependency tracking runs. "
            'e.g. "config" searches package ``requires``. '
            '"guess" is hacky but may cover more cases.',
        )
        build_order.set_defaults(execute=_build_order)

    def _set_up_preprocess_help(inner_parsers):
        description = "Generate an automated Rez help attribute. This command is for internal use."
        preprocess_help = inner_parsers.add_parser(
            "preprocess-help",
            description=description,
            help=description,
        )
        preprocess_help.add_argument(
            "package_source_root",
            help="The directory where the source package.py lives.",
        )
        preprocess_help.add_argument(
            "initial_help",
            nargs=argparse.REMAINDER,
            help="The package.py `help` attribute to extend with extra data.",
        )
        preprocess_help.set_defaults(execute=_preprocess_help)

    description = "Check the order which packages should run."
    suggest = sub_parsers.add_parser(
        "suggest",
        description=description,
        help=description,
    )
    inner_parsers = suggest.add_subparsers(dest="command")
    inner_parsers.required = True

    _set_up_build_order(inner_parsers)
    _set_up_preprocess_help(inner_parsers)


def _set_up_view(sub_parsers):
    """Add :doc:`view_command` CLI parameters.

    Args:
        sub_parsers (argparse._SubParsersAction):
            A collection of parsers which the :doc:`view_command` will be
            appended onto.

    """

    def _set_up_view_conf(inner_parsers):
        description = (
            "Show your documentation's Sphinx conf.py settings. Useful for debugging!"
        )

        view_conf = inner_parsers.add_parser(
            "sphinx-conf",
            description=description,
            help=description,
        )

        view_conf.add_argument(
            "fields",
            nargs="*",
            help="A space-separated list of fields to print. "
            "If not provided, everything is shown.",
        )

        _add_directory_argument(view_conf)

        view_conf.set_defaults(execute=_view_conf)

    def _set_up_view_package_help(inner_parsers):
        description = (
            "Display the `help` attribute of the package, on-build / on-release. "
            "Useful for debugging."
        )

        view_package_help = inner_parsers.add_parser(
            "package-help",
            description=description,
            help=description,
        )

        _add_directory_argument(view_package_help)
        view_package_help.set_defaults(execute=_view_package_help)

    def _set_up_view_repository_uri(inner_parsers):
        description = "The location where build documentation is published to."
        repository_uri = inner_parsers.add_parser(
            "repository-uri",
            description=description,
            help=description,
        )

        _add_directory_argument(repository_uri)
        repository_uri.set_defaults(execute=_view_repository_uri)

    def _set_up_view_view_url(inner_parsers):
        description = "Show where you can view this published documentation."
        view_publish_url = inner_parsers.add_parser(
            "view-url",
            description=description,
            help=description,
        )

        _add_directory_argument(view_publish_url)
        view_publish_url.set_defaults(execute=_view_publish_url)

    description = "Check the order which packages should run."
    view = sub_parsers.add_parser(
        "view",
        description=description,
        help=description,
    )
    inner_parsers = view.add_subparsers(dest="command")
    inner_parsers.required = True

    _set_up_view_conf(inner_parsers)
    _set_up_view_package_help(inner_parsers)
    _set_up_view_repository_uri(inner_parsers)
    _set_up_view_view_url(inner_parsers)


def _show_all(namespace):
    """Print every configuration value path."""
    package = finder.get_nearest_rez_package(namespace.directory)

    print("All available paths:")

    for path in sorted(preference.get_preference_paths(package=package)):
        print(path)


def _show(namespace):
    """Print the configuration value(s) the user asked for.

    Args:
        namespace (argparse.Namespace):
            The parsed user content. It contains all of the necessary
            attributes to run :ref:`rez_sphinx config show`.

    """
    names = namespace.names
    package = finder.get_nearest_rez_package(namespace.directory)

    if not names:
        # If no name is specified, show everything
        names = sorted(preference.get_preference_paths(package=package))

    if not package:
        _LOGGER.warning(
            'Directory "%s" has no Rez package. Checking global preferences only.',
            namespace.directory,
        )

    if len(names) == 1:
        print(preference.get_preference_from_path(names[0], package=package))

        return

    values = []
    invalids = set()

    for name in names:
        try:
            values.append(
                (
                    name,
                    pprint.pformat(
                        preference.get_preference_from_path(name, package=package),
                        indent=4,
                    ),
                )
            )
        except exception.ConfigurationError:
            invalids.add(name)

    if invalids:
        if len(invalids) == 1:
            print(
                'Name "{invalids}" does not exist.'.format(
                    invalids=", ".join(sorted(invalids))
                )
            )

            return

        print(
            'Names "{invalids}" do not exist.'.format(
                invalids=", ".join(sorted(invalids))
            )
        )

        return

    print("Found Output:")

    for name, value in values:
        print("{name}:\n    {value}".format(name=name, value=value))


def _split_build_arguments(namespace):
    """Conform ``namespace`` attributes so other functions can use it more easily.

    Warning:
        This function will modify ``namespace`` in-place.

    Args:
        namespace (argparse.Namespace):
            The parsed user content. It contains all of the necessary
            attributes to generate Sphinx documentation.

    """
    namespace.api_doc_arguments = shlex.split(namespace.api_doc_arguments or "")

    if not namespace.remainder:
        return

    namespace.api_doc_arguments.extend(namespace.remainder)


def _split_init_arguments(namespace):
    """Conform ``namespace`` attributes so other functions can use it more easily.

    Warning:
        This function will modify ``namespace`` in-place.

    Args:
        namespace (argparse.Namespace):
            The parsed user content. It contains all of the necessary
            attributes to generate Sphinx documentation.

    """
    namespace.quick_start_arguments = shlex.split(namespace.quick_start_arguments or "")

    if not namespace.remainder:
        return

    namespace.quick_start_arguments.extend(namespace.remainder)


def _validate_base_settings(package=None):
    """Check if the user's settings won't cause :ref:`rez_sphinx` to break.

    Args:
        package (rez.packages.Package, optional):
            A Rez package which may override the global setting.  If the
            package doesn't define an opinion, the global setting / default
            value is used instead.

    """
    try:
        preference.validate_base_settings(package=package)
    except exception.ConfigurationError:
        print(
            "Checker `rez_sphinx config check` failed. "
            "See below for details or run the command to repeat this message.",
            file=sys.stderr,
        )

        raise


def _validate_readable(path):
    """Ensure ``path`` is readable.

    Args:
        path (str): The file or directory on-disk.

    Raises:
        PermissionError: If ``path`` isn't readable.

    """
    if not os.path.exists(path):
        raise exception.DoesNotExist('Path "{path}" does not exist.'.format(path=path))

    if not os.access(path, os.R_OK):
        raise exception.PermissionError(
            'Path "{path}" is not readable.'.format(path=path)
        )


def _view_conf(namespace):
    """Print every `Sphinx`_ attribute in ``namespace``.

    Args:
        namespace (argparse.Namespace):
            The parsed user content. It contains all of the necessary
            attributes to generate Sphinx documentation.

    """
    inspector.print_fields_from_directory(
        namespace.directory, fields=set(namespace.fields)
    )


def _view_package_help(namespace):
    """Print the resolved `help`_ of the package in ``namespace``.

    Args:
        namespace (argparse.Namespace):
            The parsed user content. It contains a directory of some Rez source
            package to query from.

    Raises:
        NoPackageFound: If no package was found in ``namespace``.
        ConfigurationError: If any preprocessor / release hook issue was found.

    """
    directory = os.path.normpath(namespace.directory)
    _LOGGER.debug('Found "%s" directory.', directory)

    package = finder.get_nearest_rez_package(directory)

    if not package:
        raise exception.NoPackageFound(
            'Directory "{directory}" is not in a Rez package.'.format(
                directory=directory
            )
        )

    root = finder.get_package_root(package)

    _validate_base_settings(package=package)

    found_methods = preference.get_auto_help_methods()

    if not found_methods:
        _LOGGER.warning(
            "No preprocess or release hook found. Results may not be fully resolved."
        )

    issues = preference.validate_help_settings(package=package)

    if issues:
        raise exception.ConfigurationError(
            'Found exceptions: "{issues}".'.format(issues=issues)
        )

    pprint.pprint(hook.preprocess_help(root, package.help), indent=4)


def _view_common(namespace):
    """Get the Rez package underneath ``namespace`` and check for validity.

    Args:
        namespace (argparse.Namespace):
            The parsed user content. It contains all of the necessary
            attributes to find a Rez package to query.

    Raises:
        MissingPlugIn: If publishing is disabled.
        NoPackageFound: If no Rez package was found.

    Returns:
        rez.packages.Package: The found package.

    """
    if not environment.is_publishing_enabled():
        raise exception.MissingPlugIn(
            "Must must include .rez_sphinx.feature.docbot_plugin==1 "
            "in your resolve to use this command."
        )

    directory = os.path.normpath(namespace.directory)
    _LOGGER.debug('Found "%s" directory.', directory)

    package = finder.get_nearest_rez_package(directory)

    if package:
        return package

    raise exception.NoPackageFound(
        'Directory "{directory}" is not in a Rez package.'.format(directory=directory)
    )


def _view_repository_uri(namespace):
    """Print the URL where documentation for the package in ``namespace`` publishes to.

    Args:
        namespace (argparse.Namespace):
            The parsed user content. It contains all of the necessary
            attributes to find a Rez package to query.

    Raises:
        MissingPlugIn: If publishing is disabled.
        NoPackageFound: If no Rez package was found.

    """
    package = _view_common(namespace)

    # Order doesn't matter so we might as well sort it
    for uri, required in sorted(environment.get_all_repository_uris(package)):
        print(
            'URI: "{uri}" / Required: "{required}"'.format(uri=uri, required=required)
        )


def _view_publish_url(namespace):
    """Print the URL where documentation for this package is viewable from.

    Args:
        namespace (argparse.Namespace):
            The parsed user content. It contains all of the necessary
            attributes to find a Rez package to query.

    Raises:
        MissingPlugIn: If publishing is disabled.
        NoPackageFound: If no Rez package was found.

    """
    package = _view_common(namespace)

    print(environment.get_publish_url(package))


def main(text):
    """Parse and run ``text``, the user's terminal arguments for :ref:`rez_sphinx`.

    Args:
        text (list[str]):
            The user-provided arguments to run via :ref:`rez_sphinx`.
            This is usually space-separated CLI text like
            ``["init", "--directory", "/path/to/rez/package"]``.

    """
    namespace = parse_arguments(text)

    if namespace.verbose:
        # Each Python log level increments by 10. So we decrement by 10 for
        # each verbosity level
        # If the user wants verbose logging, give it to them
        root_namespace = ".".join(__name__.split(".")[:-1])  # Should be "rez_sphinx"
        root_logger = logging.getLogger(root_namespace)
        new_level = root_logger.level - (len(namespace.verbose) * 10)
        root_logger.setLevel(new_level)

    run(namespace)


def parse_arguments(text):
    """Check the given text for validity and, if valid, parse + return the result.

    Args:
        text (list[str]):
            The user-provided arguments to run via :ref:`rez_sphinx`.
            This is usually space-separated CLI text like
            ``["init", "--directory", "/path/to/rez/package"]``.

    Returns:
        argparse.Namespace: The parsed user content.

    """
    parser = _HelpPrinter(
        description="Auto-generate Sphinx documentation for Rez packages.",
    )

    parser.add_argument(
        "--verbose",
        action="append_const",
        const=None,
        help="By default, Only warnings and errors are printed. "
        "In included, info messages are added. Repeat for more verbosity.",
    )

    sub_parsers = parser.add_subparsers(
        dest="command",
        description="All available rez_sphinx commands. Provide a name here.",
    )
    sub_parsers.required = True

    _set_up_build(sub_parsers)
    _set_up_config(sub_parsers)
    _set_up_init(sub_parsers)
    _set_up_publish(sub_parsers)
    _set_up_suggest(sub_parsers)
    _set_up_view(sub_parsers)

    return parser.parse_args(text)


def run(namespace, modify=True):
    """Run the selected subparser.

    Args:
        namespace (argparse.Namespace):
            The parsed user content. It should have a callable method called
            "execute" which takes ``namespace`` as its only argument.
        modify (bool, optional):
            If True, run extra calls directly modifying ``namespace``
            before calling the main execution function. If False, just
            take ``namespace`` directly as-is.

    """
    if modify and hasattr(namespace, "directory"):
        namespace.directory = path_control.expand_path(namespace.directory)

    namespace.execute(namespace)
