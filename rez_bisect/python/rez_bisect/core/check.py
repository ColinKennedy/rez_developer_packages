import subprocess


def is_bad(context, command):
    return not is_good(context, command)


def is_good(context, command):
    """Check if `context` can run `command` without failing.

    Args:
        context (:class:`rez.resolved_context.ResolvedContext`):
            A Rez resolve which might fail if it runs `command`.
        command (str):
            The path to a shell script which, when run, will pass or succeed.

    Returns:
        bool: If the `command` succeeded.

    """
    process = context.execute_command(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    process.communicate()

    return process.returncode == 0
