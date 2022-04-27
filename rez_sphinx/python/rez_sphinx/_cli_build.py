"""A companion module for :mod:`.cli`, which sets up :ref:`rez_sphinx build`."""

import operator
import shlex

from .commands.builder import runner
from .core import api_builder, cli_helper, exception


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

    runner.build(
        namespace.directory,
        api_mode=namespace.api_documentation,
        api_options=namespace.api_doc_arguments,
        no_api_doc=namespace.no_api_doc,
        quiet=False,
    )


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


def set_up_build(sub_parsers):
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
        cli_helper.add_directory_argument(build_runner)
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

        cli_helper.add_remainder_argument(build_runner)

    description = "Compile Sphinx documentation from a Rez package."
    build = sub_parsers.add_parser("build", description=description, help=description)
    command = build.add_subparsers(dest="command")
    command.required = True
    _add_build_run_parser(command)
