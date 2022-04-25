Features

- Allow publishing to a relative path, instead of to the root repository location!

   - rename inner_path to relative_path
   - add unittest to make sure the inner folders are created
   
- Make sure there's a mechanism to force publish (versioned / latest)
- If package doesn't have a version

   - if latest is disabled, error
   - don't create a version folder, since there's no version

- Go through the configuration. Make sure I'm not being too permissive about the text users may write
- Add a "create repository" callback. So users can insert their own requirements
- Need a unittest when the authenticated user doesn't have permissions to push / create repository etc as another user (ColinKennedy repo mismatch)


Documentation
- Do TODO notes (many of them)
- Check that I have references for all :ref: tags.
- :ref:`publish_pattern`.""
