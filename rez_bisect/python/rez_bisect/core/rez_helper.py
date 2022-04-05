import subprocess
import os

from rez.config import config
from rez import resolved_context

from . import exception, path_helper


_REQUEST_SEPARATOR = " "


def _is_relative_context(text):
    # TODO : Find a more reliable way to do this
    return text.endswith(".rxt")


def normalize_requests(requests, root):
    missing = set()
    output = []

    for request in requests:
        if os.path.isabs(request) and not os.path.isfile(request):
            missing.add(request)

        if missing:
            continue

        if _is_relative_context(request):
            request = path_helper.normalize(request, root)
            raise NotImplementedError('Need to handle .rxt files here. Maybe.')
        else:
            output.append(request.split(_REQUEST_SEPARATOR))

    if not missing:
        return output

    raise exception.BadRequest('Requests "{missing}" could not be found.'.format(missing=missing))


def to_contexts(requests, packages_path=None):
    if not packages_path:
        packages_path = config.packages_path

    failed = set()
    contexts = []

    for request in requests:
        # TODO : Add context load support, here
        context = resolved_context.ResolvedContext(
            package_requests=request,
            package_paths=packages_path,
        )

        if not context.success:
            failed.add(request)

            continue

        contexts.append(context)

    if failed:
        raise exception.BadRequest('Requests "{failed}" were not resolvable.'.format(failed=failed))

    return contexts


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
