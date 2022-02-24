name = "rpm2cpio"

version = "2017"

description = "A Lightweight implementation of rpm2cpio written in Python."

authors = ["ruda"]

help = [
    ["Git Mirror", "https://github.com/ruda/rpm2cpio"],
    ["Home Page", "https://rudamoura.com/rpm2cpio"],
    ["Source Code", "https://rudamoura.com/rpm2cpio"]
]

private_build_requires = ["python-2.7+<4"]

build_command = "python {root}/rezbuild.py"


def commands():
    import os
    
    env.PYTHONPATH.append(os.path.join("{root}", "python"))
