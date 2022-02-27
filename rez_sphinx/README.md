# rez_sphinx
A tool which makes initializing and building Sphinx documentation using Rez a snap.

To get started, here's all you need to do.

TODO: Revisit these instructions later

1. `cd` into the Rez Python package that you want (e.g. my_package)
2. Create a Rez resolve of your package + rez_sphinx and run rez_sphinx init

```sh
rez-env my_package rez_sphinx -- rez-sphinx init
```

This initialization command adds a "documentation" folder and Sphinx-related
files and edits your package.py with things rez-sphinx needs to build
documentation.

You're now ready to build! Just run `rez-test my_package build_documentation`.

Seems so simple, right? There's a lot going on under the hood to make it that
slick. A regular user who just wants documentation and doesn't care about the
specifics only needs to know that. But if you want greater customization, check
out the full documentation for more information.

TODO : Add a link here


# Building / Publishing Remotely
The default state of `rez-sphinx` is to build documentation locally in Rez packages.
However many who use this tool may want documentation to be added online.

TODO : Add support for these
TODO : Add links for both of these

`rez-sphinx` comes with publishing capabilities out of box for

- GitHub Pages
- readthedocs.org

Click the links above to learn how that's done.
