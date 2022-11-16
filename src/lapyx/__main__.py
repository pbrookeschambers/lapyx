


import argparse


def parse_arguments():
    # Parse command line arguments, all optional
    # -C, --no-compile (no arguments)
    # -o, --output (one argument)
    # -t, --temp (one argument)
    # -d, --debug (no arguments)
    # -c, --compiler-arguments (one argument)
    # -h, --help (no arguments)
    # file (required)
    parser = argparse.ArgumentParser(
        description="Parse embedded python code in a LaTeX file and compile.")
    parser.add_argument("-C", "--no-compile", action="store_true",
                        help="Do not compile the LaTeX file.")
    parser.add_argument("-o", "--output", type=str, default="",
                        help="Specify the output file path for the compiled .pdf file.")
    parser.add_argument("-t", "--temp", type=str, default="",
                        help="Specify the file path for the temporary files." 
                        + "If terminated with a slash, this will be a directory for the temporary files."
                        + "Otherwise, this will be a prefix for the temporary files.")
    parser.add_argument("-d", "--debug", action="store_true",
                        help="Do not delete the temporary files.")
    parser.add_argument("-c", "--compiler-arguments", type=str, default="",
                        help="Specify arguments to pass to the LaTeX compiler as a string.")
    parser.add_argument("file", type=str, help="The LaTeX file to compile.")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    import lapyx.main
    import os
    # check if file exists
    if not os.path.isfile(args.file):
        raise Exception(f"File {args.file} does not exist")
    
    file = args.file
    compile = not args.no_compile
    output = args.output if args.output else None
    temp = args.temp if args.temp else None
    debug = args.debug
    compiler_arguments = args.compiler_arguments if args.compiler_arguments else None

    lapyx.main.process_file(
        args.file, 
        compile = compile, 
        output = output, 
        temp = temp, 
        debug = debug, 
        compiler_arguments = compiler_arguments
    )