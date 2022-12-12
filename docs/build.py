#!/usr/bin/env python3


import argparse
import subprocess
import os
from termcolor import colored
from capture import capture_subprocess_output
from tabulate import tabulate
import re


def center(text: str):
    terminal_width = os.get_terminal_size().columns
    lines = text.splitlines()
    for i, line in enumerate(lines):
        lines[i] = line.center(terminal_width)
    return "\n".join(lines)

def colour_table(table: str, color: str, outline_only: bool = False):
    # start colour at ╒, ╞, ├, and ╘
    # end colour at ╕, ╡, ┤, and ╛
    # colour │ individually

    if color is None:
        return table
    
    # map colour to ansii escape code
    color_map = {
        "red": "\033[31m",
        "yellow": "\033[33m",
        "green": "\033[32m"
    }

    code = color_map[color]
    normal = "\033[0m"

    if outline_only:
        # replace ╒, ╞, and ╘ with code + ╒, code + ╞, and code + ╘
        # replace ╕, ╡, and ╛ with ╕ + normal, ╡ + normal, and ╛ + normal
        # replace ├ and ┤ with code + ├ + normal and code + ┤ + normal
        # if line starts and ends with │, replace first and last with code + │ + normal

        lines = table.splitlines()
        left_pad = len(lines[0]) - len(lines[0].lstrip())
        right_pad = len(lines[0]) - len(lines[0].rstrip())
        lines = [l.strip() for l in lines]

        # if any line starts with ╞, we're have a header
        in_header = any(line.startswith("╞") for line in lines)
        for i, line in enumerate(lines):
            if in_header:
                lines[i] = " " * left_pad + code + line + normal + " " * right_pad
                if line.startswith("╞"):
                    in_header = False
                continue
            if line.startswith("╘"):
                lines[i] = " " * left_pad + code + line + normal + " " * right_pad
                continue
            lines[i] = " " * left_pad + code + line[0] + normal + line[1:-1] + code + line[-1] + normal + " " * right_pad
            
        return "\n".join(lines)

    table = table.replace("╒", code + "╒")   \
                 .replace("╞", code + "╞")   \
                 .replace("├", code + "├")   \
                 .replace("╘", code + "╘")   \
                 .replace("╕", "╕" + normal) \
                 .replace("╡", "╡" + normal) \
                 .replace("┤", "┤" + normal) \
                 .replace("╛", "╛" + normal) \
                 .replace("│", code + "│" + normal)

    return table


def parse_args():
    # Parse command line arguments
    # -r, --regenerate: If true, regenerate the entire .rst file structure
    # -p, --plots: If true, regenerate the plots
    # -v, --verbose: If true, print more information
    parser = argparse.ArgumentParser()

    parser.add_argument("-r", "--regenerate", action="store_true",
                        help="regenerate the entire .rst file structure.")
    parser.add_argument("-p", "--plots", action="store_true",
                        help="regenerate the plots.")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="print more information.") 
    
    return parser.parse_args()

