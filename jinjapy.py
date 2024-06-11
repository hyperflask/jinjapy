import sys
import os.path
import runpy
from importlib.abc import MetaPathFinder, SourceLoader
from importlib.util import spec_from_file_location
from importlib.machinery import SourceFileLoader
from jinja2 import PackageLoader, ChoiceLoader, TemplateNotFound


FILE_EXT = "jpy"


def register_package(package_name, path=None, template_prefix=None, file_exts=None, env=None):
    if template_prefix is None:
        template_prefix = package_name.replace(".", os.sep) + os.sep
    elif template_prefix:
        template_prefix = template_prefix.rstrip(os.sep) + os.sep

    sys.meta_path.insert(0, JinjapyPackageFinder(package_name, path, template_prefix, file_exts))

    loader = JinjapyLoader(package_name, template_prefix, file_exts)
    if env:
        env.loader = ChoiceLoader([env.loader, loader]) if env.loader else loader
    return loader


def execute_module(env, module_name, **globals):
    ctx = runpy.run_module(module_name, globals)
    if "__jinja_template__" in ctx:
        return env.get_template(ctx["__jinja_template__"]).render(**ctx)
    return ""


class JinjapyLoader(PackageLoader):
    def __init__(self, package_name, prefix=None, file_exts=None):
        super().__init__(package_name, "")
        self.prefix = prefix
        self.file_exts = file_exts or [FILE_EXT]

    def get_source(self, environment, template):
        source, frontmatter, filename, uptodate = self._split_source(template)
        return source, filename, uptodate
    
    def split_source(self, template):
        source, frontmatter, filename, uptodate = self._split_source(template)
        return source, frontmatter
    
    def _split_source(self, template):
        if (self.prefix and not template.startswith(self.prefix)):
            raise TemplateNotFound(template)
        if self.prefix and template.startswith(self.prefix):
            template = template[len(self.prefix):]
        source, filename, uptodate = super().get_source(None, template)
        source, frontmatter = extract_frontmatter(source)
        if template.endswith(".py"):
            return None, source, filename, uptodate
        return source, frontmatter, filename, uptodate
    
    def list_files(self, module_with_package=True, with_template_prefix=True, empty_template_for_pymodules=True):
        results = []
        for template in super().list_templates():
            if "__pycache__" in template:
                continue
            module_name, ext = template.rsplit(".", 1)
            if ext == "py" and empty_template_for_pymodules:
                template = None
            elif ext != "py" and ext not in self.file_exts:
                module_name = None
            if template and self.prefix and with_template_prefix:
                template = self.prefix + template
            if module_name:
                module_name = module_name.strip(os.sep).replace(os.sep, '.')
                if module_with_package:
                    module_name = f"{self.package_name}.{module_name}"
            results.append((module_name, template))
        return results
    
    def list_templates(self):
        return [r[1] for r in self.list_files() if r[1]]
    
    def list_modules(self, with_package=True):
        return [r[0] for r in self.list_files(with_package) if r[0]]
    
    def get_file_from_module(self, module_name):
        for m, t in self.list_files(empty_template_for_pymodules=False):
            if m == module_name:
                return t
    
    def get_template_from_module(self, module_name):
        for m, t in self.list_files():
            if m == module_name:
                return t
    
    def get_module_from_template(self, template):
        for m, t in self.list_files():
            if t == template:
                return m


class JinjapyPackageFinder(MetaPathFinder):
    def __init__(self, package_name, path=None, template_prefix=None, file_exts=None):
        if not path:
            path = os.path.join(os.getcwd(), package_name.replace(".", os.sep))
        self.package_name = package_name
        self.path = path
        self.template_prefix = template_prefix
        self.file_exts = file_exts or [FILE_EXT]

    def find_spec(self, fullname, path, target=None):
        if not fullname.startswith(self.package_name):
            return
        
        if fullname == self.package_name:
            relname = ""
        else:
            relname = fullname[len(self.package_name)+1:].replace(".", os.sep)

        if os.path.isdir(os.path.join(self.path, relname)):
            filename = os.path.join(self.path, relname, "__init__.py")
            loader_class = SourceFileLoader if os.path.exists(filename) else EmptyFileLoader
            return spec_from_file_location(fullname, filename, loader=loader_class(fullname, filename),
                submodule_search_locations=[os.path.join(self.path, relname)])
        
        filename = os.path.join(self.path, f"{relname}.py")
        if os.path.exists(filename):
            return spec_from_file_location(fullname, filename, loader=SourceFileLoader(fullname, filename),
                                            submodule_search_locations=None)
        
        for ext in self.file_exts:
            filename = os.path.join(self.path, f"{relname}.{ext}")
            if os.path.exists(filename):
                template = f"{relname}.{ext}"
                if self.template_prefix:
                    template = f"{self.template_prefix}{template}"
                return spec_from_file_location(fullname, filename, loader=JinjapyFileLoader(fullname, filename, template),
                                                submodule_search_locations=None)


class JinjapyFileLoader(SourceLoader):
    def __init__(self, fullname, filename, template):
        self.fullname = fullname
        self.filename = filename
        self.template = template

    def get_filename(self, fullname):
        return self.filename

    def get_data(self, filename):
        with open(filename) as f:
            source = f.read()
        source = extract_frontmatter(source)[1] or ""
        return "\n%s\n\n__jinja_template__ = '%s'" % (source, self.template)


class EmptyFileLoader(SourceLoader):
    def __init__(self, fullname, filename):
        self.fullname = fullname
        self.filename = filename

    def get_filename(self, fullname):
        return self.filename

    def get_data(self, filename):
        return ""


def extract_frontmatter(source, loads=None):
    if source.startswith("---\n"):
        frontmatter_end = source.find("\n---\n", 4)
        if frontmatter_end == -1:
            frontmatter = source[4:]
            source = ""
        else:
            frontmatter = source[4:frontmatter_end]
            source = source[frontmatter_end + 5:]
        if loads:
            frontmatter = loads(frontmatter)
        return source, frontmatter
    return source, None
