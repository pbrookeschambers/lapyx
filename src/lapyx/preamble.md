 - Add documentclass if not already present
 - Add packages 
    - `standard` : standard LaTeX packages
        - `geometry`, with `margin` specified
        - `amsmath`
        - `amssymb`
        - `xcolor`
        - `graphicx`
        - `hyperref`
    - `tikz`
        - All `standard` packages
        - `tikz`
        - `pgfplots`
        - tikz libraries:
            - `arrows`
            - `arrows.meta`
            - `calc`
            - `decorations.pathmorphing`
            - `positioning`
    - `technical`
        - All `standard` packages
        - `siunitx`
        - `physics`
        - `chemfig`
        - `circuitikz`



# `main()`

- Takes in the entire document as a string
- extracts the preamble from the document
- searches for documentclass, recording whether it's present
- searches for any included packages
    - Saves the package name and options into the `packages` dictionary
    - removes the `\usepackage` statement from the document
- searches for a `\py_preamble` (`\lapyx_preamble`?) macro
    - Processes the options
        - adds a documentclass if it wasn't already present
        - adds any packages, combining options for packages that are already present
    - removes the `\py_preamble` macro from the document
- adds the documentclass and packages to the document
- returns the document

## `extract_preamble()`

- Takes in the entire document as a string
- returns the preamble as a string

## `extract_document_class()`

- Takes in the entire preamble as a string
- Searches line-by-line for the `\documentclass` command, taking into account whether it's commented out
- extracts the documentclass (str) and options (dict)
- replaces the `\documentclass` command with a unique ID from _generate_ID(): f"\py{{{ID}}}"
- returns (preamble, documentclass, options, ID)
                     ^-----------^  ^-----^  ^^
                     |---None if not present--|
## `extract_packages()`

- Takes in the entire preamble as a string, and a packages dictionary
- Searches line-by-line for the `\usepackage` command, taking into account whether it's commented out
- extracts the package name (str) and options (dict)
    - Adds the package and options to the packages dictionary, updating options if the package is already present 
    - Removes the `\usepackage` command from the preamble
- returns preamble (packages is edited in-place)

## `process_preamble_macro()`

- Takes in the entire preamble as a string, and a packages dictionary, and a bool indicating whether a documentclass was present
- Searches line-by-line for the `\py_preamble` (`\lapyx_preamble`?) command, taking into account whether it's commented out
- extracts the options (dict)
- removes the `\py_preamble` command from the preamble
- Processes the options
    - Special options can be:
        - `documentclass = class`, `documentclass = {class, options}` 
        - `standard`, `standard = options`, `standard = {package = options}`
            - If options are specified for standard but aren't a package, then they will by default be passed to the geometry package
        - `tikz standard`, `tikz standard = options`, `tikz standard = {package = options}`
            - If options are specified for tikz standard but aren't a package, then they will by default be passed to the tikz package.
        - `technical`, `technical = {package = options}`
    - Any unknown keys will be assumed to be a package and added to the packages dictionary, with its associated options
-


```python
if "documentclass" in self._preamble_macro_options:
            # We could extract this into a separate function, but really what's the point?
            dclass_value = self._preamble_macro_options["documentclass"]
            if isinstance(dclass_value, str):
                dclass_name = dclass_value
                dclass_options = {}
            elif isinstance(dclass_value, Arg):
                if len(dclass_value) != 1:
                    raise LatexParsingError("Invalid documentclass value.\n" + 
                        "The documentclass value must be a string or a dictionary with a single key-value pair, the key of which should be the name of the documentclass.\n" + 
                        "E.g., \t" + self.__lapyx_preamble_macro + "{documentclass = article}\n" +
                        "\t" + self.__lapyx_preamble_macro + "{documentclass = {article}}" + "\n" + 
                        "\t" + self.__lapyx_preamble_macro + "{documentclass = {article = {a4paper, fleqn}}}"
                    )
                dclass_name = dclass_value[0].key
                dclass_options = dclass_value[0].value
            else:
                raise LatexParsingError("Invalid documentclass value encountered after processing. This is an internal error. Please report it.")                

            if self._documentclass is not None and self._documentclass.key != dclass_name:
                raise LatexParsingError(
                    "Documentclass specified in lapyx preamble macro does not match documentclass specified in document.\n" + 
                    "Recieved: \t" + self.__lapyx_preamble_macro + "{documentclass = " + dclass_name + "}\n" +
                    "Expected: \t" + self.__lapyx_preamble_macro + "{documentclass = " + self._documentclass + "}"
                )
            
            # remove the documentclass option from the preamble macro options
            del self._preamble_macro_options["documentclass"]


            if self._documentclass is None:
                self._documentclass = KeyVal(dclass_name, dclass_options)
            else:
                self._documentclass.update_value(dclass_options)

        elif self._documentclass is None:
                self._documentclass = KeyVal("article", Arg("fleqn, a4paper"))


        adding_standard_packages = False
        if "tikz standard" in self._preamble_macro_options:
            options = self._preamble_macro_options["tikz standard"]
            # we're adding all packages from self._package_sets["tikz standard"] to the packages dict, and removing the option from the preamble macro options
            # also adding all libraries from self._package_sets["tikz libraries"] to the libraries dict, creating it first.
            adding_standard_packages = True
            for package in self.__package_sets["tikz standard"]:
                if options is not None and package in options:
                    self._packages.update([KeyVal(package, options)])
                    del options[package]
                else:
                    self._packages.update([KeyVal(package)])
            # if we have any options left over, raise an error.
            if options is not None and len(options) > 0:
                raise LatexParsingError(
                    "Invalid option(s) specified for tikz standard: " + str(options) + "\n" +
                    "The `tikz standard` package set does not allow options which are not explicitly associated with a package."
                )
            self._tikz_libraries = self.__package_sets["tikz libraries"] # no options to bother with here
            del self._preamble_macro_options["tikz standard"]
        
        if "technical" in self._preamble_macro_options:
            options = self._preamble_macro_options["technical"]
            # we're adding all packages from self._package_sets["technical"] to the packages dict, and removing the option from the preamble macro options
            adding_standard_packages = True
            for package in self.__package_sets["technical"]:
                if options is not None and package in options:
                    self._packages.update([KeyVal(package, options)])
                    del options[package]
                else:
                    self._packages.update([KeyVal(package)])
            # if we have any options left over, raise an error.
            if options is not None and len(options) > 0:
                raise LatexParsingError(
                    "Invalid option(s) specified for technical: " + str(options) + "\n" +
                    "The `technical` package set does not allow options which are not explicitly associated with a package."
                )
            del self._preamble_macro_options["technical"]

        if adding_standard_packages:
            for package in self.__package_sets["standard"]:
                if not package in self._packages:
                    self._packages.update([KeyVal(package)])
                
        if "standard" in self._preamble_macro_options:
            options = self._preamble_macro_options["standard"]
            # we're adding all packages from self._package_sets["standard"] to the packages dict, and removing the option from the preamble macro options
            for package in self.__package_sets["standard"]:
                if options is not None and package in options:
                    self._packages.update(options[package], key = package)
                    del options[package]
                else:
                    self._packages.append([KeyVal(package)])
            # if we have any options left over, pass them to the `geometry` package
            if options is not None and len(options) > 0:
                self._packages.update(options, key = "geometry")
            if "standard" in self._preamble_macro_options:
                del self._preamble_macro_options["standard"]
        
        # now any remaining keys in self._preamble_macro_options are packages and their options. Add them all
        self._packages.update(self._preamble_macro_options)
```