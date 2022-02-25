Hey everyone,

I'm writing a tool to convert RPM into a slightly different package manager and have some questions related to RPM's versioning syntax.


In versioning, What is the epoch for? Is 2:0.1.1 higher than 2:100.0.0, for example?


Are files like "libpthread.so.0'" listed in the requirements guaranteed to be
on my distribution already? Each example I've found so far has been but I
wanted to be sure. Any reference documentation would be very helpful.

Can I ignore rpmlib?

http://jfearn.fedorapeople.org/en-US/RPM/0.1/html/RPM_Guide/ch-advanced-packaging.html

https://www.linuxquestions.org/questions/linux-newbie-8/rtld-gnu_hash-please-help-me-668727/

```
Fedora 5 is ancient, which may be part of your problem. rtld(GNU_HASH) is part of the GLIBC package. The VNC RPM you downloaded is probably built on a newer version of everything.

Try downloading the VNC source, and build from there.
```
