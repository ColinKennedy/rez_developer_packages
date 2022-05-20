from .schemas import _attribute

_CONFLICT_KEY = "fontcolor"
_CONFLICT_COLOR = "red"
_CONFLICT_VALIDATOR = _attribute.get_from_name(_attribute.FONT_COLOR)


def is_conflict_edge(attributes):
    for key, value in attributes:
        if key != _CONFLICT_KEY:
            continue

        if _CONFLICT_VALIDATOR(value) == _CONFLICT_COLOR:
            return True

    return False
