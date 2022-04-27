############################
rez_sphinx As A Release Hook
############################

When releasing packages, it's possible to auto build and publish documentation.
To do this, :ref:`rez_sphinx` recruits the help of a plug-in,
:ref:`rez_docbot`.

If you'd like to add publishing on-release, the basic steps are as follows:

- Install :ref:`<rez_docbot> rez_docbot:installation` and follow its steps
- Set up a basic publisher configuration. We'll show a simple one below:

.. code-block:: python

    optionvars = {
        "rez_docbot": {
            "publishers": [
                {
                    "authentication": {
                        "user": "YourUserName",
                        "token": "some_access_token",
                        "type": "github",
                    },
                    "branch": "gh-pages",
                    "repository_uri": "git@github.com:YourUserName/{package.name}",
                    "view_url": "https://YourUserName.github.io/{package.name}",
                },
            ],
        },
    }

The above configuration assumes that you're publishing to GitHub and already
you have a username and password for GitHub. Make sure to edit
``"authentication"``, ``"repository_uri"``, and ``"view_url"`` with your
details.

For more details on other available ``rez_docbot`` configurations, check out:
:ref:`rez_docbot:other configuration options`.

- To confirm everything is set up correctly so far, run this command:

.. code-block:: sh

    rez-sphinx view view-url

It should print back ``"https://YourUserName.github.io/your_package_name"``.
Note that ``{package.name}`` would be replaced with your current Rez package name.

.. seealso::

    :ref:`rez_sphinx view view-url`

- Now confirm the returned output of :ref:`rez_sphinx view repository-uri`

If you have a GitHub user set up and both URLs / URIs point to their expected
locations, you're ready to enable the release hook.


.. _rez_sphinx release hook:

***********************
rez_sphinx release hook
***********************

The steps for adding the release hook is much easier than the previous steps.
To do it, you must:

- rez-release / rez-build :ref:`rez_sphinx`
- Append to your `plugin_path`_ and `release_hooks`_ in your `rezconfig`_.

TODO : Confirm that this path works

.. code-block:: python

    # rezconfig.py

    plugin_path = ["/path/to/rez_sphinx/1.0.0/python-3/python/rez_sphinx_plugins"]
    release_hooks = ["publish_documentation"]

And you're done. Any Rez source package which you've ran :ref:`rez_sphinx init`
on will auto-release and auto-link as expected, whenever you call
`rez-release`_.
