# Contains methods which will be called from within the temporary python file

from lapyx.components import Table, Figure, Subfigures, Itemize, Enumerate, Environment, Macro, EmptyEnvironment

output_dict = {}
current_ID = ""
base_dir = ""
temp_dir = ""
prefix = ""

should_export = True




def _init(base_dir_in: str,temp_dir_in: str, prefix_in: str) -> None:
    global output_dict, temp_dir, prefix, base_dir
    temp_dir = temp_dir_in
    base_dir = base_dir_in
    output_dict = {}
    prefix = prefix_in

def no_export() -> None: 
    """Suppress any subsequent output in the current code block."""
    global should_export
    should_export = False

def export(output: str | Table | Figure, **kwargs) -> None:
    """Export the arguments to the output LaTeX file, converting LaTeX objects to strings. 

    Parameters
    ----------
    output : str | :class:`~lapyx.components.Table` | :class:`~lapyx.components.Figure`
        The object to export. If a string, it will be exported as-is. If a Table, Figure, 
        Subfigures, or Environment, these will be correctly formatted as LaTeX markup. Any other
        type will be converted to a string using its ``__str__`` method.

    Raises
    ------
    Exception
        If ``export`` is somehow called before an ID is set.
    """    
    # For now say that this only takes a string, expand support later
    global output_dict
    global current_ID
    global temp_dir
    global should_export

    if not should_export:
        return

    if current_ID == "":
        raise Exception("No ID set")
    if isinstance(output, Table):
        output_dict[current_ID].append(output.to_latex())
        return

    if isinstance(output, Figure):
        output_dict[current_ID].append(output.to_latex(base_dir, temp_dir, **kwargs))
        return

    if isinstance(output, Subfigures):
        output_dict[current_ID].append(output.to_latex(base_dir, temp_dir, **kwargs))
        return


    if isinstance(output, str):
        output_dict[current_ID].append(output)
        return

    # otherwise, just try to convert it to a string
    output_dict[current_ID].append(str(output))

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
    with open(os.path.join(temp_dir, f"{prefix}lapyx_output.json"), "w") as output_file:
        json.dump(output_dict, output_file, indent = 2)
    


