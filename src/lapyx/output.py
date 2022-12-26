# Contains methods which will be called from within the temporary python file

from pathlib import Path
from functools import singledispatch

from .components import Table, Figure, Subfigures, Itemize, Enumerate, Environment, Macro, Container

output_dict = {}
current_ID = ""
base_dir = ""
temp_dir = ""
prefix = ""

should_export = True




def _init(base_dir_in: str | Path, temp_dir_in: str | Path, prefix_in: str) -> None:
    global output_dict, temp_dir, prefix, base_dir
    if isinstance(base_dir_in, str):
        base_dir = Path(base_dir_in)
    else:
        base_dir = base_dir_in
    if isinstance(temp_dir_in, str):
        temp_dir = Path(temp_dir_in)
    else:
        temp_dir = temp_dir_in
    output_dict = {}
    prefix = prefix_in

def no_export() -> None: 
    """Suppress any subsequent output in the current code block."""
    global should_export
    should_export = False

@singledispatch
def export(output):
    """Export the arguments to the output LaTeX file, converting LaTeX objects to strings. 

    Parameters
    ----------
    output : str | :codelink:`Table` | :code:`Figure` | :code:`Subfigures` | :code:`Environment` | :code:`Macro` | :code:`Container`
        The object to export. If a string, it will be exported as-is. If a Table, Figure, 
        Subfigures, or Environment, these will be correctly formatted as LaTeX markup. Any other
        type will be converted to a string using its ``__str__`` method.

    Raises
    ------
    Exception
        If ``export`` is somehow called before an ID is set.
    """    

    global output_dict
    global current_ID
    global temp_dir
    global should_export

    if not should_export:
        return

    if current_ID == "":
        raise Exception("No ID set")
    
    output_dict[current_ID].append(str(output))

@export.register
def _(output: Table) -> None:
    export(output.to_latex())

@export.register
def _(output: Figure, **kwargs) -> None:
    export(output.to_latex(base_dir, temp_dir, **kwargs))

@export.register
def _(output: Subfigures, **kwargs) -> None:
    export(output.to_latex(base_dir, temp_dir, **kwargs))

def _setID(ID: str) -> None:
    global output_dict
    global current_ID
    global should_export
    should_export = True
    if ID in output_dict:
        raise Exception("ID already exists")
    output_dict[ID] = []
    current_ID = ID

def _finish() -> None:
    import json
    import os
    # write the output_dict to `lapyx_output.json`
    global output_dict
    global temp_dir
    global prefix
    with open(temp_dir / f"{prefix}lapyx_output.json", "w") as output_file:
        json.dump(output_dict, output_file, indent = 2)
    


