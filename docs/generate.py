import inspect
import importlib
import argparse
from types import ModuleType
from typing import Type, Callable
import os
import json  # just for pretty printing

newline = "\n"

def parse_args():
    # generate [options] <package>
    # -n, --dry-run: don't create any files, just print what would be done
    # o, --output: specify the output directory
    # -h, --help: print help

    parser = argparse.ArgumentParser(
        description="Generate rst file structure for sphinx documentation from a python package.")
    parser.add_argument("-n", "--dry-run", action="store_true",
                        help="Do not create any files, just print what would be done.")
    parser.add_argument("-o", "--output", type=str, default=".",
                        help="Specify the output directory.")
    # get the package name from the command line
    parser.add_argument("package", type=str,
                        help="The python package to document.")
    return parser.parse_args()



def main():
    print("")
    args = parse_args()
    base_dir = args.output
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    package_str = args.package
    package = importlib.import_module(package_str)
    mod_dict = read_module(package)
    # print(
    #     json.dumps(
    #         mod_dict,
    #         # default = lambda x: f"{x.__name__}{' from ' + x.__module__ if not inspect.ismodule(x) else ''}",
    #         default=lambda x: repr(x),
    #         indent=4)
    # )

    # count the total number of files that would be created (two per module, class, and function)
    generate_module(mod_dict, base_dir=base_dir)


ignore_private = True  # Exclude private functions, classes, variables, etc.
ignore_abstract = True  # Exclude abstract classes


def read_module(mod: ModuleType) -> dict:

    # Return cursor to the start of the line, then print full name of module,
    # including parent module if it is a submodule
    print(f"\033[F\033[KFound module {mod.__name__}", end = "\n", flush = True)


    # retrieve a list of
    # - submodules
    # - classes
    # - functions
    # - variables
    #
    # Create a dict with the following structure:
    # { "submodules": [submodule1, submodule2, ...],
    #   "classes": [class1, class2, ...],
    #   "functions": [function1, function2, ...],
    #   "variables": [variable1, variable2, ...] }

    # get any submodules of `mod`, but not modules that are imported
    submodules = []
    for name, obj in inspect.getmembers(mod, inspect.ismodule):
        if obj.__name__.startswith(mod.__name__ + "."):
            submodules.append(read_module(obj))



    # get any classes of `mod`, but not classes that are imported

    # classes = [{"name": name, "class": obj} for name, obj in inspect.getmembers(mod, inspect.isclass)
    #            if obj.__module__ == mod.__name__]
    classes = []
    for name, obj  in inspect.getmembers(mod, inspect.isclass):
        if obj.__module__ == mod.__name__:
            print(f"\033[F\033[KFound class {obj.__qualname__}")
            classes.append({"name": name, "class": obj})
    
    # sort classes into source order using _, line_number = inspect.getsourcelines(obj)
    classes.sort(key=lambda cls: inspect.getsourcelines(cls["class"])[1])

    # get any functions of `mod`, but not functions that are imported
    # functions = [{"name": name, "function": obj} for name, obj in inspect.getmembers(mod, inspect.isfunction)
    #              if obj.__module__ == mod.__name__]
    functions = []
    for name, obj in inspect.getmembers(mod, inspect.isfunction):
        if obj.__module__ == mod.__name__:
            print(f"\033[F\033[KFound function {obj.__qualname__}")
            functions.append({"name": name, "function": obj})

    # sort functions into source order using _, line_number = inspect.getsourcelines(obj)
    functions.sort(key=lambda func: inspect.getsourcelines(func["function"])[1])

    if ignore_private:
        # remove any private functions, classes, variables, etc.
        submodules = [
            submodule for submodule in submodules if not submodule["name"].startswith("_")]
        classes = [cls for cls in classes if not cls["name"].startswith(
            "_") and (ignore_abstract and not inspect.isabstract(cls["class"]))]
        functions = [
            func for func in functions if not func["name"].startswith("_")]

    # for each submodule, call handle_module with parent = mod

    # for i, submodule in enumerate(submodules):
    #     submodules[i]["contents"] = read_module(submodule["module"])

    for i, cls in enumerate(classes):
        classes[i]["contents"] = read_class(cls["class"])

    return {
        "name": mod.__name__,
        "module": mod,
        "contents": {
            "submodules": submodules,
            "classes": classes,
            "functions": functions
        }
    }


def read_class(cls: Type):

    # Return cursor to the start of the line, then print full name of class,
    # including module
    print(f"\033[F\033[KFound class {cls.__qualname__}", end = "\n", flush = True)
    # return a list containing all methods of the class `cls`
    # functions = [{"name": name, "function": obj}
    #              for name, obj in inspect.getmembers(cls, inspect.isfunction)]
    functions = []
    for name, obj in inspect.getmembers(cls, inspect.isfunction):
        print(f"\033[F\033[KFound function {obj.__qualname__}")
        functions.append({"name": name, "function": obj})

    # sort functions into source order using _, line_number = inspect.getsourcelines(obj)
    functions.sort(key=lambda func: inspect.getsourcelines(func["function"])[1])

    if ignore_private:
        functions = [
            func for func in functions if not func["name"].startswith("_")]

    for function in functions:
        read_function(function["function"])

    return functions


def read_function(func: Callable):
    # Return cursor to the start of the line, then print full name of function,
    # including class if it is a method
    print(f"\033[F\033[KFound function {func.__qualname__}", end = "\n", flush = True)


