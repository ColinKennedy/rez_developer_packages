#########################
Adding Extra Interlinking
#########################

As mentioned in other pages, :ref:`rez_sphinx build` is able to auto-find the
documentation of dependency Rez packages and links it with the documentation
you're attempting to build.

How It Works
************

Before the documentation is built:

- Grab all Rez package dependencies, (`requires`_, `variants`_, `tests`_ etc)
- For each item in the list, check if there's a defined ``REZ_{NAME}_ROOT``
  environment variable defined.
  - If it is, check if the `package.py`_ at that directory has defined documentation.
  - If so, add it to `intersphinx_mapping`_ so `sphinx.ext.intersphinx`_ sees it.

From there, `sphinx-build`_ runs like it normally does. There's a bunch of
extra checks, like skipping ephemerals, conflicting packages, etc. But that's
the jist.


.. _rez_sphinx build inspect-conf intersphinx_mapping:

Checking Your Interlinks
************************


Run :ref:`rez_sphinx view sphinx-conf intersphinx_mapping`. It'll tell you
exactly what :ref:`rez_sphinx build run` sees, just before your documentation
gets built.


Adding Extra Links
******************

Imagine you want to interlink your project with documentation that isn't listed
in :ref:`rez_sphinx view sphinx-conf intersphinx_mapping`. To do that, you
have two options.


Add To build_documentation
==========================

If the other Rez package you want to include already has :ref:`rez_sphinx`
included, adding it to your package is easy.

.. code-block:: python

    tests = {
       "build_documentation": {
           "command": "rez_sphinx build run",
           "requires": [
               "rez_sphinx-1+<2",
               "other_rez_package-2.3+<3",  # <-- This is for interlinking
           ]
       }
    }

.. note::

    "build_documentation" is the Rez tests key used to build documentation.
    But your pipeline may have renamed it to something else. Use
    :ref:`rez_sphinx config show build_documentation_key` to confirm.

Adding a package to ``build_documentation``'s list of requirements means

- :ref:`rez_sphinx build run` will be able to see it
- You didn't have to include it as a `requires`_ on your package

.. important::

    If you still have interlinks even after adding the Rez package, confirm
    with :ref:`rez_sphinx view sphinx-conf intersphinx_mapping` that
    :ref:`rez_sphinx build run` can see it.


Manually Adding to intersphinx_mapping
======================================

If the documentation that you want to link to either isn't a Rez package or
isn't a Rez package that you can control (e.g. it could be a `rez-pip`_ built
Rez package), you can always write the link like you would any other Sphinx
project.

- Open your `Sphinx conf.py`
- Add this to it, **below** :ref:`rez_sphinx bootstrap`

.. code-block:: python

    intersphinx_mapping.update(
       {
           # Assuming you want to add documentation for https://pypi.org/project/schema/
           "https://schema.readthedocs.io/en/latest/": None
       }
    )

For any Rez package you are able to modify, it's always best to either A. Add
:ref:`rez_sphinx` to it or B. Update the package to point to the URL so
rez_sphinx can auto pick it up.

.. note::

    rez_sphinx is able to see any Sphinx documentation, even if it isn't built
    with :ref:`rez_sphinx`. See
    :doc:`linking_rez_sphinx_with_other_documentation_tools` for details.


Searching For Documentation
===========================

If the package you want to add is:

- A third-party tool that you can't easily modify (in Rez or in general)
- In a known location
- Used as interlinks to other Rez packages

It may make sense to define those paths globally with ``rez_sphinx config``.


As A {"package": "documentation URL"} Dict
------------------------------------------

There's a way to make a Python dictionary like
``{"the_rez_package": "https://www.package.com/the/sphinx/docs"}``.
Any time the_rez_package is found but no documentation URL exists, it'll use
that as a fallback.

In short, read :ref:`rez_sphinx.intersphinx_settings.package_link_map`.
