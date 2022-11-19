# Contains functions for managing the reading of the lapyx file,
# extraction and running of the python code, and the generation and
# compilation of the LaTeX file.

import random
import string
import os
import subprocess
from typing import List, Tuple
import re

base_dir = ""
py_block_start = r"\begin{python}"
py_block_end = r"\end{python}"
inline_py_start = r"\py{"



def _generate_ID() -> str:
    """Generate a random 10-character ID

    Returns
    -------
    str
        A random 10-character ID, consisting of upper- and lower-case letters and digits.
    """    
    return ''.join(
        random.choice(
            string.ascii_uppercase
            + string.ascii_lowercase
            + string.digits
        ) for _ in range(10))


def _find_matching_bracket(string: str) -> int:
    """Find the offset of a matching bracket in `string`, assuming that the first character of `string` is the opening bracket.

    Parameters
    ----------
    string : str
        The tring in which to find the matching bracket.

    Returns
    -------
    int
        The index of the matching bracket, or None if no matching bracket is found.
    """    

    bracketPairs = {
        "{": "}",
        "[": "]",
        "(": ")"
    }
    endBracket = bracketPairs[string[0]]
    bracketCount = 1
    for i in range(1, len(string)):
        if string[i] == string[0]:
            bracketCount += 1
        elif string[i] == endBracket:
            bracketCount -= 1
        if bracketCount == 0:
            return i
    return None


def _set_base_dir() -> None:
    global base_dir
    base_dir = os.getcwd()


def process_file(
    input_file_path: str,
    *,
    compile: bool = True,
    output: str = None,
    temp: str = None,
    debug: bool = False,
    compiler_arguments: str = None,
    keep_figures: bool = False
) -> None:
    """Process a LaPyX file, extracting and running any Python code, then generating and optionally compiling the LaTeX file.

    Parameters
    ----------
    input_file_path : str
        The file path to the LaPyX file. This is not checked for validity; it is assumed this has already been done.    
    compile : bool, optional
        If `False`, the generated LaTeX file is not compiled, by default True
    output : str, optional
        If provided, this will be used as the base name and path for the final compiled .pdf file, by default None
    temp : str, optional
        If provided, any temporary files created by LaPyX will be prefixed by this file path, creating directories if necessary, by default None
    debug : bool, optional
        If `True`, all temporary files created by LaPyX will not be deleted after compilation, by default False
    compiler_arguments : str, optional
        Additional arguments to be passed to the LaTeX compiler. This should be a single string, by default None
    keep_figures : bool, optional
        If `True`, any temporary figures created by LaPyX will not be deleted after compilation, by default False
    """
    import json
    # set the base_dir
    _set_base_dir()

    jobname = os.path.splitext(os.path.basename(input_file_path))[0]

    if output:
        # add .pdf extension if not present
        output_file_name = output + \
            (".pdf" if not output.endswith(".pdf") else "")
    else:
        output_file_name = jobname + ".pdf"

    temp_dir = base_dir
    temp_prefix = ""
    if temp:
        # if temp is an absolute path
        if os.path.isabs(temp):
            prefix = ""
        else:
            prefix = base_dir
        temp_dir = os.path.abspath(os.path.join(prefix, os.path.dirname(temp)))
        temp_prefix = os.path.basename(temp)
        if temp_prefix:
            temp_prefix += "__"

    # if temp_dir doesn't exist, create it
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    py_out_lines = []
    latex_out_lines = []
    # assume input_file_path is a valid path, checked by the main program
    with open(input_file_path, "r") as input_file:
        input_text = input_file.read()

    py_out_lines.append(f"""
from lapyx.output import _init, _finish, _setID, export, no_export
from lapyx.components import *

_init("{base_dir}","{temp_dir}", "{temp_prefix}")
""")

    skip_lines = 0
    input_lines = input_text.splitlines()
    for i, line in enumerate(input_lines):
        if skip_lines > 0:
            skip_lines -= 1
            continue

        if line.startswith("%"):
            # LaTeX comment, ignore
            latex_out_lines.append(line)
            continue

        if inline_py_start in line:
            # inline python code
            new_py_lines, new_latex_line = _handle_inline_py(input_lines[i])
            py_out_lines.extend(new_py_lines)
            latex_out_lines.append(new_latex_line)
            continue

        if py_block_start in line and ("%" not in line or line.find(py_block_start) < line.find("%")):
            new_lines, new_latex_line, skip_lines = _handle_py_block(
                input_lines[i:])
            py_out_lines.extend(new_lines)
            latex_out_lines.append(new_latex_line)
            continue

        latex_out_lines.append(line)

    py_out_lines.append("_finish()")

    # write py_out_lines to a temporary file `{temp_dir}/{temp_prefix}lapyx_temp.py`
    with open(os.path.join(temp_dir, f"{temp_prefix}lapyx_temp.py"), "w+") as temp_py_file:
        temp_py_file.write("\n".join(py_out_lines))

    # run the temporary python file as a subprocess
    result = subprocess.run(
        [
            "python3",
            os.path.join(temp_dir, f"{temp_prefix}lapyx_temp.py")
        ],
        capture_output=True
    )
    if result.returncode != 0:
        print("Error running python file. stdout:\n\n")
        print(result.stdout.decode("utf-8"))
        raise Exception(result.stderr.decode("utf-8"))

    # read the temporary file `lapyx_output.json`
    with open(os.path.join(temp_dir, f"{temp_prefix}lapyx_output.json"), "r") as output_file:
        output_json = json.load(output_file)

    new_text = "\n".join(latex_out_lines)

    # replace all instances of \pyID{ID} with the corresponding output
    for ID, output in output_json.items():
        new_text = new_text.replace(f"\\pyID{{{ID}}}", "\n".join(output))

    # write the new text to the output file `base_dir/lapyx_temp.tex`
    with open(os.path.join(temp_dir, f"{temp_prefix}lapyx_temp.tex"), "w+") as output_file:
        output_file.write(new_text)

    if compile:
        compile_kwargs = {}
        if compiler_arguments:
            compile_kwargs["compiler_arguments"] = compiler_arguments
        _compile_latex(os.path.join(
            temp_dir, f"{temp_prefix}lapyx_temp.tex"), **compile_kwargs)

        # move newly-created pdf to `jobname.pdf`
        os.rename(os.path.join(temp_dir, f"{temp_prefix}lapyx_temp.pdf"),
                  os.path.join(base_dir, output_file_name))

    if not keep_figures:
        # remove all figures, stored in `temp_dir/lapyx_figures`
        figures_dir = os.path.join(temp_dir, "lapyx_figures")
        if os.path.exists(figures_dir):
            for file in os.listdir(figures_dir):
                os.remove(os.path.join(figures_dir, file))
            os.rmdir(figures_dir)
            
    if not debug:
        # remove any temporary files starting with `lapyx_temp`
        for file in os.listdir(temp_dir):
            if file.startswith(f"{temp_prefix}lapyx_temp"):
                os.remove(os.path.join(temp_dir, file))
        os.remove(os.path.join(temp_dir, f"{temp_prefix}lapyx_output.json"))
        # if temp_dir is not base_dir, remove it if its empty
        if temp_dir != base_dir and not os.listdir(temp_dir):
            os.rmdir(temp_dir)




