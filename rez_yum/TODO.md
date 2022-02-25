- Clean up existing code
- Add CI commands
- Add `def commands()` as part of auto-generation
- Add an option to copy the original .rpm file into the installed directory. So users never "lose" the install.

- Check if I can use provides to auto-find the lib files I've been skipping

- Maybe the lib files can come from one of the other, related Rez packages?
2022-02-23 20:49:52,925 - rez_yum._core.rpm_helper - DEBUG - Skipped: "libplc4.so()(64bit)" requirement because
2022-02-23 20:49:52,925 - rez_yum._core.rpm_helper - DEBUG - Skipped: "libplds4.so()(64bit)" requirement because
2022-02-23 20:49:52,925 - rez_yum._core.rpm_helper - DEBUG - Skipped: "libpthread.so.0()(64bit)" requirement be
2022-02-23 20:49:52,925 - rez_yum._core.rpm_helper - DEBUG - Skipped: "libnspr4.so()(64bit)" requirement because
2022-02-23 20:49:52,924 - rez_yum._core.rpm_helper - DEBUG - Skipped: "libdl.so.2()(64bit)" requirement because
2022-02-23 20:49:52,924 - rez_yum._core.rpm_helper - DEBUG - Skipped: "libc.so.6(GLIBC_2.4)(64bit)" requirement

- You need to make sure RPM requires dependencies are parsed correctly
- Also, make sure to include as much as possible about the RPM in the package.py
- Consider how to use modules!
- How do I handle version names like 'libX11_common-1.6.7-4.el7_9'? IIRC el7_9 is a variant
- Can I ignore the ".so.6" part of libc? Some examples:
    - 'libc.so.6'
    - 'libdl.so.2'
    - 'libxcb.so.1'
	- from gcc install
	2022-02-23 22:22:40,756 - rez_yum._core.rpm_helper - DEBUG - Skipped: "libgmp.so.10()(64bit)" requirement becau
	2022-02-23 22:22:40,756 - rez_yum._core.rpm_helper - DEBUG - Skipped: "libgomp.so.1()(64bit)" requirement becau
	2022-02-23 22:22:40,756 - rez_yum._core.rpm_helper - DEBUG - Skipped: "liblto_plugin.so.0()(64bit)" requirement
	2022-02-23 22:22:40,756 - rez_yum._core.rpm_helper - DEBUG - Skipped: "libm.so.6()(64bit)" requirement because
	2022-02-23 22:22:40,756 - rez_yum._core.rpm_helper - DEBUG - Skipped: "libmpc.so.3()(64bit)" requirement becaus
	2022-02-23 22:22:40,756 - rez_yum._core.rpm_helper - DEBUG - Skipped: "libmpfr.so.4()(64bit)" requirement becau
	2022-02-23 22:22:40,756 - rez_yum._core.rpm_helper - DEBUG - Skipped: "libmpc.so.3()(64bit)" requirement becaus
	e it comes from the host OS.
	See https://man7.org/linux/man-pages/man7/libc.7.html for details.
	2022-02-23 22:22:40,756 - rez_yum._core.rpm_helper - DEBUG - Skipped: "libmpfr.so.4()(64bit)" requirement becau
- Check if https://pypi.org/project/extractcode would be better for cpio extraction


- for python-libarchive, you must install
```sh
yum install libarchive libarchive-devel

Or you may get these errors on-install

libarchive/_libarchive_wrap.c:2963:21: fatal error: archive.h: No such file or directory
 #include <archive.h>

libarchive/_libarchive_wrap.c:2963:21: fatal error: archive.h: No such file or directory
 #include <archive.h>
```

- If using yum --downloadonly, make sure the user has `yum-plugin-downloadonly` downloaded
 - Reference: https://ostechnix.com/download-rpm-package-dependencies-centos/

- Add quality-related CI rez-test commands
- Add plug-in system so people can append extra behavior for specific macros

- Determine what to do about RPM names like "libc.so.6(GLIBC_2.0)", wihch contain ()s
- Also RPMs which contain a suffix like "libX11.so.6". Is that .so.6 necessary? What is that?

1. When I see that a RPM has a requirement like

libc.so.6(GLIBC_2.14)(64bit)
libc.so.6(GLIBC_2.2.5)(64bit)
libc.so.6(GLIBC_2.34)(64bit)
libc.so.6(GLIBC_2.4)(64bit)

How should I read that? Is it saying that it requires 4 versions of libc.so.6,
built for different GLIBC versions? Or is it saying that any version of libc is
okay as long as that version is built from GLIBC 2.14, 2.2.5, 2.34, or 2.4?
Also a related question, isn't GLIBC also an rmp / yum package? I see with `yum
search` there's "glibc" but no "GLIBC". Is the fact that the names are similar
a coincidence? Or is it that, in this "libc.so.6(GLIBC_2.14)(64bit)" line,
GLIBC is assumed to be the same as the yum package but with its name
capitalized?


If I see a requirement like

liblldMinGW.so.14()(64bit)

What does the empty ()s denote?
