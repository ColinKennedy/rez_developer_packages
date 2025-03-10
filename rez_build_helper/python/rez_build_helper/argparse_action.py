"""Extensions to :mod:`argparse` to make parsing user arguments easier."""

import argparse
import os
import typing

from . import exceptions, namespacer

_CLI_ARGUMENT_NAMESPACE_SEPARATOR = ":"
_PYTHON_NAMESPACE_SEPARATOR = "."


class NamespacePathPair(argparse.Action):
    """A parser for namespace:directory/ arguments in :mod:`rez_build_helper`."""

    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: typing.Optional[typing.Union[str, typing.Sequence[str]]],
        option_string: typing.Optional[str] = None,
    ) -> None:
        """Make sure ``values`` specifies a namespace and a relative path.

        Args:
            parser:
                The current parser that this instance is applied onto.
            namespace:
                The destination where parsed values are placed onto.
            values:
                Raw user input content to split and add to the parser.
            option_string:
                The flag from the CLI.

        Raises:
            UserInputError: If the user provided a malformed namespace:directory/ input.

        """
        output: typing.List[namespacer.PythonPackageItem] = []
        root = os.environ["REZ_BUILD_SOURCE_PATH"]

        for text in values or []:
            item = _validate_text(text)

            _validate_relative_path(item.relative_path, root=root)

            output.append(item)

        setattr(namespace, self.dest, output)


class Path(argparse.Action):
    """A file/directory path validator :mod:`rez_build_helper`."""

    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: typing.Optional[typing.Union[str, typing.Sequence[str]]],
        option_string: typing.Optional[str] = None,
    ) -> None:
        """Make sure ``values`` specifies a namespace and a relative path.

        Args:
            parser:
                The current parser that this instance is applied onto.
            namespace:
                The destination where parsed values are placed onto.
            values:
                Raw user input content to split and add to the parser.
            option_string:
                The flag from the CLI.

        Raises:
            UserInputError: If the user didn't provide a valid directory.

        """
        output = []
        root = os.environ["REZ_BUILD_SOURCE_PATH"]

        for path in values or []:
            _validate_relative_path(path, root=root)
            output.append(path)

        setattr(namespace, self.dest, output)


def _validate_relative_path(path: str, root: typing.Optional[str] = "") -> None:
    """Make sure ``path`` corresponds to some file or directory on-disk.

    Args:
        text: A relative path to somewhere on-disk.
        root: An absolute path to the Rez package's source directory.

    Raises:
        UserInputError: If ``text`` is misspelled or points to nothing on-disk.

    """
    if not path:
        raise exceptions.UserInputError("Path cannot be empty.")

    root = root or os.environ["REZ_BUILD_SOURCE_PATH"]
    full = os.path.join(root, path)

    if not os.path.exists(full):
        raise exceptions.UserInputError(
            'Path "{full}" from "{path}" does not exist. Check spelling and try again.'.format(
                full=full,
                path=path,
            )
        )


def _validate_text(text: str) -> namespacer.PythonPackageItem:
    """Make sure ``text`` matches ``"namespace:folder/"`` or ``"namespace:folder"``.

    Args:
        text: Raw user input to parse for parts.

    Raises:
        UserInputError: If ``text`` is malformed.

    Returns:
        The parsed output.

    """
    parts = []

    for part in text.split(_CLI_ARGUMENT_NAMESPACE_SEPARATOR):
        part = part.strip()

        if part:
            parts.append(part)

    if not parts:
        raise exceptions.UserInputError(
            'Text cannot be empty. Expected "some_root.namespace:python_folder/".'
        )

    if len(parts) != 2:
        raise exceptions.UserInputError(
            'Text "{text}" must be namespace:subfolder. '
            'Expected "some_root.namespace:python_folder/"'.format(
                text=text,
            )
        )

    namespace_text = parts[0]
    namespace_parts = namespace_text.split(_PYTHON_NAMESPACE_SEPARATOR)

    return namespacer.PythonPackageItem(namespace_text, namespace_parts, parts[1])
