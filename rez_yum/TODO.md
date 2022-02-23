
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
