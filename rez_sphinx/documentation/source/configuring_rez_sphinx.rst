######################
Configuring rez_sphinx
######################

All :ref:`rez_sphinx` commands and flags have many ways to be changed for your needs.
There's two main ways to configure documentation:

- Globally, using :ref:`global configuration`
- Within an individual package, using :ref:`per-package configuration`

Which method you choose will depend on what your intended effect is and your
pipeline's constraints. This page serves as a guide to both explain every
:ref:`rez_sphinx` setting and also why you may want one approach, versus
another.

.. note::

    Every section below asssumes that you're defining these settings for
    **all** Rez packages. However, every section can be adapted to its
    "per-package" counterpart very easily.


.. _global configuration:

How To Configure All Rez Packages
*********************************

Rez allows configuration files to influence how it behaves. You can read about
that more at `Configuring Rez`_. :ref:`rez_sphinx` works the same way. It
simply places its settings under `optionvars`_, which is a dedicated
configuration space for "custom" settings.

Anything you set here will be applied to all Rez packages. It also applies
to those packages immediately. Care and caution should be taken when
rolling out any change using `optionvars`_.


.. _per-package configuration:

Per-Package Configuration
*************************

As mentioned in other sections, this page assumes that you're changing :ref:`rez_sphinx`
configuration settings at the "global" level, using `optionvars`_. But you can
also apply it on an individual Rez package, like so:

TODO : Make sure this tutorial works

- Define a new attribute called ``rez_sphinx`` in your `package.py`_
- Add your settings to this ``rez_sphinx`` variable like you normally would.


So if this is the "global" approach:

.. code-block:: python

    optionvars = {
        "rez_sphinx": {
            "sphinx-apidoc": {
                "allow_apidoc_templates": False,
            },
        }
    }


This is what the equivalent would look like, in a `package.py`_.

.. code-block:: python

    rez_sphinx = {
        "sphinx-apidoc": {
            "allow_apidoc_templates": False,
        },
    }

and that's it. All sections in this page can be converted this way.


.. _rez_sphinx.api_toctree_line:

api_toctree_line
****************

When API documentation is built during :ref:`rez_sphinx build run`, this
setting controls what get's added to your documentation's `toctree`_.

Default: ``"API Documentation <api/modules>"``

You can rename the previous to whatever you like but, for best results, leave
the ``<api/modules>`` part alone.

.. code-block:: python

   optionvars = {
       "rez_sphinx": {
           "api_toctree_line": "API Documentation <api/modules>",
       }
   }

TODO : Make unittest for this


.. _rez_sphinx.auto_help.filter_by:

auto_help.filter_by
*******************

