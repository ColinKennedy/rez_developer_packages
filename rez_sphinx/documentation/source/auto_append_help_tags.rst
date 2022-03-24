.. _rez_sphinx tag:

#####################
Auto-Append Help Tags
#####################

TODO : Make sure all of this works as expected. Also talk about how rez_docbot
factors into it.

:ref:`rez_sphinx` is capable of connecting to `rez-help`_ out of box.  By
default, the :ref:`default file entries`, ``user_documentation`` and
``developer_documentation`` are added to your package.py `help`_ attribute each
time the Rez package is built.

You can also tell :ref:`rez_sphinx build run` to include other files by adding
this snippet into any .rst file:

::

    ..
        rez_sphinx_help:Optional Label


Including "rez_sphinx_help:Optional Label" adds this to your `help`_ attribute
on-build:

.. code-block:: python

   help = [
       ["Existing documentation", "README.md"],
       ["Optional Label", "{root}/path/to/your/file.rst"],
   ]

If you just use "rez_sphinx_help" and omit the text after ":", the top-level
header of that file is used as a label, instead.

Though this behavior is available out of box as mentioned, it isn't enabled by
default. It's easy to add though. See :ref:`rez_sphinx auto-help`.


.. _rez_sphinx auto-help:

Enabling auto-help
******************

TODO Make sure this works - in general but also outside of a rez_sphinx environment.

Add this to your global `rezconfig.py`_.


TODO : Clean up these files paths. Make sure they work well.

.. code-block:: python


    package_definition_build_python_paths = ["/path/to/built/rez_sphinx/python"]
    package_preprocess_function = ["api.package_preprocess_function"]

If you don't want to specify a raw file path in the global `rezconfig.py`_, I
don't blame you.  There's also the option of importing the function and using
it directly in the `rezconfig.py`_.

.. code-block:: python

    from rez_sphinx.api import package_preprocess_function

But this requires :ref:`rez_sphinx` to be included in your PYTHONPATH, which
for many, this is easier said than done.

.. seealso::

    `package_preprocess_function`_

TODO : Probably need to also talk about local builds
