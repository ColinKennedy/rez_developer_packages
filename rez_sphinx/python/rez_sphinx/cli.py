"""The entry point for :ref:`rez_sphinx` on the terminal."""

from __future__ import print_function

import argparse
import json
import logging
import operator
import os
import pprint
import shlex

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


# TODO : Make sure everything here has documentation


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

    preference.validate_base_settings()

    print("All rez_sphinx settings are valid!")


def _init(namespace):
    """Create a Sphinx project, rooted at ``namespace``.

    Args:
        namespace (argparse.Namespace):
            The parsed user content. It contains all of the necessary
            attributes to generate Sphinx documentation.

    """
    preference.validate_base_settings()

    _split_init_arguments(namespace)

    directory = os.path.normpath(namespace.directory)
    _LOGGER.debug('Found "%s" directory.', directory)
    package = finder.get_nearest_rez_package(directory)

    if not package:
        raise exception.NoPackageFound(
            'Directory "{directory}" is not in a Rez package. Cannot continue.'.format(
                directory=directory
            )
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
    if not namespace.sparse:
        data = preference.get_base_settings()
    else:
        data = preference.serialize_override_settings()

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

    """
    if not environment.is_publishing_enabled():
        raise exception.MissingPlugIn(
            "Must must include .rez_sphinx.feature.docbot_plugin==1 "
            "in your resolve to use this command."
        )

    package = finder.get_nearest_rez_package(namespace.directory)
    publishers = publish_run.get_all_publishers(package)

    built_documentation = publish_run.build_documentation(namespace.directory)

    for documentation in built_documentation:
        _LOGGER.info('Publishing "%s" documentation.', documentation)

        for publisher in publishers:
            _LOGGER.debug('Publishing with publisher "%s".', publisher)
            publisher.quick_publish(documentation)


def _preprocess_help(namespace):
    # TODO : Docstring
    # TODO : Make this parsing much cleaner
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

    def _add_build_run_parser(commands):
        build_runner = commands.add_parser(
            "run",
            help="Generates documentation from your .rst files.",
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

    build = sub_parsers.add_parser(
        "build", description="Compile Sphinx documentation from a Rez package."
    )
    commands = build.add_subparsers()
    _add_build_run_parser(commands)


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
        list_default = inner_parser.add_parser(
            "list-defaults",
            description="Show the rez_sphinx's default settings.",
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
        list_overrides = inner_parser.add_parser(
            "list-overrides",
            description="Show non-default rez_sphinx's settings.",
        )
        _add_format_argument(list_overrides)
        list_overrides.add_argument(
            "--sparse",
            action="store_true",
            help="If included, the reported config shows overrides, only.",
        )
        list_overrides.set_defaults(execute=_list_overrides)

    config = sub_parsers.add_parser(
        "config",
        help="All commands related to rez_sphinx configuration settings.",
    )
    # TODO : Figure out how to make sure a subparser is chosen
    inner_parser = config.add_subparsers()

    check = inner_parser.add_parser(
        "check", description="Report if the current rez_sphinx user settings are valid."
    )
    _add_directory_argument(check)
    check.set_defaults(execute=_check)

    show = inner_parser.add_parser(
        "show",
        description="Print the value of any configuration attribute.",
    )
    show.add_argument(
        "names",
        nargs="*",
        help="Configuration attributes to check for. Specify inner dicts using "
        '"foo.bar" syntax. Use --list to show all possible values.',
    )
    show.add_argument(
        "--list-all",
        action="store_true",
        help="If included, print available names. Don't actually query anything.",
    )
    _add_directory_argument(show)
    show.set_defaults(execute=_show)

    _set_up_list_default(inner_parser)
    _set_up_list_overrides(inner_parser)


def _set_up_init(sub_parsers):
    """Add :ref:`rez_sphinx init` CLI parameters.

    Args:
        sub_parsers (argparse._SubParsersAction):
            A collection of parsers which the :ref:`rez_sphinx init` will be
            appended onto.

    """
    init = sub_parsers.add_parser(
        "init", description="Set up a Sphinx project in a Rez package."
    )
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
    # TODO : Docstring here
    publish = sub_parsers.add_parser(
        "publish", description="Build & Send your documentation to the network. "
        "Requires rez-docbot to function."
    )
    inner_parsers = publish.add_subparsers()
    publish_runner = inner_parsers.add_parser(
        "run",
        help="Builds + publishs your documentation.",
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
        build_order = inner_parsers.add_parser("build-order")
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

    def _set_up_preprocess_help(inner_parers):
        # TODO : Make this parser better and more explicit
        preprocess_help = inner_parsers.add_parser("preprocess-help")
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

    suggest = sub_parsers.add_parser(
        "suggest", description="Check the order which packages should run."
    )
    inner_parsers = suggest.add_subparsers()

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
        view_conf = inner_parsers.add_parser(
            "sphinx-conf",
            help="Show your documentation's Sphinx conf.py settings. Useful for debugging!",
        )

        view_conf.add_argument(
            "fields",
            nargs="*",
            help="A space-separated list of fields to print. "
            "If not provided, everything is shown.",
        )

        _add_directory_argument(view_conf)

        view_conf.set_defaults(execute=_view_conf)

    def _set_up_view_publish_url(inner_parsers):
        view_publish_url = inner_parsers.add_parser(
            "publish-url", help="Show where this documentation will be published to."
        )

        _add_directory_argument(view_publish_url)
        view_publish_url.set_defaults(execute=_view_publish_url)

    view = sub_parsers.add_parser(
        "view", description="Check the order which packages should run."
    )
    inner_parsers = view.add_subparsers()

    _set_up_view_conf(inner_parsers)


def _show(namespace):
    """Print the configuration value(s) the user asked for.

    If --list-all is provided, all potential configuration values are printed instead.

    Args:
        namespace (argparse.Namespace):
            The parsed user content. It contains all of the necessary
            attributes to run :ref:`rez_sphinx config show`.

    """
    # TODO : This function needs to take into account the user's directory and
    # query stuff from the user's package.py
    #
    if namespace.list_all:
        print("All available paths:")

        for path in sorted(preference.get_preference_paths()):
            print(path)

        return

    names = namespace.names

    if not names:
        # If no name is specified, show everything
        names = sorted(preference.get_preference_paths())

    if len(names) == 1:
        print(preference.get_preference_from_path(names[0]))

        return

    values = []
    invalids = set()

    for name in names:
        try:
            values.append(
                (
                    name,
                    pprint.pformat(preference.get_preference_from_path(name), indent=4),
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


def _view_publish_url(namespace):
    """Print the URL where documentation for the package in ``namespace`` publishes to.

    Args:
        namespace (argparse.Namespace):
            The parsed user content. It contains all of the necessary
            attributes to find a Rez package to query.

    """
    # TODO : Add this + add unittests
    raise NotImplementedError(namespace)


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
    parser = argparse.ArgumentParser(
        description="Auto-generate Sphinx documentation for Rez packages.",
    )

    parser.add_argument(
        "--verbose",
        action="append_const",
        const=None,
        help="By default, Only warnings and errors are printed. "
        "In included, info messages are added. Repeat for more verbosity.",
    )

    sub_parsers = parser.add_subparsers(dest="commands")
    sub_parsers.required = True

    _set_up_build(sub_parsers)
    _set_up_config(sub_parsers)
    _set_up_init(sub_parsers)
    _set_up_publish(sub_parsers)
    _set_up_suggest(sub_parsers)
    _set_up_view(sub_parsers)

    # TODO : Fix the error where providing no subparser command
    # DOES NOT show the help message
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
    # TODO : This is weird. Remove it
    if modify and hasattr(namespace, "directory"):
        namespace.directory = path_control.expand_path(namespace.directory)

    namespace.execute(namespace)
