# Jinjapy

New hybrid file format combining a Jinja template with Python code in a frontmatter.

## Installation

    pip install jinjapy

## Usage

A jinjapy file is a standard python module which is attached to a jinja template.

A folder containing multiple jinjapy files is registered as a python package using `register_package()`.
This returns a Jinja loader than can be used to create a Jinja environment.

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

*my_package/module.jpy*:

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

- If the frontmatter is missing, the file only contains a Jinja template. It won't be available as a python module.
- If the frontmatter is left unclosed (the file starts with "---" on a single line followed by some python code), the file has no template

## Editor support

A [VS Code extension](https://marketplace.visualstudio.com/items?itemName=hyperflask.jinjapy-language-support) is available to add syntax highlighting for jinjapy files.

## Syntax highlighting

A [pyment](https://pygments.org/) lexer is provided, named "jinjapy" or "jpy". It will also match .jpy files.

## How does it work

A custom package finder and package loader is added to python search path. The loader extracts the python code from the frontmatter on load.

The returned Jinja loader does the same for the jinja template: it removes the frontmatter and only returns the remplate code.