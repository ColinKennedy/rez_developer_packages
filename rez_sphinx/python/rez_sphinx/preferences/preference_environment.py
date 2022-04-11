import ast
import os


_ENVIRONMENT_SEPARATOR = "_"


def _get_default_type(schema, location):
    raise ValueError()


def _to_environment_variable(path):
    return path.upper().replace(_PREFERENCE_DICT_SEPARATOR, _ENVIRONMENT_SEPARATOR)


def _create_parent_defaults(parts, schema):
    current = []
    context = {}

    for key in parts:
        if not current:
            current = [key]

        class_name = _get_default_type(schema, current)
        context = context.setdefault(key, class_name())
        current = current[key]

    return context


def _read_variable(variable):
    return ast.literal_eval(os.environ[variable])


def get_overrides(schema):
    paths, _ = _get_schema_preference_paths()
    context = {}

    for path in paths:
        variable = _to_environment_variable(path)

        if variable not in os.environ:
            continue

        parts = path.split(_PREFERENCE_DICT_SEPARATOR)

        context = _create_parent_defaults(parts[:-1], schema)
        raise ValueError('STOP', context)
        key = parts[-1]
        value = _read_variable(variable)
        context[key] = value

    raise ValueError(paths)
