# Contains functions for managing the reading of the lapyx file,
# extraction and running of the python code, and the generation and
# compilation of the LaTeX file.

from pathlib import Path
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
    return ''.join(
        random.choice(
            string.ascii_uppercase
            + string.ascii_lowercase
            + string.digits
        ) for _ in range(10))


def _find_matching_bracket(string: str) -> int:
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
    # base_dir = os.getcwd()
    base_dir = Path(__file__).parent.absolute() 


def process_file(
    input_file_path: str | Path,
    *,
    compile: bool = True,
    output: str = None,
    temp: str = None,
    debug: bool = False,
    compiler_arguments: str = None,
    keep_figures: bool = False,
    verbose: bool = False,
    quiet: bool = False,
    latex_comments: bool = False
) -> None:
    """Process a ``.tex`` LaPyX file, extracting any Python code blocks and replacing them with their 
    output. The resultant document is then optionally compiled with pdflatex.

    Parameters
    ----------
    input_file_path : str
        Path to the ``.tex`` file to be processed. This is not verified; it is assumed to be a vaild 
        file path to a valid LaTeX document.
    compile : bool, optional, default ``True``
        If ``True``, the resulting new LaTeX file will be compiled with ``pdflatex``.
    output : str, optional, default ``None``
        File name for the compiled ``pdf`` file. The ``.pdf`` file extension will be added if it 
        is ommitted. If not provided, the ouput name will be infered from the input file.
    temp : str, optional, default ``None``
        Path and prefix for any temporary files generated by LaPyX. ``temp`` may be of the form
        ``directory/``, ``directory/prefix``, or ``prefix``. If a directory is provided, it will be
        created if it does not exist, and all temprary files will be placed in that directory. If a
        prefix is provided, all temporary file names will be prefixed accordingly. 
    debug : bool, optional, default ``False``
        If ``True``, the temporary files generated by LaPyX will not be deleted.
    compiler_arguments : str, optional, default ``None``
        If provided, these arguments will be passed to ``pdflatex`` when compiling the document.
        All arguments should be provided as a single string.
    keep_figures : bool, optional, default ``False``
        If ``True``, the figures generated by LaPyX will not be deleted.
    verbose : bool, optional, default ``False``
        If ``True``, more detailed information will be printed to the console, including all output
        from ``pdflatex``.
    quiet : bool, optional, default ``False``
        If ``True``, nothing will be printed to the console except for errors.
    latex_comments : bool, optional, default ``False``
        If ``True``, lines staring with ``%`` will be treated as comments even if they occur inside
        a Python code block.
    """    
    import json
    # set the base_dir
    _set_base_dir()
    global base_dir

    if isinstance(input_file_path, str):
        input_file_path = Path(input_file_path)
    jobname = input_file_path.stem

    if output:
        if isinstance(output, str):
            output = Path(output)
        # add .pdf extension if not present
        output_file_name = output.with_suffix(".pdf")
    else:
        output_file_name = f"{jobname}.pdf"

    if isinstance(base_dir, str):
        base_dir = Path(base_dir)

    if temp:
        # temp is currently a string.
        if temp.endswith("/"):
            temp_dir = Path(temp)
            temp_prefix = ""
        else:
            temp = Path(temp)
            temp_dir = temp.parent
            temp_prefix = temp.stem
    else:
        temp_dir = base_dir
        temp_prefix = ""
        
    temp_prefix += "__"


    # if temp_dir doesn't exist, create it
    if not temp_dir.exists():
        temp_dir.mkdir(parents=True)

    py_out_lines = []
    latex_out_lines = []

    py_out_lines.append(f"""
from lapyx.output import _init, _finish, _setID, export, no_export
from lapyx.components import *

_init("{base_dir.absolute()}","{temp_dir.absolute()}", "{temp_prefix}")
""")

    # assume input_file_path is a valid path, checked by the main program
    with input_file_path.open("r") as input_file:
        input_text = input_file.read()
    
    if not quiet:
        print(f"Found file {input_file_path.absolute()}, extracting Python code...", end = "", flush = True)

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
            new_py_lines, new_latex_line = _handle_inline_py(input_lines[i], latex_comments = latex_comments)
            py_out_lines.extend(new_py_lines)
            latex_out_lines.append(new_latex_line)
            continue

        if py_block_start in line and ("%" not in line or line.find(py_block_start) < line.find("%")):
            new_lines, new_latex_line, skip_lines = _handle_py_block(
                input_lines[i:],
                latex_comments = latex_comments
            )
            py_out_lines.extend(new_lines)
            latex_out_lines.append(new_latex_line)
            continue

        latex_out_lines.append(line)

    py_out_lines.append("_finish()")

    if not quiet:
        print(" Done")

    # write py_out_lines to a temporary file `{temp_dir}/{temp_prefix}lapyx_temp.py`
    temp_py_file_name = temp_dir / f"{temp_prefix}lapyx_temp.py"
    if verbose:
        print(f"Writing extracted Python code to file {temp_py_file_name.absolute()}")

    with temp_py_file_name.open("w") as temp_py_file:
        temp_py_file.write("\n".join(py_out_lines))

    # run the temporary python file as a subprocess
    if not quiet:
        print("Running extracted Python code as subprocess...", end = "", flush = True)
    result = subprocess.run(
        [
            "python3",
            temp_py_file_name.absolute()
        ],
        capture_output=True
    )
    if result.returncode != 0:
        print("Error running python file. stdout:\n\n")
        print(result.stdout.decode("utf-8"))
        raise Exception(result.stderr.decode("utf-8"))
    if not quiet:
        print(" Done")
    if verbose:
        temp_output = result.stdout.decode("utf-8")
        if len(temp_output.strip()) > 0:
            print(f"Python code output:\n{'OUTPUT START':-^40}")
            print(temp_output + f"\n{'OUTPUT END':-^40}\n")
        else:
            print("Python code produced no output to stdout")
    # read the temporary file `lapyx_output.json`
    with (temp_dir / f"{temp_prefix}lapyx_output.json").open("r") as output_file:
        output_json = json.load(output_file)

    new_text = "\n".join(latex_out_lines)

    # replace all instances of \pyID{ID} with the corresponding output
    if verbose:
        print("Replacing Python blocks with output...", end = "", flush = True)
    for ID, output in output_json.items():
        new_text = new_text.replace(f"\\pyID{{{ID}}}", "\n".join(output))
    if verbose:
        print(" Done")


    # write the new text to the output file `base_dir/lapyx_temp.tex`
    latex_temp_file_name = temp_dir / f"{temp_prefix}lapyx_temp.tex"
    if verbose:
        print(f"Writing LaTeX output to file {latex_temp_file_name}")
    with latex_temp_file_name.open("w+") as output_file:
        output_file.write(new_text)

    if compile:
        compile_kwargs = {}
        if compiler_arguments:
            compile_kwargs["compiler_arguments"] = compiler_arguments
        _compile_latex(latex_temp_file_name, verbose = verbose, quiet = quiet, **compile_kwargs)

        # move newly-created pdf to `jobname.pdf`
        if verbose:
            print(f"Moving {latex_temp_file_name.absolute()[:-4]}.pdf to {output_file_name.absolute()}")
        (temp_dir / f"{temp_prefix}lapyx_temp.pdf").rename(output_file_name)
    elif not quiet:
        print("Skikping compilation")

    if not keep_figures:
        # remove all figures, stored in `temp_dir/lapyx_figures`
        if verbose:
            print(f"Removing figures in {temp_dir.absolute()}/lapyx_figures")
        elif not quiet:
            print("Cleaning temporary figures")
        figures_dir = temp_dir / "lapyx_figures"
        if figures_dir.exists():
            for file in figures_dir.iterdir():
                file.unlink()
            figures_dir.rmdir()
            
    if not debug:
        if not quiet:
            print("Cleaning temporary files")
        # remove any temporary files starting with `lapyx_temp`
        for file in temp_dir.iterdir():
            if file.name.startswith(f"{temp_prefix}lapyx_temp"):
                file.unlink()
        (temp_dir / f"{temp_prefix}lapyx_output.json").unlink()
        # if temp_dir is not base_dir, remove it if its empty
        if temp_dir != base_dir and not list(temp_dir.iterdir()):
            temp_dir.rmdir()




