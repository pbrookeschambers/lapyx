#!/usr/bin/env python3


import argparse
import subprocess
import os
from termcolor import colored

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
    result = subprocess.run(
        ["make", "html"]
    )
    if result.returncode != 0:
        raise ValueError("Process failed")
    
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

def separator(string):
    # try getting terminal width, defaulting it to 80 if it fails
    try:
        term_width = os.get_terminal_size().columns
    except OSError:
        term_width = 80
    print(f"\n{'| ' + colored(string, 'green') + ' |':-^{term_width}}\n")


if __name__ == "__main__":
    main()
