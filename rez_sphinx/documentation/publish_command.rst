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

######################
rez_sphinx publish run
######################

This builds and publishes your current package's documentation. The default
behavior of :ref:`rez_docbot` is to only build documentation for each major /
minor release so just because you run this command doesn't guarantee that
documentation will be built for it, unless you add the
``--force-version-publish`` flag.

TODO : add ``--force-version-publish``
