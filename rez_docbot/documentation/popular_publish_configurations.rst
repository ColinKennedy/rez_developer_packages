##############################
Popular Publish Configurations
##############################

Like the saying "there's more than one way to skin a cat", there's more than
one way to set up documentation. We'll define each term and then explain what
those terms mean and how to set them up.

- :ref:`Dedicated user & separate repositories`
- :ref:`Dedicated user & central repository`
- :ref:`Same user & same repository`

Some prefer to have a dedicated GitHub user / group / organization, with
dedicated log-in / password credentials, to publish documentation into. Others
prefer to keep it all within the same user, so that developers who already
have access do a repository are guaranteed to have the same permissions
in their documentation repositories.

.. important::

    Keep in mind that these configurations are not mutually exclusive.  In
    fact, since you can provide as many publishers as you want to
    :ref:`rez_docbot`, you can have any combination of these configurations at
    any time! And if certain Rez packages need to be treated differently
    compared to others, you can override it at the package level to do
    different things. See :ref:`per-package configuration` for details.


.. _Dedicated user & separate repositories:

Dedicated user & separate repositories
======================================

Imagine you're working on 3 Rez packages (which may be in 3 separate
repositories or one single repository, in subdirectories).

e.g.

::

    github.com/rez-packages/package_a
    github.com/rez-packages/package_b
    github.com/rez-packages/package_c

It's decided that users want each documentation to be listed using the package
name. But they also don't want that code to be committed to source code
repositories like ``rez-packages/package_a``. They want the documentation in
another owner. So they make a new group / GitHub organization called
"OurDocs" and make one repository per Rez package.

e.g.

::

    github.com/OurDocs/package_a
    github.com/OurDocs/package_b
    github.com/OurDocs/package_c

Here's what such as set-up would look like, as a :ref:`rez_docbot` configuration:

.. code-block:: python

    optionvars = {
        "rez_docbot": {
            "publishers": [
                {
                    "authentication": {"token": "asdfasdf", "user": "MyUser"},
                    "branch": "gh-pages",
                    "publisher": "github",
                    "repository_uri": "git@github.com:OurDocs/{package.name}",
                    "view_url": "https://OurDocs.github.io/{package.name}",
                },
            ],
        },
    }

When you publish your documentation, the documentation will be pushed to
``"git@github.com:OurDocs/{package.name}"`` and be viewable at
``"https://OurDocs.github.io/{package.name}"``.


Pros
****

- Documentation is kept separate from the source repository (which makes source
  repositories more lightweight)
- A dedicated user for documentation means access / push permissions can be
  more easily controlled, per-user / per-group etc.

Cons
****

- A repository is created per Rez package. If you have lots of Rez packages,
  that will make many repositories.
- Documentation may not be viewable / accessible to everyone, even if they are
  able to publish the documentation.


.. _Dedicated user & central repository:

Dedicated user & central repository
===================================

This variant is actually the same as :ref:`Dedicated user & separate
repositories`. The only difference is that, instead of creating new
repositories per-package, there's a dedicated, single documentation repository
and the documentation for all Rez packages live within it.


.. code-block:: python

    optionvars = {
        "rez_docbot": {
            "publishers": [
                {
                    "authentication": {"token": "asdfasdf", "user": "MyUser"},
                    "branch": "gh-pages",
                    "publisher": "github",
                    "relative_path": "packages/{package.name}"
                    "repository_uri": "git@github.com:OurDocs/all_documentation",
                    "view_url": "https://OurDocs.github.io/all_documentation",
                },
            ],
        },
    }

When you publish your documentation, the documentation will be pushed to
``"git@github.com:OurDocs/all_documentation"`` and copied into a subdirectory
based on ``"packages/{package.name}"``. And then the documentation is viewable
at ``"https://OurDocs.github.io/all_documentation/packages/{package.name}"``.


Pros
****

- Documentation is kept separate from the source repository (which makes source
  repositories more lightweight)
- A dedicated user for documentation means access / push permissions can be
  more easily controlled, per-user / per-group etc.
- Only one git repository is needed. All documentation lives there


Cons
****

- That repository can get quite large over time, since it'll be hosting the
  documentation for any package it's meant to keep + its older versioned
  documentation.
- The view URL is now longer. From ``"https://OurDocs.github.io/{package.name}"``.
  to ``"https://OurDocs.github.io/all_documentation/packages/{package.name}"``.

- A repository is created per Rez package. If you have lots of Rez packages,
  that will make many repositories.
- Documentation may not be viewable / accessible to everyone, even if they are
  able to publish the documentation.


.. _Same user & same repository:

Same user & same repository
===========================

Some people will prefer to not publish documentation as another, separate
"OurDocs" user but instead re-use the current user and repository wherever the
Rez package currently lives. This can be done, using the following:

.. code-block:: python

    optionvars = {
        "rez_docbot": {
            "publishers": [
                {
                    "authentication": {"token": "asdfasdf", "user": "MyUser"},
                    "branch": "gh-pages",
                    "publisher": "github",
                    "repository_uri": None,
                    "view_url": "https://OurDocs.github.io/{package.name}",
                },
            ],
        },
    }

Since ``"repository_uri"`` is blank, the package's git push URL is queried and
reused instead. The ``"gh-pages"`` branch is used to copy and push the
documentation.


Pros
****

- Anyone that has access to the repository should have access to view the documentation
- The original git repository is re-used. No new git repository is needed to
  host the documentation.


Cons
****

- Committing documentation .html files with the source code in one repository


Final Thoughts
==============

Astute readers will see that these aren't the only configurations which are
possible. However these are typically the most popular ones.
