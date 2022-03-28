- Make sure everything is documented (not just that pydocstyle is happy)


TODO Fill this page later

TODO - reorganize the existing Python modules, once made, to be easier to understand

TODO :

- unittests
  - invalid schema gives a good result return result
     - bad authentication should say what the problem(s) were for each of them
     - bad general settings should say why
  - general
    - publish to the root of a repository
      - Or to an inner folder (make the folder if it doesn't exist)
    - make sure latest gets updated if needed. Or not, if back-patching
  - github
    - username / password
      - raw
      - by-file
    - access token
      - raw
      - by-file
    - two-factor authentication

- Make sure there's a mechanism to force publish (versioned / latest)
- Allow multiple publish patterns
- Allow publish patterns which use regex
  - Add a "semver" regex pattern people can use

- Check that I have references for all :ref: tags.
  - Also check the `foo`_ stuff
  `GitHub`_

- Go through the configuration. Make sure I'm not being too permissive about the text users may write

- Add a "create repository" callback

- Need a unittest when the authenticated user doesn't have permissions to push / create repository etc as another user (ColinKennedy repo mismatch)

::

    optionvars = {
        "rez_docbot": {
            "credentials": {
                "access_token": "asdfasfsdf",
            },
        }
    }

Possible GitHub APIs
- https://pygithub.readthedocs.io/en/latest/examples.html
- https://github3py.readthedocs.io/en/master/examples/github.html
   - https://github3py.readthedocs.io/en/master/narrative/getting-started.html#using-the-library
- https://gist.github.com/avullo/b8153522f015a8b908072833b95c3408
- https://www.thepythoncode.com/article/using-github-api-in-python

- rez_docbot.credentials notes
    - credentials
        -- can be user + password pair - need to add this into the adapter
        -- can be access token - need to add this into the adapter
        - ! both options can be raw OR use a file on-disk
        -- URI base?
        -- needs a type specifier (e.g. GitHub) and a matching adapter
            -- fail if no matching adapter
        -- required True / False
            -- So it doesn't have to publish to that location, if not found
            - log with a warning though, either way
        -- repository_template
            -- allow users to use Python {}s to change anything in the URL
            -- Needs to support documentation (multiple per repo) somehow
    - publish_scheme
        -- default: "{package.version.major}.{package.version.minor}"
        -- Other configurations can be used to bump documentation
        - needs a force mechanism
        - If backpatching, don't mess with latest
        -- latest_name
            -- default: "latest"
            -- If unset, don't set a latest
    - adapters
        - GitHub
            - Needs some kind of templater which includes .nojekyll and stuff
    - master page?
        - Maybe useful?
    - Somehow this has to hook back into the package.py's `help`_ attribute.
        - It needs to be able to point to the repository end-point.
            - And that end-point needs to match the "publish_scheme"
        - The URL where users interface with the documentation is not necesarily
          the same that they publish to (GitHub pages for example is different)
            - https://github.com/ColinKennedy/colinkennedy.github.io is where I push
            - https://colinkennedy.github.io where the documentation would
              actually live. And the objects.inv is located in either place.
              But users would want `help`_ to go where the end-facing docs live
                - To futher emphasize this point, if there's a split
                  documentation setup with GitHub and readthedocs.io, then
                  those would be located in completely different websites
    - Extra considerations
        - 2 factor authentication? https://github3py.readthedocs.io/en/master/narrative/getting-started.html#using-the-library
    - Each adapter should have a place where they can define custom, extra data
        - e.g. an adapter may actually log into a specific user
