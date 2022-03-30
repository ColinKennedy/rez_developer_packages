.. _rez_sphinx view:

###############
rez_sphinx view
###############

This command shows you "resolved" data. Unlike :ref:`rez_sphinx config show`,
which only reports configuration / fallback values, the commands in
``rez_sphinx view`` are **exactly** what your Rez package sees and uses while
any of the :ref:`rez_sphinx commands` are running.


.. _rez_sphinx view publish-url:

rez_sphinx view publish-url
***************************

This command can be used to check where your Rez package's documentation will
point to after it is built, using `rez-build`_.

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

and then you call ``rez_sphinx view publish-url``, the command will output

``https://SomeUserOrOrganization.github.io/your_package_name_here``.

TODO add unittest ensuring the command works + that it gives resolved URLs back.

This command is mostly just for debugging to make sure your package publishes
to where you expect.


.. _rez_sphinx view sphinx-conf:

rez_sphinx view sphinx-conf
***************************

Query any attribute in your `Sphinx conf.py`_ using this command.

Since :ref:`rez_sphinx build run` tends to alter your `Sphinx conf.py`_, it's
sometimes unclear your configuration is working the way you expect. This
``rez_sphinx view sphinx-conf`` debug command tells you for certain what
`Sphinx`_ sees before building.


.. _rez_sphinx view sphinx-conf intersphinx_mapping:

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
