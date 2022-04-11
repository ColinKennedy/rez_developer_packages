"""A preference module which specializes in parsing environment variables."""

import ast
import inspect
import os

import schema as schema_
import six
from six.moves import collections_abc

from ..core import schema_optional

_ENVIRONMENT_PREFIX = "REZ_SPHINX_"
_ENVIRONMENT_SEPARATOR = "_"
SEPARATOR = "."


def _get_default(location, schema):
    """Find the recorded, default value in ``schema``, at ``location``.

    Args:
        location (iter[str]): The dict keys to look within ``schema`` for.
        schema (dict[str, dict[str, object] or object]): A nested dictionary.

    Raises:
        NotImplementedError:
            If dict key is found which we don't know how to process yet.

    Returns:
        object:
            A class or an instance of a class. It could be any value.  If
            ``location`` is the start or middle of a nested dict, then this
            function always returns a class type. But if it's a "leaf" end of a
            dict, it could be a class or instance of anything.

    """

    def _guess_real_key(part, schema):
        if part in schema:
            return part

        for key in schema.keys():
            if isinstance(key, schema_.Optional):
                if schema_optional.get_raw_key(key) != part:
                    continue

                return key

            if isinstance(key, schema.Use):
                continue

            raise NotImplementedError(
                'Key "{key}" is currently unsupported.'.format(key=key)
            )

    current = schema

    for part in location:
        real_key = _guess_real_key(part, current)
        current = current[real_key]

    return current


def _to_environment_variable(path):
    """Convert a dot-separated dict location to an environment variable.

    Args:
        path (str):
            Some preferences path to check for. The list of possible values can
            be queried using :ref:`rez_sphinx config show-all`.
            e.g. ``"sphinx-apidoc.allow_apidoc_templates"``.

    Returns:
        str:
            The equivalent environment variable for ``path``. e.g.
            ``"REZ_SPHINX_SPHINX_APIDOC_ALLOW_APIDOC_TEMPLATES"``.

    """
    path = path.upper()

    # Preference paths may be named "sphinx-apidoc.allow_api_doc_templates".
    # We must convert "- / ." -> "_" so we get the environment variable.
    #
    for character in ["-", SEPARATOR]:
        path = path.replace(character, _ENVIRONMENT_SEPARATOR)

    return _ENVIRONMENT_PREFIX + path


def _create_parent_defaults(parts, schema, context):
    """Generate a nested Python structure for ``parts``.

    Warning:
        ``context`` will be directly mutated by this function.

    Args:
        parts (iter[str]):
            The address to generate objects towards. e.g. ``["sphinx-apidoc"]``.
        schema (dict[str, dict[str, object] or object]):
            A nested dictionary. This object's nested types will be "mirrored"
            across to ``context``.
        context (dict[str, dict[str, object] or object]):
            The object which will have new entries added by this function.

    Returns:
        object:
            The leaf location, that represents the end of ``parts``, which was
            just created if it didn't already exist.

    """
    location = []
    current = context

    for key in parts:
        if not location:
            location = [key]

        class_type = _get_default(location, schema).__class__
        current[key] = current.setdefault(key, class_type())
        current = current[key]

    return context


