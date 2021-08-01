- Check command must be able to take a rez-test command
- CLI must support
 - comparing 2 contexts
 - using 1 context, and start from the first version of each package

- Make sure implicit packages also work as expected


rez-bisect run /tmp/bad.rxt /tmp/checker.sh
rez-bisect run /tmp/bad.rxt /tmp/checker.sh --good /tmp/good.rxt 
rez-bisect run `cat /tmp/bad.rxt` /tmp/checker.sh --good /tmp/good.rxt 
rez-bisect run "foo-1 bar-1+<2" /tmp/checker.sh --good /tmp/good.rxt 



