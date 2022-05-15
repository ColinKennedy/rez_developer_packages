"""The main module for formatting text for the :ref:`tree sub-command`."""

from . import _display_tree

DEFAULT = _display_tree.as_text

OPTIONS = {
    "text": DEFAULT,
    "json": _display_tree.as_json,
}


def get_option(text):
    """Choose a caller function matching ``text``.

    Args:
        text (str): A registered display option. e.g. ``"json"`` or ``"text"``.

    Returns:
        callable[dict[str, dict[str, ...]]]:
            A function that takes a tree of package dependencies and prints
            them to the terminal.

    Raises:
        ValueError: If ``text`` has no registered caller function.

    """
    try:
        return OPTIONS[text]
    except KeyError:
        raise ValueError(
            'Text "{text}" was invalid. Options were "{OPTIONS}".'.format(
                text=text, OPTIONS=sorted(OPTIONS.keys())
            )
        )
