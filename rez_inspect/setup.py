import setuptools


setuptools.setup(
    name="inspect",
    version="1.0.0",
    package_dir={"inspect": ""},
    packages=[
        "inspect",
        "inspect.rezplugins",
        "inspect.rezplugins.command",
    ],
)
