######################
Configuring rez_sphinx
######################

TODO Add


.. _rez_sphinx.build_documentation_key:

rez_sphinx.build_documentation_key
**********************************


.. _sphinx-quickstart customization:

rez_sphinx.sphinx-quickstart
****************************

TODO Add


.. _default file entries:

rez_sphinx.init_options.default_files
*************************************

By default, `sphinx-quickstart`_ adds a `index.rst`_ when your project is first
generated. :ref:`rez_sphinx` does a little extra and adds a
``user_documentation.rst`` and ``developer_documentation.rst`` file.

This is for 2 reasons:

- To give people a good starting ground for documenting their work.
- To have something to check for, during :ref:`rez_sphinx build`.

If the files are their default state, the build stops early unless
:ref:`rez_sphinx.init_options.check_default_files` is set to False.  It's a
small reminder to the user to not blindly make documentation but give it some
meaning too.

Changing both file contents will make the check pass. Deleting either or both
files also make the checks pass. If you like the feature but prefer to have
different default files, you can define them like so:

.. code-block:: python

    optionvars = {
        "rez_sphinx": {
            "init_options": {
                "default_files": [
                    {
                        "base_text": "Some default text",
                        "path": "inner_folder/developer_documentation",
                        "title": "Developer Documentation",
                    },
                    {
                        "base_text": "Another default file",
                        "path": "user_documentation",
                        "title": "User Documentation",
                    },
                ],
            }
        }
    }

If you want no files to be generated, define an empty list:


.. code-block:: python

    optionvars = {"rez_sphinx": {"init_options": {"default_files": []}}}


If you like the files but don't want the validation check, see
:ref:`rez_sphinx.init_options.check_default_files`.


.. _rez_sphinx.init_options.check_default_files:

rez_sphinx.init_options.check_default_files
*******************************************

TODO add stuff here


.. _rez_sphinx.sphinx-apidoc.allow_apidoc_templates:

rez_sphinx.sphinx-apidoc.allow_apidoc_templates
***********************************************

This is already covered in :ref:`rez_sphinx apidoc templates` but basically, in
Python 3+, there's an option to make the Sphinx's `toctree`_ look much cleaner.
If you prefer the default display, use this option to get it back:

.. code-block:: python


    optionvars = {
        "rez_sphinx": {
            "sphinx-apidoc": {
                "allow_apidoc_templates": False,
            },
        }
    }

As mentioned, `sphinx-apidoc`_ templates are a Python 3+ feature. Specifically
Sphinx 2.2+. Adding this setting in < Python 2 does nothing.


.. _rez_sphinx.sphinx_conf_overrides:

rez_sphinx.sphinx_conf_overrides
********************************

This setting allows you to change in a `conf.py`_. See `conf.py customization`
for a full list of the supported variables and what each of them do.

.. code-block:: python

    optionvars = {
        "rez_sphinx": {
            "sphinx_conf_overrides": {
                "add_module_names": True,  # Use full names in API documentation
            }
        }
    }
