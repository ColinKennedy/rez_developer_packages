Rez packages can define rez-test commands, which have their own
environment requirements. `rez_test_env` is a small wrapper which can
make a rez-env which includes the test requirements of whatever tests
you desire.

## How To Run
Assuming you have a Rez package called "foo" and a test called "bar"

```sh
rez_test_env foo bar
```

Then you'll be placed in a shell which includes "foo" resolved packages + any requirements needed for "bar".

## Test Options
You can resolve multiple tests at once and use glob expressions.

```sh
rez_test_env foo bar bazz  # Resolve "foo" package with "bar" and "bazz" test requirements
```

```
rez_test_env foo unittest_python_*  # Make a resolved environment for "foo", including all tests which match "unittest_python_*"
```
