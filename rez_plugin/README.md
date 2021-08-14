TODO

rez-doc
 - A plug-in system for documentation
 - Anything can register into it
  - Relevant commands
   - check
   - create
   - build   
   - publish

rez-doc - basically just rez-help but runs a preprocessor function
- Add instructions on how add rez-help integration

rez-helpx - just rez-help with a configuration built in

doxygen {root}/source {root}/build && rez-doc generic publish --from {root}/doxygen/build
rez-doc sphinx create
rez-doc sphinx build -a --source {root}/documentation/source --destination {root}/documentation/build
rez-doc sphinx auto-publish -a --from {root}/documentation/build
 - Publishes for each new minor
 - Skips patches
 - Runs on each rez-release (make sure run_on is just prerelease, related)

- Have a forkable publish logic set in-place. So people can publish non minor versions if they want to

- Hooks for GitHub credentials
 - allow a global configuration
 - allow a user credential file

- Sphinx_object as a separate attribute, not as a part of the help attribute

package dependency reading
 - make sure ephemerals and weak requirements which aren't in the resolve are skipped

