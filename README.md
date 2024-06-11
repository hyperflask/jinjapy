# Jinjapy

New hybrid file format combining a Jinja template with Python code in a frontmatter

```python
from jinja2 import Environment
import jinjapy

loader = jinjapy.register_package("my_package")
env = Environment(loader=loader)

# execute the module + render the template
# the module globals are used as the template context
template_output = jinjapy.execute_module(env, "my_package.module")

# module is available like any other import
import foo from my_package.module
```

*my_package/module.html*:

```
---
foo = "bar"
---
{{ foo }}
```

## Specification

A jinjapy file contains 2 sections:

- A frontmatter with some Python code (enclosed by lines containg 3 dashes "---")
- A body containing some Jinja template code

Both are optional:

- If the frontmatter is missing, the file only contains a Jinja template
- If the frontmatter is left unclosed (the file starts with "---" on a single line followed by some python code), the file has no template