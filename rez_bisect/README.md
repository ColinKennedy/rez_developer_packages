
PR to fix resolved_context
 - Add paths=self.package_paths
  - /home/selecaotwo/rez-2.93.0-python-2.7/lib/python2.7/site-packages/rez/resolved_context.py

- Check command must be able to take a rez-test command
- CLI must support
 - comparing 2 contexts
 - using 1 context, and start from the first version of each package

- Add an argument to check the command against the "good" and "bad" to make sure they're good / bad
 - Add an argument to opt out of those checks

- Make sure it works with 
 - added packages
 - removed packages
 - older packages

- Make sure implicit packages also work as expected


- Handle bad, inner resolves to make sure that one bad environment doesn't break the bisect

- Do TODO notes
- Do NotImplementedError notes

- Need to check if before / after are the same environment

rez-bisect run /tmp/bad.rxt /tmp/checker.sh
rez-bisect run /tmp/bad.rxt /tmp/checker.sh --good /tmp/good.rxt 
rez-bisect run `cat /tmp/bad.rxt` /tmp/checker.sh --good /tmp/good.rxt 
rez-bisect run "foo-1 bar-1+<2" /tmp/checker.sh --good /tmp/good.rxt 



