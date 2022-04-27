.. _rez_sphinx init:

###############
rez_sphinx init
###############

``rez_sphinx init`` is starting point of any :ref:`rez_sphinx` documentation.
It's ran once (and then ideally never again).

``rez_sphinx init`` does the following:

- Creates a source / build folder for the documentation
- Runs `sphinx-quickstart`_ with automated settings

    - See :ref:`sphinx-quickstart customization` to customize this

- Creates any pre-defined :ref:`default file entries` and adds them to `index.rst`_.
- Hijacks your `Sphinx conf.py`_ with a special :ref:`rez_sphinx bootstrap`
- Directly edits your `package.py`_ as needed

    - Increments a new minor version
    - Defines "build_documentation" key to the `rez tests attribute`_ attribute.

.. code-block::

    tests = {
        "build_documentation": {
            "command": "rez_sphinx build run",
            "requires": ["rez_sphinx-1"],
        },
    }


And that's all :ref:`rez_sphinx` does for now. If you rebuild your Rez package,
should be able to run ``rez-test package_name build_documentation`` to create
.html files from the .rst you just generated.


************************************
The build_documentation rez-test key
************************************

TODO : Possibly add "run_on": "post_release" here. Or just make sure it works.
Or "explicit", at least

A typical key looks like:

.. code-block:: python

   tests = {
       # ... more tests ...
       "build_documentation": {
           "command": "rez_sphinx build run",
           "requires": ["rez_sphinx-1+<2"],
       },
   }

It's the entry point for ``rez_sphinx`` to do its work.

If you want to rename the default key from "build_documentation" to something
else, see :ref:`rez_sphinx.build_documentation_key`.


*******************************
sphinx-quickstart customization
*******************************

You may want to override or influence the creation of your package's
documentation.  To do that, you can pass ``init
--quickstart-arguments="--ext-coverage"``, for example, to forcibly pass
``--ext-coverage`` to the `sphinx-quickstart`_ command.

If you find yourself passing the same arguments to `sphinx-quickstart`_, you
can add those settings to :ref:`sphinx-quickstart customization` so they're
added automatically.


*************
Parting Notes
*************

``rez_sphinx init`` sets up your docmentation but to build the documentation,
see :doc:`build_command`.
