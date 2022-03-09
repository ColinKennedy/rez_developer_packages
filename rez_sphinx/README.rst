==========
rez_sphinx
==========

A tool which makes initializing and building Sphinx documentation using Rez a snap.

Features Overview
=================

- Auto-inits Sphinx documentation
- conf.py grabs directly from package.py
- Link any Rez package's documentation to any other Rez package
- Auto-submit PRs
- Auto-append commands building / publishing documentation
- Auto-configure Rez :ref:`package help`
- Auto-generate Python API documentation
- Publish documentation locally, to GitHub, or readthedocs.io
- Extra documentation-only validation


Running :ref:`rez_sphinx init`
==============================

When you generate documentation for the first time, :ref:`rez_sphinx` will...

- Generate a default Sphinx :ref:`conf.py`
    - ``rez_sphinx`` adds a :ref:`minimal bootstrapper` directly to the :ref:`conf.py`.
- Auto-add extra documentation files for users to fill out
- Bump your Rez package minor version
- Append :ref:`rez-test` entries so the documentation can be built / published

So far this is nothing special. But this is just a start.


Running :ref:`rez_sphinx build`
===============================

Calling a build is as easy as writing `rez-test your_package_name
build_documentation`. What happens when you do that? It will...

- Validate that your documentation files are filled out.
- Auto-generate Python API documentation just in time :ref:`sphinx-apidoc`
- Link your current Rez package to other Rez packages containing documentation,
  by parsing your :ref:`package requires`
    - Want more documentation-only interlinking? See :doc:`adding_extra_interlinking`
- Auto-configure Sphinx, using your :ref:`package.py` contents
- Auto-appends entries to your installed Rez package's
  :ref:`package help <help attribute>`

Some important things to note:

- The "Auto-generate API documentation" feature just calls :ref:`sphinx-apidoc`
  under the hood. But because the API documentation files are generated before
  the documentation builds, they are always kept up to date with your source
  code. To top it off, A common problem with :ref:`sphinx-apidoc` is it
  generates thousands of tiny, "10 lines or less" .rst files. This feature
  fixes that problem.
- Interlinking one Rez package's documentation to another will **always** work,
  due to how ``rez_sphinx`` is configured. No more "This old link that used to
  work now points to nothing".

After building the documentation, you can use ``rez-help my_package_name`` to
see all of the documentation you just generated and even auto-open those links
at will.


Publishing Your Documentation
=============================

If that's all it did, ``rez_sphinx`` wouldn't be special. But there's more.
``rez_sphinx`` is also a ``rez_docbot`` plug-in. You can publish documentation
either at-will or during each package's post-release.

TODO: Revisit these "features" later


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
