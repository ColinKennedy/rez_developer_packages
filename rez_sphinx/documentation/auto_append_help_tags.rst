.. _auto_append_help_tags:

##################################
Adding Documentation Automatically
##################################

By default when you :ref:`rez_sphinx init`, the :ref:`default file entries`,
``user_documentation`` and ``developer_documentation``, are created and later
get added to your `package.py`_ `help`_ attribute.  This means those files will
be visible whenever you call `rez-help`_ from the terminal.

You can add other files to the `help`_ during `rez-build`_ using these two options:

- :ref:`automated auto help appending`
- Define the paths to the files manually.

.. important::

    Appending to your package `help`_ isn't enabled by default. See
    :doc:`enabling_rez_help_integration` to learn how to add it!


.. _rez_sphinx_help:

.. _automated auto help appending:

************************************************
Let :ref:`rez_sphinx` write to ``help``, for you
************************************************

Simply add this snippet into any of your ``.rst`` files:

::

    ..
        rez_sphinx_help:Optional Label


Including "rez_sphinx_help:Optional Label" adds this to your `help`_ attribute
on-build:

.. code-block:: python

   help = [
       ["Existing documentation", "README.md"],
       ["Optional Label", "{root}/file_path.html"],
   ]

And later the ``{root}/`` gets replaced either with nothing, and the path stays
relative or it is replaced by an external website URL.

.. important::

    External website support is disabled by default and must be configured.
    See :doc:`enable_external_website_publishing`.


***********
Label Logic
***********

The ``"Optional Label"`` portion of ``["Optional Label", "{root}/file_path.html"]``
is determined using the following rules:

- If any text after the ":" in ``rez_sphinx_help:Foo``, if it exists
- If no ":" + label, re-use the current file's header text
- If no found header (which by the way is a Sphinx error), use the file's name, instead.


Write the .html, yourself
=========================

You can always write the path to .html by-hand.

.. code-block:: python

   help = [
       ["Existing documentation", "README.md"],
       ["Hand Written Entry Here", "{root}/file_path.html"],
   ]

.. note::

    If you have a .rst file located at
    ``{rez_package_root}/documentation/file_path.rst``, then you'd want to
    write ``"{root}/file_path.html"`` here.

When the `help`_ substitution occurs, the ``{root}/`` is replaced like normal.

This isn't super recommended though because what if you move, rename or delete
your ``file_path.rst`` file later? The next time documentation builds, ``Hand
Written Entry Here`` will point to an invalid path. It's better to use the
automated :ref:`automated auto help appending` method, instead.
