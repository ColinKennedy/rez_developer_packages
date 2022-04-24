"""Get the recommended remote documentation publisher."""

from ..publishers import github

_PUBLISHERS = {
    github.Github.get_name(): github.Github,
}


def get_by_name(name):
    """Get the recommended remote documentation publisher for ``name``.

    Args:
        name (str): Some type to query. e.g. ``"github"``.

    Raises:
        ValueError: If ``name`` is unknown.

    Returns:
        Publisher: The found :ref:`publisher type` class.

    """
    try:
        return _PUBLISHERS[name]
    except KeyError:
        raise ValueError(
            'Name "{name}" is invalid. Options were, "{options}".'.format(
                name=name,
                options=sorted(_PUBLISHERS.keys()),
            )
        )
