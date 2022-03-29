.. _rez_sphinx config:

#################
rez_sphinx config
#################

The command used to interact with :ref:`rez_sphinx's <rez_sphinx>` many
configuration options.  The ``config`` does nothing by itself but houses
several sub-commands. See below for details.


.. _rez_sphinx config check:

rez_sphinx config check
***********************

A simple command which reads your currently-applied configuration settings. If
everything is valid, the function returns. But if there's unexpected keys or
values, those details are shown in the terminal.


.. _rez_sphinx config list-overrides:

rez_sphinx config list-overrides
********************************

This commands shows all :ref:`rez_sphinx` configuration settings. The default
command, ``rez_sphinx config list-overrides`` shows all overrides + default
settings at once.  If you want to see just the overrides and nothing else,
choose ``rez_sphinx config list-overrides --sparse``.

There's also a ``--format`` option, for outputting to `yaml`_.


.. _rez_sphinx config list-defaults:

rez_sphinx config list-defaults
*******************************

Unlike :ref:`rez_sphinx config list-overrides`, which includes user-defined
overrides, this command only considers the settings which :ref:`rez_sphinx`
provides by default and ignores any user settings. This command good as
reference or for setting up your own set of overrides.

As usual, ``--sparse`` and ``--format`` customize the output + display.

TODO add this :ref:`rez_sphinx config show`.
:ref:`rez_sphinx config show --list-all`.


.. _rez_sphinx config show:

rez_sphinx config show
**********************

``rez_sphinx config show`` is the main command to query configuration values
for :ref:`rez_sphinx`.  Don't confuse this command with
:ref:`rez_sphinx view sphinx-conf` because they do different things.

- :ref:`rez_sphinx config show`: Get all :ref:`rez_sphinx` settings.

    - See :doc:`configuring_rez_sphinx` for example values

- :ref:`rez_sphinx view sphinx-conf`

    - Queries your `Sphinx conf.py`_ for resolved values.

:ref:`rez_sphinx config show` returns values that, often times, are only
suggested fallbacks. They aren't guaranteed to make it into your documentation
settings. :ref:`rez_sphinx view sphinx-conf` however is what `Sphinx`_ actually
sees when it's building your packages's documentation and should be preferred
for debugging a specific package.


.. _rez_sphinx config show --list-all:

rez_sphinx config show --list-all
*********************************

This command shows every setting which :ref:`rez_sphinx` supports. "." note
nested dictionaries. For example, ``auto_help.filter_by`` would be written in a
configuration as:

.. code-block:: python

    optionvars = {
        "rez_sphinx": {
            "auto_help": {
                "filter_by": "prefer_generated",
            },
        },
    }

Each printed preference path from this command has an effect on
:ref:`rez_sphinx`. See :doc:`configuring_rez_sphinx` to learn about those
preference path options.


.. _rez_sphinx config show build_documentation_key:

rez_sphinx config show build_documentation_key
==============================================

This important command returns a `rez-test`_ string label. By default,
"build_documentation". This label, which may seem simple and unimportant, is
the glue that most of :ref:`rez_sphinx` relies on for its automated processes.

Don't change this configuration value unless you know what you're doing. And if
you must, change it at the :ref:`global configuration` level, affecting all
packages. Do not set this at the :ref:`per-package configuration` level.


Configuration Options
*********************

So as you can see, ``rez_sphinx config`` queries your active configuration and
default values. But you may be wondering "how do I customize rez_sphinx,
myself"? Head over to :doc:`configuring_rez_sphinx` to learn more.
