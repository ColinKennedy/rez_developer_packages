rez-doc - basically just rez-help but runs a preprocessor function
 - Add instructions on how add rez-help integration

- Add instructions for `hython` / `mayapy` / etc

- rez-sphinx CLI command
	- Relevant commands
	 - check
	 - create
	 - build   
	 - publish

- rez-helpx
 - Add instructions to integrate with the regular rez-help


- Auto-generate API .rst files by default (manual as an option)

doxygen {root}/source {root}/build && rez-doc generic publish --from {root}/doxygen/build
rez-sphinx create
rez-sphinx build -a --source {root}/documentation/source --destination {root}/documentation/build
rez-sphinx auto-publish -a --from {root}/documentation/build
 - Publishes for each new minor
 - Skips patches
 - Runs on each rez-release (make sure run_on is just prerelease, related)

- Have a forkable publish logic set in-place. So people can publish non minor versions if they want to

- Hooks for GitHub credentials
 - allow a global configuration
 - allow a user credential file

- Sphinx_object as a separate attribute, not as a part of the help attribute

- Add a home-page option. When included, the CSS picks it up(?)

package dependency reading
 - make sure ephemerals and weak requirements which aren't in the resolve are skipped

