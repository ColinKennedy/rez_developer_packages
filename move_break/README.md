# TODO : Add unittests that checks for bad arguments
- Need unittest to make sure the CLI works
 - There needs to be a unittest that reads namespaces as text
 - another that reads from process substitution
 - another that reads from file paths.

-  Add an option to allow namespace endings to be aliased (if the tail doesn't match the original)
 - e.g. [("foo.bar", "thing.other")]
  - "from foo import bar" would be come "from thing import other as bar"
  - instead of "from thing import other"
  - this is for ultra-conservative people who want to make sure code doesn't break
