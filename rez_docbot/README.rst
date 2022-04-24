- Go through the configuration. Make sure I'm not being too permissive about the text users may write
- Add a "create repository" callback. So users can insert their own requirements
- Need a unittest when the authenticated user doesn't have permissions to push / create repository etc as another user (ColinKennedy repo mismatch)


- Make sure there's a mechanism to force publish (versioned / latest)

- Make sure nested repositories still publish correctly (when inner_path is defined, basically)
- Need to ensure a lacking configuration is reported to the user (explain what is missing)


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

- Check that I have references for all :ref: tags.
  - Also check the `foo`_ stuff
  `.nojekyll`_
  `GitHub`_
  `Sphinx`_
  `git`_
  `CRUD`_
  `GitHub enterprise`_
  `access token`_

  `GitHub organization`_, or
  :ref:`publish_pattern`."""

::

    optionvars = {
        "rez_docbot": {
            "credentials": {
                "access_token": "asdfasfsdf",
            },
        }
    }

- rez_docbot.credentials notes
    - credentials
        - repository_template
            - allow users to use Python {}s to change anything in the URL
            - Needs to support documentation (multiple per repo) somehow
            - needs to work with mono repositories
    - publish_scheme
        - needs a force mechanism
        - latest_name
         - If unset, don't set a latest
    - master page?
        - Maybe useful?
