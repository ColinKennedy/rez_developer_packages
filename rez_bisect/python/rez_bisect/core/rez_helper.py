import subprocess
import os

from rez.config import config
from rez import resolved_context

from . import exception, path_helper


_REQUEST_SEPARATOR = " "


def _is_relative_context(text):
    # TODO : Find a more reliable way to do this
    return text.endswith(".rxt")


def to_contexts(requests, root, packages_path=None):
    if not packages_path:
        packages_path = config.packages_path

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

        contexts.append(context)

    if missing:
        raise exception.BadRequest(
            'Context files "{missing}" do not exist on-disk.'.format(missing=missing)
        )

    if failed:
        raise exception.BadRequest(
            'Requests "{failed}" were not resolvable.'.format(failed=failed)
        )

    return contexts


def to_request_list(request):
    return request.split(_REQUEST_SEPARATOR)


def to_script_runner(path):
    def _run_in_context(context):
        process = context.execute_command(
            path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        process.communicate()

        return process.returncode == 0

    return _run_in_context
