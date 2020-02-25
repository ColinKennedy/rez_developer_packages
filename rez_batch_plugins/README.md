- Document this file, properly
- Check all modified packages
    - All tests must pass
    - CI everything


# Example Commands
## yaml2py

```sh
python -m rez_batch_process run yaml2py pr_prefix some-github-token --temporary-directory /tmp/place --keep-temporary-files                                                                 
```


## move_imports

```sh
$ python -m rez_batch_process run move_imports pr_prefix github-token --temporary-directory /tmp/place3 --keep-temporary-files --why "asdfomthing" --arguments "'. foo,bar' --requirements foo_package,bar --deprecate existing,foo"
```


TODO
 - Add "bump" command
 - Add "add_to_attribute" command
 - Add "coverage" report command
 - move_imports doesn't clone stuff correctly. Fix this!
