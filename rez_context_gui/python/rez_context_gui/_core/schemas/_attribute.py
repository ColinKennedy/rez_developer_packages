"""A quick registry for validating Rez :ref:`context` :ref:`digraph` attributes."""

from . import schema_type

# Edges
ARROW_SIZE = "arrowsize"
FONT_COLOR = "fontcolor"

# Nodes
FILL_COLOR = "fillcolor"
FONT_SIZE = "fontsize"
LABEL = "label"
STYLE = "style"


_OPTIONS = {
    # Edges
    ARROW_SIZE: schema_type.NON_ZERO,
    FONT_COLOR: schema_type.GENERIC_COLOR,

    # Nodes
    FILL_COLOR: schema_type.HEX,
    FONT_SIZE: schema_type.NON_ZERO,
    LABEL: schema_type.LABEL_TEXT,
    STYLE: schema_type.STYLE,
}


def get_from_name(name):
    """Find a validator schema, given some :ref:`digraph` attribute ``name``.

    Args:
        name (str): The name of some attribute to find a validator for.

    Raises:
        ValueError: If ``name`` is not a known attribute name.

    """
    try:
        return _OPTIONS[name]
    except KeyError:
        raise ValueError(
            'Name "{name}" is unknown. Options were, "{options}".'.format(
                name=name,
                options=sorted(_OPTIONS.keys()),
            )
        )
