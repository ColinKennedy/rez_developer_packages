"""Extra functions so the CLI works with Rez as expected."""

import logging
import os
import subprocess

from rez import resolved_context

from . import exception, path_helper

_REQUEST_SEPARATOR = " "
_LOGGER = logging.getLogger(__name__)


def _is_relative_context(text):
    """Check if ``text`` is meant to point to a Rez :ref:`context` file."""
    # TODO : Find a more reliable way to do this
    return text.endswith(".rxt")


def to_contexts(requests, root, packages_path=None, allow_unresolved=False):
    """Convert ``requests`` into Rez :ref:`contexts`.

    Important:
        It's assumed that the packages in ``requests`` represent
        :ref:`installed` Rez packages.

    Args:
        requests (iter[str]):
            Each :ref:`.rxt` resolve file or a raw request ``"foo-1+<2 bar==3.0.0"``
            to convert into Rez contexts.
        root (str):
            An absolute path used whenever a request in ``requests`` points to
            a relative file / folder.
        packages_path (list[str], optional):
            The paths used to search for Rez packages while resolving.
            If no paths are given, the default paths are used instead.
        allow_unresolved (bool, optional):
            If False, every :ref:`request` in ``requests`` must resolve into a
            valid context. If True, contexts which don't resolve are just
            ignored and filtered from the output.

    Raises:
        BadRequest:
            If a request in ``requests`` point to a :ref:`.rxt` file which
            doesn't exist on-disk or any request that failed to resolve.

    Returns:
        list[rez.resolved_context.ResolvedContext]: The found resolves.

    """
    failed = set()
    missing = set()
    contexts = []

    for request in requests:
        if os.path.isabs(request) and not os.path.isfile(request):
            missing.add(request)

        if missing:
            continue

        if _is_relative_context(request):
            request = path_helper.normalize(request, root)
            context = resolved_context.ResolvedContext.load(request)
        else:
            context = resolved_context.ResolvedContext(
                package_requests=to_request_list(request),
                package_paths=packages_path,
            )

        if not context.success:
            failed.add(request)

            continue

        if contexts and context == contexts[-1]:
            _LOGGER.info('Duplicate context "%s" found and skipped.', context)
        else:
            # Prevent duplicate, consecutive contexts from being added. It's a
            # total waste to compute them as separate items.
            #
            contexts.append(context)

    if len(missing) == 1:
        raise exception.BadRequest(
            'Context file "{missing}" does not exist on-disk.'.format(
                missing=next(iter(missing))
            )
        )
    elif missing:
        raise exception.BadRequest(
            'Context files "{missing}" do not exist on-disk.'.format(missing=missing)
        )

    if not allow_unresolved:
        if len(failed) == 1:
            raise exception.BadRequest(
                'Request "{failed}" was not resolvable.'.format(
                    failed=next(iter(failed))
                )
            )
        elif failed:
            raise exception.BadRequest(
                'Requests "{failed}" were not resolvable.'.format(failed=failed)
            )

    return contexts


def to_request_list(request):
    """Convert a raw ``request`` to a list of package requests.

    Args:
        request (str): A raw request. e.g. ``"foo-1+<2 bar==3.0.0"``

    Returns:
        list[str]: The split request, e.g. ``["foo-1+<2", "bar==3.0.0"]``.

    """
    return request.split(_REQUEST_SEPARATOR)


def to_script_runner(path):
    """Convert an executable into a callable Python function.

    Args:
        path (str): The absolute path to an executable file on-disk to run, later.

    Returns:
        callable[rez.resolved_context.Context] -> bool:
            A function that returns True if the executable ``path`` fails.
            Otherwise, it returns False, indicating success. It takes a Rez
            :ref:`context` as input.

    """

    def _run_in_context(context):
        process = context.execute_command(
            path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        process.communicate()

        return process.returncode == 0

    return _run_in_context
