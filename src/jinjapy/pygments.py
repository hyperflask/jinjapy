from pygments.lexer import inherit, bygroups, using
from pygments.token import *
from pygments.lexers.python import PythonLexer
from pygments.lexers.templates import DjangoLexer


__all__ = ('JinjapyLexer',)


class JinjapyLexer(DjangoLexer):
    name = "jinjapy"
    aliases = ["jpy"]
    filenames = ["*.jpy"]
    tokens = {
        "root": [
            (r"^---\n", Comment, "frontmatter"),
            inherit
        ],
        "frontmatter": [
            (r"(.+?)(\n---\n)", bygroups(using(PythonLexer), Comment), "#pop")
        ]
    }