# isort_black

[isort](https://github.com/PyCQA/isort) and
[black](https://github.com/psf/black) are both individually great tools but
sometimes they don't play nice when used together. For example, a line with many imports will differ.

black wants this:

```python
from ._core import (
    cli_helper,
    display_levels,
    display_list,
    display_tree,
    exception,
    streamer,
    tree_accumulator,
)
```

isort wants this:

```python
from ._core import (cli_helper, display_levels, display_list, display_tree,
                    exception, streamer, tree_accumulator)
```

Generally, black should be preferred because it's less likely to produce merge
conflicts. This package, `isort_black`, conforms isort so it always recommends
the same thing as black.

See 
https://black.readthedocs.io/en/stable/guides/using_black_with_other_tools.html#isort
for details.


## Testing That It Works
If you call `rez-env isort_black -- isort_black --show-config`, it should
return something like:

```
# ... more stuff ...
"multi_line_output": "VERTICAL_HANGING_INDENT",
"include_trailing_comma": true,
"force_grid_wrap": 0,
"use_parentheses": true,
"ensure_newline_before_comments": true,
"line_length": 88,
# ... more stuff ...
```
