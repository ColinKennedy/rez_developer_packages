## readthedocs.io Support Idea
- On rez-release, a documentation + publish to readthedocs.
 - I guess you'd need to also create a GitHub-hosted repository
  - !!! user authentication + creation permission
 - If the destination doesn't exist, it's created
  - Requires user authentication
  - !!! Requires API for user authentication
 - If the readthedocs.io end-point does not exist, it is created
  !!! Requires API for that
 - The RTD page would then need to be updated to use the GitHub location

- On `rez-release`
 - The GitHub documentation host end-point is consulted
  - If it exists, use it. if not, make it
   - Enable .nojekyll and any custom settings are added. e.g. rez-config for collaborators and the like
  - Based on Rez version, make hard-coded folders
 - If new patch, no new docs UNLESS this is the first patch for that major / minor
  - Add --force to make it update the docs anyway
 - If new major / minor, add documentation
 - If latest, update the "latest" folder
 - If user's rez-config wants it as a PR, submit a PR, hold CI
 - If not, continue automatically clone, change, and push
  - Make sure to force add and push every file
 - The user's released Rez package will need to be point to the hard-coded major.minor folder
 - tag the documentation with a unique rez-package name + version
  - !!! If the end-point is RTD, we'll need to change the tag and do a re-build
	of the documentation. So RTD is up to date with the latest + the other
	version folders

- In readthedocs.io
 - Basically just an end-point to display just files. 
 !!! Requires updating on new rez-release runs.


# Free GitHub support
- Creating a unique user name based on the Rez package name and linking that to
  the Rez package.


# Paid GitHub Support
- I guess it's the same as RTD support but we'd clone + push to the "gh-pages" git branch


# Convince The Rez Maintainers to allow pre-build hooks
And then mess with a package's `help`, using this snippet


```python
self.package.resource._data["help"] = "asdf"  # Works
del self.package.resource.__dict__["help"]
```

# Add an "auto-append" option which finds "pages to add to the package's Rez
help attribute" by scanning documentation for a known tag.
