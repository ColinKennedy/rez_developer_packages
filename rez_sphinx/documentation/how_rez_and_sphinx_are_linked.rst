#############################
How Rez And Sphinx Are Linked
#############################

When you call :ref:`rez_sphinx init` for the first time, as mentioned in the
:doc:`init_command`, several changes happen behind the scenes.

One of the changes, the most important change, happens in the generated
`Sphinx conf.py`_ file.


.. _rez_sphinx bootstrap:

The Bootstrap Line
******************

In the generated `Sphinx conf.py`_ file, these lines are added:

.. code-block:: python

    from rez_sphinx import api
    locals().update(api.bootstrap(locals()))

It's a bit magical looking but it's actually simple. ``locals()`` is a built-in
Python variable containing all variables that you can query or modify at any
given time in a Python file. It's a standard Python ``dict``. `Sphinx conf.py`_
is Sphinx's main customization file for your documentation.

What this line is really saying:

"override any or all variables with the output of
:func:`.bootstrap.bootstrap`". The bootstrap also takes into consideration any
existing values, which is why ``locals()`` is passed to ``api.bootstrap(locals())``.

:func:`.bootstrap.bootstrap` doesn't change every variable. By default it...:

- extends `extensions`_ with things :ref:`rez_sphinx` needs.
- sets `intersphinx_mapping`_, a variable for `sphinx.ext.intersphinx`_.

    - This extension is what allows your documentation to communicate with
      **other** Rez package's documentation.

- sets these vanilla `Sphinx`_ variables based on what's in your `package.py`_:

    - `author`_
    - `copyright`_
    - `master_doc`_
    - `project_copyright`_
    - `project`_
    - `release`_
    - `version`_

While this is fairly aggressive, please note that:

- Anything you add after ``locals().update(api.bootstrap(locals()))`` will
  overwrite whatever has just been set.
- Anything you add beforehand will be taken into consideration during
  :func:`.bootstrap.bootstrap`.
- If you absolutely don't want :ref:`rez_sphinx` messing with a particular
  variable, you can add ``skip={"project", }``, for example, to skip the setting
  of the project name.


Adding Extra Overrides
**********************

If you find yourself adding the same overrides to your `Sphinx conf.py`_,
consider adding it as a configuration value using
:ref:`rez_sphinx.sphinx_conf_overrides`.
