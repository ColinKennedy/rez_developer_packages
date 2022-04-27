###########################
Batch-Publish Documentation
###########################

If you want to add documentation in-batch, the steps are very similar to
:doc:`getting_started`, with some adjustments.

- cd to the root of some git repository containing **source** Rez packages
- Make a ``rez-env`` containing these packages

    - rez_sphinx
    - rez_inspect

- Run this in the terminal:

TODO : double-check that this script works

.. important::

    You'll need to build and include rez-inspect, which is a Rez package
    located in this repository.


.. code-block:: sh

    # add_rez_sphinx.sh
    #!/usr/bin/env sh

    set -e  # Stop execution on the first error. This is optional

    export REZ_SPHINX_INIT_OPTIONS_CHECK_DEFAULT_FILES=0

    message="Added rez_sphinx documentation"
    directories=`rez_sphinx suggest build-order . --search-mode source --display-as directories --filter already_released`
    root=`git rev-parse --show-toplevel`
    branch=features/adding_rez_sphinx

    cd $root

    if [ "`git branch --show-current`" != "$branch" ]
    then
        if [ `git branch --list $branch` ]
        then
            git checkout $branch
        else
            git checkout -b $branch
        fi
    fi

    for directory in $directories
    do
        cd $directory

        rez-build --clean --install
        package_name=`rez-inspect name --style=pretty`
        package_version=`rez-inspect version --style=pretty`
        rez-env "$package_name==$package_version" rez_sphinx -- rez_sphinx init --skip-existing
        git add --all .
        git commit -m $message

        # You can uncomment the line below if you already have the release_hook set up
        # git push -u origin $branch && rez-release -m $message
    done

    git push -u origin $branch

The jist of the script is, cd to every Rez package, run ``rez_sphinx init`` and
push the branch. Assuming you followed :doc:`rez_sphinx_as_a_release_hook`, the
next time any of those packages are released via `rez-release`_, you'll have
beautiful documentation waiting for you. The script assumes you want to place
your changes under a new feature branch called ``features/adding_rez_sphinx``
so you can make PR(s) as needed. There's the option to run this all in the
master branch too, if you want but exercise common sense and don't do that
without prior approval.


****************************
When You're Ready To Release
****************************

.. important::

   If you want auto-linking, auto-publishing, and the like to work, you must
   opt-in to those features before following this tutorial.

   Follow the steps in :doc:`rez_sphinx_as_a_release_hook` first before continuing.


Assuming you go through PR, everything's merged into master, and you're ready
to release. This script will automate that.

TODO : double-check that this script works

.. code-block:: sh

    export REZ_SPHINX_INIT_OPTIONS_CHECK_DEFAULT_FILES=0

    message="Added rez_sphinx documentation"
    directories=`rez_sphinx suggest build-order . --search-mode source --display-as directories --filter already_released`

    root=`git rev-parse --show-toplevel`
    cd $root

    for directory in $directories
    do
        cd $directory
        rez-release -m $message
    done


*********************
Why This Script Works
*********************

The long command at the start, ``rez_sphinx suggest build-order . etc etc etc``
determines

- Does the package need documentation
- Is the Rez package already released with documentation

If either condition is False, the package's path is returned.

Then during the for-loop, ``rez_sphinx init --skip-existing`` stops early if it
sees documentation (rez_sphinx documentation or not). If it doesn't have
documentation, it's added. From there, you have the option to just push /
release / etc.


***************
After releasing
***************

**Important**: Whenever you choose to batch- `rez-release`_, remember that you
did it with ``export REZ_SPHINX_INIT_OPTIONS_CHECK_DEFAULT_FILES=0``. Assuming
you haven't changed your default configuration to :ref:`always ignore default
files <rez_sphinx.init_options.check_default_files>` (which by the way is
**not** recommended), that means the default files are still unedited. Make
sure to tell maintainers to **add hand-written documentation** to the default
files, "developer_documentation.rst" and "user_documentation.rst", so that
future `rez-release`_ don't error on them!