def _handle_inline_py(line: str) -> Tuple[List[str], str]:
    """Finds (non-recursively) and handles all inline python in a line of text.

    Parameters
    ----------
    line : str
        The line of text to be processed.

    Returns
    -------
    new_lines: List[str]
        The new lines of Python code to be added to the temporary Python file.
    line: str
        The line to be written to the output LaTeX file in place of the input line.        

    Raises
    ------
    Exception
        If no closing brace can be found to exit the `\py` macro argument, an exception is raised.
    """    

    new_lines = []
    while inline_py_start in line:
        # find the first instance of inline_py_start
        start_index = line.find(inline_py_start) + len(inline_py_start)
        code_length = _find_matching_bracket(line[start_index - 1:])
        if code_length == None:
            raise Exception("No matching bracket found")
        end_index = start_index + code_length - 1
        code = line[start_index:end_index]
        # generate an ID for this code block
        ID = _generate_ID()
        # add setID to output
        new_lines.append(f"_setID(\"{ID}\")")
        # if the code is a single line, does not call export, and does not have an = sign, add export

        last_segment = code.split(";")[-1]
        # if last_segment doesn't have a match to ^\s*\w+?\s*=\s*[\w\(\{\[].*$, add export
        if len(last_segment.strip()) > 0 and not re.match(r"^\s*\w+?\s*=\s*[\w\(\{\[].*$", last_segment):
            if not last_segment.lstrip().startswith("export("):
                last_segment = f"export({last_segment})"
        code = "\n".join(code.split(";")[:-1] + [last_segment])

        # add the code to output
        new_lines.append(code)
        # replace the code in the line with the ID
        line = line[:start_index - len(inline_py_start)] + \
            f"\pyID{{{ID}}}" + line[end_index + 1:]
    return new_lines, line


