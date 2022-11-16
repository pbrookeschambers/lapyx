# Contains functions for generating common LaTeX components


import io
from typing import Any
import numpy as np
import pandas as pd
from lapyx.main import generate_ID


import matplotlib
from matplotlib.figure import Figure as mplFigure
import matplotlib.pyplot as plt
import os


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
        self.header_format = ""
        self.max_rows_before_split = None
        self.split_table_into_columns = None
        self.use_headers = True

        # self.data will be a list of lists. Each list is a row, and each element is a cell
        self.data = [[]]
        self.set_data(data, **kwargs)

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
        if "header_format" in kwargs:
            self.set_header_format(kwargs["header_format"])
        if "max_rows_before_split" in kwargs:
            self.max_rows_before_split = kwargs["max_rows_before_split"]
        if "split_table_into_columns" in kwargs:
            self.split_table_into_columns = kwargs["split_table_into_columns"]

    def set_data(self, new_data, **kwargs) -> None:
        self.data = [[]]
        if new_data is not None:
            # if data is a string or file object, read it
            if isinstance(new_data, str) or isinstance(new_data, io.TextIOBase):
                # assume a file, attempt to read with pandas before converting to nested list. Use `csv_options` if provided as a kwarg
                if "csv_options" in kwargs:
                    csv_options = kwargs["csv_options"]
                else:
                    csv_options = {}
                read_data = pd.read_csv(new_data, **csv_options)
                self.data = read_data.values.tolist()
                self.headers = read_data.columns.tolist()

            else:
                # if data is a numpy array, convert to a nested list
                if isinstance(new_data, np.ndarray):
                    new_data = new_data.tolist()
                # if data is a pandas dataframe, convert to a nested list
                elif isinstance(new_data, pd.DataFrame):
                    new_data = new_data.values.tolist()
                    self.headers = new_data.columns.tolist()
                # if data is a dict, convert to a nested list saving the keys as headers
                elif isinstance(new_data, dict):
                    self.headers = list(new_data.keys())
                    new_data = list(new_data.values())

                # if data is not a list or tuple of lists or tuples, raise an error
                if not isinstance(new_data, list) and not isinstance(new_data, tuple):
                    raise TypeError("data must be a list or tuple")
                # if the elements of data are not lists or tuples, wrap in a list
                if not isinstance(new_data[0], list) and not isinstance(new_data[0], tuple):
                    # raise Exception("first element is not a list or tuple\n\n" + str(new_data))
                    new_data = [new_data]
                self.data = new_data
            # check that all rows have the same length
            for row in self.data:
                if len(row) != len(self.data[0]):
                    raise ValueError("All rows must have the same length")
        self.num_columns = len(self.data[0])
        self.num_rows = len(self.data)

        # Ensure each column-based property is the correct length, filling with defaults where necessary
        self.headers = self.adjust_length(self.headers, self.num_columns, "")
        self.format = self.adjust_length(self.format, self.num_columns, None)
        self.alignment = self.adjust_length(
            self.alignment, self.num_columns, "l")
        self.column_widths = self.adjust_length(
            self.column_widths, self.num_columns, None)

    @staticmethod
    def adjust_length(l: list, length: int, default: Any) -> list:
        if l is None or len(l) == 0 or all(e is default for e in l):
            return [default] * length
        if len(l) > length:
            return l[:length]
        if len(l) < length:
            return l + [default] * (length - len(l))
        return l

    def add_row(self, new_data=None, index: int = None):
        if new_data is None:
            # add a blank row
            new_data = ["" for i in range(self.num_columns)]
            self.add_rows(new_data, index=index)  # this might be unnecessary
            return

        # if new_data is a pandas dataframe or series, convert to a list
        if isinstance(new_data, pd.DataFrame) or isinstance(new_data, pd.Series):
            new_data = new_data.values.tolist()
        # if new_data is a numpy array, convert to a list
        elif isinstance(new_data, np.ndarray):
            new_data = new_data.tolist()
        # if new_data is a dict, convert to a list saving the keys as headers
        elif isinstance(new_data, dict):
            # deal with this later, could be a headache
            print("This is not yet implemented")

        # check if new_data contains iterables
        if any(isinstance(i, list) or isinstance(i, tuple) for i in new_data):
            raise ValueError(
                "new_data must be a list of values, not a list of lists. If you want to add multiple rows, use add_rows() instead.")

        # using num_columns since num_rows will initially be 1 (empty) row
        if self.num_columns == 0:
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
            # deal with this later, could be a headache
            print("This is not yet implemented")

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

    def add_column(self, new_data=None, index: int = None, column_name: str = None):
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
            self.headers = [new_column_name]
            self.format = [None]
            self.alignment = ["l"]
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
            self.add_column(new_data, index=index,
                            column_name=column_names[0] if column_names else None)
            return
        # pass each element to add_column if it does, iterating backwards so that the indices don't get messed up
        for i, column in enumerate(reversed(new_data)):
            if index is not None:
                self.add_column(
                    column, index=index, column_name=column_names[i] if column_names else None)
            else:
                self.add_column(
                    column, column_name=column_names[i] if column_names else None)

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

    def long(self, long: bool = True):
        self.long = long

    def insert_at(
        self,
        destination: list,
        new_values: list | str,
        start_index=None,
        end_index=None
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
            destination[start_index:end_index] = [
                new_values] * (end_index - start_index)
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
                    + "If no end_index is specified, len(new_values) elements will be replaced. "
                    + f"Received {len(new_values)}, expected {len(destination[start_index:])}"
                )
            # replace len(new_values) elements of destination with new_values
            destination[start_index:start_index + len(new_values)] = new_values
            return destination

        # length of new_values must be the length of destination[start_index:end_index]
        if len(new_values) != end_index - start_index:
            raise ValueError(
                "Received too many or too few new_values. "
                + "If an end_index is specified, end_index - start_index elements will be replaced. "
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

    def set_header_format(self, new_format: str) -> None:
        self.header_format = new_format

    def set_caption(self, caption: str):
        self.caption = caption
        # can't have a caption if we're not floating
        self.floating = True

    def set_label(self, label: str):
        self.label = label
        # can't have a label if we're not floating
        self.floating = True

    def use_headers(self, use: bool = True):
        self.use_headers = use

    def split_after_rows(self, num_rows):
        self.max_rows_before_split = num_rows

    def split_into_columns(self, num_columns):
        self.split_table_into_columns = num_columns

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

        # if we're splitting the table into columns, we need to do that now
        if self.split_table_into_columns is not None:
            # work out how many rows should be in each column to be most evenly distributed
            rows_per_column = self.num_rows // self.split_table_into_columns
            # the first n_extended_columns will have an extra row
            n_extended_columns = self.num_rows % self.split_table_into_columns

            table_lines = []
            used_rows = 0
            for i in range(self.split_table_into_columns):
                # the first n_extended_columns columns will have an extra row
                if i < n_extended_columns:
                    rows = rows_per_column + 1
                else:
                    rows = rows_per_column
                if i > 0:
                    table_lines.append(r"\hspace{1cm}")

                # get the table lines for this column
                table_lines.extend(self.construct_tabular(
                    self.headers,
                    self.header_format,
                    self.use_headers,
                    self.data[used_rows:used_rows + rows],
                    self.alignment,
                    self.column_widths,
                    self.format
                ))
                used_rows += rows

        elif self.max_rows_before_split is not None and self.num_rows > self.max_rows_before_split:
            table_lines = []
            for i in range(0, self.num_rows, self.max_rows_before_split):
                table_lines.extend(self.construct_tabular(
                    self.headers,
                    self.header_format,
                    self.use_headers,
                    self.data[i:i+self.max_rows_before_split],
                    self.alignment,
                    self.column_widths,
                    self.format
                ))
                table_lines.append(r"\hspace{1cm}")
        else:
            table_lines = self.construct_tabular(
                self.headers,
                self.header_format,
                self.use_headers,
                self.data,
                self.alignment,
                self.column_widths,
                self.format
            )

        if self.caption is not None and self.caption_position == "bottom":
            after_lines.append(f"\caption{{{self.caption}}}")
        before = "\n".join(before_lines)
        table = "\n".join(table_lines)
        after = "\n".join(after_lines[::-1])
        return before + table + after

    @staticmethod
    def construct_tabular(
        headers: list,
        header_format: list,
        use_headers: bool,
        data: list,
        alignment: list,
        column_widths: list,
        format_strings: list
    ) -> list:

        begin_tab_line = r"\begin{tabular}{"

        alignment_map = {
            "l": "p",
            "c": "m",
            "r": "b"
        }

        begin_tab_line += "|"
        begin_tab_line += "|".join([
            f"{alignment_map[align]}{{{width}}}" if width is not None else align for align, width in zip(alignment, column_widths)
        ])

        begin_tab_line += "|}\hline"
        table_lines = []

        table_lines.append(begin_tab_line)

        if use_headers:
            table_lines.append(" & ".join(
                [f"{header_format}{{{h}}}" for h in headers]))

        for row in data:
            # for each element in row, format using the corresponding format string as f"{val:format_string}", or just f"{val}" if format_string is None
            row = [f"{val:{format_string}}" if format_string is not None else f"{val}" for val,
                   format_string in zip(row, format_strings)]
            table_lines.append(" & ".join([str(e) for e in row]))

        if use_headers:
            table_lines[1] += r"\\\hline\hline"
            table_lines[2:] = [line + r"\\\hline" for line in table_lines[2:]]
        else:
            table_lines[1:] = [line + r"\\\hline" for line in table_lines[1:]]

        table_lines.append(r"\end{tabular}")
        # strip empty lines
        table_lines = [line for line in table_lines if line.strip() != ""]
        return table_lines


class Figure:

    def __init__(
        self,
        figure: mplFigure = None
    ):

        self.id = generate_ID()
        if figure is None:
            # check for an active figure, creating one if there isn't one already
            figure = plt.gcf()
        self.figure = figure
        self.figure_name = self.id # this will be useful when we can also pass a filepath instead of a mplFigure

        self.caption = None
        self.centered = True
        self.floating = False
        self.label = None
        self.size = {"width": None, "height": None, "scale": None}

    def set_figure(self, figure: mplFigure):
        self.figure = figure

    def set_caption(self, caption: str):
        self.caption = caption
        self.floating = True # if we have a caption, we need to be floating
    
    def set_label(self, label: str):
        self.label = label
        self.floating = True
    
    def set_size(self, width: float = None, height: float = None, scale: float = None):
        if width is not None:
            self.size["width"] = width
        if height is not None:
            self.size["height"] = height
        if scale is not None:
            self.size["scale"] = scale

    def set_width(self, width: float):
        self.set_size(width=width)
    
    def set_height(self, height: float):
        self.set_size(height=height)
    
    def set_scale(self, scale: float):
        self.set_size(scale=scale)

    def float(self):
        self.floating = True

    def center(self):
        self.centered = True

    ## matplotlib functions --------------------------------------------------------------------

    def plot(self, *args, **kwargs):
        self.figure.gca().plot(*args, **kwargs)
    
    def scatter(self, *args, **kwargs):
        self.figure.gca().scatter(*args, **kwargs)
    
    def errorbar(self, *args, **kwargs):
        self.figure.gca().errorbar(*args, **kwargs)
    
    def hist(self, *args, **kwargs):
        self.figure.gca().hist(*args, **kwargs)
    
    def imshow(self, *args, **kwargs):
        self.figure.gca().imshow(*args, **kwargs)

    def xlabel(self, *args, **kwargs):
        self.figure.gca().set_xlabel(*args, **kwargs)
    
    def ylabel(self, *args, **kwargs):
        self.figure.gca().set_ylabel(*args, **kwargs)
    
    def title(self, *args, **kwargs):
        self.figure.gca().set_title(*args, **kwargs)
    
    def legend(self, *args, **kwargs):
        self.figure.gca().legend(*args, **kwargs)
    
    def xlim(self, *args, **kwargs):
        self.figure.gca().set_xlim(*args, **kwargs)
    
    def ylim(self, *args, **kwargs):
        self.figure.gca().set_ylim(*args, **kwargs)
    
    def savefig(self, *args, **kwargs):
        self.figure.savefig(*args, **kwargs)

    # Any other matplotlib functions should be called on the figure directly, otherwise this will get out of hand

    def to_latex(self, base_dir: str):

        # if we have a figure, save it to {base_dir}/lapyx_figures/{id}.pdf
        # create {base_dir}/lapyx_figures if it doesn't exist
        if not os.path.exists(os.path.join(base_dir, "lapyx_figures")):
            os.mkdir(os.path.join(base_dir, "lapyx_figures"))
        if self.figure is not None:
            self.figure.savefig(os.path.join(base_dir, "lapyx_figures", f"{self.figure_name}.pdf"), bbox_inches='tight')


        before_lines = []
        after_lines = []

        if self.floating:
            before_lines.append(r"\begin{figure}[ht!]")
            after_lines.append(r"\end{figure}")
            if self.centered:
                before_lines.append(r"\centering")
        else:
            if self.centered:
                before_lines.append(r"\begin{center}")
                after_lines.append(r"\end{center}")
        
        if self.label is not None:
            after_lines.append(f"\label{{{self.label}}}")
        
        if self.caption is not None:
            after_lines.append(f"\caption{{{self.caption}}}")

        includegraphics_opts = []
        if self.size["width"] is not None:
            includegraphics_opts.append(f"width={self.size['width']}")
        if self.size["height"] is not None:
            includegraphics_opts.append(f"height={self.size['height']}")
        if self.size["scale"] is not None:
            includegraphics_opts.append(f"scale={self.size['scale']}")
        if len(includegraphics_opts) > 0:
            includegraphics_opts = f"[{', '.join(includegraphics_opts)}]"
        figure_line = rf"\includegraphics{includegraphics_opts}{{{base_dir}/lapyx_figures/{self.figure_name}.pdf}}"

        return "\n".join(before_lines + [figure_line] + after_lines[::-1])



