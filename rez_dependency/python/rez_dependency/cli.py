"""The main module for parsing and calling user CLI input."""

import argparse

from rez import resolved_context

from ._core import (
    cli_helper,
    display_levels,
    display_list,
    display_tree,
    exception,
    streamer,
    tree_accumulator,
)


def _get_context(namespace):
    """rez.resolvedContext.ResolvedContext: Find packages from a request + paths."""
    context = resolved_context.ResolvedContext(
        namespace.request, package_paths=namespace.packages_path
    )

    if context.success:
        return context

    raise exception.InvalidContext(
        'Request + Packages path "{namespace.request} + {namespace.packages_path}" '
        "could not resolve.".format(namespace=namespace)
    )


def _get_query_type(namespace):
    """Get every dependency query from ``namespace``.

    Args:
        namespace (argparse.Namespace):
            The parsed user arguments to query from. e.g. :ref:`--build-requires`.

    Returns:
        list[callable[rez.packages.Package]] -> list[rez.utils.formatting.PackageRequest]:  # pylint: disable=line-too-long
            Given some package, query it for requirements.

    """
    output = []

    if namespace.build_requires:
        output.append(tree_accumulator.get_attribute_getter("build_requires"))

    if namespace.private_build_requires:
        output.append(tree_accumulator.get_attribute_getter("private_build_requires"))

    if output:
        output.insert(0, tree_accumulator.get_attribute_getter("requires"))

    return output


def _parse_arguments(text):
    """Convert user-provided CLI text into Python objects.

    Args:
        text (list[str]): Space-separated CLI user input. e.g. ``["tree", "foo-1"]``.

    Returns:
        argparse.Namespace: The parsed output.

    """
    parser = argparse.ArgumentParser(
        description="Query Rez package dependencies and display them at will.",
    )
    sub_parsers = parser.add_subparsers()
    _set_up_levels_parser(sub_parsers)
    _set_up_list_parser(sub_parsers)
    _set_up_tree_parser(sub_parsers)

    return parser.parse_args(text)


def _print_levels(namespace):
    """Print all dependencies by-depth, as flat lists.

    Args:
        namespace (argparse.Namespace):
            The parsed user arguments to query from. e.g. :ref:`--build-requires`.

    """
    context = _get_context(namespace)
    query_using = _get_query_type(namespace)
    tree = tree_accumulator.collect_tree(context, query_using=query_using)

    streamer.printer("\n".join(display_levels.get_lines(tree)))


def _print_list(namespace):
    """Print all unique package dependencies family names as a single list.

    Args:
        namespace (argparse.Namespace):
            The parsed user arguments to query from. e.g. :ref:`--build-requires`.

    """
    context = _get_context(namespace)
    query_using = _get_query_type(namespace)
    tree = tree_accumulator.collect_tree(context, query_using=query_using)

    streamer.printer("\n".join(display_list.get_lines(tree)))


def _print_tree(namespace):
    """Print package dependencies in the order the dependencies are required.

    This is the "full" dependency tree.

    Args:
        namespace (argparse.Namespace):
            The parsed user arguments to query from. e.g. :ref:`--build-requires`.

    """
    context = _get_context(namespace)
    query_using = _get_query_type(namespace)
    tree = tree_accumulator.collect_tree(context, query_using=query_using)

    namespace.display_as(tree)


def _set_up_levels_parser(sub_parsers):
    """Add ``levels`` as a sub-command in ``sub_parsers``.

    Args:
        sub_parsers (argparse._SubParsersAction):
            The group to add the sub-command under.

    """
    help_ = 'Display dependencies in banks, based on how "deep" the dependency is.'

    parser = sub_parsers.add_parser("levels", description=help_, help=help_)
    cli_helper.add_build_requires_parameter(parser)
    cli_helper.add_packages_path_parameter(parser)
    cli_helper.add_private_build_requires_parameter(parser)
    cli_helper.add_request_parameter(parser)
    parser.set_defaults(execute=_print_levels)


def _set_up_list_parser(sub_parsers):
    """Add ``list`` as a sub-command in ``sub_parsers``.

    Args:
        sub_parsers (argparse._SubParsersAction):
            The group to add the sub-command under.

    """
    help_ = "Display all found Rez packages as a single, unique list of packages."

    parser = sub_parsers.add_parser("list", description=help_, help=help_)
    cli_helper.add_build_requires_parameter(parser)
    cli_helper.add_packages_path_parameter(parser)
    cli_helper.add_private_build_requires_parameter(parser)
    cli_helper.add_request_parameter(parser)
    parser.set_defaults(execute=_print_list)


def _set_up_tree_parser(sub_parsers):
    """Add ``tree`` as a sub-command in ``sub_parsers``.

    Args:
        sub_parsers (argparse._SubParsersAction):
            The group to add the sub-command under.

    """
    help_ = "Display dependencies as a tree."

    parser = sub_parsers.add_parser("tree", description=help_, help=help_)
    cli_helper.add_build_requires_parameter(parser)
    cli_helper.add_packages_path_parameter(parser)
    cli_helper.add_private_build_requires_parameter(parser)
    cli_helper.add_request_parameter(parser)
    parser.add_argument(
        "--display-as",
        action=cli_helper.SelectDisplayer,
        choices=sorted(display_tree.OPTIONS.keys()),
        default=display_tree.DEFAULT,
        help="Print the output using the given format.",
    )
    parser.set_defaults(execute=_print_tree)


def main(text):
    """Parse and execute the user's input.

    Args:
        text (list[str]): Space-separated CLI user input. e.g. ``["tree", "foo-1"]``.

    """
    namespace = _parse_arguments(text)
    namespace.execute(namespace)