def _handle_inline_py(line: str, latex_comments: bool = False) -> Tuple[List[str], str]:
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
            if not last_segment.lstrip().startswith("export(") and not last_segment.lstrip().startswith("import"):
                last_segment = f"export({last_segment})"
        code = "\n".join(code.split(";")[:-1] + [last_segment])

        # add the code to output
        new_lines.append(code)
        # replace the code in the line with the ID
        line = line[:start_index - len(inline_py_start)] + \
            f"\pyID{{{ID}}}" + line[end_index + 1:]
    return new_lines, line


def _handle_py_block(lines: List[str], latex_comments: bool = False) -> Tuple[List[str], str, int]:
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
    if latex_comments:
        # remove any lines which start with "%"
        new_lines = [line for line in new_lines if not line.lstrip().startswith("%")]

    # de-indent all lines based on the first line
    indent = len(new_lines[0]) - len(new_lines[0].lstrip())
    for i, line in enumerate(new_lines):
        new_lines[i] = line[indent:]
    
    last_line = new_lines[-1]
    # if any line matches "\Wexport\(.*?\)" or "\WnoExport\(.*?\)", don't add export
    addExport = not any([re.match(r"^\s*export\(.*?\)", line) or re.match(r"^\s*noExport\(.*?\)", line) for line in new_lines])

    # if last_line doesn't have a match to ^\s*\w+?\s*=\s*[\w\(\{\[].*$ and no previous line has called export or noExport, add export
    if addExport and len(last_line.strip()) > 0 and not re.match(r"^\s*\w+?\s*=\s*[\w\(\{\[].*$", last_line) :
        if not last_line.lstrip().startswith("export(") and not last_line.lstrip().startswith("import"):
            last_line = f"export({last_line})"
    new_lines[-1] = last_line

    # prepend setID to output
    new_lines.insert(0, f"_setID(\"{ID}\")")
    return new_lines, new_latex_line, end_index


