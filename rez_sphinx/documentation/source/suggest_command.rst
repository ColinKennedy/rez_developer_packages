.. _rez_sphinx suggest:

##################
rez_sphinx suggest
##################

This generic command is simply for querying things about Rez packages which
users or :ref:`rez_sphinx` uses. See the sections below for example
sub-commands.


.. _rez_sphinx suggest build-order:

******************************
rez_sphinx suggest build-order
******************************

This command can look at a group of directories, scan the Rez packages found
within it, and recommend the order in which their documentation should be
built. Imagine you have two packages:

- dependency
- package_that_needs_dependency

Imagine again these packages both have new changes that affect their
documentation.  ``package_that_needs_dependency`` refers to something new
within ``dependency``.  If you build documentation for ``dependency`` first,
followed by ``package_that_needs_dependency``, everything works as intended.
But if you accidentally build in the opposite order, any links
``package_that_needs_dependency`` have to ``dependency`` will be messed up.

``rez_sphinx suggest build-order`` exists to automate this discovery + package
ordering process.


.. _build-order --search-mode:

rez_sphinx suggest build-order --search-mode
============================================

To find Rez packages, we must provide ``build-order`` some directories to
search within. But that's not enough because those directories may contain
multiple Rez packages. The directory could be the root of installed packages,
like ``~/packages`` or ``~/.rez/packages/int``. Or the directory could be a git
repository with a completely arbitrary folder structure.

``build-order --search-mode`` handles this and comes in 3 flavors.

- source - ``./*`` - Search all immediate subfolders for Rez packages
- installed - ``./*/*`` - Search for {family_name}/{version} Rez packages
- recursive - ``./**/**`` - Search everywhere for Rez packages


.. _build-order --suggestion-mode:

rez_sphinx suggest build-order --suggestion-mode
================================================

Once Rez packages are found, we need to query those Rez packages for
"dependencies" needed by :ref:`rez_sphinx`. Normally the default value, which
checks for `requires`_ and `variants`_ will work for 90%+ of Rez packages and
is most recommended.  But if your pipeline has special considerations,
``rez_sphinx suggest build-order --suggestion-mode=guess`` might be for you.

.. _build-order --display-as:

rez_sphinx suggest build-order --display-as
===========================================

``--display-as`` determines how found packages will be printed to the terminal.

``--display-as=names`` Copies the style of `rez-depends`_, which looks like this:

::

    rez_sphinx suggest build-order /path/to/source/rez/packages --display-as=names

    #0: package_with_no_dependencies another_package
    #1: package_that_depends_on_something_in_row_0
    #2: package_that_depends_on_something_in_row_1
    #3: package_that_depends_on_something_in_row_2

    etc.

``--display-as=directories`` shows all directories which contain Rez packages.

::

    rez_sphinx suggest build-order /path/to/source/rez/packages --display-as=directories

    /path/to/source/rez/packages/package_with_no_dependencies_directory
    /path/to/source/rez/packages/another_package_directory
    /path/to/source/rez/packages/package_that_depends_on_something_in_row_0
    /path/to/source/rez/packages/package_that_depends_on_something_in_row_1
    /path/to/source/rez/packages/package_that_depends_on_something_in_row_2

It's useful for automation purposes and debugging. Though
``--display-as=names`` is definitely more readable.
