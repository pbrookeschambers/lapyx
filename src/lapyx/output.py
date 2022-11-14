# Contains methods which will be called from within the temporary python file

output_dict = {}
current_ID = ""
base_dir = ""

def init(dir_in: str) -> None:
    global output_dict, base_dir
    base_dir = dir_in
    output_dict = {}

def export(output: str) -> None:
    # For now say that this only takes a string, expand support later
    global output_dict
    global current_ID
    if current_ID == "":
        raise Exception("No ID set")
    output_dict[current_ID].append(output)

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
    with open(os.path.join(base_dir, "lapyx_output.json"), "w") as output_file:
        json.dump(output_dict, output_file, indent = 2)

