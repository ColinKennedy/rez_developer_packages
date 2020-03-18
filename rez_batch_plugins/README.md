# Example Commands
## yaml2py

```sh
python -m rez_batch_process run yaml2py pr_prefix some-github-token --temporary-directory /tmp/place --keep-temporary-files                                                                 
```


## move_imports

```sh
$ python -m rez_batch_process run move_imports pr_prefix github-token --temporary-directory /tmp/place3 --keep-temporary-files --why "asdfomthing" --arguments "'. foo,bar' --requirements foo_package,bar --deprecate existing,foo"
```

## bump

# TODO : Add unittest to changing multiple packages at once
# TODO : ensure the user provides a valid package/package+version. Make a unittest for it
# TODO : need unittest to deal with non-semantic versions

```sh
$ python -m rez_batch_process run bump pr_prefix github-token --temporary-directory /tmp/place3 --keep-temporary-files --packages my_package-1+<2 --instructions `cat instructions.txt` --search-paths /some/path/that/includes/my_package/here
```



TODO
 - Add "add_to_attribute" command
 - Add "coverage" report command
 - move_imports doesn't clone stuff correctly. Fix this!
