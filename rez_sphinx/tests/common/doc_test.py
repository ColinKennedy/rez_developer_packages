import os


def add_to_default_text(directory):
    source = os.path.join(directory, "documentation", "source")

    for path in (
        os.path.join(source, "developer_documentation.rst"),
        os.path.join(source, "user_documentation.rst"),
    ):
        with open(path, "a") as handler:
            handler.write("Extra text here")