def build(regenerate: bool, plots: bool, verbose: bool):

    terminal_width = os.get_terminal_size().columns

    if plots:
        separator("Example Plots")
        os.chdir("source")
        result = subprocess.run(
            [
                "python3", 
                "./example_figures.py"
            ]
        )
        if result.returncode != 0:
            raise ValueError("Process failed")
        os.chdir("..")

    if regenerate:
        separator('less')

        result = subprocess.run(
            [
                "lessc",
                "--verbose",
                "./source/_static/css/custom.less",
                "./source/_static/css/custom.css"
            ]
        )
        if result.returncode != 0:
            raise ValueError("Process failed")
            
        separator('generate.py')
        result = subprocess.run(
            [
                "python3",
                "./generate.py",
                "-o",
                "./source",
                "lapyx"
            ]
        )
        if result.returncode != 0:
            raise ValueError("Process failed")
    
    separator('sphinx')

    replace_line = False
    warnings = []
    errors = []
    def process_line(line):
        nonlocal replace_line, verbose
        should_output = verbose
        # check if the line should overwrite the previous line
        if (
            line.startswith("reading sources") or
            line.startswith("writing output") or
            line.startswith("copying images")
        ):
            should_output = True
            if replace_line:
                # back up one line, clear, then print the line
                line = "\033[F\033[K" + line
            else:
                replace_line = True
        else:
            replace_line = False
            if "warning" in line.lower() and not line.lower().startswith("build succeeded"):
                # line = colored(line, "yellow")
                warnings.append(line)
                return ""
            if "error" in line.lower() or "critical" in line.lower():
                # line = colored(line, "red")
                errors.append(line)
                return ""
            if "success" in line.lower():
                line = colored(line, "green")
                should_output = True
            if not should_output:
                return ""
        return line

    success, output = capture_subprocess_output(
        ["make", "html"],
        process_line
    )
    if not success:
        raise ValueError("Process failed")
    if len(warnings) > 0:
        separator("Sphinx Warnings", color = "yellow")
        table = [["File", "Line", "Message"]]
        for line in warnings:
            # use regex to parse the line
            # the line should look like this:
            # /path/to/file.rst:line: WARNING: message
            match = re.match(r"^(.*):(\d+): WARNING: (.*)$", line.strip())
            if match is None:
                print(colored("Could not parse line: ", "red") + line.strip())
            table.append([
                match.group(1),
                match.group(2),
                match.group(3).capitalize()
            ])
        colwidths = [
            (terminal_width - 4) // 2,
            8,
            (terminal_width - 4) // 2
        ]
        print(
            colour_table(
                center(
                    tabulate(
                        table, 
                        headers="firstrow", 
                        tablefmt='fancy_grid', 
                        maxcolwidths = colwidths, 
                        colalign = ["left", "center", "left"]
                    )
                ),
                "yellow",
                outline_only = True
            )
        )


    if len(errors) > 0:
        separator("Sphinx Errors", color = "red")
        table = [["File", "Line", "Message", "Error Type", "Submessage"]]
        skip_next_line = False
        for i in range(len(errors)):
            if skip_next_line:
                skip_next_line = False
                continue
            line = errors[i]
            # if line ends with a colon, we're on the first line of a multi-line error
            if line.strip().endswith(":"):
                second_line = errors[i + 1]
                # use regex to parse the second line
                # the line should look like this:
                # ErrorType: [Errno 2] submessage
                # extract the error type and submessage
                match_string = r"^(\w+): \[Errno .+?\]\s?(.*)$"
                match = re.match(match_string, second_line.strip())
                if match is None:
                    print(colored("Could not parse line: ", "red") + second_line.strip())
                    print("Width regex:\t", match_string)
                error_type = match.group(1)
                submessage = match.group(2)
                skip_next_line = True

            else:
                error_type = ""
                submessage = ""
            # use regex to parse the line
            # the line should look like this:
            # /path/to/file.rst:line: [ERROR|CRITICAL]: message
            match_string = r"^(.*):(\d+): (ERROR|CRITICAL): (.*)$"
            match = re.match(match_string, line.strip())
            if match is None:
                print(colored("Could not parse line: ", "red") + line.strip())
                print("Width regex:\t", match_string)
            table.append([
                match.group(1),
                match.group(2),
                match.group(4).capitalize().rstrip(":"),
                error_type,
                submessage
            ])

        colwidths = [
            (terminal_width - 33) // 3,
            8,
            (terminal_width - 33) // 3,
            10,
            (terminal_width - 33) // 3
        ]
        print(
            colour_table(
                center(
                    tabulate(
                        table, 
                        headers="firstrow", 
                        tablefmt='fancy_grid', 
                        maxcolwidths = colwidths, 
                        colalign = [
                            "left", 
                            "center", 
                            "left", 
                            "center", 
                            "left"
                        ]
                    )
                ),
                "red",
                outline_only = True
            )
        )
    
    
    separator('postprocess.py')
    os.chdir("./source")
    result = subprocess.run(
        [
            "python3",
            "./postprocess.py",
            "-q" if not verbose else ""
        ]
    )
    if result.returncode != 0:
        raise ValueError("Process failed")
    
def main():
    args = parse_args()
    build(args.regenerate, args.plots, args.verbose)

def separator(string, color = "green"):
    # try getting terminal width, defaulting it to 80 if it fails
    try:
        term_width = os.get_terminal_size().columns
    except OSError:
        term_width = 80
    right_pad = (term_width - (len(string) + 4)) // 2
    left_pad = term_width - (len(string) + 4) - right_pad
    print(
        "\n" + 
        "═" * left_pad + "╡ " + 
        colored(string, color) + 
        " ╞" + "═" * right_pad +
        "\n"
    )


if __name__ == "__main__":
    main()
