# Contains functions for generating common LaTeX components


import io
import numpy as np
import pandas as pd


class Table:

    def __init__(self, data=None, **kwargs):

        # default values
        self.centered = True
        self.floating = False
        self.caption = None
        self.caption_position = "bottom"
        self.label = None
        self.long = False
        self.headers = []
        self.print_headers = True
        self.alignment = []
        self.column_widths = []
        self.format = []

        # self.data will be a list of lists. Each list is a row, and each element is a cell
        self.data = [[]]
        if data is not None:
            # if data is a string or file object, read it
            if isinstance(data, str) or isinstance(data, io.TextIOBase):
                # assume a file, attempt to read with pandas before converting to nested list. Use `csv_options` if provided as a kwarg
                if "csv_options" in kwargs:
                    csv_options = kwargs["csv_options"]
                else:
                    csv_options = {}
                read_data = pd.read_csv(data, **csv_options)
                self.data = read_data.values.tolist()
                self.headers = read_data.columns.tolist()

            else:
                # if data is a numpy array, convert to a nested list
                if isinstance(data, np.ndarray):
                    data = data.tolist()
                # if data is a pandas dataframe, convert to a nested list
                elif isinstance(data, pd.DataFrame):
                    data = data.values.tolist()
                    self.headers = data.columns.tolist()
                # if data is a dict, convert to a nested list saving the keys as headers
                elif isinstance(data, dict):
                    self.headers = list(data.keys())
                    data = list(data.values())
                
                # if data is not a list or tuple of lists or tuples, raise an error
                if not isinstance(data, list) and not isinstance(data, tuple):
                    raise TypeError("data must be a list or tuple")
                # if the elements of data are not lists or tuples, wrap in a list
                if not isinstance(data[0], list) and not isinstance(data[0], tuple):
                    raise Exception("first element is not a list or tuple\n\n" + str(data))
                    data = [data]
                self.data = data
            # check that all rows have the same length
            for row in self.data:
                if len(row) != len(self.data[0]):
                    raise ValueError("All rows must have the same length")
        self.num_columns = len(self.data[0])
        self.num_rows = len(self.data)

        if len(self.headers) == 0 or all(h == "" for h in self.headers):
            self.headers = [""] * self.num_columns
        self.format        = [None] * self.num_columns
        self.alignment     = ["l"]  * self.num_columns
        self.column_widths = [None] * self.num_columns

        # set any kwargs
        if "center" in kwargs:
            self.center(kwargs["center"])
        if "float" in kwargs:
            self.float(kwargs["float"])
        if "caption" in kwargs:
            self.set_caption(kwargs["caption"])
        if "caption_position" in kwargs:
            self.caption_position = kwargs["caption_position"]
        if "label" in kwargs:
            self.set_label(kwargs["label"])
        if "long" in kwargs:
            self.long(kwargs["long"])
        if "headers" in kwargs:
            self.set_headers(kwargs["headers"])
        if "print_headers" in kwargs:
            self.use_headers(kwargs["print_headers"])
        if "alignment" in kwargs:
            self.set_alignment(kwargs["alignment"])
        if "column_widths" in kwargs:
            self.set_column_widths(kwargs["column_widths"])
        if "format" in kwargs:
            self.set_format(kwargs["format"])


    def add_row(self, new_data = None, index: int = None):
        if new_data is None:
            # add a blank row
            new_data = ["" for i in range(self.num_columns)]
            self.add_rows(new_data, index=index) # this might be unnecessary
            return

        # if new_data is a pandas dataframe or series, convert to a list
        if isinstance(new_data, pd.DataFrame) or isinstance(new_data, pd.Series):
            new_data = new_data.values.tolist()
        # if new_data is a numpy array, convert to a list
        elif isinstance(new_data, np.ndarray):
            new_data = new_data.tolist()
        # if new_data is a dict, convert to a list saving the keys as headers
        elif isinstance(new_data, dict):
            print("This is not yet implemented")  # deal with this later, could be a headache

        # check if new_data contains iterables
        if any(isinstance(i, list) or isinstance(i, tuple) for i in new_data):
            raise ValueError(
                "new_data must be a list of values, not a list of lists. If you want to add multiple rows, use add_rows() instead.")

        if self.num_columns == 0: # using num_columns since num_rows will initially be 1 (empty) row
            self.data = [new_data]
            self.num_rows = 1
            self.num_columns = len(new_data)
            self.headers = [f"Column{i}" for i in range(self.num_columns)]
            return

        # check if new_data has the correct length
        if len(new_data) != self.num_columns:
            raise ValueError(
                f"new_data must have the same length as the number of columns in the table: received {len(new_data)}, expected {self.num_columns}")

        if index is not None:
            self.data.insert(index, new_data)
        else:
            self.data.append(new_data)
        self.num_rows += 1
    
    def add_rows(self, new_data, index: int = None):
        # if new_data is a pandas dataframe or series, convert to a list
        if isinstance(new_data, pd.DataFrame) or isinstance(new_data, pd.Series):
            new_data = new_data.values.tolist()
        # if new_data is a numpy array, convert to a list
        elif isinstance(new_data, np.ndarray):
            new_data = new_data.tolist()
        # if new_data is a dict, convert to a list saving the keys as headers
        elif isinstance(new_data, dict):
            print("This is not yet implemented") # deal with this later, could be a headache
        
        # check if new_data contains iterables
        if not any(isinstance(i, list) or isinstance(i, tuple) for i in new_data):
            # pass straight to add_row if not
            if index is not None:
                self.add_row(new_data, index=index)
            else:
                self.add_row(new_data)
            return
        # pass each row to add_row if it does, iterating backwards so that the indices don't get messed up
        for row in reversed(new_data):
            self.add_row(row, index=index)

    def add_column(self, new_data = None, index: int = None, column_name: str = None):
        if new_data is None:
            # add a column of empty strings
            new_data = [""] * self.num_rows
            self.add_column(new_data, index=index, column_name=column_name)
            return
        # if new_data is a pandas dataframe or series, convert to a list
        new_column_name = column_name if column_name else f"Column{index if index is not None else self.num_columns}"
        if isinstance(new_data, pd.DataFrame) or isinstance(new_data, pd.Series):
            new_data = new_data.values.tolist()
        # if new_data is a numpy array, convert to a list
        elif isinstance(new_data, np.ndarray):
            new_data = new_data.tolist()
        # if new_data is a dict, convert to a list saving the keys as headers
        elif isinstance(new_data, dict):
            print("This is not yet implemented")
    
        # check if new_data contains iterables
        if any(isinstance(i, list) or isinstance(i, tuple) for i in new_data):
            raise ValueError(
                "new_data must be a list of values, not a list of lists. If you want to add multiple columns, use add_columns() instead.")
        
        if self.num_columns == 0:
            self.data = [[i] for i in new_data]
            self.num_rows = len(new_data)
            self.num_columns = 1
            self.headers       = [new_column_name]
            self.format        = [None]
            self.alignment     = ["l"]
            self.column_widths = [None]
            return 

        # check if new_data has the correct length
        if len(new_data) != self.num_rows:
            raise ValueError(
                f"new_data must have the same length as the number of rows in the table: received {len(new_data)}, expected {self.num_rows}")
        
        if index is not None:
            for i, row in enumerate(self.data):
                row.insert(index, new_data[i])
            self.headers.insert(index, new_column_name)
            self.format.insert(index, None)
            self.alignment.insert(index, "l")
            self.column_widths.insert(index, None)
        else:
            for i, row in enumerate(self.data):
                row.append(new_data[i])
            self.headers.append(new_column_name)
            self.format.append(None)
            self.alignment.append("l")
            self.column_widths.append(None)

        self.num_columns += 1
    
    def add_columns(self, new_data, index: int = None, column_names: list = None):
        # if new_data is a pandas dataframe or series, convert to a list
        if isinstance(new_data, pd.DataFrame) or isinstance(new_data, pd.Series):
            new_data = new_data.values.tolist()
        # if new_data is a numpy array, convert to a list
        elif isinstance(new_data, np.ndarray):
            new_data = new_data.tolist()
        # if new_data is a dict, convert to a list saving the keys as headers
        elif isinstance(new_data, dict):
            print("This is not yet implemented")
    
        # check if new_data contains iterables
        if not any(isinstance(i, list) or isinstance(i, tuple) for i in new_data):
            # pass straight to add_column if not
            self.add_column(new_data, index=index, column_name=column_names[0] if column_names else None)
            return
        # pass each element to add_column if it does, iterating backwards so that the indices don't get messed up
        for i, column in enumerate(reversed(new_data)):
            if index is not None:
                self.add_column(column, index=index, column_name=column_names[i] if column_names else None)
            else:
                self.add_column(column, column_name=column_names[i] if column_names else None)

    def transpose(self, include_headers: bool = True):
        self.data = list(map(list, zip(*self.data)))
        self.num_columns = len(self.data[0])
        self.num_rows = len(self.data)
        if not include_headers:
            self.headers = [""] * self.num_columns
            return
        self.add_column(self.headers, index=0)
        self.headers = [""] * self.num_columns

    def center(self, centered: bool = True):
        self.centered = centered

    def float(self, floating: bool = True):
        self.floating = floating

    def set_caption(self, caption: str):
        self.caption = caption
        # can't have a caption if we're not floating
        self.floating = True

    def set_label(self, label: str):
        self.label = label
        # can't have a label if we're not floating
        self.floating = True

    def long(self, long: bool = True):
        self.long = long

    def insert_at(
        self, 
        destination: list, 
        new_values: list | str, 
        start_index = None, 
        end_index = None
    ):

        if isinstance(new_values, str):
            if start_index is None:
                # replace all elements of destination with new_values
                destination[:] = [new_values] * len(destination)
                return destination

            if end_index is None:
                # replace a single element of destination with new_values
                destination[start_index] = new_values
                return destination

            # replace a range of elements of destination with new_values
            destination[start_index:end_index] = [new_values] * (end_index - start_index)
            return destination
        
        if start_index is None:
            # new_values must be the same length as destination
            if len(new_values) != len(destination):
                raise ValueError(
                    f"new_values must be the same length as destination: received {len(new_values)}, expected {len(destination)}")
            # replace all elements of destination with new_values
            destination[:] = new_values
            return destination
        
        if end_index is None:
            # length of new_values must be less than or equal to the length of destination[start_index:]
            if len(new_values) > len(destination[start_index:]):
                raise ValueError(
                       "Received too many new_values. "
                    +  "If no end_index is specified, len(new_values) elements will be replaced. "
                    + f"Received {len(new_values)}, expected {len(destination[start_index:])}"
                )
            # replace len(new_values) elements of destination with new_values
            destination[start_index:start_index + len(new_values)] = new_values
            return destination
        
        # length of new_values must be the length of destination[start_index:end_index]
        if len(new_values) != end_index - start_index:
            raise ValueError(
                   "Received too many or too few new_values. "
                +  "If an end_index is specified, end_index - start_index elements will be replaced. "
                + f"Received {len(new_values)}, expected {end_index - start_index}"
            )
        
        # replace a range of elements of destination with new_values
        destination[start_index:end_index] = new_values

        return destination
       

    def set_headers(self, headers: list | str, column_index: int = None, column_end_index: int = None):
        self.headers = self.insert_at(
            self.headers, headers, column_index, column_end_index)

    def set_alignment(self, alignment: list | str, column_index: int = None, column_end_index: int = None):
        self.alignment = self.insert_at(
            self.alignment, alignment, column_index, column_end_index)

    def set_column_widths(self, widths: list | str, column_index: int = None, column_end_index: int = None):
        self.column_widths = self.insert_at(
            self.column_widths, widths, column_index, column_end_index)

    def set_format(self, format_string: list | str, column_index: int = None, column_end_index: int = None):
        self.format = self.insert_at(
            self.format, format_string, column_index, column_end_index)
    
    def use_headers(self, use: bool = True):
        self.use_headers = use

    def to_latex(self):
        before_lines = []
        after_lines = []
        table_lines = []

        if self.floating:
            before_lines.append(r"\begin{table}[ht!]")
            after_lines.append(r"\end{table}")
        if self.centered:
            if self.floating:
                before_lines.append(r"\centering")
            else:
                before_lines.append(r"\begin{center}")
                after_lines.append(r"\end{center}")
        if self.caption is not None and self.caption_position == "top":
            before_lines.append(f"\caption{{{self.caption}}}")
        if self.label is not None:
            after_lines.append(f"\label{{{self.label}}}")
        # add \begin{tabular} with correct alignment and column widths
        begin_tab_line = r"\begin{tabular}{"

        alignment_map = {
            "l": "p",
            "c": "m",
            "r": "b"
        }

        begin_tab_line += "|"
        begin_tab_line += "|".join([
            alignment_map[align] if width is not None else align for align, width in zip(self.alignment, self.column_widths)
        ])
        begin_tab_line += "|}"

        before_lines.append(begin_tab_line)
        if self.caption is not None and self.caption_position == "bottom":
            after_lines.append(f"\caption{{{self.caption}}}")
        after_lines.append(r"\end{tabular}")
        if self.use_headers:
            table_lines.append(" & ".join(self.headers))
        for row in self.data:
            
            # for each element in row, format using the corresponding format string as f"{val:format_string}", or just f"{val}" if format_string is None
            row = [f"{val:{format_string}}" if format_string is not None else f"{val}" for val, format_string in zip(row, self.format)]
            table_lines.append(" & ".join([str(e) for e in row]))
        before = "\n".join(before_lines)
        if self.use_headers:
            table_lines[0] += r"\\\hline\hline"
            table_lines[1:] = [line + r"\\\hline" for line in table_lines[1:]]
        else:
            table_lines = [line + r"\\\hline" for line in table_lines]
        table = r"\hline" + "\n" + "\n".join(table_lines)
        after = "\n".join(after_lines[::-1])
        return before + "\n" + table + "\n" + after



