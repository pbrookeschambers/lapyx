# Contains methods which will be called from within the temporary python file

from lapyx.components import Table, Figure

output_dict = {}
current_ID = ""
base_dir = ""
prefix = ""




def init(dir_in: str, prefix_in: str) -> None:
    global output_dict, base_dir, prefix
    base_dir = dir_in
    output_dict = {}
    prefix = prefix_in

def export(output: str | Table) -> None:
    # For now say that this only takes a string, expand support later
    global output_dict
    global current_ID
    global base_dir
    if current_ID == "":
        raise Exception("No ID set")
    if isinstance(output, Table):
        output_dict[current_ID].append(output.to_latex())
        return

    if isinstance(output, Figure):
        output_dict[current_ID].append(output.to_latex(base_dir))
        return

    if isinstance(output, str):
        output_dict[current_ID].append(output)
        return

    # otherwise, just try to convert it to a string
    output_dict[current_ID].append(str(output))

def setID(ID: str) -> None:
    global output_dict
    global current_ID
    if ID in output_dict:
        raise Exception("ID already exists")
    output_dict[ID] = []
    current_ID = ID

def finish() -> None:
    import json
    import os
    # write the output_dict to `lapyx_output.json`
    global output_dict
    global base_dir
    global prefix
    with open(os.path.join(base_dir, f"{prefix}lapyx_output.json"), "w") as output_file:
        json.dump(output_dict, output_file, indent = 2)
    