def _compile_latex(file_path: str, verbose: bool = False, quiet: bool = False, options: str = "", bibtex: bool = False, bibtex_options: str = "") -> None:
    # compile the LaTeX file, quitting on errors
    pdflatex_call = [
        "pdflatex",
        "-interaction=nonstopmode",
        "-output-directory",
        str(file_path.parent),
        file_path
    ]

    if not quiet and not verbose:
        print("Compiling LaTeX file...", end="", flush=True)
    if verbose:
        print(f"Compiling LaTeX file {file_path}")

    if options:
        pdflatex_call.extend(options.split())
    pdflatex_call.append(file_path)
    result = subprocess.run(pdflatex_call, capture_output=True)
    if result.returncode != 0:
        raise Exception(result.stdout.decode("utf-8"))
    elif verbose:
        print(result.stdout.decode("utf-8"))
    # compile a second time to get references right
    result = subprocess.run(pdflatex_call, capture_output=True)
    if result.returncode != 0:
        raise Exception(result.stdout.decode("utf-8"))
    elif verbose:
        print(result.stdout.decode("utf-8"))
    # compile bibtex if necessary
    if not bibtex:
        # We're done
        if not quiet and not verbose:
            print(" Done")
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
    elif verbose:
        print(result.stdout.decode("utf-8"))
    # compile a third time to get references right
    result = subprocess.run(pdflatex_call, capture_output=True)
    if result.returncode != 0:
        raise Exception(result.stdout.decode("utf-8"))
    elif verbose:
        print(result.stdout.decode("utf-8"))

