# TO DO

## Output structure

- Creates a temporary `lapyx_temp.py` file and imports `lapyx.output` and `from lapyx.output import export`. 
- In the LaTeX code, each python block is identified
    - a unique ID is created
    - `lapyx.output.setID(ID)` is added to the `lapyx_temp.py` file
    - the code block is added to the `lapyx_temp.py` file
        - If the block is inline, a single line, and does not contain an `export` statement, the block is wrapped in `export()`
    - the code block is replaced in the LaTeX file with the ID
- Some footer code is added to the `lapyx_temp.py` file
- The `lapyx_temp.py` file is run
    - on startup, a dictionary `lapyx_output` is created to store the output
    - on `lapyx.output.setID(ID)`, the ID is added to the dictionary, initialised to an empty list.
    - on `export(output)`, a string representation of the output is added to the list associated with the current ID
    - on completion, the dictionary is saved to a temporary file `lapyx_output.json`
- The dictionary is read from the temporary file `lapyx_output.json`
- Each ID in the LaTeX file is replaced with the corresponding output from the dictionary, joined with double newlines.
- The modified LaTeX is written to a temporary file `jobname.lapyx.tex
- The temporary file `jobname.lapyx.tex` is compiled with `pdflatex`, twice if necessary and with bibtex if necessary.
- The resulting PDF is moved to `jobname.pdf`
- Temporary files (including LaTeX auxiliary files) are deleted.


## Components

`lapyx.components` should contain functions for generating common LaTeX components

- table/tabular
    - Generate a tabular (optionally inside a table float) from a `.csv` file, or an array-like object
    - Add labels, captions etc.
    - options for long table etc
- figure
    - from filename
    - from matplotlib figure; save figure and import in latex

## Main file

Main file should take command line arguments:
- `-C`, `--no-compile`
    - Do not compile the LaTeX file
- `-o`, `--output`
    - Specify the output filename for the `.pdf` file
- `-t`, `--temp`
    - Specify a temporary file name or path to use, not including the extension
- `-d`, `--debug`
    - Do not delete temporary files
- `-c`, `--compiler-options`
    - Specify options to pass to the compiler as a string