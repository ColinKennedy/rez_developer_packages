############
How It Works
############

The steps that this tool does can be summarized like this:

- Given some file / folder paths
- Find the Rez package that describes those paths
- If the Rez package is not installed (e.g. it's a source Rez package)
    - Build the package to a temporary location
- Search each of the given file / folder paths for Python files
- For each Python file, get every import statement
- Find every Python module that each import comes from
- If the module comes from a recognizable Rez package or Python package
    - Get the package's name
- Search for a documentation URL that matches that package's name
- Format the package + URL data as intersphinx data
- Print the intersphinx data or write it to-disk
