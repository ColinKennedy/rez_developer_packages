##############
GitHub Details
##############

Because of how GitHub documentation works, publishing for GitHub has some
common "idioms" which we'll describe in this page.


*****************
Branch publishing
*****************

GitHub documentation is meant to be published to a "gh-pages" branch. To
specify that on a configuration, just include ``"branch": "gh-pages"`` in the
publisher, like so:

.. code-block:: python

    optionvars = {
        "rez_docbot": {
            "publishers": [
                {
                    # ... more settings ...
                    "branch": "gh-pages",
                    "publisher": "github",
                    # ... more settings ...
                },
            ],
        },
    }


.. _GitHub access tokens:

********************
GitHub Access Tokens
********************

To be able to query, push, and publish documentation, rez_docbot needs an
access token which at least contains these permissions:

- repo

    - [x] public_repo

.. image: images/github_access_example_settings.png

As long as you give an access token with that enabled, publishing in rez_docbot
is possible for public git repositories.

To add a personal access token like the one shown above for your org / user, go here:

#. In the upper-right corner of any page, click your profile photo, then click Settings.
#. In the left sidebar, click Developer settings.
#. In the left sidebar, click Personal access tokens.
#. Click Generate new token.

These steps were copied from GitHub's `Personal access token tutorial
<https://docs.github.com/en/enterprise-server@3.4/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token>`_.

Once you've created your Personal access token and set permissions like shown
above, you're ready to use this token for ``rez_docbot``. Check out
:doc:`authenticating` to learn more.
