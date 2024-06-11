from jinja2 import Environment
import jinjapy

loader = jinjapy.register_package("my_package")
env = Environment(loader=loader)

print(loader.list_files())

print(loader.get_template_from_module("my_package.index"))
print(jinjapy.execute_module(env, "my_package.index"))

print("my_package/sub_package/today.html")
print(jinjapy.execute_module(env, "my_package.sub_package.today"))

import my_package.my_module