Part of :ref:`rez_sphinx`'s features is that it can auto-generate your `package
help`_ automatically. If you have an existing `help`_ attribute already
defined, an auto-generated `help`_ may conflict with what already exists.

This preference controls which keys should be kept. Your original keys or the
auto-generated ones.

Default: ``"prefer_generated"``

Options:

- "none": Keep both your original and the auto-generated `help`_ keys.
- "prefer_generated": Replace original keys with the auto-generated keys.
- "prefer_original": Replace auto-generated keys with the original keys.


.. code-block:: python

    optionvars = {
        "rez_sphinx": {
            "auto_help": {
                "filter_by": "prefer_generated",
            },
        },
    }


.. _rez_sphinx.auto_help.sort_order:

auto_help.sort_order
********************

This setting is similar to :ref:`rez_sphinx.auto_help.filter_by`. However
:ref:`rez_sphinx.auto_help.filter_by` defines what :ref:`rez_sphinx` should do
when it encounters conflicting `help`_ keys. But for all other, non-conflicting
`help`_ keys, :ref:`rez_sphinx.auto_help.sort_order` is used instead.

Default: ``"alphabetical"``

Options:

- "alphabetical": Mix auto-generated and original `help`_ keys together, in ascending order.
- "prefer_generated": List the auto-generated `help`_ keys first, then originals.
- "prefer_original": List the original `help`_ keys first, then auto-generated.

.. code-block:: python

    optionvars = {
        "rez_sphinx": {
            "auto_help": {
                "sort_order": "alphabetical",
            },
        },
    }


.. _rez_sphinx.build_documentation_key:

build_documentation_key
***********************

Whenever you run :ref:`rez_sphinx init`, a new key is added to `rez tests
attribute`_, ``build_documentation``. As mentioned in many other documentation
pages, this key is used to find, build, and even publish documentation. It's a
very important part of how :ref:`rez_sphinx` works so a good name is important.

This setting allows you to change the name of the key, if you'd prefer to call
it something else.

Default: ``"build_documentation"``

.. code-block:: python

    optionvars = {
        "rez_sphinx": {
            "build_documentation": "build_documentation",
        }
    }

You can also specify **a list of possible keys**.

.. code-block:: python

    optionvars = {
        "rez_sphinx": {
            "build_documentation": ["build_documentation", "fallback_test_name"],
        }
    }

However if you do, you must keep in mind the following details:

TODO: Revisit this. Make sure we don't get from the current user environment

- The first key is always used whenever you call :ref:`rez_sphinx init` in a package.
- During :ref:`rez_sphinx build run` when the `intersphinx_mapping`_ is generated,
  the first key in the list defined in your `package.py`_ is used to query
  extra package "requires".

    - For more information on how this works, see :doc:`adding_extra_interlinking`.


.. _rez_sphinx.documentation_root:

documentation_root
******************

When you run :ref:`rez_sphinx init`, we need a preferred folder name where the
initial documentation files will be placed into. This setting controls the name
of that folder.

Default: ``"documentation"``

.. code-block:: python

    optionvars = {
        "rez_sphinx": {
            "documentation_root": "documentation",
        },
    }


.. important::

   Several other places in :ref:`rez_sphinx` use this folder name while
   querying things about your documentation. But in general, :ref:`rez_sphinx`
   tries to not assume what the documentation is called, when it can.


TODO: Add unittest


.. _rez_sphinx.extra_requires:

extra_requires
**************

If you want to use `sphinx-rtd-theme`_ to make your documentation pretty, In
order for Rez to "see" it, you would need to add it to every Rez resolve where
you build documentation.  In practical terms, it means updating all of your Rez
packages to include a ``sphinx_rtd_theme`` package in the test ``requires``.

.. code-block:: python

    tests = {
        "build_documentation": {
            "command": "rez_sphinx build run",
            "requires": ["rez_sphinx-1+<2", "sphinx_rtd_theme-1+<2"],
        }
    }

And you'd have to do that everywhere that you build documentation, potentially
hundreds of places. Imagine needing to modify the version range one day in the
future, how much effort that would take!

``extra_requires`` gives you a better alternative. Add those "common" package
requirements there and any resolve including the ``rez_sphinx`` package will
bring them along, automatically.

Default: ``[]``

.. code-block:: python

    optionvars = {
        "rez_sphinx": {
            "extra_requires": [],  # <-- Your extra packages here
        },
    }

If you want to learn more how to use this to customize Sphinx themes, for
example, see :doc:`using_sphinx_rtd_theme` for details.


.. _rez_sphinx.init_options.check_default_files:

init_options.check_default_files
********************************

TODO


.. _rez_sphinx.init_options.default_files:

.. _default file entries:

init_options.default_files
**************************

By default, `sphinx-quickstart`_ adds a `index.rst`_ when your project is first
generated. :ref:`rez_sphinx` does a little extra and adds a
``user_documentation.rst`` and ``developer_documentation.rst`` file.

This is for 2 reasons:

- To give people a good starting ground for documenting their work.
- To have something to check for, during :ref:`rez_sphinx build run`.

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


.. _rez_sphinx.intersphinx_settings.package_link_map:

intersphinx_settings.package_link_map
*************************************

If you're trying to link your Rez package to another Rez package, but that
package cannot be editted (it could be a third-party PyPI package or
something), you can use this option to help :ref:`rez_sphinx build run` find
the documentation for that package.

.. code-block:: python

   optionvars = {
       "rez_sphinx": {
           "intersphinx_settings": {
               "package_link_map": {
                   "schema": "https://schema.readthedocs.io/en/latest",
               }
           }
       }
   }

The value, ``"https://schema.readthedocs.io/en/latest"``, must be the root
documentation which contains a `objects.inv`_ file. When building your
documentation, if a Rez package named ``schema`` is found but its `package.py`_
doesn't define the documentation properly,
``https://schema.readthedocs.io/en/latest`` is used as a fallback.


.. _rez_sphinx.sphinx-apidoc.allow_apidoc_templates:

sphinx-apidoc.allow_apidoc_templates
************************************

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
Sphinx 2.2+. Adding this setting in Python 2 does nothing.


.. _rez_sphinx.sphinx-apidoc.arguments:

sphinx-apidoc.arguments
***********************

TODO


.. _rez_sphinx.sphinx-apidoc.arguments:

sphinx-apidoc.arguments
***********************

TODO


.. _rez_sphinx.sphinx-apidoc.enable_apidoc:

sphinx-apidoc.enable_apidoc
***************************

TODO


.. _rez_sphinx.sphinx-quickstart:

.. _sphinx-quickstart customization:

sphinx-quickstart
*****************

TODO Add


.. _rez_sphinx.sphinx_conf_overrides:

sphinx_conf_overrides
*********************

This setting allows you to change in a `Sphinx conf.py`_. See `conf.py
customization` for a full list of the supported variables and what each of them do.

.. code-block:: python

    optionvars = {
        "rez_sphinx": {
            "sphinx_conf_overrides": {
                "add_module_names": True,  # Use full names in API documentation
            }
        }
    }


.. _rez_sphinx.sphinx_conf_overrides.add_module_names:

sphinx_conf_overrides.add_module_names
**************************************

TODO


.. _rez_sphinx.sphinx_conf_overrides.master_doc:

sphinx_conf_overrides.master_doc
********************************

TODO


.. _rez_sphinx.sphinx_extensions:

sphinx_extensions
*****************

TODO
