######################
Publishing Per Version
######################

By default, :ref:`rez_docbot` assumes that you want to publish new
documentation for each ``{version.major}.{version.minor}``. This means that
patches will simply overwrite an existing minor's documentation, instead of
creating completely new documentation per-version.

While this generates less duplicate documentation over time, some users may
want 1-to-1 parity between every version and documentation. Or they may be
authoring a project which doesn't use `SemVer`_.

.. important::

   This feature is only available for the publishers which support it.
   rez_docbot's default publishers all support it. See :doc:`publisher_types`
   to confirm that the publisher that you plan to use supports it!


.. _publish every version:

*********************
Publish Every Version
*********************

You can specify "please build documentation for all package versions" with this
configuration:

.. code-block:: python

    optionvars = {
        "rez_docbot": {
            "publishers": [
                {
                    # ... More publisher settings ...
                    "publish_pattern": "",  # <-- setting empty means "publish every version"
                    "publisher": "github",
                    # ... More publisher settings ...
                },
            ],
        },
    }

Here's a more complete example of the same idea:

.. code-block:: python

    optionvars = {
        "rez_docbot": {
            "publishers": [
                {
                    "authentication": {"token": "asdfasdf", "user": "MyUser"},
                    "branch": "gh-pages",
                    "publish_pattern": "",  # <-- setting empty means "publish every version"
                    "publisher": "github",
                    "repository_uri": "git@github.com:MyUser/{package.name}",
                    "view_url": "https://MyUser.github.io/{package.name}",
                },
            ],
        },
    }


.. _publish every major:

*******************
Publish Every Major
*******************

.. code-block:: python

    optionvars = {
        "rez_docbot": {
            "publishers": [
                {
                    # ... More publisher settings ...
                    "publish_pattern": "{package.version.major}",
                    "publisher": "github",
                    # ... More publisher settings ...
                },
            ],
        },
    }


.. _publish every minor / major:

***************************
Publish Every Minor / Major
***************************

.. note::

    This behavior is the default publish pattern. You don't need to set the publish pattern explicitly.

.. code-block:: python

    optionvars = {
        "rez_docbot": {
            "publishers": [
                {
                    # ... More publisher settings ...
                    "publish_pattern": "{package.version.major}.{package.version.minor}",
                    "publisher": "github",
                    # ... More publisher settings ...
                },
            ],
        },
    }

See this other page, :ref:`publish_pattern`, for details.


**********************
Custom Publish Version
**********************

It's also worth noting that ``"publish_pattern"`` can take any regex string or
compiled regex.

``"publish_pattern": ".+"`` is the same as ``"publish_pattern": ""``.

.. code-block:: python

    import re

    optionvars = {
        "rez_docbot": {
            "publishers": [
                {
                    # ... More publisher settings ...
                    "publish_pattern": re.compile("anything here"),
                    "publisher": "github",
                    # ... More publisher settings ...
                },
            ],
        },
    }

With these options, you should be able to express any type of version
publishing scheme.
