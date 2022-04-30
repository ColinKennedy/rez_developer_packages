######################
Configuring rez_docbot
######################

rez_docbot allows users to define multiple publish locations for documentation
through configuration settings. The exact details of "what settings are allowed
in each configuration" depends on the publisher. However, everything in this
page is supported by all, current publisher types. If you want to read about
per-publisher details, check out :doc:`publisher_types`.

In general, users can define configuration settings in 1 of 2 ways:

- Globally, for all packages
- :ref:`per-package configuration`


**************
Configurations
**************

These are the general, customizable settings for :ref:`rez_docbot`. They affect
anything from publish behavior, what folders end up getting written to disk,
and where publish data is made available.


.. _rez_docbot.publishers:

rez_docbot.publishers
=====================

This setting is where you define all publish destinations for documentation.
You are free to create 1 or more publishers and each destination will be
published to. Most of the time, users will only define a single publisher.
However if you do make more than one publisher, note:

- The first publisher is special. All other publishers are considered fallbacks
  / redundancy publishers.
- If you make more than one publisher, always place the most important
  publisher first.

Here's an example configuration:

.. code-block:: python

    optionvars = {
        "rez_docbot": {
            "publishers": [
                {
                    "authentication": {
                        "token": "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",
                        "user": "Foo",
                    },
                    "branch": "gh-pages",
                    "publisher": "github",
                    "repository_uri": "git@github.com:Foo/{package.name}",
                    "view_url": "https://Foo.github.io/{package.name}",
                },
            ],
        },
    }

This simple configuration carries the meaning of:

- For every Rez package

    - Create a repository using the package's family name
    - Set it up for GitHub (`gh-pages`_, `.nojekyll`_, etc)
    - View the documentation at ``https://Foo.github.io/{package.name}``

This is a really simple example. You can nest multiple packages in the same
repository, control how and when new documentation is generated, etc.

.. seealso::

    :doc:`popular_publish_configurations`

    :ref:`Control how new documentation is made <publish_pattern>`


.. _rez_docbot.publishers.*.authentication:

rez_docbot.publishers.*.authentication
======================================

For cloning and pushing, you must provide some valid access information
(username / password, access token, etc).

.. code-block:: python

    optionvars = {
        "rez_docbot": {
            "publishers": [
                {
                    # ... more settings ...
                    "authentication": {
                        "token": "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",
                        "user": "Foo",
                    },
                    # ... more settings ...
                },
            ],
        },
    }

.. code-block:: python

    optionvars = {
        "rez_docbot": {
            "publishers": [
                {
                    # ... more settings ...
                    "authentication": {
                        "password": "Some raw password (not recommended)",
                        "user": "Foo",
                    },
                    # ... more settings ...
                },
            ],
        },
    }

- ``"authentication"`` accepts a dict as well as a list-of-dicts. So if one
  authentication method fails, you can provide fallbacks.
- You can also store credentials in a file and load that instead. See
  :ref:`authentication indirection` for details.


rez_docbot.publishers.*.commit_message
======================================

When documentation is committed, this setting defines the message used for the
git commit.

**Default**: ``'Added "{package.name}" documentation!'``

.. code-block:: python

    optionvars = {
        "rez_docbot": {
            "publishers": [
                {
                    # ... more settings ...
                    "commit_message": 'Added "{package.name}-{package.version}" documentation!',
                    # ... more settings ...
                },
            ],
        },
    }


.. _rez_docbot.publishers.*.latest_folder:

rez_docbot.publishers.*.latest_folder
=====================================

By default, :ref:`rez_docbot` tries to build 2 sets of documentation when
you publish documentation for a new package version.

- :ref:`latest documentation`
- :ref:`versioned documentation`

This setting concerns :ref:`latest documentation`. Whatever text is used here
will be the name of the folder where the most recent package's documentation
will live.

**Default**: ``"latest"``.

.. code-block:: python

    optionvars = {
        "rez_docbot": {
            "publishers": [
                {
                    # ... more settings ...
                    "latest_folder": "latest",
                    # ... more settings ...
                },
            ],
        },
    }


.. important::

    To **disable** the "latest" folder, simply set ``"latest_folder": ""``.


.. _publish_pattern:

rez_docbot.publishers.*.publish_pattern
=======================================

Depending on how a package is set up, you may want to only publish versioned
documentation:

- :ref:`publish every version`
- :ref:`publish every minor / major`
- :ref:`publish every major`

``rez_docbot.publishers.*.publish_pattern`` gives you more granular control
over how packages publish.

**Default**: ``"{package.version.major}.{package.version.minor}"``

.. code-block:: python

    optionvars = {
        "rez_docbot": {
            "publishers": [
                {
                    # ... more settings ...
                    "publish_pattern": "{package.version.major}.{package.version.minor}"
                    # ... more settings ...
                },
            ],
        },
    }

You can also specify multiple publish patterns, which :ref:`rez_docbot` will
try to match against when looking for pre-existing, versioned documentation:

.. code-block:: python

    optionvars = {
        "rez_docbot": {
            "publishers": [
                {
                    # ... more settings ...
                    "publish_pattern": [
                        "{package.version.major}.{package.version.minor}",
                        "{package.version.major}",
                    ],
                    # ... more settings ...
                },
            ],
        },
    }

