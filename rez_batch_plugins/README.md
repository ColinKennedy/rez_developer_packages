- move_imports doesn't clone stuff correctly. Fix this!
- Add docstrings
- Documenat this file, properly
- Check all modified packages
    - All tests must pass
    - CI everything


# Example Commands
## yaml2py

```sh
python -m rez_batch_process run yaml2py pr_prefix some-github-token --temporary-directory /tmp/place --keep-temporary-files                                                                 
```


## move_imports


>> selecaotwo@localhost:/home/selecaotwo/env/config/rez_developer_packages/rez_batch_plugins$ python -m rez_batch_process run move_imports pr_prefix d59886d4cc709cb98800aa09b50dd4508921c556 --temporary-directory /tmp/place3 --keep-temporary-files --why "asdfomthing" --arguments "'. foo,bar' --requirements foo_package,bar --deprecate existing,foo" --packages-path /tmp/thing 

>> selecaotwo@localhost:/home/selecaotwo/env/config/rez_developer_packages/rez_batch_plugins$ python -m rez_batch_process run move_imports pr_prefix d59886d4cc709cb98800aa09b50dd4508921c556 --temporary-directory /tmp/place3 --keep-temporary-files --why "asdfomthing" --arguments "'. foo,bar' --requirements foo_package,bar --deprecate existing,foo"

TODO: Remove this later d59886d4cc709cb98800aa09b50dd4508921c556

```sh
python -m rez_batch_process run move_imports pr_prefix d59886d4cc709cb98800aa09b50dd4508921c556 --temporary-directory /tmp/place --keep-temporary-files --why "because it we need it!" --arguments ". some.namespace.here,a.new.space.somewhere,some.namespace.there,a.new.space.over,some.namespace.everywhere,a.new.space.rainbox"
```

```sh
python -m rez_batch_process run move_imports pr_prefix some-github-token --temporary-directory /tmp/place --keep-temporary-files
```


TODO
 - Add "bump" command
 - Add "add_to_attribute" command
 - Add "coverage" report command
