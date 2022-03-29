######################
Configuring rez_sphinx
######################

All :ref:`rez_sphinx` commands and flags have many ways to be changed for your
needs.

.. important::

   Every setting here can be queried at any time using the :ref:`rez_sphinx
   config show --list-all` command.

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
        },
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
       },
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
        },
    }

You can also specify **a list of possible keys**.

.. code-block:: python

    optionvars = {
        "rez_sphinx": {
            "build_documentation": ["build_documentation", "fallback_test_name"],
        },
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
        },
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

In general, :ref:`rez_sphinx` tries to get out of the user's way and make
documentation as fast as possible.  The one exception to that is a pre-build
check during :ref:`rez_sphinx build run`.

If you have default files defined
(:ref:`rez_sphinx.init_options.default_files`), it's expected that you either
add handmade documentation to those files or delete the files completely.

If you don't, :ref:`rez_sphinx build run` fails to run.

This check may rub some users the wrong way but the intent is to ensure people
are using :ref:`rez_sphinx` to write quality documentation and checking their
work.  As very often, poor documentation is be worse than no documentation.

That said, if you really don't like this check, it can be disabled.

Default: ``True``

.. code-block:: python

    optionvars = {
        "rez_sphinx": {
            "init_options.check_default_files": True,
        },
    }

The other option for disabling the pre-build check is to remove all default
files. You can do that, using :ref:`rez_sphinx.init_options.default_files`.


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

Raw terminal arguments you can pass directly to `sphinx-apidoc`_. These
arguments get referenced and called during :ref:`rez_sphinx build run`, just
before `sphinx-build`_ gets called.

A common value for this is ``["--private"]``, if you want to also create API
documentation for "private" Python modules. See `sphinx-apidoc --private`_ for
details about that.

Default: ``[]``

.. code-block:: python

    optionvars = {
        "rez_sphinx": {
            "sphinx-apidoc": {
                "arguments": [],
            },
        },
    }

TODO Add unittest


.. _rez_sphinx.sphinx-apidoc.enable_apidoc:

sphinx-apidoc.enable_apidoc
***************************

Just before documentation is built, :ref:`rez_sphinx build run` generates API
documentation .rst files based on the Python files for your package that it
could find.

If you don't want these .rst files to be generated (for example, you're writing
a Rez package of just hand-written documentation and doesn't contain Python
files), you can disable this option.

Default: ``True``

.. code-block:: python

    optionvars = {
        "rez_sphinx": {
            "sphinx-apidoc": {
                "enable_apidoc": True,
            },
        },
    }


.. _rez_sphinx.sphinx-quickstart:

.. _sphinx-quickstart customization:

sphinx-quickstart
*****************

TODO: Make this consistent with other options

Like :ref:`rez_sphinx.sphinx-apidoc.arguments`, which allows you to pass
arguments directly to `sphinx-apidoc`_, this setting customizes the arguments
passed to ``sphinx-quickstart``.

An example for this would be to enable the `sphinx.ext.coverage`_ extension,
using ``["--ext-coverage"]``.

.. code-block:: python

    optionvars = {
        "rez_sphinx": {
            "sphinx-quickstart": ["--ext-coverage"],
        },
    }

TODO Add unittest


.. _rez_sphinx.sphinx_conf_overrides:

sphinx_conf_overrides
*********************

This setting allows you to change in a `Sphinx conf.py`_. See `conf.py
customization` for a full list of the supported variables and what each of them do.

.. code-block:: python

    optionvars = {
        "rez_sphinx": {
            "sphinx_conf_overrides": {
                "add_module_names": False,  # Use short names in API documentation
            }
        }
    }


.. _rez_sphinx.sphinx_conf_overrides.add_module_names:

sphinx_conf_overrides.add_module_names
**************************************

When you document with `Sphinx`_ it prefers to render API function names with
the full namespace, like this:

``some_package_root.inner_folder.another_folder.core.you.get.the.point.my_function``

Versus just:

``my_function``

This option is controlled with `add_module_names`_, which you can set directly
on your `Sphinx conf.py`_.

However in the interest of making documentation pretty by default,
:ref:`rez_sphinx build run` sets this to ``False`` by default.

If you don't like this decision, use this setting to revert it:

.. code-block:: python

    optionvars = {
        "rez_sphinx": {
            "sphinx_conf_overrides": {
                "add_module_names": False,  # Set this to True to get old behavior back
            }
        }
    }


.. _rez_sphinx.sphinx_conf_overrides.master_doc:

sphinx_conf_overrides.master_doc
********************************

When you open documentation in `Sphinx`_, one .rst file must serve as the
"starting point" that all other documentation is based on. In web terms, you
might call this the "landing page".

While well intentioned, this setting causes problems when `Sphinx`_ and its
extensions `disagree on what the master_doc name should be called
<https://github.com/readthedocs/readthedocs.org/issues/2569>`_. To make
:ref:`rez_sphinx` more bullet-proof, the name is set for you by default so you
don't get burned by this issue by accident later.


Default: ``"index"``

.. code-block:: python

    optionvars = {
        "rez_sphinx": {
            "sphinx_conf_overrides": {
                "master_doc": "index",
            }
        }
    }


.. _rez_sphinx.sphinx_extensions:

sphinx_extensions
*****************

TODO move this to sphinx_conf_overrides and make sure there's unittests for it.
