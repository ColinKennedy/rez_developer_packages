import atexit
import functools
import os
import shutil
import tempfile
import textwrap


def _delete_later(directory):
    atexit.register(functools.partial(shutil.rmtree, directory))


def make_simple_developer_package():
    directory = tempfile.mkdtemp(suffix="make_simple_developer_package")
    _delete_later(directory)

    with open(os.path.join(directory, "package.py"), "w") as handler:
        handler.write(
            textwrap.dedent(
                """\
                name = "some_package"

                version = "1.0.0"

                def commands():
                    import os

                    env.PYTHONPATH.append(os.path.join(root, "python"))
                """
            )
        )

    python_directory = os.path.join(directory, "python")
    os.makedirs(python_directory)

    with open(os.path.join(python_directory, "file.py"), "w") as handler:
        handler.write('print("Hello, World!")')

    return directory
