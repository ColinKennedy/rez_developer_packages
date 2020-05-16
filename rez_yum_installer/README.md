- need to somehow get the yum package from online
- read its spec

- Get an installed version of the Yum
 - install to a variant folder
- alternative: get the source version of the yum and use that + make it install-able
 - probably going to be much more difficult to do

- need variant information for the yum package
- download it to a package location (needs a variant, too)

- requirement names need to be converted from YUM style to Rez style
- do this recursively for each requirement


https://stackoverflow.com/questions/5613954/extract-the-spec-file-from-rpm-package
https://github.com/bkircher/python-rpm-spec
https://linuxhint.com/yum_centos_python/
https://unix.stackexchange.com/questions/226705/extract-the-spec-file-out-of-an-rpm
http://ftp.rpm.org/max-rpm/s1-rpm-query-handy-queries.html
https://rpm-packaging-guide.github.io/

- Remove cpiofile if it turns out to be useless
