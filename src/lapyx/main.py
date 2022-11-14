# Contains functions for managing the reading of the lapyx file,
# extraction and running of the python code, and the generation and
# compilation of the LaTeX file.

import random
import string
import os
import subprocess
from typing import List

base_dir = ""
py_block_start = r"\begin{python}"
py_block_end = r"\end{python}"
inline_py_start = r"\py{"


def generate_ID() -> str:
    """Generates a random ID for the temporary python file"""
    return ''.join(
        random.choice(
            string.ascii_uppercase
            + string.ascii_lowercase
            + string.digits
        ) for _ in range(10))


def find_matching_bracket(string: str) -> int:
    """Finds the index of the matching bracket in a string"""
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


def set_base_dir() -> None:
    # set the base_dir to the current working directory
    global base_dir
    base_dir = os.getcwd()


def process_file(input_file_path: str) -> None:
    import json
    # set the base_dir
    set_base_dir()
    jobname = os.path.splitext(os.path.basename(input_file_path))[0]
    print(jobname)
    temp_py_lines = []
    latex_out_lines = []
    # assume input_file_path is a valid path, checked by the main program
    with open(input_file_path, "r") as input_file:
        input_text = input_file.read()

    temp_py_lines.append(f"""
from lapyx.output import init, finish, setID, export
from lapyx.components import *

init("{base_dir}")
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
            new_py_lines, new_latex_line = handle_inline_py(input_lines[i])
            temp_py_lines.extend(new_py_lines)
            latex_out_lines.append(new_latex_line)
            continue

        if py_block_start in line:
            new_lines, new_latex_line, skip_lines = handle_py_block(
                input_lines[i:])
            temp_py_lines.extend(new_lines)
            latex_out_lines.append(new_latex_line)
            continue

        latex_out_lines.append(line)

    temp_py_lines.append("finish()")

    # write temp_py_lines to a temporary file `base_dir/lapyx_temp.py`
    with open(os.path.join(base_dir, "lapyx_temp.py"), "w+") as temp_py_file:
        temp_py_file.write("\n".join(temp_py_lines))

    # run the temporary python file as a subprocess
    result = subprocess.run(["python3", os.path.join(
        base_dir, "lapyx_temp.py")], capture_output=True)
    if result.returncode != 0:
        raise Exception(result.stderr.decode("utf-8"))

    # read the temporary file `lapyx_output.json`
    with open(os.path.join(base_dir, "lapyx_output.json"), "r") as output_file:
        output_json = json.load(output_file)

    new_text = "\n".join(latex_out_lines)

    # replace all instances of \pyID{ID} with the corresponding output
    for ID, output in output_json.items():
        new_text = new_text.replace(f"\\pyID{{{ID}}}", "\n".join(output))

    # write the new text to the output file `base_dir/lapyx_temp.tex`
    with open(os.path.join(base_dir, "lapyx_temp.tex"), "w+") as output_file:
        output_file.write(new_text)

    compile(os.path.join(base_dir, "lapyx_temp.tex"))

    # move newly-created pdf to `jobname.pdf`
    os.rename(os.path.join(base_dir, "lapyx_temp.pdf"),
              os.path.join(base_dir, f"{jobname}.pdf"))
              
    # remove any temporary files starting with `lapyx_temp`
    for file in os.listdir(base_dir):
        if file.startswith("lapyx_temp"):
            os.remove(os.path.join(base_dir, file))
    os.remove(os.path.join(base_dir, "lapyx_output.json"))


def handle_inline_py(line: str) -> List[str]:
    new_lines = []
    while inline_py_start in line:
        # find the first instance of inline_py_start
        start_index = line.find(inline_py_start) + len(inline_py_start)
        code_length = find_matching_bracket(line[start_index - 1:])
        if code_length == -1:
            raise Exception("No matching bracket found")
        end_index = start_index + code_length - 1
        code = line[start_index:end_index]
        # generate an ID for this code block
        ID = generate_ID()
        # add setID to output
        new_lines.append(f"setID(\"{ID}\")")
        # add the code to output
        new_lines.append(code)
        # replace the code in the line with the ID
        line = line[:start_index - len(inline_py_start)] + \
            f"\pyID{{{ID}}}" + line[end_index + 1:]
    return new_lines, line


def handle_py_block(lines: List[str]) -> List[str]:
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
    ID = generate_ID()
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

    # de-indent all lines based on the first line
    indent = len(new_lines[0]) - len(new_lines[0].lstrip())
    for i, line in enumerate(new_lines):
        new_lines[i] = line[indent:]
    # prepend setID to output
    new_lines.insert(0, f"setID(\"{ID}\")")
    return new_lines, new_latex_line, end_index

def compile(file_path: str, bibtex: bool = False) -> None:
    # compile the LaTeX file, quitting on errors
    result = subprocess.run(["pdflatex", "-halt-on-error",
                            os.path.join(base_dir, "lapyx_temp.tex")], capture_output=True)
    if result.returncode != 0:
        raise Exception(result.stderr.decode("utf-8"))
    # compile a second time to get references right
    result = subprocess.run(["pdflatex", "-halt-on-error",
                            os.path.join(base_dir, "lapyx_temp.tex")], capture_output=True)
    if result.returncode != 0:
        raise Exception(result.stderr.decode("utf-8"))
    # compile bibtex if necessary
    if not bibtex:
        # We're done
        return
    
    # compile bibtex
    result = subprocess.run(["bibtex", os.path.join(
        base_dir, "lapyx_temp.aux")], capture_output=True)
    if result.returncode != 0:
        raise Exception(result.stderr.decode("utf-8"))
    # compile a third time to get references right
    result = subprocess.run(["pdflatex", "-halt-on-error",
                            os.path.join(base_dir, "lapyx_temp.tex")], capture_output=True)
    if result.returncode != 0:
        raise Exception(result.stderr.decode("utf-8"))


