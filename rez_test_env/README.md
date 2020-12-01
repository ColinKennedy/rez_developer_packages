`rez_test_env` is a small wrapper for `rez-env`. It gives a Rez
environment + any requirements of your requested Rez tests.


## How To Run
Assuming you have a Rez package called "foo" and a test called "bar"

```sh
rez_test_env request foo bar
```

Or if you want to just run a test from the package that's in your
current directory ($PWD), then use this.

```sh
rez_test_env directory bar
```

And you can override the directory, if you want.


```sh
rez_test_env directory --directory /some/path/on/disk/to/foo bar
```

In all 3 cases, you'll be placed in a shell which includes "foo"
resolved packages + any requirements needed for the "bar" test.


## Test Options
### Multiple Requests
You can resolve multiple tests at once and use glob expressions.

```sh
rez_test_env request foo bar bazz  # Resolve "foo" package with "bar" and "bazz" test requirements
```

### Glob matching
If you want to match more than one test at a time and you know the tests
all have a similar name convention, you can use glob "\*" to resolve all
of the tests at once.

```sh
rez_test_env foo unittest_python_*  # Make a resolved environment for "foo", including all tests which match "unittest_python_*"
```
