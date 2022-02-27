rez-docbot github publish .
 - Get the Rez package at the current .
 - If the package defines an end-point directly, use it
 - If not, fallback to a rez-config template like "git@github.com:ColinKennedy/{this.name}.git" - format this with the package
  - If no fallback template, error

 - Publishing process is essentially
  - Build to a local, temporary location as normal
  - Decide from that build whether to copy into the installed package and/or submit to github / readthedocs etc

- Add a config for whether to do local or remote publishing
