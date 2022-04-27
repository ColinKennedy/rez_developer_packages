##############
Authenticating
##############

This page explains the different ways you can connect to remote services like
GitHub. To do this, you must provide :ref:`rez_docbot` with log-in
credentials (username and password, access token, etc).

A typical authentication configuration may look like this `rezconfig.py`_:

.. code-block:: python

    optionvars = {
        "rez_docbot": {
            "publishers": [
                {
                    # ... More publisher information ...
                    "authentication": {
                        "token": "kjhaweliufhawe_some_access_token_asiudfhasdf",
                        "user": "MyUser",
                    },
                    "type": "github",
                    # ... More publisher information ...
                },
            ],
        }

It's important to remember these following types:

- You do not need to directly write authentication details directly in `rezconfig.py`_

    - See :ref:`authentication indirection`

- :ref:`rez_docbot` allows publishers to authenticate any way they'd like.  So
  the configuration above may only be true for publishers of type ``"type":
  "github"``. Though publisher types will try to be as consistent as possible
  and point out any differences where applicable.


.. _authentication indirection:

Authentication Indirection
==========================

Putting raw user / token credenticals in a `rezconfig.py`_ that someone can
conceivably view by calling ``rez-config optionvars`` is not good `OPSEC`_. To
make it a bit harder for users to see sensitive log-in information, you can
tell publishers such as the :ref:`github publisher type` to read authentication
details from a file, like so:

.. code-block:: python

    optionvars = {
        "rez_docbot": {
            "publishers": [
                {
                    # ... More publisher information ...
                    "authentication": {
                        "payload": "~/.github_authentication_test.json",
                        "type": "from_json_path",
                    },
                    "type": "github",
                    # ... More publisher information ...
                },
            ],
        }


That file, ``~/.github_authentication_test.json``, may look like this:

.. code-block:: json

    {
        "token": "kjhaweliufhawe_some_access_token_asiudfhasdf",
        "user": "MyUser",
    }

Having an extra file that is only available from the computer that builds the
documentation like that is a simple way to keep your data more secure.

(By the way, I'm no security expert. If you have suggestions, please feel free
to open feature request!)

That said though, if we're talking about GitHub, access tokens can be given
limited permission sets so even if a bad actor got those log-in details, they
wouldn't be able to do much with it as long as your token's permissions is set
correctly.

To see rez_docbot's recommended GitHub permissions settings, see
:ref:`GitHub access tokens`.
