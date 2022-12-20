from typing import List
from .parsing import Arg, KeyVal

from .exceptions import LatexParsingError
from .main import _generate_ID, _find_matching_bracket

import re


class Preamble:

    __package_sets = {
        "standard": Arg("geometry, amsmath, amssymb, xcolor, graphicx, hyperref"),
        "tikz standard": Arg("tikz"),
        "tikz libraries": "arrows, arrows.meta, calc, decorations.pathmorphing, positioning",
        "technical": Arg("siunitx, physics, chemfig, circuitikz")
    }

    __lapyx_preamble_macro = r"\py_preamble" # store as class variable so it can be changed 
    # universally at a later date

    def __init__(self, document: str):
        # internally, document and preamble etc will be stored as lists of lines

        self._packages = Arg()
        self._document = document.strip().splitlines()
        self._extract_preamble()
        self._extract_documentclass()
        self._extract_existing_packages()
        self._extract_lapyx_preamble_options()
        self._process_lapyx_preamble_options()
        self._reconstruct_preamble()



    def _extract_preamble(self):
        for i, line in enumerate(self._document):
            if "%" in line:
                line = line[:line.index("%")]
            if "\\begin{document}" in line:
                if i == 0:
                    self._preamble = []
                    # be careful with when to pass the list by reference and when to pass it by value
                    self._body = self._document.copy()
                    return
                self._preamble = self._document[:i]
                self._body = self._document[i:]
                return
        raise LatexParsingError("No \\begin{document} found while searching for preamble")

    def _extract_documentclass(self):
        # extracts the documentclass and any associated options, 
        # and replaces the documentclass macro with an ID to be replaced later
        # If no documentclass is present, then the documentclass and options will be None
        # and the ID will be prepended to the preamble list

        self._ID = _generate_ID()

        for i, line in enumerate(self._preamble):
            if "%" in line:
                line = line[:line.index("%")]
            match = re.match(r"\\documentclass(\[(?P<options>.*)\])?\{(?P<class>.*)\}", line)
            if match is None:
                continue

            options = match.group("options")
            options = Arg(options)
            documentclass = match.group("class")
            self._documentclass = KeyVal(documentclass, options)

            self._preamble[i] = re.sub(
                r"\\documentclass(\[(?P<options>.*)\])?\{(?P<class>.*)\}", 
                f"\\py{{{self._ID}}}", 
                self._preamble[i] # use this instead of line to preserve comments
            )
            return

        self._documentclass = None
        self._preamble.insert(0, f"\\py{{{self._ID}}}")

    def _extract_existing_packages(self):

        usepackage_regex = r"\\usepackage(\[(?P<options>.*)\])?\{(?P<package>.*)\}"

        for i, line in enumerate(self._preamble):
            if "%" in line:
                line = line[:line.index("%")]
            matches = re.finditer(
                usepackage_regex, 
                line
            ) # using this to avoid inconsistent returns from re.findall
            for match in matches:
                options = match.group("options")
                options = Arg(options) # Case for options = None already handled in options_to_dict

                package = match.group("package")
                if package is None:
                    raise LatexParsingError("No package name found in \\usepackage macro: " + line)
                packages = package.split(",")
                for package in packages:
                    self._packages.update([KeyVal(package, options)])
            # remove the usepackage macros from the line
            self._preamble[i] = re.sub(
                usepackage_regex,
                "",
                self._preamble[i]
            )

    def _extract_lapyx_preamble_options(self):
        # extracts the options stored in the lapyx preamble macro
        # returns the options as a dictionary

        for i, line in enumerate(self._preamble):
            if "%" in line:
                line = line[:line.index("%")]
            if self.__lapyx_preamble_macro not in line:
                continue

            macro_start_index = line.find(self.__lapyx_preamble_macro)
            options_start_index = macro_start_index + len(self.__lapyx_preamble_macro)
            options_end_index = _find_matching_bracket(line[options_start_index:]) + options_start_index
            options = line[options_start_index + 1:options_end_index] # +1 to remove the opening bracket
            options = Arg(options)
            self._preamble_macro_options = options
            # remove the macro from the line
            self._preamble[i] = self._preamble[i][:macro_start_index] + self._preamble[i][options_end_index + 1:]
            return
        
        self._preamble_macro_options = Arg()
    
    def _process_lapyx_preamble_options(self):

        """
            1. Extract the documentclass and options as a KeyVal object
                - remove the documentclass from the preamble_macro_options
            2. check for `tikz standard`
                - If present, `add_standard_packages = True`
                - self._packages.update(self.__package_sets["tikz standard"])
                - self._tikz_libraries = self.__package_sets["tikz libraries"]
                - if self._preamble_macro_options[`tikz standard`] is not None:
                    - options = self._preamble_macro_options[`tikz standard`]
                    - If any([not o._has_value for o in options]), raise an error
                    - If any([o.key not in self.__package_sets["tiz standard"] for o in options]), raise an error
                    - self._packages.update(options)
                - remove the tikz standard option from the preamble_macro_options
            3. check for `technical`
                - If present, `add_standard_packages = True`
                - self._packages.update(self.__package_sets["technical"])
                - if self._preamble_macro_options[`technical`] is not None:
                    - options = self._preamble_macro_options[`technical`]
                    - If any([not o._has_value for o in options]), raise an error
                    - If any([o.key not in self.__package_sets["technical"] for o in options]), raise an error
                    - self._packages.update(options)
                - remove the technical option from the preamble_macro_options
            4. if `add_standard_packages = True`
                - self._packages.update(self.__package_sets["standard"])
            5. check for `standard`
                - self._packages.update(self.__package_sets["standard"])
                - if self._preamble_macro_options[`standard`] is not None:
                    - options = self._preamble_macro_options[`standard`]
                    - geometry_options = Arg()
                    - other_options = Arg()
                    - for o in options:
                        - if o.key not in self.__package_sets["standard"]:
                            - geometry_options.append(o)
                        - else:
                            - other_options.append(o)
                    - if len(geometry_options) > 0:
                        - self._packages.update(geometry_options, "geometry")
                    - if len(other_options) > 0:
                        - self._packages.update(other_options)
                - remove the standard option from the preamble_macro_options
            6. self._packages.update(self._preamble_macro_options)
        """

        self._tikz_libraries = ""
        add_standard_packages = False

        # 1. Extract the documentclass and options as a KeyVal object

        if "documentclass" in self._preamble_macro_options:
            new_documentclass = self._preamble_macro_options["documentclass"]
            if len(new_documentclass) > 1:
                raise LatexParsingError("Documentclass macro can only have one option.")
            new_documentclass = new_documentclass[0]
            if self._documentclass is not None and self._documentclass.key != new_documentclass.key:
                raise LatexParsingError("Documentclass already defined in preamble. To add new options to the documentclass, the same documentclass must be specified.\n"
                + f"Expected \"{self._documentclass.key}\" but found \"{new_documentclass.key}\"")
            if self._documentclass is None:
                self._documentclass = new_documentclass
            else:
                self._documentclass.update_value(new_documentclass.value)
            self._preamble_macro_options.remove("documentclass")
        else:
            if self._documentclass is None:
                self._documentclass = KeyVal("article", "fleqn")
            
        # 2. check for `tikz standard`

        if "tikz standard" in self._preamble_macro_options:
            add_standard_packages = True
            self._packages.update(self.__package_sets["tikz standard"])
            self._tikz_libraries = self.__package_sets["tikz libraries"]
            options = self._preamble_macro_options["tikz standard"]
            if options is not None:
                if any([not o._has_value for o in options]):
                    raise LatexParsingError("All options for the `tikz standard` package set must have a value.")
                if any([o.key not in self.__package_sets["tikz standard"] for o in options]):
                    raise LatexParsingError("Invalid option for the `tikz standard` package set.")
                self._packages.update(options)
            self._preamble_macro_options.remove("tikz standard")
        
        # 3. check for `technical`

        if "technical" in self._preamble_macro_options:
            add_standard_packages = True
            self._packages.update(self.__package_sets["technical"])
            options = self._preamble_macro_options["technical"]
            if options is not None:
                if any([not o._has_value for o in options]):
                    raise LatexParsingError("All options for the `technical` package set must have a value.")
                if any([o.key not in self.__package_sets["technical"] for o in options]):
                    raise LatexParsingError("Invalid option for the `technical` package set.")
                self._packages.update(options)
            self._preamble_macro_options.remove("technical")
        
        # 4. if `add_standard_packages = True`

        if add_standard_packages:
            self._packages.update(self.__package_sets["standard"])

        # 5. check for `standard`

        if "standard" in self._preamble_macro_options:
            self._packages.update(self.__package_sets["standard"])
            options = self._preamble_macro_options["standard"]
            geometry_options = Arg()
            other_options = Arg()
            if options is not None:
                for o in options:
                    if o.key not in self.__package_sets["standard"]:
                        geometry_options.append(o)
                    else:
                        other_options.append(o)
                if len(geometry_options) > 0:
                    self._packages.update(geometry_options, "geometry")
                if len(other_options) > 0:
                    self._packages.update(other_options)
            self._preamble_macro_options.remove("standard")
        
        # 6. self._packages.update(self._preamble_macro_options)

        self._packages.update(self._preamble_macro_options)
        

    def _reconstruct_preamble(self):

        if self._documentclass.value is None or len(self._documentclass.value) == 0:
            documentclass_line = "\\documentclass{" + self._documentclass.key + "}"
        else:
            documentclass_line = fr"\documentclass[{self._documentclass.value}]{{{self._documentclass.keyl}}}"

        packages = []
        for package, options in self._packages:
            if options is None or len(options) == 0:
                packages.append("\\usepackage{" + package + "}")
            else:
                opt_string = str(options)
                if opt_string[0] == "{" and opt_string[-1] == "}":
                    opt_string = opt_string[1:-1]
                packages.append(fr"\usepackage[{opt_string}]{{{package}}}")
        
        if self._tikz_libraries is not None and len(self._tikz_libraries) > 0:
            packages.append("\\usetikzlibrary{" + self._tikz_libraries + "}")

        self._preamble = "\n".join(self._preamble).replace(rf"\py{{{self._ID}}}", documentclass_line + "\n" + "\n".join(packages))
        self._document = self._preamble + "\n" + "\n".join(self._body)

