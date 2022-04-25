##################################
Mono Vs Multi Package Repositories
##################################

Developers tend to create Rez source packages in one of two ways, using git.

Either they have a repository which contains 1+ Rez package, as subfolders.
e.g.

::

    {root}/
        package_a/
            package.py
        package_b/
            package.py
        package_c/
            package.py

Most of the advice and documentation in :ref:`rez_docbot` assumes that your
repositories are set up like this. However some companies prefer to write git
repositories containing only a single Rez Rez package, like this:

::

    {root}/
        package.py

:ref:`rez_docbot` supports both ways of working as well, out of the box! If
you're having trouble getting your repositories set up, you may want to check
out :doc:`popular_publish_configurations` for more details.
