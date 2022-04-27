.. _rez_sphinx publish:

##################
rez_sphinx publish
##################

The main command which takes your local documentation and copies it to a
network / the Internet.

There's a couple interesting things to note about this command:

- Most users will never need to run this command. Publishing is done
  automatically for the user, as long as :doc:`rez_sphinx is set up as a
  release hook <rez_sphinx_as_a_release_hook>`. It's only if you want to force
  publish that you'd ever really use this command from the terminal.
- This command is enabled only if you add
  ``.rez_sphinx.feature.docbot_plugin==1`` to your Rez environment. It'll error
  early if it's missing.


.. _rez_sphinx publish run:

**********************
rez_sphinx publish run
**********************

This builds and publishes your current package's documentation. Most of the
actual behavior is determined by :ref:`rez_docbot` so definitely head to that
documentation page for specifics. But let's summarize the workflow.

.. important::

   If you have the :ref:`rez_sphinx release hook
   <rez_sphinx_as_a_release_hook>` set up, you should never need to run this
   command.

When :ref:`rez_sphinx publish run` is called...

- your documentation is built from scratch
- all configured repositories are cloned locally
- If your documentation is the latest major / minor version, the cloned
  repository's "latest" folder is replaced with your build documentation.
- If you have versioned documentation enabled (which is the default), a
  "versions/{package.version.major}.{package.version.minor}" folder is made for you.

    - If the folder already exists and you're publishing a patch, the folder is
      overwritten.