def _read_variable(variable, type_context):
    """Parse and read the environment variable.

    Example:
        $ export REZ_SPHINX_SPHINX_APIDOC_ALLOW_APIDOC_TEMPLATES=0

        >>> _read_variable("REZ_SPHINX_SPHINX_APIDOC_ALLOW_APIDOC_TEMPLATES", bool)
        # Result: False

    Args:
        variable (str):
            An environment variable to query. e.g.
            ``"REZ_SPHINX_SPHINX_APIDOC_ALLOW_APIDOC_TEMPLATES"``.
        type_context (callable or :class:`schema.Schema` or :class:`schema.Use`):
            The object needed to "interpret" the returned variable value.  For
            example, a user might set an environment variable as ``"0"``.  How
            do we know that's meant to be a raw string or a bool (whose value
            is meant to be ``False``).  The only way to tell for sure is to
            pass ``bool`` to ``type_context``.

    Raises:
        NotImplementedError: If we don't know how to use ``type_context``.

    Returns:
        object: The parsed output.

    """
    try:
        parsed = ast.literal_eval(os.environ[variable])
    except ValueError:
        # This may happen if the user sets a string environment variable
        # without wrapping it in ""s. This is pretty common so we should just
        # escape the string for them.
        #
        parsed = ast.literal_eval('"' + os.environ[variable] + '"')

    if hasattr(type_context, "validate"):  # Types from :mod:`schema` use this method
        return parsed

    if callable(type_context):
        return type_context(parsed)

    raise NotImplementedError(
        'Context "{type_context}" is not written yet. Please add it!'.format(
            type_context=type_context,
        )
    )


def get_overrides(schema):
    """Find every override which comes from the user's environment variables.

    Args:
        schema (dict[str, dict[str, object] or object]):
            A nested dictionary used to discover and read environment variable data.

    Returns:
        dict[str, dict[str, object] or object]:
            All found overrides, if any. Most of the time, this will be an
            empty dict. Most people probably won't set overrides via
            environment variables.

    """
    paths, _ = get_paths(schema)
    overrides = {}

    for path in paths:
        variable = _to_environment_variable(path)

        if variable not in os.environ:
            continue

        # Get parent / context information, for later
        parts = path.split(SEPARATOR)
        tail = parts[:-1]
        key = parts[-1]
        type_context = _get_default(parts, schema)

        if not isinstance(type_context, schema_.Use) and not inspect.isclass(
            type_context
        ):
            type_context = type_context.__class__

        # Construct the parent location and read the environment variable
        parent = _create_parent_defaults(tail, schema, overrides)
        value = _read_variable(variable, type_context)

        # Set ``overrides`` as needed
        if tail:
            parent[tail[-1]][key] = value
        else:
            parent[key] = value

    return overrides


def get_paths(schema):
    """Get every preference path that depends on a schema.

    Args:
        schema (dict[str, dict[str, object] or object]): A nested dictionary.

    Returns:
        tuple[set[str], set[str]]:
            Every preference path, split into two sets. The first set contains
            "normal" preference paths which have no dynamic content. The second
            set has at least some content that must be provided by the user in
            order to fully resolve.

    """

    def _get_mapping(mapping, context):
        outputs = set()
        exceptional_cases = set()

        for key, value in mapping.items():
            if isinstance(key, schema_.Optional):
                key = schema_optional.get_raw_key(key)

            if isinstance(key, schema_.Use):
                # We wouldn't really know how to handle this situation. Just ignore it.
                exceptional_cases.add(context)

                continue

            if not isinstance(value, collections_abc.Mapping):
                if not isinstance(key, six.string_types):
                    # We wouldn't really know how to handle this situation.
                    # Just ignore it.
                    #
                    exceptional_cases.add(context)
                else:
                    outputs.add(key)

                continue

            inner_context = key

            if context:
                inner_context = "{context}{SEPARATOR}{key}".format(
                    context=context,
                    SEPARATOR=SEPARATOR,
                    key=key,
                )

            inner_output, extra_cases = _get_mapping(value, inner_context)

            if not inner_output:
                # When this happens, it's because a nested object is empty by
                # default. We still want the context key, in this case.
                #
                # e.g. "intersphinx_settings.package_link_map"
                #
                outputs.add(key)

            exceptional_cases.update(extra_cases)

            for inner_key in inner_output:
                if isinstance(inner_key, schema_.Optional):
                    inner_key = schema_optional.get_raw_key(inner_key)

                outputs.add(
                    "{key}{SEPARATOR}{inner_key}".format(
                        key=key,
                        SEPARATOR=SEPARATOR,
                        inner_key=inner_key,
                    )
                )

        return outputs, exceptional_cases

    return _get_mapping(
        schema,
        context="",
    )
