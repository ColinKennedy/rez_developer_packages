rez_symbl - Rez **Sym**link **B**ui**l**der

In an environment with thousands of Rez package releases, rez resolves
can be very slow. Even if you use memcache or any of Rez's caching
behaviors to make repeated resolves faster, the initial resolve can
still take a lot of time.

rez_symbl aims to make known, "pre-baked" Rez resolves which are
lightweight and lightning fast to resolve.

## How To Use

- To make a "bake" of "python-2" and "a version of arch"

```sh
rez-env rez_symbl -- python -m rez_symbl bake-from-request "rez_utilities" --output-directory /tmp/location --force
```

There's also a variation which bakes using your current environment
(assuming you're already inside of a Rez resolve).

```sh
rez-env rez_syml -- python -m rez_symbl bake-from-current-environment --output-directory /tmp/location3 --force /tmp/location 
```

Using either command will generate symlinks to /tmp/location.
You can now rez-env using /tmp/location e.g.

```sh
REZ_PACKAGES_PATH=/tmp/location rez-env python-2 arch
```

Now you're resolved into the same environment but at a fraction of the time.
