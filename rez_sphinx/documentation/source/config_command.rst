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


Configuration Options
*********************

So as you can see, ``rez_sphinx config`` queries your active configuration and
default values. But you may be wondering "how do I customize rez_sphinx,
myself"? Head over to :doc:`configuring_rez_sphinx` to learn more.
