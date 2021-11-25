{
	"docbot_build": "rez_docbot build sphinx -- --source documentation/source --destination documentation/build",
	"docbot_publish": "rez_docbot publish github -- documentation/build",
}


Unittests
 - Exclude !package_requirement
 - Exclude ephemeral packages
 - Make sure requirements are found via `requires` as well as the test `requires`

- Read from REZ_DOCBOT_BUILDER_PLUGINS
- Add a test for if there's only one build + publish pair
- Add a test to allow multiple build + publish pairs


Parsing
 - If the user provides "--help" or "-h" and no " -- ", print the general help
 - If the user provides "--help" or "-h" to the left of " -- " but no valid right-hand arguments, print the general help
 - If the user provides "--help" or "-h" to the right of " -- ", show the plug-in help

 - If " -- " provided, pass
 - If " -- " not provided, error with a good message
 - If " -- " provided but insufficient left or right arguments, error with a good message
