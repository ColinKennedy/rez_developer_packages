Adding Documentation Automatically
**********************************

TODO : Double-check the wording of this page. It should make sense on its own
but link to :doc:`enabling_rez_help_integration`

By default, the :ref:`default file entries`, ``user_documentation`` and
``developer_documentation`` are added to your package.py `help`_ attribute.
This means those files will be visible whenever you call `rez-help`_ from the
terminal.

If you want to add other files to the `help`_ during `rez-build`_,

you've got two options:

- Let :ref:`rez_sphinx` add your files for you
- Define the paths to the files manually.


.. _automated_auto_help_appending:

Let :ref:`rez_sphinx` write to ``help``, for you
================================================

Simply add this snippet into any of your .rst files:

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

And later the {root} gets replaced by your publisher documentation URL, using
``view_url``.

The found "Optional Label" logic goes like this:

- If there's a label defined after like ``rez_sphinx_help:Foo``, use it
- If not, get the current file's header text
- If no found header, use the file's name, instead.


Write the .html, yourself
=========================

You can always write the path to the .html that your .rst files generates by-hand.

.. code-block:: python

   help = [
       ["Existing documentation", "README.md"],
       ["Hand Written Entry Here", "{root}/file_path.html"],
   ]

If you have a .rst file located at ``{rez_package_root}/documentation/file_path.rst``,
then you'd want to write ``"{root}/file_path.html"``.

This isn't super recommended though because what if you move, rename or delete
your file_path.rst file later? Then the next time documentation builds, ``Hand
Written Entry Here`` will point to nothing. It's better to use the automated
:ref:`automated_auto_help_appending` method, instead.