.. note::

    publish_patterns can also be regex as well, instead of a raw string.


If you never want to publish versioned folders, see
:ref:`rez_docbot.publishers.*.version_folder`.


rez_docbot.publishers.*.relative_path
=====================================

By default when publishing documentation, it's assumed that you want to publish
to the root of the documentation repository.
``rez_docbot.publishers.*.relative_path`` allows users to publish documentation
within a sub-folder.

**Default**: ``""``

.. code-block:: python

    optionvars = {
        "rez_docbot": {
            "publishers": [
                {
                    # ... more settings ...
                    "relative_path": "path/to/{package.name}",
                    "repository_uri": "git@github.com:Foo/all_documentation",
                    "view_url": "https://Foo.github.io/all_documentation",
                    # ... more settings ...
                },
            ],
        },
    }

In the configuration above, :func:`.preference.get_first_versioned_view_url`
would return
``"https://Foo.github.io/all_documentation/path/to/{package.name}"``, to
reflect not just the view URL but also relative sub-folder path.


rez_docbot.publishers.*.repository_uri
======================================

The remote where documentation will be cloned, committed, and pushed into.
This is **not** the URL for viewing that documentation. For that, see
:ref:`rez_docbot.publishers.*.view_url`.

.. code-block:: python

    optionvars = {
        "rez_docbot": {
            "publishers": [
                {
                    # ... more settings ...
                    "repository_uri": "git@github.com:FakeUser/{package.name}",
                    "view_url": "https://www.FakeUser.github.io/{package.name}",
                    # ... more settings ...
                },
            ],
        },
    }


rez_docbot.publishers.*.required
================================

A setting which implies "fail execution if for some reason documentation could
not be pushed / published". Most of the time, you'll probably want this to be
True.

**Default**: ``True``

.. code-block:: python

    optionvars = {
        "rez_docbot": {
            "publishers": [
                {
                    # ... more settings ...
                    "required": True,
                    # ... more settings ...
                },
            ],
        },
    }


rez_docbot.publishers.*.skip_existing_version
=============================================

:ref:`rez_docbot` publishes for each new major + minor Rez package version, by
default. Each patched version, if any, will overwrite an existing major + minor
versioned documentation folder. If you don't like this behavior, you can
disable it using this setting.  That way, versioned documentation folders are
immutable and cannot be changed due to later releases. Users must increment the
minor / major to get new documentation.

Generally, this setting isn't expected to be used by most people.

**Default**: ``False``

.. code-block:: python

    optionvars = {
        "rez_docbot": {
            "publishers": [
                {
                    # ... more settings ...
                    "skip_existing_version": False,
                    # ... more settings ...
                },
            ],
        },
    }


.. _rez_docbot.publishers.*.version_folder:

rez_docbot.publishers.*.version_folder
======================================

By default, :ref:`rez_docbot` tries to build 2 sets of documentation when
you publish documentation for a new package version.

- :ref:`latest documentation`
- :ref:`versioned documentation`

This setting concerns :ref:`versioned documentation`. Whatever text is used
here will be the name of the folder where all copied, versioned documentation
will live.

**Default**: ``"versions"``.

.. code-block:: python

    optionvars = {
        "rez_docbot": {
            "publishers": [
                {
                    # ... more settings ...
                    "version_folder": "versions",
                    # ... more settings ...
                },
            ],
        },
    }

.. important::

    To **disable** the "versions" folder, simply set ``"version_folder": ""``.

.. seealso::

    Related API function: :func:`.preference.get_first_versioned_view_url`

See :doc:`publishing_per_version` for details on controlling how often
versioned documentation is generated.


.. _rez_docbot.publishers.*.view_url:

rez_docbot.publishers.*.view_url
================================

``view_url`` is the URL (or directory on-disk) to wherever documentation is
expected to be viewed.

.. code-block:: python

    optionvars = {
        "rez_docbot": {
            "publishers": [
                {
                    # ... more settings ...
                    "repository_uri": "git@github.com:FakeUser/{package.name}",
                    "view_url": "https://www.FakeUser.github.io/{package.name}",
                    # ... more settings ...
                },
            ],
        },
    }

In a typical documentation set up, you typically would push documentation to a
remote location, like ``"git@github.com:FakeUser/{package.name}"`` but then
that documentation is viewable to the average user at
``https://www.FakeUser.github.io/{package.name}"``.

.. important::

    Tools such as :ref:`rez_sphinx:rez_sphinx` rely on this URL being accurate
    in order to link Sphinx documentation to Rez. This is done via the
    :func:`.preference.get_first_versioned_view_url`. In short, absolutely make
    sure this setting is accurate!


.. _per-package configuration:

*************************
Per-Package Configuration
*************************

All settings on this page show how to define these settings globally. However
they can also be overwritten at the `package.py`_ level.

This is how a setting may look, globally:

.. code-block:: python

    optionvars = {
        "rez_docbot": {
            "publishers": [
                {
                    # ... more settings ...
                    "latest_folder": "latest",
                    # ... more settings ...
                },
            ],
        },
    }

And here's the same setting, as part of a `package.py`_.

.. code-block:: python

    name = "some_package"

    version "1.2.3"

    rez_docbot_configuration  = {
        "publishers": [
            {
                # ... more settings ...
                "latest_folder": "latest",
                # ... more settings ...
            },
        ],
    }
