# Contains functions for generating common LaTeX components


import io
from typing import Any, List, Tuple, Type
from abc import ABC, abstractmethod
try:
    import numpy as np
    has_numpy = True
except ImportError:
    has_numpy = False

try:
    import pandas as pd
    has_pandas = True
except ImportError:
    has_pandas = False

import csv

from lapyx.main import _generate_ID

try:
    from matplotlib.figure import Figure as mplFigure
    import matplotlib.pyplot as plt
    has_matplotlib = True
except ImportError:
    has_matplotlib = False
import os


class Table:
    """A helper class for generating LaTeX tables and tabulars from a variety of sources."""    
    

    def __init__(
        self, 
        data:                       pd.DataFrame | np.ndarray | List[List[Any]] | str =  None, 
        centered:                   bool            =  True,
        floating:                   bool            =  False,
        floating_position:          str             = "ht!",
        caption:                    str             =  None,
        caption_position:           str             = "bottom",
        label:                      str             =  None,
        long:                       bool            =  False,
        headers:                    str | List[str] =  None,
        use_headers:                bool            =  True,
        alignment:                  str | List[str] =  None,
        column_widths:              str | List[str] =  None,
        format_string:              str | List[str] =  None,
        header_format:              str             =  None,
        max_rows_before_split:      int             =  None,
        split_table_into_columns:   int             =  None,
        csv_reader:                 str             =  None,
        csv_options:                dict            =  {}
    ):
        """Creates a Table object for storing and manipulating data to be exported as a LaTeX 
        table or tabular.

        Parameters
        ----------
        data : pd.DataFrame | np.ndarray | List[List[Any]] | str, optional
            The data to be included in the table. If this is a string, it will be treated as a file
            path to a .csv file and read accordingly. By default None
        centered : bool, optional
            If `True`, the resulting LaTeX table will be centered horizontally, either with 
            `\\centering` or in a `center` environment, whichever is more appropriate. By default 
            True
        floating : bool, optional
            If `True`, the resulting tabular will be eclosed in a `table` environment. By default 
            False
        floating_position : str, optional
            If `floating`, this will be the positional optional string passed to the `table` 
            environment. By default "ht!"
        caption : str, optional
            The caption for the table. If provided, `floating` will automatically be set to `True`.
            By default None
        caption_position : str, optional
            Where to place the caption relative to the tabular in a `table` environment. Should be 
            either `"top"` or `"bottom"`. By default "bottom"
        label : str, optional
            The reference label for the `table` environment. If provided, `floating` will 
            automatically be set to `True`. By default None
        long : bool, optional
            If `True`, the output tabular will instead be a `longtable` environment, allowing for 
            page breaks. By default False
        headers : str | List[str], optional
            Headers for each column in the table. Where possible, this will be extracted from 
            `data`. By default None
        use_headers : bool, optional
            If `True`, `headers` will be used as the first row of the tabular, separated by a 
            double rule. By default True
        alignment : str | List[str], optional
            Text alignments per column. Each element should be "l", "c", or "r"; if `column_widths` 
            are specified, alignment characters will be adjusted automatically. By default None
        column_widths : str | List[str], optional
            The width of each column, including units. Accepts all LaTeX lengths such as 
            `\\textwidth` etc. By default None
        format_string : str | List[str], optional
            Python format string for each column of `data`. These will be passed as 
            `{value:format_string}` when generating the output table row. By default None
        header_format : str, optional
            LaTeX formatting to be applied to each cell of the header row. The final macro can 
            optionally take the header text as an argument. By default None
        max_rows_before_split : int, optional
            If set, the table will be split after every `max_rows_before_split`, outputting 
            multiple `tabular` environments. By default None
        split_table_into_columns : int, optional
            If set, the table will be split into this many separate tabular environments, with rows 
            distributed as evenly as possible by number (not by rendered height). By default None
        csv_reader : str, optional
            If set, a specific library will be used to read any .csv files. Options are `"pandas"`,
            `"numpy"`, and `"csv"`. This is also the order of preference if `csv_reader` is not 
            specified. By default None
        csv_options : dict, optional
            Optional `kwargs` to be passed to the function used to read any .csv files. This is 
            passed to either `pandas.read_csv`, `numpy.genfromtxt`, or `csv.reader`. By default {}
        """                    

        # default values
        self.centered                   = centered
        self.floating                   = floating
        self.floating_pos               = floating_position
        self.set_caption(caption)
        self.caption_position           = caption_position
        self.set_label(label)
        self.is_long                    = long
        self.headers                    = headers
        self.alignment                  = alignment
        self.column_widths              = column_widths
        self.format                     = format_string
        self.header_format              = header_format
        self.max_rows_before_split      = max_rows_before_split
        self.split_table_into_columns   = split_table_into_columns
        self.use_header_row             = use_headers
        self.csv_reader                 = csv_reader
        self.csv_options                = csv_options

        # self.data will be a list of lists. Each list is a row, and each element is a cell
        self.data = [[]]
        self.set_data(data)

    def set_data(self, new_data: pd.DataFrame | np.ndarray | List[List[Any]] | str) -> None:
        """Set the data for the table

        Parameters
        ----------
        new_data : pd.DataFrame | np.ndarray | List[List[Any]] | str
            The data to be included in the table. If this is a string, it will be treated as a file path to a .csv file and read accordingly.

        Raises
        ------
        ImportError
            If the requested csv reader could not be found
        ValueError
            If the requested csv reader is not known
        TypeError
            If the data is of an unsuitable type
        ValueError
            If the data rows do not have consistent lengths
        """        
        self.data = [[]]
        if new_data is not None:
            # if data is a string or file object, read it
            if isinstance(new_data, str) or isinstance(new_data, io.TextIOBase):
                # assume a file, attempt to read with pandas before converting to nested list. Use `csv_options` if provided as a kwarg
                if self.csv_reader is not None:
                    match self.csv_reader:
                        case "pandas":
                            if has_pandas:
                                self.__csv_from_pandas(new_data, self.csv_options)
                            else:
                                raise ImportError(
                                    "Requested pandas for reading .csv but a pandas installation could not be found.")
                        case "numpy":
                            if has_numpy:
                                self.__csv_from_numpy(new_data, self.csv_options)
                            else:
                                raise ImportError(
                                    "Requested numpy for reading .csv but a numpy installation could not be found.")
                        case "csv":
                            self.__csv_from_csv(new_data, self.csv_options)
                        case _:
                            raise ValueError(
                                "csv_reader must be one of 'pandas', 'numpy', or 'csv'")
                else:
                    # order of preference: pandas, numpy, csv
                    if has_pandas:
                        self.__csv_from_pandas(new_data, self.csv_options)
                    elif has_numpy:
                        self.__csv_from_numpy(new_data, self.csv_options)
                    else:
                        self.__csv_from_csv(new_data, self.csv_options)

            else:
                # if data is a numpy array, convert to a nested list
                if has_numpy and isinstance(new_data, np.ndarray):
                    new_data = new_data.tolist()
                # if data is a pandas dataframe, convert to a nested list
                elif has_pandas and isinstance(new_data, pd.DataFrame):
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
        self.headers = self.__adjust_length(self.headers, self.num_columns, "")
        self.format = self.__adjust_length(self.format, self.num_columns, None)
        self.alignment = self.__adjust_length(
            self.alignment, self.num_columns, "l")
        self.column_widths = self.__adjust_length(
            self.column_widths, self.num_columns, None)

    def __csv_from_pandas(self, file_name: str, csv_options):
        read_data = pd.read_csv(file_name, **csv_options)
        self.data = read_data.values.tolist()
        self.headers = read_data.columns.tolist()

    def __csv_from_numpy(self, file_name: str, csv_options):
        read_data = np.genfromtxt(file_name, **csv_options)
        self.data = read_data.tolist()

    def __csv_from_csv(self, file_name: str, csv_options):
        read_data = []
        with open(file_name, newline='') as csvfile:
            reader = csv.reader(csvfile, **csv_options)
            for row in reader:
                read_data.append(row)
        self.data = read_data

    @staticmethod
    def __adjust_length(l: list, length: int, default: Any) -> list:
        if l is None or len(l) == 0 or all(e is default for e in l):
            return [default] * length
        if len(l) > length:
            return l[:length]
        if len(l) < length:
            return l + [default] * (length - len(l))
        return l

    def add_row(
        self, 
        new_data: pd.DataFrame | np.ndarray | List[Any] = None, 
        index: int = None
    ):
        """Add a new row to the table, optionally at a specified index

        Parameters
        ----------
        new_data : pd.DataFrame | np.ndarray | List[Any], optional
            The new row to be added. If not provided, a row of empty strings will be added. By default None
        index : int, optional
            The index at which the new row should be inserted. If not provided, the row will be appended to the table. By default None

        Raises
        ------
        ValueError
            If the new row contains iterables
        ValueError
            if the new row is not the same length as the existing rows
        """               
        if new_data is None:
            # add a blank row
            new_data = ["" for i in range(self.num_columns)]
            self.add_rows(new_data, index=index)  # this might be unnecessary
            return

        # if new_data is a pandas dataframe or series, convert to a list
        if has_pandas and isinstance(new_data, pd.DataFrame) or isinstance(new_data, pd.Series):
            new_data = new_data.values.tolist()
        elif has_numpy and isinstance(new_data, np.ndarray):
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

    def add_rows(
        self, 
        new_data: pd.DataFrame | np.ndarray | List[List[Any]], 
        index: int = None
    ):
        """Add multiple rows to the table, optionally at a specified index

        Parameters
        ----------
        new_data : pd.DataFrame | np.ndarray | List[List[Any]]
            New rows to be added to the table.
        index : int, optional
            The index at which the new rows should be inserted. If multiple rows are added, this will be the index of the first new row. If not provided, the new rows will be appended to the table. By default None
        """    
        # if new_data is a pandas dataframe or series, convert to a list
        if has_pandas and isinstance(new_data, pd.DataFrame) or isinstance(new_data, pd.Series):
            new_data = new_data.values.tolist()
        # if new_data is a numpy array, convert to a list
        elif has_numpy and isinstance(new_data, np.ndarray):
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

    def add_column(
        self, 
        new_data: pd.DataFrame | np.ndarray | List[Any] = None, 
        index: int = None, 
        column_name: str = None
    ):
        """Add a new column to the table, optionally at a specified index, and optionally with a specified header.

        Parameters
        ----------
        new_data : pd.DataFrame | np.ndarray | List[Any], optional
            The new column to be added. If not provided, a column of empty strings will be added instead. By default None
        index : int, optional
            The index at which the new column should be inserted. By default None
        column_name : str, optional
            If provided, the header of the new column. By default None

        Raises
        ------
        ValueError
            If the new column contains iterables
        ValueError
            If the new column is not the same length as the existing columns
        """    
        if new_data is None:
            # add a column of empty strings
            new_data = [""] * self.num_rows
            self.add_column(new_data, index=index, column_name=column_name)
            return
        # if new_data is a pandas dataframe or series, convert to a list
        new_column_name = column_name if column_name else ""
        if has_pandas and isinstance(new_data, pd.DataFrame) or isinstance(new_data, pd.Series):
            new_data = new_data.values.tolist()
        # if new_data is a numpy array, convert to a list
        elif has_numpy and isinstance(new_data, np.ndarray):
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

    def add_columns(
        self, 
        new_data: pd.DataFrame | np.ndarray | List[List[Any]], 
        index: int = None, 
        column_names: list = None
    ):
        """Add multiple columns to the table, optionally at a specified index, and optionally with specified headers.

        Parameters
        ----------
        new_data : pd.DataFrame | np.ndarray | List[List[Any]]
            The new columns to be added.    
        index : int, optional
            The index at which the new columns should be inserted. If multiple columns are added, this will be the index of the first new column. If not provided, the new columns will be appended to the table. By default None
        column_names : list, optional
            If provided, the headers of the new columns. By default None
        """    
        # if new_data is a pandas dataframe or series, convert to a list
        if has_pandas and isinstance(new_data, pd.DataFrame) or isinstance(new_data, pd.Series):
            new_data = new_data.values.tolist()
        # if new_data is a numpy array, convert to a list
        elif has_numpy and isinstance(new_data, np.ndarray):
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
        """Transpose the table.

        Parameters
        ----------
        include_headers : bool, optional
            If `True`, column headers become the first column of the new table. By default True
        """        
        self.data = list(map(list, zip(*self.data)))
        self.num_columns = len(self.data[0])
        self.num_rows = len(self.data)
        if not include_headers:
            self.headers = [""] * self.num_columns
            return
        self.add_column(self.headers, index=0)
        self.headers = [""] * self.num_columns

    def center(self, centered: bool = True):
        """Center the table, either with `\\centering` or a `center` environment, depending on 
        whether the table is a float or not.

        Parameters
        ----------
        centered : bool, optional
            If `True`, the table is centered. By default True
        """        
        self.centered = centered

    def float(self, floating: bool = True, floating_pos: str = None):
        """Float the table, optionally specifying the position.

        Parameters
        ----------
        floating : bool, optional
            If `True`, the table becomes a float with the `tabular` environment wrapped in a 
            `table` environment. By default True
        pos : str, optional
            If provided, sets the position optional argument to the `table` environment. By 
            default None
        """        
        self.floating = floating
        if floating_pos is not None:
            self.floating_pos = floating_pos

    def long(self, long: bool = True):
        """Use a `longtable` environment to allow for page breaks. Currently not implemented.

        Parameters
        ----------
        long : bool, optional
            If `True`, a `longtable` environment will be used instead of `tabular`. By default True
        """        
        self.long = long

    def __insert_at(
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
        """Set the headers for all or some columns in the table. Behaviour is different if 
        `headers` is a single string or a list.

        If `headers` is a single string, and no other arguments are provided, all headers are set 
        to this value. If `column_index` is provided, but `column_end_index` is not, only the 
        single column at `column_index` is set to this value. If `column_index` and 
        `column_end_index` are both provided, all columns between `column_index` and 
        `column_end_index` are set to this value.

        If `headers` is a list and no other arguments are provided, if must have length equal to 
        the number of columns in the table (unless no data has been set). `column_end_index` 
        is assumed to be `-1` if it is not specified. If `column_index` is provided, `headers` 
        must have length `column_end_index - column_index`. All specified columns are set to the 
        corresponding values in `headers`.

        Parameters
        ----------
        headers : list | str
            A list of the headers, or a single header. 
        column_index : int, optional
            If provided, the first column index to be set. By default None
        column_end_index : int, optional
            if provided, the last column index to be set. By default None
        """        
        self.headers = self.__insert_at(
            self.headers, headers, column_index, column_end_index)

    def set_alignment(self, alignment: list | str, column_index: int = None, column_end_index: int = None):
        """Set the alignment for all or some columns in the table. Behaviour is different if 
        `alignment` is a single string or a list.

        If `alignment` is a single string, and no other arguments are provided, all alignment 
        specifiers are set to this value. If `column_index` is provided, but `column_end_index` is 
        not, only the single column at `column_index` is set to this alignment. If `column_index` 
        and `column_end_index` are both provided, all columns between `column_index` and 
        `column_end_index` are set to this alignment.

        If `alignment` is a list and no other arguments are provided, if must have length equal to 
        the number of columns in the table (unless no data has been set). `column_end_index` is 
        assumed to be `-1` if it is not specified. If `column_index` is provided, `alignment` must 
        have length `column_end_index - column_index`. All specified columns are set to the 
        corresponding alignment specifiers in `alignment`.

        Parameters
        ----------
        alignment : list | str
            A list of alignments, or a single alignment specifier. 
        column_index : int, optional
            If provided, the first column index to be set. By default None
        column_end_index : int, optional
            if provided, the last column index to be set. By default None
        """        
        self.alignment = self.__insert_at(
            self.alignment, alignment, column_index, column_end_index)

    def set_column_widths(self, widths: list | str, column_index: int = None, column_end_index: int = None):
        """Set the column widths for all or some columns in the table. Behaviour is different if 
        `column_widths` is a single string or a list.

        If `column_widths` is a single string, and no other arguments are provided, all columns are
        set to this width. If `column_index` is provided, but `column_end_index` is not, only the 
        single column at `column_index` is set to this width. If `column_index` and 
        `column_end_index` are both provided, all columns between `column_index` and 
        `column_end_index` are set to this width.

        If `column_widths` is a list and no other arguments are provided, if must have length equal
        to the number of columns in the table (unless no data has been set). `column_end_index` is 
        assumed to be `-1` if it is not specified. If `column_index` is provided, `column_widths` 
        must have length `column_end_index - column_index`. All specified columns are set to the 
        corresponding widths in `column_widths`.

        Parameters
        ----------
        column_widths : list | str
            A list of the column widths, or a single width. These must include units, and can include 
            any LaTeX length (e.g., `\\linewidth`). 
        column_index : int, optional
            If provided, the first column index to be set. By default None
        column_end_index : int, optional
            if provided, the last column index to be set. By default None
        """        
        self.column_widths = self.__insert_at(
            self.column_widths, widths, column_index, column_end_index)

    def set_format(self, format_string: list | str, column_index: int = None, column_end_index: int = None):
        """Set the format specifiers for all or some columns in the table. Behaviour is different 
        if `format_string` is a single string or a list.

        If `format_string` is a single string, and no other arguments are provided, all format 
        specifiers are set to this value. If `column_index` is provided, but `column_end_index` is 
        not, only the single column at `column_index` is set to this specifier. If `column_index` 
        and `column_end_index` are both provided, all columns between `column_index` and 
        `column_end_index` are set to this specifier.

        If `format_string` is a list and no other arguments are provided, if must have length equal to 
        the number of columns in the table (unless no data has been set). `column_end_index` is 
        assumed to be `-1` if it is not specified. If `column_index` is provided, `format_string` must 
        have length `column_end_index - column_index`. All specified columns are set to the 
        corresponding format specifiers in `format_string`.

        Parameters
        ----------
        format_string : list | str
            A list of format specifiers, or a single format specifier. 
        column_index : int, optional
            If provided, the first column index to be set. By default None
        column_end_index : int, optional
            if provided, the last column index to be set. By default None
        """    
        self.format = self.__insert_at(
            self.format, format_string, column_index, column_end_index)

    def set_header_format(self, new_format: str) -> None:
        """Set the LaTeX format for the header row (e.g., `\\bfseries`)

        Parameters
        ----------
        new_format : str
            The LaTeX format for the header row, prepended to each header. The final macro can optionally take the header as an argument.
        """        
        self.header_format = new_format

    def set_caption(self, caption: str):
        """Set the LaTeX caption for the table. If it's not already, this will cause the table to float.

        Parameters
        ----------
        caption : str
            The caption to include in the output LaTeX.
        """        
        self.caption = caption
        if caption is not None:
            # can't have a caption if we're not floating
            self.floating = True

    def set_label(self, label: str):
        """Set the LaTeX label for the table. If it's not already, this will cause the table to float.

        Parameters
        ----------
        label : str
            The reference label to include in the output LaTeX.
        """        
        self.label = label
        if label is not None:
            # can't have a label if we're not floating
            self.floating = True

    def use_headers(self, use: bool = True):
        """Include or exclude the header row in the output LaTeX.

        Parameters
        ----------
        use : bool, optional
            If `True`, the headers will be included as the first row of the output LaTeX tabular, by default True
        """        
        self.use_header_row = use

    def split_after_rows(self, num_rows: int):
        """Split the data into multiple `tabular` environments if the number of rows exceeds this value. If headers are included, the header row will be repeated at the top of each new `tabular` environment. 

        Parameters
        ----------
        num_rows : int--
            The maximum number of rows in each `tabular` environment.
        """        
        self.max_rows_before_split = num_rows

    def split_into_columns(self, num_columns: int):
        """Split the data into this many `tabular` environments, distributing the number of rows as evenly as possible. If headers are included, the header row will be repeated at the top of each new `tabular` environment.

        Parameters
        ----------
        num_columns : int
            The number of `tabular` environments into which the data should be split.
        """        
        self.split_table_into_columns = num_columns


    def to_latex(self) -> str:

        container = EmptyEnvironment()
        
        if self.split_table_into_columns is not None:
            # work out how many rows should be in each column to be most evenly distributed
            rows_per_column = self.num_rows // self.split_table_into_columns
            # the first n_extended_columns will have an extra row
            n_extended_columns = self.num_rows % self.split_table_into_columns

            tabulars = []
            used_rows = 0
            for i in range(self.split_table_into_columns):
                # the first n_extended_columns columns will have an extra row
                if i < n_extended_columns:
                    rows = rows_per_column + 1
                else:
                    rows = rows_per_column
                if i > 0:
                    tabulars.append(r"\hspace{1cm}")

                # get the table lines for this column
                tabulars.append(self.__construct_tabular(
                    self.headers,
                    self.header_format,
                    self.use_header_row,
                    self.data[used_rows:used_rows + rows],
                    self.alignment,
                    self.column_widths,
                    self.format
                ))
                used_rows += rows
        elif self.max_rows_before_split is not None and self.num_rows > self.max_rows_before_split:
            tabulars = []
            for i in range(0, self.num_rows, self.max_rows_before_split):
                tabulars.append(self.__construct_tabular(
                    self.headers,
                    self.header_format,
                    self.use_header_row,
                    self.data[i:i+self.max_rows_before_split],
                    self.alignment,
                    self.column_widths,
                    self.format
                ))
                tabulars.append(r"\hspace{1cm}")
        else:
            tabulars = self.__construct_tabular(
                self.headers,
                self.header_format,
                self.use_header_row,
                self.data,
                self.alignment,
                self.column_widths,
                self.format
            )
        
        
        if self.floating:
            table = Environment("table")
            container.add_content(table)
            if self.floating_pos is not None:
                table.add_argument(self.floating_pos, optional = True)
            else:
                table.add_argument("ht!", optional = True)
            if self.centered:
                table.add_content(Macro("centering"))
            if self.caption is not None and self.caption_position == "top":
                table.add_content(Macro("caption", arguments = self.caption))
            table.add_content(tabulars)
            if self.caption is not None and self.caption_position == "bottom":
                table.add_content(Macro("caption", arguments = self.caption))
            if self.label is not None:
                table.add_content(Macro("label", arguments = self.label))
        else:
            if self.centered:
                center = Environment("center")
                center.add_content(tabulars)
                container.add_content(center)
            else:
                container.add_content(tabulars)
        return str(container)
        
            
        

    @staticmethod
    def __construct_tabular(
        headers: list,
        header_format: list,
        use_headers: bool,
        data: list,
        alignment: list,
        column_widths: list,
        format_strings: list
    ) -> "Environment":

        tabular = Environment("tabular")

        alignment_map = {
            "l": "p",
            "c": "m",
            "r": "b"
        }

        alignment_string = "|" + "|".join([
            f"{alignment_map[align]}{{{width}}}" if width is not None else align for align, width in zip(alignment, column_widths)
        ]) + "|"

        tabular.add_argument(alignment_string)
        tabular.add_content(r"\hline")

        if use_headers:
            tabular.add_content(" & ".join(
                [f"{header_format if header_format is not None else ''}{{{h}}}" for h in headers]) + r"\\\hline\hline")

        for row in data:
            # for each element in row, format using the corresponding format string as f"{val:format_string}", or just f"{val}" if format_string is None
            row = [f"{val:{format_string}}" if format_string is not None else f"{val}" for val,
                   format_string in zip(row, format_strings)]
            tabular.add_content(" & ".join([str(e) for e in row]) + r"\\\hline")

        return tabular


class Figure:

    """A helper class for generating LaTeX figures."""

    def __init__(
        self,
        figure: mplFigure | str = None,
        caption: str = None,
        label: str = None,
        floating: bool = False,
        floating_position: str = "ht!",
        centered: bool = True,
        width: str = None,
        height: str = None,
        scale: str = None
    ):
        """Creates a Figure object for storing and manipulating a `matplotlib` figure or image file 
        to be exported to a LaTeX figure.

        Parameters
        ----------
        figure : mplFigure | str, optional
            The figure to be associated with this object. If this is a string, it will be treated 
            as a file path to an image. If this is not provided, an active `matplotlib` figure will
            be found or created, by default None
        caption : str, optional
            The caption for the figure. If provided, `floating` will be automatically set to True, 
            by default None
        label : str, optional
            The reference label for the `figure` environment. If provided, `floating` will 
            automatically be set to `True`. By default None
        floating : bool, optional
            If `True`, the resulting image will be eclosed in a `figure` environment. By default 
            False
        floating_position : str, optional
            If `floating`, this will be the positional optional string passed to the `table` 
            environment. By default "ht!"
        centered : bool, optional
            If `True`, the resulting LaTeX table will be centered horizontally, either with 
            `\\centering` or in a `center` environment, whichever is more appropriate. By default 
            True
        width : str, optional
            Width of the output image. This must include units, but can also include any valid 
            LaTeX length such as `\\textwidth`. By default None
        height : str, optional
            Height of the output image. This must include units, but can also include any valid 
            LaTeX length such as `\\textwidth`. By default None
        scale : str, optional
            Scale of the output image, by default None

        Raises
        ------
        TypeError
            If the provided `figure` is not a `matplotlib` figure or a string
        """        

        self.using_file = False  # Using a pre-existing file instead of a new figure

        self.id = _generate_ID()
        if has_matplotlib and figure is None:
            # check for an active figure, creating one if there isn't one already
            figure = plt.gcf()
        if isinstance(figure, mplFigure):
            self.figure = figure
            # this will be useful when we can also pass a filepath instead of a mplFigure
            self.figure_name = self.id
        elif isinstance(figure, str):
            self.figure_name = figure
            self.using_file = True
            self.figure = None
        else:
            raise TypeError(
                "Figure must be a matplotlib figure or a filepath, or not provided")
        self.caption = caption
        self.centered = centered
        self.floating = floating
        self.floating_pos = floating_position
        self.label = label
        self.size = {"width": width, "height": height, "scale": scale}

    def set_figure(self, figure: mplFigure | str):
        """Set the `matplotlib` figure or file path associated with this Figure.

        Parameters
        ----------
        figure : mplFigure | str
            The figure to be associated with this object. If this is a string, it will be treated 
            as a file path to an image.

        Raises
        ------
        TypeError
            If the provided `figure` is not a `matplotlib` figure or a string
        """        
        if isinstance(figure, mplFigure):
            self.figure = figure
            self.figure_name = self.id
            self.using_file = False
        elif isinstance(figure, str):
            self.figure_name = figure
            self.using_file = True
            self.figure = None
        else:
            raise TypeError("figure must be a matplotlib figure or a filepath")

    def set_caption(self, caption: str):
        """Set the LaTeX caption for the figure. If it's not already, this will cause the figure to float.

        Parameters
        ----------
        caption : str
            The caption to include in the output LaTeX.
        """        
        self.caption = caption
        if caption is not None:
            self.floating = True  # if we have a caption, we need to be floating

    def set_label(self, label: str):
        """Set the LaTeX label for the figure. If it's not already, this will cause the figure to float.

        Parameters
        ----------
        label : str
            The reference label to include in the output LaTeX.
        """        
        self.label = label
        if label is not None:
            self.floating = True

    def set_size(self, width: float = None, height: float = None, scale: float = None):
        """Set multiple size parameters for the output image simultaneously.

        Parameters
        ----------
        width : float, optional
            Width of the output image. This must include units, but can also include any valid 
            LaTeX length such as `\\textwidth`. By default None
        height : str, optional
            Height of the output image. This must include units, but can also include any valid 
            LaTeX length such as `\\textwidth`. By default None
        scale : str, optional
            Scale of the output image, by default None
        """        
        if width is not None:
            self.size["width"] = width
        if height is not None:
            self.size["height"] = height
        if scale is not None:
            self.size["scale"] = scale

    def set_width(self, width: float):
        """Set the width of the output image.

        Parameters
        ----------
        width : float
            Width of the output image. This must include units, but can also include any valid 
            LaTeX length such as `\\textwidth`. By default None
        """        
        self.set_size(width=width)

    def set_height(self, height: float):
        """Set the height of the output image.

        Parameters
        ----------
        height : float
            Height of the output image. This must include units, but can also include any valid 
            LaTeX length such as `\\textwidth`. By default None
        """        
        self.set_size(height=height)

    def set_scale(self, scale: float):
        """Set the scale of the output image.

        Parameters
        ----------
        scale : float
            Scale of the output image, by default None
        """        
        self.set_size(scale=scale)

    def float(self, floating: bool = True, floating_pos: str = None):
        """Float the image inside a `figure` environment, optionally specifying the position.

        Parameters
        ----------
        floating : bool, optional
            If `True`, the image becomes a float with the `\\includegraphics` macro wrapped in a 
            `figure` environment. By default True
        floating_pos : str, optional
            If provided, sets the position optional argument to the `figure` environment. By 
            default None
        """        
        self.floating = floating
        if floating_pos is not None:
            self.floating_pos = floating_pos

    def center(self, centered: bool = True):
        """Center the table, either with `\\centering` or a `center` environment, depending on 
        whether the image is a float or not.

        Parameters
        ----------
        centered : bool, optional
            If `True`, the figure is centered. By default True
        """        
        self.centered = centered

    # matplotlib functions --------------------------------------------------------------------

    def __check_for_figure(self):
        if self.figure is None:
            raise ValueError(
                "There is no matplotlib figure associated with this Figure object.")

    def plot(self, *args, **kwargs):
        """A wrapper for the `matplotlib.pyplot.plot` function.
        """        
        self.__check_for_figure()
        self.figure.gca().plot(*args, **kwargs)

    def scatter(self, *args, **kwargs):
        """A wrapper for the `matplotlib.pyplot.scatter` function.
        """        
        self.__check_for_figure()
        self.figure.gca().scatter(*args, **kwargs)

    def errorbar(self, *args, **kwargs):
        """A wrapper for the `matplotlib.pyplot.errorbar` function.
        """
        self.__check_for_figure()
        self.figure.gca().errorbar(*args, **kwargs)

    def hist(self, *args, **kwargs):
        """A wrapper for the `matplotlib.pyplot.hist` function.
        """        
        self.__check_for_figure()
        self.figure.gca().hist(*args, **kwargs)

    def imshow(self, *args, **kwargs):
        """A wrapper for the `matplotlib.pyplot.imshow` function.
        """    
        self.__check_for_figure()
        self.figure.gca().imshow(*args, **kwargs)

    def xlabel(self, *args, **kwargs):
        """A wrapper for the `matplotlib.pyplot.xlabel` function.    
        """        
        self.__check_for_figure()
        self.figure.gca().set_xlabel(*args, **kwargs)

    def ylabel(self, *args, **kwargs):
        """A wrapper for the `matplotlib.pyplot.ylabel` function.
        """        
        self.__check_for_figure()
        self.figure.gca().set_ylabel(*args, **kwargs)

    def title(self, *args, **kwargs):
        """A wrapper for the `matplotlib.pyplot.title` function.
        """        
        self.__check_for_figure()
        self.figure.gca().set_title(*args, **kwargs)

    def legend(self, *args, **kwargs):
        """A wrapper for the `matplotlib.pyplot.legend` function.
        """        
        self.__check_for_figure()
        self.figure.gca().legend(*args, **kwargs)

    def xlim(self, *args, **kwargs):
        """A wrapper for the `matplotlib.pyplot.xlim` function.
        """        
        self.__check_for_figure()
        self.figure.gca().set_xlim(*args, **kwargs)

    def ylim(self, *args, **kwargs):
        """A wrapper for the `matplotlib.pyplot.ylim` function.
        """        
        self.__check_for_figure()
        self.figure.gca().set_ylim(*args, **kwargs)

    def savefig(self, *args, **kwargs):
        """A wrapper for the `matplotlib.pyplot.savefig` function.
        """        
        self.__check_for_figure()
        self.figure.savefig(*args, **kwargs)

    # Any other matplotlib functions should be called on the figure directly, otherwise this will get out of hand

    def to_latex(self, base_dir: str, temp_dir: str, **kwargs) -> str:
        """Convert the figure to LaTeX syntax, obeying all the formatting options set. If there is
        a matplotlib figure associated with this object, it will be saved to a temporary file with
        a random file name, then included with `\\includegraphics`.

        Parameters
        ----------
        base_dir : str
            The directory in which the original LaPyX file is located.
        temp_dir : str
            The directory and prefix in which to save the temporary files.

        Returns
        -------
        str
            The LATeX syntax for the figure.
        """ 

        container = EmptyEnvironment()           

        figure_file_name = os.path.join(base_dir, self.figure_name)
        if not self.using_file:
            # if we have a figure, save it to {temp_dir}/lapyx_figures/{id}.pdf
            # create {temp_dir}/lapyx_figures if it doesn't exist
            if not os.path.exists(os.path.join(temp_dir, "lapyx_figures")):
                os.mkdir(os.path.join(temp_dir, "lapyx_figures"))
            if self.figure is not None:
                figure_file_name = os.path.join(
                        temp_dir, 
                        "lapyx_figures", 
                        f"{self.figure_name}.{kwargs['extension'] if 'extension' in kwargs else 'pdf'}"
                    )
                self.figure.savefig(
                    figure_file_name, 
                    bbox_inches='tight',
                    **kwargs
                )


        
        includegraphics_opts = KWArgs()
        if self.width is not None:
            includegraphics_opts.add_arg("width", self.width)
        if self.height is not None:
            includegraphics_opts.add_arg("height", self.height)
        if self.scale is not None:
            includegraphics_opts.add_arg("scale", self.scale)
        
        includegraphics = Macro("includegraphics")
        if not includegraphics_opts.is_empty():
            includegraphics.add_arg(OptArg(includegraphics_opts))
        includegraphics.add_arg(figure_file_name)

        
        if self.floating:
            outer_figure = Environment("figure")
            container.add_content(outer_figure)
            if self.floating_pos is not None:
                outer_figure.set_optional_arg(self.floating_pos)
            else:
                outer_figure.set_optional_arg("ht!")
            outer_figure.add_content(includegraphics)
            if self.centered:
                outer_figure.add_content(r"\centering")
            if self.caption is not None:
                outer_figure.add_content(Macro("caption", arguments = self.caption))
            if self.label is not None:
                outer_figure.add_content(Macro("label", arguments = self.label))
        else:
            if self.centered:
                center = Environment("center")
                container.add(center)
                center.add_content(includegraphics)
            else:
                container.add_content(includegraphics)
        return str(container)

class KWArgs:

    def __init__(self, args: dict = None):
        if args is None:
            args = {}
        self.args = args
        self._check_values()
        
    def _check_values(self):

        #check that all values are either strings or `Arg` instances
        for key, value in self.args.items():
            if  (
                not isinstance(value, str) and 
                not isinstance(value, int) and
                not isinstance(value, float) and
                not isinstance(value, bool) and 
                not isinstance(value, Arg) 
            ):
                raise TypeError(f"Value for argument {key} must be a string or an `Arg` instance.")


    def add_arg(self, key: str, value: str):
        self.args[key] = value
        self._check_values()
    
    def set_arg(self, key: str, value: str):
        self.add_arg(key, value)

    def remove_arg(self, key: str):
        del self.args[key]

    def set_args(self, new_values: dict):
        self.args = {**self.args, **new_values}
        self._check_values()

    def remove_args(self, keys: List[str]):
        for key in keys:
            self.remove_arg(key)

    def __str__(self):
        arg_strings = []
        for key, value in self.args.items():
            if isinstance(value, Arg):
                arg_strings.append(f"{key} = {value}")
            else:
                arg_strings.append(f"{key} = {{{value}}}")
        return ", ".join(arg_strings)

    def is_empty(self):
        return len(self.args) == 0

class Arg:

    brackets = ("{", "}")

    def __init__(self, value: str = None):
        self.set_values(value)
    
    def set_values(self, new_values = None):
        if new_values is not None:
            if not isinstance(new_values, List):
                if isinstance(new_values, tuple):
                    new_values = list(new_values)
                elif isinstance(new_values, dict):
                    new_values = [KWArgs(new_values)]
                else:
                    new_values = [new_values]
            else: 
                # it is a list, so check if any of the elements are dicts
                for i, v in enumerate(new_values):
                    if isinstance(v, dict):
                        new_values[i] = KWArgs(v)
                    elif isinstance(v, list) or isinstance(v, tuple):
                        raise TypeError("Nested lists are not allowed.")
            self.value = new_values
        else:
            self.value = []

    def add_value(self, value: str):
        if isinstance(value, dict):
            value = KWArgs(value)
            self.value.append(value)
            return
        if not isinstance(value, str) and not isinstance(value, KWArgs):
            raise TypeError(f"Value must be a string, dictionary, or KWArgs instance.")
        self.value.append(value)
    
    def set_value(self, value: str, index: int):
        # check if index is in range
        if index >= len(self.value):
            raise IndexError(f"Cannot set value, index {index} is out of range.")
        if isinstance(value, dict):
            value = KWArgs(value)
            self.value[index] = value
            return
        if not isinstance(value, str) and not isinstance(value, KWArgs):
            raise TypeError(f"Value must be a string, dictionary, or KWArgs instance.")
        self.value[index] = value
    
    def insert_value(self, value: str, index: int):
        # check if index is in range
        if index > len(self.value):
            raise IndexError(f"Cannot insert value, index {index} is out of range.")
        if isinstance(value, dict):
            value = KWArgs(value)
            self.value.insert(index, value)
            return
        if not isinstance(value, str) and not isinstance(value, KWArgs):
            raise TypeError(f"Value must be a string, dictionary, or KWArgs instance.")
        self.value.insert(index, value)
    
    def remove_value(self, index: int):
        # check if index is in range
        if index >= len(self.value):
            raise IndexError(f"Cannot remove value, index {index} is out of range.")
        del self.value[index]
    
    def __str__(self):
        return self.brackets[0] + ", ".join([str(v) for v in self.value]) + self.brackets[1]

    def __repr__(self):
        return f"Args({self.value})"

class OptArg(Arg):
    brackets = ("[", "]")

    def __repr__(self):
        return f"OptArgs({self.value})"

class CommandBase(ABC):
    def __init__(
        self,
        name: str,
        arguments: Arg | OptArg | str | List[str | Arg | OptArg] = None
    ):
        self.name = name
        self.arguments = []
        if arguments is None:
            arguments = []
        elif not isinstance(arguments, list):
            if isinstance(arguments, tuple):
                arguments = list(arguments)
            else:
                arguments = [arguments]
        for a in arguments:
            self.add_argument(a)


    def add_argument(self, argument: Arg | OptArg | str, optional: bool = False):
        if not isinstance(argument, Arg) and not isinstance(argument, OptArg):
            if optional:
                argument = OptArg(argument)
            else:
                argument = Arg(argument)
        self.arguments.append(argument)
    
    def set_argument(self, argument: Arg | OptArg | str, index: int, optional: bool = False):
        # Set an option at a specific index. If the index is out of range, raise an error
        if index >= len(self.arguments):
            raise IndexError(f"Cannot set option: index {index} is out of range for options list of length {len(self.arguments)}")
        if not isinstance(argument, Arg) and not isinstance(argument, OptArg):
            if optional:
                argument = OptArg(argument)
            else:
                argument = Arg(argument)
        self.arguments[index] = argument

    def insert_argument(self, argument: Arg | OptArg | str, index: int, optional: bool = False):
        # Insert an option at a specific index. If the index is out of range, raise an error
        if index > len(self.arguments):
            raise IndexError(f"Cannot insert option: index {index} is out of range for options list of length {len(self.arguments)}")
        if not isinstance(argument, Arg) and not isinstance(argument, OptArg):
            if optional:
                argument = OptArg(argument)
            else:
                argument = Arg(argument)
        self.arguments.insert(index, argument)
    
    def remove_argument(self, index: int):
        # Remove an option at a specific index. If the index is out of range, raise an error
        if index >= len(self.arguments):
            raise IndexError(f"Cannot remove option: index {index} is out of range for options list of length {len(self.arguments)}")
        del self.arguments[index]
    
    @abstractmethod
    def __str__(self):
        pass

class Macro(CommandBase):
    def __init__(
        self,
        name: str,
        arguments: Arg | OptArg | str | List[str | Arg | OptArg] = None
    ):
        super().__init__(name, arguments)

    def __str__(self):
        return f"\\{self.name}" + "".join([str(a) for a in self.arguments])

    def __repr__(self):
        return f"Macro({self.name}, {self.arguments})"

class Environment(CommandBase):

    def __init__(
        self, 
        name: str, 
        arguments: Arg | OptArg | str | List[str | Arg | OptArg] = None,
        content: str | Table | Figure | List[ str | Table | Figure]  = None 
        # can also be Environment or list of Environments, but for type hints only in python >= 3.11   
    ):
        super().__init__(name, arguments)
        
        if content is None:
            self.content = []
        elif not isinstance(content, list):
            self.content = [content]
        else:
            self.content = content
    
    def add_content(self, content: str | Table | Figure):
        # content can also be Environment or list of Environments, but for type hints only in python >= 3.11   
        if isinstance(content, list) or isinstance(content, tuple):
            self.content.extend(content)
        else:
            self.content.append(content)

    def set_content(self, content: str | Table | Figure, index: int):
        # content can also be Environment or list of Environments, but for type hints only in python >= 3.11   
        # Set an option at a specific index. If the index is out of range, raise an error
        if index >= len(self.content):
            raise IndexError(f"Cannot set content: index {index} is out of range for content list of length {len(self.content)}")
        self.content[index] = content
    
    def insert_content(self, content: str | Table | Figure, index: int):
        # content can also be Environment or list of Environments, but for type hints only in python >= 3.11   
        # Insert an option at a specific index. If the index is out of range, raise an error, unless the index is the length of the array in which case just append
        if index > len(self.content):
            raise IndexError(f"Cannot insert content: index {index} is out of range for content list of length {len(self.content)}")
        self.content.insert(index, content)
    
    def remove_content(self, index: int):
        # Remove an option at a specific index. If the index is out of range, raise an error
        if index >= len(self.content):
            raise IndexError(f"Cannot remove content: index {index} is out of range for content list of length {len(self.content)}")
        del self.content[index]

    def set_parent(self, other):
        if not isinstance(other, Environment):
            raise TypeError(f"Cannot set parent: {other} is not an Environment")
        other.add_content(self)

    def __str__(self):
        # start_line = f"\\begin{{{self.name}}}{''.join([str(o) for o in self.arguments])}"
        start_line = str(Macro("begin", [self.name] + self.arguments))
        # end_line = f"\\end{{{self.name}}}"
        end_line = str(Macro("end", [self.name]))
        mid_lines = "\n".join([str(item) for item in self.content])
        # indent each of mid_lines by one tab
        mid_lines = "\n".join(["\t" + line for line in mid_lines.split("\n")])
        return start_line + "\n" + mid_lines + "\n" + end_line
    
class EmptyEnvironment(Environment):
    def __init__(self, content = None):
        super().__init__(name = None, content = content)

    def __str__(self):
        return "\n".join([str(item) for item in self.content])
