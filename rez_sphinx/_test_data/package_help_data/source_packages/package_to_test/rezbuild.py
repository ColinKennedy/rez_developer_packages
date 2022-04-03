import os
import shutil


def main(source_root, destination_root):
    source = os.path.join(source_root, "python")
    destination = os.path.join(destination_root, "python")

    if os.path.isfile(destination) or os.path.islink(destination):
        os.remove(destination)
    elif os.path.isdir(destination):
        shutil.rmtree(destination)

    shutil.copytree(source, destination)


if __name__ == "__main__":
    main(os.environ["REZ_BUILD_SOURCE_PATH"], os.environ["REZ_BUILD_INSTALL_PATH"])
