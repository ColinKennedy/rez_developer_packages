.. _rez_sphinx view:

###############
rez_sphinx view
###############

This command shows you "resolved" data. Unlike :ref:`rez_sphinx config show`,
which only reports configuration / fallback values, the commands in
``rez_sphinx view`` are **exactly** what your Rez package sees and uses while
any of the :ref:`rez_sphinx commands` are running.


.. _rez_sphinx view package-help:

****************************
rez_sphinx view package-help
****************************

When you enable :doc:`auto_append_help_tags`, :ref:`rez_sphinx` starts to
influence your Rez package's `help`_ attribute on-build / on-release.

The ``rez_sphinx view package-help`` command lets you see what modifications
:ref:`rez_sphinx` would make to the `help`_ without having to explicitly build
/ release.


.. note::

    you want to customize the output paths / order / etc of `help`_, there's a
    number of options such as :ref:`rez_sphinx.auto_help.filter_by` and
    :ref:`rez_sphinx.auto_help.sort_order`.


.. _rez_sphinx view repository-uri:

******************************
rez_sphinx view repository-uri
******************************

This command shows every remote destination, if any, your package will push
its documentation to whenever :ref:`rez_sphinx publish run` is called.

If you have auto-publishing enabled, via :doc:`the rez_sphinx release_hook
plugin <rez_sphinx_as_a_release_hook>`, this list also shows where documentation
is pushed to during `rez-release`_.


.. code-block:: python

    optionvars = {
        "rez_docbot": {
            "publishers": [
                {
                    # ... more stuff here ...
                    "repository_uri": "git@github.com:SomeUserOrOrganization/{package.name}",
                },
            ],
        }
    }

and then you call ``rez_sphinx view repository-uri``, the command will output

``URI: "git@github.com:SomeUserOrOrganization/your_package_name_here" / Required: "True / False"``.

The default behavior of publishing is to assume any found URI is required but
not every URI is. Beside each URI is an indicator whether publishing will fail
or just warn if documentation fails to publish.

This command is mostly just for debugging to make sure your package publishes
to where you expect.


.. _rez_sphinx view view-url:

************************
rez_sphinx view view-url
************************

This command can be used to check where your Rez package's documentation will
point to after it is built.

For example if you have a configuration like this:

.. code-block:: python

    optionvars = {
        "rez_docbot": {
            "publishers": [
                {
                    # ... more stuff here ...
                    "repository_uri": "git@github.com:SomeUserOrOrganization/{package.name}",
                    "view_url": "https://SomeUserOrOrganization.github.io/{package.name}",
                },
            ],
        }
    }

and then you call ``rez_sphinx view view-url``, the command will output

``https://SomeUserOrOrganization.github.io/your_package_name_here``.

This command is mostly just for debugging to make sure your package publishes
to where you expect.


.. _rez_sphinx view sphinx-conf:

***************************
rez_sphinx view sphinx-conf
***************************

Query any attribute in your `Sphinx conf.py`_ using this command.

Since :ref:`rez_sphinx build run` tends to alter your `Sphinx conf.py`_, it's
sometimes unclear your configuration is working the way you expect. This
``rez_sphinx view sphinx-conf`` debug command tells you for certain what
`Sphinx`_ sees before building.


.. _rez_sphinx view sphinx-conf intersphinx_mapping:

***********************************************
rez_sphinx view sphinx-conf intersphinx_mapping
***********************************************

``rez_sphinx view sphinx-conf intersphinx_mapping`` is a common debug command to
run while setting up a Rez package with documentation for the first time.

The returned :class:`dict` tells you exactly what found Rez dependency packages
were found, if any, and what URls they point to. If you don't see a package
that you expected, it may be because

1. The package doesn't declare its documentation URL(s)

    - The package may need to be built after :doc:`auto_append_help_tags` is set up.
    - If the package is third-party, consider using
      :ref:`rez_sphinx.intersphinx_settings.package_link_map`, instead.

2. Your don't have the dependency listed in your Package `requires`_.

    - See :doc:`adding_extra_interlinking` to walk through that process.
