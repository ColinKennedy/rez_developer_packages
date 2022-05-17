from . import schema_type


FILL_COLOR = "fillcolor"
FONT_SIZE = "fontsize"
LABEL = "label"
STYLE = "style"

_OPTIONS = {
    FILL_COLOR: schema_type.HEX,
    FONT_SIZE: schema_type.NON_ZERO,
    LABEL: schema_type.LABEL_TEXT,
    STYLE: schema_type.STYLE,
}


def get_from_name(name):
    try:
        return _OPTIONS[name]
    except KeyError:
        raise ValueError(
            'Name "{name}" is unknown. Options were, "{options}".'.format(
                name=name, options=sorted(_OPTIONS.keys()),
            )
         )