def _handle_py_block(lines: List[str]) -> Tuple[List[str], str, int]:
    """Finds and handles the python code block started on the first line of lines

    Parameters
    ----------
    lines : List[str]
        List of all lines of text starting from the line containing the start of the python code block.

    Returns
    -------
    new_lines: List[str]
        The new lines of Python code to be added to the temporary Python file.
    line: str
        The line to be written to the output LaTeX file in place of the input line.
    line_index: int
        The number of lines to skip in the main loop. This is the number of lines in the python code block, including the `\begin` and `\end` environment lines.
    """  
    new_lines = []
    # find the end of the python block
    end_index = 0
    for i, line in enumerate(lines):
        if py_block_end in line:
            end_index = i
            break
    # extract the python code
    code_start_column = lines[0].find(py_block_start) + len(py_block_start)
    pre_latex = lines[0][:code_start_column - len(py_block_start)]
    code_end_column = lines[end_index].find(py_block_end)
    post_latex = lines[end_index][code_end_column + len(py_block_end):]
    # generate ID
    ID = _generate_ID()
    new_latex_line = pre_latex + f"\pyID{{{ID}}}" + post_latex
    # add the code to output
    # if there is code on the first line, add it
    if code_start_column < len(lines[0].rstrip()):
        new_lines.append(lines[0][code_start_column:].rstrip())
    # add the rest of the lines
    new_lines.extend(lines[1:end_index])
    # if there is code on the last line, add it
    if lines[end_index][:code_end_column].strip() != "":
        new_lines.append(lines[end_index][:code_end_column].rstrip())

    # remove any lines which are just a comment or whitespace
    new_lines = [line for line in new_lines if not re.match(r"^\s*#.*$", line) and line.strip() != ""]

    # de-indent all lines based on the first line
    indent = len(new_lines[0]) - len(new_lines[0].lstrip())
    for i, line in enumerate(new_lines):
        new_lines[i] = line[indent:]
    
    last_line = new_lines[-1]
    # if last_line doesn't have a match to ^\s*\w+?\s*=\s*[\w\(\{\[].*$, add export
    if len(last_line.strip()) > 0 and not re.match(r"^\s*\w+?\s*=\s*[\w\(\{\[].*$", last_line):
        if not last_line.lstrip().startswith("export("):
            last_line = f"export({last_line})"
    new_lines[-1] = last_line

    # prepend setID to output
    new_lines.insert(0, f"_setID(\"{ID}\")")
    return new_lines, new_latex_line, end_index


def _compile_latex(file_path: str, options: str = "", bibtex: bool = False, bibtex_options: str = "") -> None:
    """Compiles the temporary LaTeX file using pdflatex

    Parameters
    ----------
    file_path : str
        file path to be compiled
    options : str, optional
        Additional command line arguments to be passed to `pdflatex` as a string, by default ""
    bibtex : bool, optional
        If `True`, `bibtex` will be run after `pdflatex`, by default False
    bibtex_options : str, optional
        Additional command line arguments to be passed to `bibtex` as a string, by default ""

    Raises
    ------
    Exception
        If `pdflatex` or `bibtex` encounter an error, compilation will be halted and the error will be passed forward as an exception.
    """

    # compile the LaTeX file, quitting on errors
    pdflatex_call = [
        "pdflatex",
        "-interaction=nonstopmode",
        "-output-directory",
        os.path.dirname(file_path),
        file_path
    ]
    if options:
        pdflatex_call.extend(options.split())
    pdflatex_call.append(file_path)
    result = subprocess.run(pdflatex_call, capture_output=True)
    if result.returncode != 0:
        raise Exception(result.stdout.decode("utf-8"))
    # compile a second time to get references right
    result = subprocess.run(pdflatex_call, capture_output=True)
    if result.returncode != 0:
        raise Exception(result.stdout.decode("utf-8"))
    # compile bibtex if necessary
    if not bibtex:
        # We're done
        return

    bibtex_call = ["bibtex"]
    if bibtex_options:
        bibtex_call.extend(bibtex_options.split())
    # append the file path, but with .aux instead of .tex
    bibtex_call.append(file_path[:-4] + ".aux")
    # compile bibtex
    result = subprocess.run(bibtex_call, capture_output=True)
    if result.returncode != 0:
        raise Exception(result.stdout.decode("utf-8"))
    # compile a third time to get references right
    result = subprocess.run(pdflatex_call, capture_output=True)
    if result.returncode != 0:
        raise Exception(result.stdout.decode("utf-8"))
