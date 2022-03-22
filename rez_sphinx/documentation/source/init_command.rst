.. _rez_sphinx init:

###############
rez_sphinx init
###############

``rez_sphinx init`` is starting point of any :ref:`rez_sphinx` documentation.
It's ran once (and then ideally never again).

``rez_sphinx init`` does the following:

- Creates a source / build folder for the documentation
- Runs ``sphinx-quickstart`` with automated settings
    - See :ref:`sphinx-quickstart customization` to customize this
- Creates any pre-defined :ref:`default file entries` and adds them to `index.rst`_.
- Hijacks your `conf.py`_ with a special :ref:`rez_sphinx bootstrap`
- Directly edits your `package.py`_ as needed
    - Increments a new minor version
    - Defines "build_command" key to the `rez tests attribute`_ attribute.

And that's all :ref:`rez_sphinx` does for now. If you rebuild your Rez package,
should be able to run ``rez-test build_documentation`` to create .html files
from the .rst you just generated.


sphinx-quickstart customization
*******************************

You may want to override or influence the creation of your package's
documentation.  To do that, you can pass ``init
--quickstart-arguments="--ext-coverage"``, for example, to forcibly pass
``--ext-coverage`` to the ``sphinx-quickstart`` command.

If you find yourself passing the same arguments to ``sphinx-quickstart``, you
can add those settings to :ref:`sphinx-quickstart customization` so they're
added automatically.


Parting Notes
*************

``rez_sphinx init`` sets up your docmentation but to build the documentation,
see :doc:`build_command`.