def count_files(mod_dict):
    count = 0
    for key, value in mod_dict["contents"].items():
        if key == "submodules":
            for submodule in value:
                count += count_files(submodule)
        else:
            count += len(value)
    return count * 2

def generate_module(mod: dict, base_dir = ""):
    mod_name_full = mod["module"].__name__
    mod_name = mod["name"]
    mod_dir = os.path.join(base_dir, mod_name_full.replace(".", os.path.sep))
    mod_file_path = os.path.join(base_dir, mod_name_full.replace(".", os.path.sep) + ".rst")
    mod_extras_file_path = os.path.join(base_dir, mod_name_full.replace(".", os.path.sep) + "_extras.rst")

    # If mod_extras_file_path does not exist:
    if not os.path.exists(mod_extras_file_path):
        # Create mod_extras_file_path
        with open(mod_extras_file_path, "w") as f:
            f.write(f"""..
    extra content for {mod_name_full}""")

    # create the directory for the module if it doesn't exist 
    # (need to do this before classes are generated)
    if not os.path.exists(mod_dir):
        os.makedirs(mod_dir)

    for submodule in mod["contents"]["submodules"]:
        generate_module(submodule, base_dir)
    for cls in mod["contents"]["classes"]:
        generate_class(cls, base_dir)
    for func in mod["contents"]["functions"]:
        generate_function(func, base_dir)

    title = mod_name_full
    toc_lines = []
    toc_lines.extend(
        [f"{submodule['name'].replace('.', os.path.sep)}" for submodule in mod["contents"]["submodules"]]
    )
    toc_lines.extend(
        [f"{mod['name'].split('.')[-1]}{os.path.sep}{cls['name']}" for cls in mod["contents"]["classes"]]
    )
    toc_lines.extend(
        [f"{mod['name'].split('.')[-1]}{os.path.sep}{func['name']}" for func in mod["contents"]["functions"]]
    )
    out_string = f""".. _RST {mod_name_full}:

{title}
{'=' * len(title)}

.. toctree::
    :hidden:

    {(newline + ' ' * 4).join([line for line in toc_lines])}

.. include:: {os.path.basename(mod_extras_file_path)}

{'''Contents
--------''' if len(mod["contents"]["classes"]) + len(mod["contents"]["functions"]) > 0 else ''}

.. automodule:: {mod_name_full}
    :members:
    :undoc-members:
    :show-inheritance:
    :inherited-members:
    :noindex:
"""
    
    # write the module file
    with open(mod_file_path, "w+") as f:
        f.write(out_string)
    

def generate_class(cls: dict, base_dir = ""):
    cls_name_full = cls["class"].__module__ + "." + cls["class"].__name__
    cls_name = cls["name"]
    cls_dir = os.path.join(base_dir, cls_name_full.replace(".", os.path.sep))
    cls_file_path = os.path.join(base_dir, cls_name_full.replace(".", os.path.sep) + ".rst")
    cls_extras_file_path = os.path.join(base_dir, cls_name_full.replace(".", os.path.sep) + "_extras.rst")
   
    # If cls_extras_file_path does not exist:
    if not os.path.exists(cls_extras_file_path):
        # Create cls_extras_file_path
        with open(cls_extras_file_path, "w") as f:
            f.write(f"""..
    extra content for {cls_name_full}""")

    # create the directory for the class if it doesn't exist 
    # (need to do this before functions are generated)
    if not os.path.exists(cls_dir):
        os.makedirs(cls_dir)

    for func in cls["contents"]:
        generate_function(func, base_dir, parent_class = cls)

    title = cls_name
    toc_lines = []
    toc_lines.extend(
        [f"{cls['name']}{os.path.sep}{func['name']}" for func in cls["contents"]]
    )
    out_string = f""".. _{cls_name_full}:
    
{title}
{'=' * len(title)}

.. toctree::
    :hidden:

    {(newline + ' ' * 4).join([line for line in toc_lines])}

.. include:: {os.path.basename(cls_extras_file_path)}

Contents
--------
    
.. autoclass:: {cls_name_full}
    :members:
    :undoc-members:
    :show-inheritance:
    :inherited-members:
    :noindex:
"""
    # write the class file
    with open(cls_file_path, "w+") as f:
        f.write(out_string)

def generate_function(func: dict, base_dir = "", parent_class: dict = None):
    if parent_class is not None:
        func_name_full = parent_class["class"].__module__ + "." + parent_class["class"].__name__ + "." + func["name"]
    else:
        func_name_full = func["function"].__module__ + "." + func["function"].__name__
    func_name = func["name"]
    func_file_path = os.path.join(base_dir, func_name_full.replace(".", os.path.sep) + ".rst")
    func_extras_file_path = os.path.join(base_dir, func_name_full.replace(".", os.path.sep) + "_extras.rst")

    # If func_extras_file_path does not exist:
    if not os.path.exists(func_extras_file_path):
        # Create func_extras_file_path
        with open(func_extras_file_path, "w") as f:
            f.write(f"""..
    extra content for {func_name_full}""")

    title = ("" if parent_class is None else parent_class["name"] + ".") + func_name
    out_string = f""".. _RST {func_name_full}:
    
{title}
{'=' * len(title)}

.. autofunction:: {func_name_full}
    :noindex:

.. include:: {os.path.basename(func_extras_file_path)}
"""
    
    # write the function file
    with open(func_file_path, "w+") as f:
        f.write(out_string)

if __name__ == "__main__":
    main()
