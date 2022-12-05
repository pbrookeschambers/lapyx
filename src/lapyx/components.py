# Contains functions for generating common LaTeX components


import io
from pathlib import Path
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
        """The ``Table`` class is designed to make LaTeX tables less of a headache. Data can be 
        added, modified, and removed from the table, and all LaTeX formatting can be easily 
        specified. The ``Table`` object can be passed directly to :meth:`~lapyx.output.export`
        to be included in the final document.

        Parameters
        ----------
        data : pd.DataFrame | np.ndarray | List[List[Any]] | str, optional, default ``None``
            The data to be inserted into the table. If a ``str`` is passed, this will be taken as a 
            file path to a ``.csv`` file. If a ``pandas.DataFrame`` or ``numpy.ndarray`` is passed,
            this will be converted to a list of lists, keeping the column names as headers if they
            are present in the ``DataFrame``. 
        centered : bool, optional, default ``True``
            If ``True``, the table will be centered in the document, either using a ``center``
            environment, or with the ``\\centering`` macro if the table is floating.
        floating : bool, optional, default ``False``
            If ``True``, the ``tabular`` environment will be wrapped in a floating ``table``
            environment.
        floating_position : str, optional, default ``"ht!"``
            The optional positional argument to be passed to the ``table`` environment if the table
            is floating. Setting this does not set ``floating`` to ``True``.
        caption : str, optional, default ``None``
            The caption to be used for the table. If ``None``, no caption will be used. Setting
            this sets ``floating`` to ``True``.
        caption_position : str, optional, default ``"bottom"``
            The position at which to place the caption relative to the tabular. This is only used
            if ``caption`` is not ``None``. Valid options are ``"top"`` or ``"bottom"``.
        label : str, optional, default ``None``
            The label to use for the ``table`` environment. Setting this sets ``floating`` to
            ``True``, and forces an empty caption if ``caption`` is ``None``.
        long : bool, optional, default ``False``
            If ``True``, the ``tabular`` environment will be replaced by a ``longtable`` 
            environment. 

            .. warning::

                This is not yet implemented.
        headers : str | List[str], optional, default ``None``
            String or list of strings to be used as the column headers for the table. If ``None``,
            no header row will be produced.
        use_headers : bool, optional, default ``True``
            If ``True``, a header row will be included in the output table, provided headers are 
            given.
        alignment : str | List[str], optional, default ``None``
            String or list of strings, each of which will be used for the alignment of the columns.
            These should be one of ``"l"``, ``"c"``, or ``"r"``, and will be adjusted as necessary
            if column widths are specified.
        column_widths : str | List[str], optional, default ``None``
            String or list of strings to specify the column widths of each table column. These must 
            be valid LaTeX lengths (i.e., with units or in terms of length macros such as
            ``\\textwidth``). If any entry is ``None``, the column width will be left unspecified.
        format_string : str | List[str], optional, default ``None``
            String or list of strings which specifies the Python format string to be used for each
            column when converting ``data`` to a string. If ``None``, the default formatting will
            be used. These will be passed as ``{data:format_string}`` in an f-string.
        header_format : str, optional, default ``None``
            String or list of strings specifying the LaTeX formatting to be prepended to each 
            header cell. If ``None``, no formatting will be applied. The final macro may optionally
            take the column header as an argument.
        max_rows_before_split : int, optional, default ``None``
            The maximum number of rows to be included in a single ``tabular`` environment before
            splitting the table into multiple columns. If ``None``, the table will not be split
            unless ``split_table_into_columns`` is specified.
        split_table_into_columns : int, optional, default ``None``
            The number of separate ``tabular`` environments to render. The ``data`` will be split 
            between the ``tabular`` s as equally as possible by number of rows (not by rendered
            height). If ``None``, the table will not be split unless ``max_rows_before_split`` is
            set. This argument takes precedence over ``max_rows_before_split``.
        csv_reader : str, optional, default ``None``
            If ``data`` is a string, this argument can be used to specify which csv reader to use.
            Valid options are ``"pandas"`` (which uses ``pandas.read_csv``), ``"numpy"`` (which
            uses ``numpy.genfromtxt``), or ``"csv"`` (using  ``csv.reader``). This is also the 
            order of preference if ``csv_reader`` is not specified.
        csv_options : dict, optional, default ``{}``
            If specified, these are passed as keyword arguments to whichever csv reader is used to 
            parse a ``csv`` file specified by ``data``.

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
        """Set the data associated with the table, from a ``pandas.DataFrame``, ``numpy.ndarray``,
        nested list, or ``.csv`` file.

        Parameters
        ----------
        new_data : pd.DataFrame | np.ndarray | List[List[Any]] | str
            The data to be inserted into the table. If a ``str`` is passed, this will be taken as a 
            file path to a ``.csv`` file. If a ``pandas.DataFrame`` or ``numpy.ndarray`` is passed,
            this will be converted to a list of lists, keeping the column names as headers if they
            are present in the ``DataFrame``. 

        Raises
        ------
        ImportError
            If ``csv_reader`` has been specified as either ``"pandas"`` or ``"numpy"``, but the
            appropriate package installation cannot be found.
        ValueError
            If the passed ``csv_reader`` is not recognised.
        TypeError
            If the ``new_data`` passed is not a nested list and cannot be converted to a nested 
            list.
        ValueError
            If the rows are of unequal length.
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
        """Add a new row to the table.

        Parameters
        ----------
        new_data : pd.DataFrame | np.ndarray | List[Any], optional, default ``None``
            The new data to be added. If a ``pandas.DataFrame`` or ``numpy.ndarray`` is passed,
            it will be converted to a list. If ``None`` is passed, a new row of empty strings
            will be added.
        index : int, optional, default ``None``
            If provided, the new row will be inserted at the given index. Otherwise, it will be
            appended to the end of the table.

        Raises
        ------
        ValueError
            If the ``new_data`` passed is not 1-dimensional; i.e., if any element of ``new_data``
            is a list or tuple.
        ValueError
            If the length of ``new_data`` does not match the number of columns in the table.
        IndexError
            If ``index`` is provided and is out of range for the table.
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
            if index >= len(self.data):
                raise IndexError(
                    f"index must be less than the number of rows in the table: received {index}, expected less than {len(self.data)}")
            self.data.insert(index, new_data)
        else:
            self.data.append(new_data)
        self.num_rows += 1

    def add_rows(
        self, 
        new_data: pd.DataFrame | np.ndarray | List[List[Any]], 
        index: int = None
    ):
        """Add multiple new rows to the table.

        Parameters
        ----------
        new_data : pd.DataFrame | np.ndarray | List[List[Any]]
            The new data to be added. If a ``pandas.DataFrame`` or ``numpy.ndarray`` is passed,
            it will be converted to a list. 
        index : int, optional, default ``None``
            If provided, the new rows will be inserted starting at the given index, maintaining
            their order. Otherwise, they will be appended to the end of the table. 
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
        """Add a new column to the table.

        Parameters
        ----------
        new_data : pd.DataFrame | np.ndarray | List[Any], optional, default ``None``
            The new data to be added. If a ``pandas.DataFrame`` or ``numpy.ndarray`` is passed,
            it will be converted to a list. If ``None`` is passed, a new column of empty strings
            will be added. If the ``DataFrame`` has a column name, it will be extracted and used
            as the column header. Otherwise, an empty string will be used.
        index : int, optional, default ``None``
            If provided, the new column will be inserted at the given index. Otherwise, it will be
            appended to the end of the table.
        column_name : str, optional, default ``None``
            If provided, the new column will be given this name. Otherwise, it will be given the
            name of the column in the ``pandas.DataFrame`` if one is provided, or an empty string
            otherwise.

        Raises
        ------
        ValueError
            If the ``new_data`` passed is not 1-dimensional; i.e., if any element of ``new_data``
            is a list or tuple.
        ValueError
            If the length of ``new_data`` does not match the number of rows in the table.
        IndexError
            If ``index`` is provided and is out of range for the table.
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
            if index >= self.num_columns:
                raise IndexError(
                    f"index must be less than the number of columns in the table: received {index}, expected less than {self.num_columns}")
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
        """Add multiple columns to the table.

        Parameters
        ----------
        new_data : pd.DataFrame | np.ndarray | List[List[Any]]
            The new data to be added. If a ``pandas.DataFrame`` or ``numpy.ndarray`` is passed,
            it will be converted to a list. If the ``DataFrame`` has column names, they will be
            extracted and used as the column headers. Otherwise, empty strings will be used.
        index : int, optional, default ``None``
            If provided, the new columns will be inserted at the given index. Otherwise, they will be
            appended to the end of the table.
        column_names : list, optional, default ``None``
            If provided, the new columns will be given these names. Otherwise, they will be given the
            names of the columns in the ``pandas.DataFrame`` if one is provided, or empty strings
            otherwise.
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
        """Transpose the table, i.e., swap the rows and columns.

        Parameters
        ----------
        include_headers : bool, optional, default ``True``
            If ``True``, the headers of the table will become the first column of the transposed table.
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
        """Center the table, either by wrapping the ``tabular`` environment in a ``center`` environment,
        or using ``\\centering`` if the table is floating.

        Parameters
        ----------
        centered : bool, optional, default ``True``
            If ``True``, table will be centered.
        """        
               
        self.centered = centered

    def float(self, floating: bool = True, floating_pos: str = None):
        """Make the ``tabular`` float by wrapping it in a ``table`` environment, optionally
        specifying the float position.

        Parameters
        ----------
        floating : bool, optional, default ``True``
            If ``True``, table will float.
        floating_pos : str, optional, default ``None``
            The optional position argument passed to the ``table`` environment. If ``None``, the
            current position is kept. 
        """        
              
        self.floating = floating
        if floating_pos is not None:
            self.floating_pos = floating_pos

    def long(self, long: bool = True):
        """Allow the table to split at page breaks by replacing it with a ``longtable``.

        .. warning::
            This is not yet implemented.

        Parameters
        ----------
        long : bool, optional, default ``True``
            If ``True``, table will be a ``longtable``.
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
        """Set one or more headers for the table. Behaviour is different depending on the type of
        ``headers``.

        * If ``headers`` is a string

          * If ``column_index`` is not specified, all headers will be set to ``headers``, equivalent to ``table_headers[:] = headers``.
          * If ``column_index`` is specified but ``column_end_index`` is not, the header at ``column_index`` will be set to ``headers``, equivalent to ``table_headers[column_index] = headers``.
          * If ``column_index`` and ``column_end_index`` are set, the slice of columns they define will be set to ``headers``, equivalent to ``table_headers[column_index:column_end_index] = headers``.

        * If ``headers`` is a list

          * If ``column_index`` is not set, then it is required that ``len(headers) == num_columns``. If this is the case, all column headings will be set to ``headers``, equivalent to ``table_headers[:] = headers``.
          * If ``column_index`` is specified, but ``column_end_index`` is not, then it is required that ``headers`` has length equal to ``num_columns - column_index``. If this is the case, the slice of columns starting at ``column_index`` will be set to ``headers``, equivalent to ``table_headers[column_index:] = headers``. 
          * If ``column_index`` and ``column_end_index`` are set, then it is required that ``len(headers) == column_end_index - column_index``. If this is the case, the slice of columns they define will be set to ``headers``, equivalent to ``table_headers[column_index:column_end_index] = headers``.

        Parameters
        ----------
        headers : list | str
            The header or headers to be applied to the table.
        column_index : int, optional, default ``None``
            The first column to which the header will be applied.
        column_end_index : int, optional, default ``None``
            The last column to which the header will be applied.
        """        
        # Double check that column_end_index does what you claim; might be off by 1 column
          
        self.headers = self.__insert_at(
            self.headers, headers, column_index, column_end_index)

    def set_alignment(self, alignment: list | str, column_index: int = None, column_end_index: int = None):
        """Set one or more alignments for the table. Behaviour is different depending on the type of
        ``alignment``. These will automatically be adjusted during compilation if ``column_widths`` 
        are specified.

        * If ``alignment`` is a string

          * If ``column_index`` is not specified, all alignments will be set to ``alignment``, equivalent to ``table_alignment[:] = alignment``.
          * If ``column_index`` is specified but ``column_end_index`` is not, the alignment at ``column_index`` will be set to ``alignment``, equivalent to ``table_alignment[column_index] = alignment``.
          * If ``column_index`` and ``column_end_index`` are set, the slice of columns they define will be set to ``alignment``, equivalent to ``table_alignment[column_index:column_end_index] = alignment``.

        * If ``alignment`` is a list

          * If ``column_index`` is not set, then it is required that ``len(alignment) == num_columns``. If this is the case, all column alignments will be set to ``alignment``, equivalent to ``table_alignment[:] = alignment``.
          * If ``column_index`` is specified, but ``column_end_index`` is not, then it is required that ``alignment`` has length equal to ``num_columns - column_index``. If this is the case, the slice of columns starting at ``column_index`` will be set to ``alignment``, equivalent to ``table_alignment[column_index:] = alignment``.
          * If ``column_index`` and ``column_end_index`` are set, then it is required that ``len(alignment) == column_end_index - column_index``. If this is the case, the slice of columns they define will be set to ``alignment``, equivalent to ``table_alignment[column_index:column_end_index] = alignment``.



        Parameters
        ----------
        alignment : list | str
            The alignment or alignments to be applied to the table. Each alignment should be one of 
            ``"l"``, ``"c"``, or ``"r"``.
        column_index : int, optional, default ``None``
            The first column to which the alignment will be applied.
        column_end_index : int, optional, default ``None``
            The last column to which the alignment will be applied.
        """        
        
        self.alignment = self.__insert_at(
            self.alignment, alignment, column_index, column_end_index)

    def set_column_widths(self, widths: list | str, column_index: int = None, column_end_index: int = None):
        """Set one or more column widths for the table. Behaviour is different depending on the 
        type of ``widths``. A column width of ``None`` indicates that the column should be allowed
        to resize to fit its contents (the default LaTeX behaviour for alignments like ``l`` and 
        ``c``).

        * If ``widths`` is a string
        
          * If ``column_index`` is not specified, all column widths will be set to ``widths``, equivalent to ``table_column_widths[:] = widths``.
          * If ``column_index`` is specified but ``column_end_index`` is not, the column width at ``column_index`` will be set to ``widths``, equivalent to ``table_column_widths[column_index] = widths``.
          * If ``column_index`` and ``column_end_index`` are set, the slice of columns they define will be set to ``widths``, equivalent to ``table_column_widths[column_index:column_end_index] = widths``.

        * If ``widths`` is a list

          * If ``column_index`` is not set, then it is required that ``len(widths) == num_columns``. If this is the case, all column widths will be set to ``widths``, equivalent to ``table_column_widths[:] = widths``.
          * If ``column_index`` is specified, but ``column_end_index`` is not, then it is required that ``widths`` has length equal to ``num_columns - column_index``. If this is the case, the slice of columns starting at ``column_index`` will be set to ``widths``, equivalent to ``table_column_widths[column_index:] = widths``.
          * If ``column_index`` and ``column_end_index`` are set, then it is required that ``len(widths) == column_end_index - column_index``. If this is the case, the slice of columns they define will be set to ``widths``, equivalent to ``table_column_widths[column_index:column_end_index] = widths``.

        Parameters
        ----------
        widths : list | str
            The column width or widths to be applied to the table. Column widths should be valid 
            LaTeX lengths, i.e. they should include units or LaTeX length macros such as 
            ``\\textwidth``.
        column_index : int, optional, default ``None``
            The first column to which the column width will be applied.
        column_end_index : int, optional, default ``None``
            The last column to which the column width will be applied.
        """        
        
        self.column_widths = self.__insert_at(
            self.column_widths, widths, column_index, column_end_index)

    def set_format(self, format_string: list | str, column_index: int = None, column_end_index: int = None):
        """Set one or more format strings for the table. Behaviour is different depending on the
        type of ``format_string``. 

        * If ``format_string`` is a string

          * If ``column_index`` is not specified, all format strings will be set to ``format_string``, equivalent to ``table_format[:] = format_string``.
          * If ``column_index`` is specified but ``column_end_index`` is not, the format string at ``column_index`` will be set to ``format_string``, equivalent to ``table_format[column_index] = format_string``.
          * If ``column_index`` and ``column_end_index`` are set, the slice of columns they define will be set to ``format_string``, equivalent to ``table_format[column_index:column_end_index] = format_string``.

        * If ``format_string`` is a list

          * If ``column_index`` is not set, then it is required that ``len(format_string) == num_columns``. If this is the case, all format strings will be set to ``format_string``, equivalent to ``table_format[:] = format_string``.
          * If ``column_index`` is specified, but ``column_end_index`` is not, then it is required that ``format_string`` has length equal to ``num_columns - column_index``. If this is the case, the slice of columns starting at ``column_index`` will be set to ``format_string``, equivalent to ``table_format[column_index:] = format_string``.
          * If ``column_index`` and ``column_end_index`` are set, then it is required that ``len(format_string) == column_end_index - column_index``. If this is the case, the slice of columns they define will be set to ``format_string``, equivalent to ``table_format[column_index:column_end_index] = format_string``.

        Parameters
        ----------
        format_string : list | str
            The format string or strings to be applied to the table. Each format string should be a 
            valid Python format specifier, which will be applied to the values in the corresponding
            column as ``{value:format_string}``. As such, to specify the default formatting for a
            column, pass an empty string.
        column_index : int, optional, default ``None``
            The first column to which the format string will be applied.
        column_end_index : int, optional, default ``None``
            The last column to which the format string will be applied.
        """        
        
        self.format = self.__insert_at(
            self.format, format_string, column_index, column_end_index)

    def set_header_format(self, new_format: str) -> None:
        """Set the format for the table headers in LaTeX. This should be valid LaTeX markup, and
        can optionally end with a macro which would take the header as an argument, such as
        ``\\bfseries\\textcolor{red}``, where the header would become the second argument to the
        ``\\textcolor`` macro.

        Parameters
        ----------
        new_format : str
            The format for the table headers.
        """        
            
        self.header_format = new_format

    def set_caption(self, caption: str):
        """Set the caption for the table. If the table is not already floating, it will be made
        to float unless the ``caption`` is not specified (or ``None``). Passing no caption will
        remove the caption, but will not unfloat the table - use ``Table.float(False)`` after
        the call to ``caption()`` for this.

        Parameters
        ----------
        caption : str
            The caption for the table.
        """        
             
        self.caption = caption
        if caption is not None:
            # can't have a caption if we're not floating
            self.floating = True

    def set_label(self, label: str):
        """Set the label for the table. If the table is not already floating, it will be made
        to float unless the ``label`` is not specified (or ``None``). Passing no label will
        remove the label, but will not unfloat the table - use ``Table.float(False)`` after
        the call to ``label()`` for this. If a label is specified but no caption is given, a blank
        caption will be inserted during compilation.

        Parameters
        ----------
        label : str
            The label for the table.
        """        
           
        self.label = label
        if label is not None:
            # can't have a label if we're not floating
            self.floating = True

    def use_headers(self, use: bool = True):
        """Set whether the table should use headers. If ``use`` is ``True``, the table will include
        the headers as the first row, with an additional separator before the data. If ``use`` is
        ``False``, the headers will not be included and the first row will receive no special
        formatting.

        Parameters
        ----------
        use : bool, optional, default ``True``
            Whether the output table should use any headers.
        """            
        self.use_header_row = use

    def split_after_rows(self, num_rows: int):
        """Set the maximum number of rows before the ``tabular`` environment should be split into
        multiple tables. This is useful for tables which are too large to fit on a single page, or 
        tables with many rows but few columns. This will be overridden if ``split_into_columns`` is
        specified. ``tabular`` s will be populated to their maximum before moving on to the next
        table, in contrast to ``split_into_columns`` which attempts to evenly distribute the rows.

        Parameters
        ----------
        num_rows : int
            The maximum number of rows in a given ``tabular``.
        """        
           
        self.max_rows_before_split = num_rows

    def split_into_columns(self, num_columns: int):
        """Set the number of columns into which the ``tabular`` environment should be split. This is
        useful for tables which are too wide to fit on a single page, or tables with many rows but
        few columns. This will override ``split_after_rows``. The data rows will be divided as
        equally as possible between ``num_columns`` tables, preferentially filling earlier tables. 
        

        Parameters
        ----------
        num_columns : int
            The number of columns into which the ``tabular`` environment should be split.
        """        
         
        self.split_table_into_columns = num_columns


    def to_latex(self) -> str:
        """Export the ``Table`` object to valid LaTeX markup, paying attention to all formatting
        options which have been applied. 

        Returns
        -------
        str
            The complete LaTeX markup for the table.
        """        

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
    

    def __init__(
        self,
        figure: mplFigure | str = None,
        centered: bool = True,
        floating: bool = False,
        floating_position: str = "ht!",
        caption: str = None,
        label: str = None,
        width: str = None,
        height: str = None,
        scale: str = None
    ):      
        """The ``Figure`` class is designed to handle the storing and exporting of matplotlib
        figures and image files to LaTeX markup. Changes to a matplotlib figure associated with
        a ``Figure`` object can be made either by directly manipulating the ``Figure`` object's
        ``Figure.figure`` attribute (which is a ``matplotlib.figure.Figure`` object), or by
        calling a number of convenience functions on the ``Figure`` object itself. The ``Figure``
        object can be passed directly to ``export()`` to be included in the final document.

        .. warning::
            It is important to not ``plt.show()`` any figures from within a LaPyX document, as
            there is no timeout condition during compilation, so the compilation will hang
            indefinitely while the figure is "shown" in the background.

        Parameters
        ----------
        figure : mplFigure | str, optional, default ``None``
            The figure to associate with this object. If a string is passed, it will be considered
            a file path to a valid, LaTeX-compatible image file. If a maptlotlib figure is passed,
            it will be used directly. If ``None`` is passed, LaPyX will search for any most recently
            active matplotlib figure, and use that if it exists. If no matplotlib figure is found,
            a new figure will be created.
        centered : bool, optional, default ``True``
            If ``True``, the figure will be centered in the document, either using a ``center``
            environment, or with the ``\\centering`` macro, depending on whether the figure is
            floating.
        floating : bool, optional, default ``False``
            If ``True``, the figure will be placed in a ``figure`` environment. If ``False``, the
            figure will simply be a call to ``\\includegraphics`` without the floating ``figure`` 
            environment.
        floating_position : str, optional, default ``"ht!"``
            The optional positional argument to be passed to the ``figure`` environment if the
            figure is floating. Setting this does not set ``floating`` to ``True``.
        caption : str, optional, default ``None``
            The caption to be used for the figure. If ``None``, no caption will be used. Setting 
            this sets ``floating`` to ``True``.
        label : str, optional, default ``None``
            The label to be used for the figure. Setting this sets ``floating`` to ``True``, and 
            forces an empty caption if ``caption`` is ``None``. 
        width : str, optional, default ``None``
            The width of the image in the final figure, i.e. the value of the ``width`` argument
            passed to ``\\includegraphics``. This must be a valid LaTeX length, i.e. with units or
            in terms of a LaTeX length macro such as ``\\textwidth``.
        height : str, optional, default ``None``
            The height of the image in the final figure, i.e. the value of the ``height`` argument
            passed to ``\\includegraphics``. This must be a valid LaTeX length, i.e. with units or
            in terms of a LaTeX length macro such as ``\\textwidth``.
        scale : str, optional, default ``None``
            The scale of the image in the final figure, i.e. the value of the ``scale`` argument
            passed to ``\\includegraphics``. 


        Raises
        ------
        TypeError
            If the ``figure`` argument is provided but is not a string or a matplotlib figure.
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
        """Set the figure associated with this object. If a string is passed, it will be considered
        a file path to a valid, LaTeX-compatible image file. If a maptlotlib figure is passed, it
        will be used directly.

        Parameters
        ----------
        figure : mplFigure | str
            The figure to associate with this object.

        Raises
        ------
        TypeError
            If the ``figure`` passed is not a string or a matplotlib figure.
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
        """Set the caption for this figure. If the figure is not already floating, it will be made
        to float unless the ``caption`` is not specified (or ``None``). Passing no caption will
        remove the caption, but will not unflaot the figure - use ``Figure.flaot(False)`` after the
        call to ``caption()`` for this.

        Parameters
        ----------
        caption : str
            The caption to be used for the figure.
        """
         
        self.caption = caption
        if caption is not None:
            self.floating = True  # if we have a caption, we need to be floating

    def set_label(self, label: str):
        """Set the label for this figure. If the figure is not already floating, it will be made
        to float unless the ``label`` is not specified (or ``None``). Passing no label will remove
        the label, but will not unflaot the figure - use ``Figure.flaot(False)`` after the call to
        ``label()`` for this. If a label is specified but no caption is given, a blank caption will 
        be inserted during compilation.

        Parameters
        ----------
        label : str
            The label to be used for the figure.
        """        
        
        self.label = label
        if label is not None:
            self.floating = True

    def set_size(self, width: float = None, height: float = None, scale: float = None):
        """Set the width, height, and/or scale of the image in the final figure. 

        Parameters
        ----------
        width : float, optional, default ``None``
            The width of the image in the final figure, i.e. the value of the ``width`` argument
            passed to ``\\includegraphics``. This must be a valid LaTeX length, i.e. with units or
            in terms of a LaTeX length macro such as ``\\textwidth``.
        height : float, optional, default ``None``
            The height of the image in the final figure, i.e. the value of the ``height`` argument
            passed to ``\\includegraphics``. This must be a valid LaTeX length, i.e. with units or
            in terms of a LaTeX length macro such as ``\\textwidth``.
        scale : float, optional, default ``None``
            The scale of the image in the final figure, i.e. the value of the ``scale`` argument
            passed to ``\\includegraphics``.
        """        
            
        if width is not None:
            self.size["width"] = width
        if height is not None:
            self.size["height"] = height
        if scale is not None:
            self.size["scale"] = scale

    def set_width(self, width: float):
        """Set the width of the image in the final figure, i.e. the value of the ``width`` argument
        passed to ``\\includegraphics``. This must be a valid LaTeX length, i.e. with units or
        in terms of a LaTeX length macro such as ``\\textwidth``.

        Parameters
        ----------
        width : float
            The width of the image in the final figure.
        """        
            
        self.set_size(width=width)

    def set_height(self, height: float):
        """Set the height of the image in the final figure, i.e. the value of the ``height`` argument
        passed to ``\\includegraphics``. This must be a valid LaTeX length, i.e. with units or
        in terms of a LaTeX length macro such as ``\\textwidth``.

        Parameters
        ----------
        height : float
            The height of the image in the final figure.
        """        
        
        self.set_size(height=height)

    def set_scale(self, scale: float):
        """Set the scale of the image in the final figure, i.e. the value of the ``scale`` argument
        passed to ``\\includegraphics``.

        Parameters
        ----------
        scale : float
            The scale of the image in the final figure.
        """        
        
        self.set_size(scale=scale)

    def float(self, floating: bool = True, floating_pos: str = None):
        """Make the image float by wrapping it in a ``figure`` environment, optionally specifying
        the float position. 

        Parameters
        ----------
        floating : bool, optional, default ``True``
            If ``True``, the image will float. 
        floating_pos : str, optional, default ``None``
            The optional position argument passed to the ``figure`` environment. If ``None``, the
            current position is kept.
        """        
        
        self.floating = floating
        if floating_pos is not None:
            self.floating_pos = floating_pos

    def center(self, centered: bool = True):
        """Center the figure, either by wrapping the call to ``\\includegraphics`` in a ``center``
        environment, or using ``\\centering`` if the figure is floating. 

        Parameters
        ----------
        centered : bool, optional, default ``True``
            If ``True``, the figure will be centered.
        """        
        self.centered = centered

    # matplotlib functions --------------------------------------------------------------------

    def __check_for_figure(self):
        if self.figure is None:
            raise ValueError(
                "There is no matplotlib figure associated with this Figure object.")

    def plot(self, *args, **kwargs):
        """A wrapper for ``matplotlib.figure.Figure.gca().plot``. All arguments and keyword
        arguments are passed directly to the ``plot`` function.

        Raises
        ------

        ValueError
            If there is no matplotlib figure associated with this Figure object.
        """
        self.__check_for_figure()
        self.figure.gca().plot(*args, **kwargs)

    def scatter(self, *args, **kwargs):
        """A wrapper for ``matplotlib.figure.Figure.gca().scatter``. All arguments and keyword
        arguments are passed directly to the ``scatter`` function.

        Raises
        ------

        ValueError
            If there is no matplotlib figure associated with this Figure object.
        """        
        self.__check_for_figure()
        self.figure.gca().scatter(*args, **kwargs)

    def errorbar(self, *args, **kwargs):
        """A wrapper for ``matplotlib.figure.Figure.gca().errorbar``. All arguments and keyword
        arguments are passed directly to the ``errorbar`` function.

        Raises
        ------

        ValueError
            If there is no matplotlib figure associated with this Figure object.
        """        
        
        self.__check_for_figure()
        self.figure.gca().errorbar(*args, **kwargs)

    def hist(self, *args, **kwargs):
        """A wrapper for ``matplotlib.figure.Figure.gca().hist``. All arguments and keyword
        arguments are passed directly to the ``hist`` function.

        Raises
        ------

        ValueError
            If there is no matplotlib figure associated with this Figure object.
        """      
        self.__check_for_figure()
        self.figure.gca().hist(*args, **kwargs)

    def imshow(self, *args, **kwargs):
        """A wrapper for ``matplotlib.figure.Figure.gca().imshow``. All arguments and keyword
        arguments are passed directly to the ``imshow`` function.

        Raises
        ------

        ValueError
            If there is no matplotlib figure associated with this Figure object.
        """      
        self.__check_for_figure()
        self.figure.gca().imshow(*args, **kwargs)

    def xlabel(self, *args, **kwargs):
        """A wrapper for ``matplotlib.figure.Figure.gca().xlabel``. All arguments and keyword
        arguments are passed directly to the ``xlabel`` function.

        Raises
        ------

        ValueError
            If there is no matplotlib figure associated with this Figure object.
        """      
        self.__check_for_figure()
        self.figure.gca().set_xlabel(*args, **kwargs)

    def ylabel(self, *args, **kwargs):
        """A wrapper for ``matplotlib.figure.Figure.gca().ylabel``. All arguments and keyword
        arguments are passed directly to the ``ylabel`` function.

        Raises
        ------

        ValueError
            If there is no matplotlib figure associated with this Figure object.
        """      
        self.__check_for_figure()
        self.figure.gca().set_ylabel(*args, **kwargs)

    def title(self, *args, **kwargs):
        """A wrapper for ``matplotlib.figure.Figure.gca().title``. All arguments and keyword
        arguments are passed directly to the ``title`` function.

        Raises
        ------

        ValueError
            If there is no matplotlib figure associated with this Figure object.
        """      
        self.__check_for_figure()
        self.figure.gca().set_title(*args, **kwargs)

    def legend(self, *args, **kwargs):
        """A wrapper for ``matplotlib.figure.Figure.gca().legend``. All arguments and keyword
        arguments are passed directly to the ``legend`` function.

        Raises
        ------

        ValueError
            If there is no matplotlib figure associated with this Figure object.
        """      
        self.__check_for_figure()
        self.figure.gca().legend(*args, **kwargs)

    def xlim(self, *args, **kwargs):
        """A wrapper for ``matplotlib.figure.Figure.gca().xlim``. All arguments and keyword
        arguments are passed directly to the ``xlim`` function.

        Raises
        ------

        ValueError
            If there is no matplotlib figure associated with this Figure object.
        """      
        self.__check_for_figure()
        self.figure.gca().set_xlim(*args, **kwargs)

    def ylim(self, *args, **kwargs):
        """A wrapper for ``matplotlib.figure.Figure.gca().ylim``. All arguments and keyword
        arguments are passed directly to the ``ylim`` function.

        Raises
        ------

        ValueError
            If there is no matplotlib figure associated with this Figure object.
        """      
        self.__check_for_figure()
        self.figure.gca().set_ylim(*args, **kwargs)

    def savefig(self, *args, **kwargs):
        """A wrapper for ``matplotlib.figure.Figure.gca().savefig``. All arguments and keyword
        arguments are passed directly to the ``savefig`` function.

        Raises
        ------

        ValueError
            If there is no matplotlib figure associated with this Figure object.
        """      
        self.__check_for_figure()
        self.figure.savefig(*args, **kwargs)

    # Any other matplotlib functions should be called on the figure directly, otherwise this will get out of hand

    def to_latex(self, base_dir: str, temp_dir: str, **kwargs) -> str:
        """Export the ``Figure`` object to valid LaTeX markup, paying attention to all formatting 
        options which have been applied. If the ``Figure`` was initialised with a file path, or
        has been given a file path with the ``Figure.set_figure`` method, this file will be passed
        to ``\\includegraphics`` directly. If there is a matplotlib figure associated with this
        ``Figure``, it will first be saved, with the file path determined by the ``base_dir`` and
        ``temp_dir`` arguments. Any additional keyword arguments are passed directly to the
        ``matplotlib.figure.Figure.savefig`` function.

        .. warning::
            It is advised that you do not call this method directly, and instead pass the ``Figure`` 
            object to ``export()`` directly. This will ensure that ``base_dir`` and ``temp_dir`` are
            correctly set, and temporary files can be cleaned after compilation.
        
        Parameters
        ----------
        base_dir : str
            The base directory of the LaTeX document. This will be supplied automatically by the
            ``export()`` function.
        temp_dir : str
            The temporary directory and prefix for the figure file. This will be supplied automatically
            by the ``export()`` function.

        Returns
        -------
        str
            The complete LaTeX markup for the figure.
        """        

        container = EmptyEnvironment()           

        if isinstance(base_dir, str):
            base_dir = Path(base_dir)
        figure_file_name = Path(base_dir, self.figure_name)
        if not self.using_file:
            # if we have a figure, save it to {temp_dir}/lapyx_figures/{id}.pdf
            # create {temp_dir}/lapyx_figures if it doesn't exist
            if not Path(temp_dir, "lapyx_figures").exists():
                Path(temp_dir, "lapyx_figures").mkdir()
            if self.figure is not None:
                figure_file_name = temp_dir / "lapyx_figures" / f"{self.figure_name}.{kwargs['extension'] if 'extension' in kwargs else 'pdf'}"
                self.figure.savefig(
                    figure_file_name, 
                    bbox_inches='tight',
                    **kwargs
                )


        
        includegraphics_opts = KWArgs()
        if self.size["width"] is not None:
            includegraphics_opts.add_argument("width", self.size["width"])
        if self.size["height"] is not None:
            includegraphics_opts.add_argument("height", self.size["height"])
        if self.size["scale"] is not None:
            includegraphics_opts.add_argument("scale", self.size["scale"])
        
        includegraphics = Macro("includegraphics")
        if not includegraphics_opts.is_empty():
            includegraphics.add_argument(OptArg(includegraphics_opts))
        includegraphics.add_argument(figure_file_name)

        
        if self.floating:
            outer_figure = Environment("figure")
            container.add_content(outer_figure)
            if self.floating_pos is not None:
                outer_figure.set_optional_arg(self.floating_pos)
            else:
                outer_figure.set_optional_arg("ht!")
            if self.centered:
                outer_figure.add_content(r"\centering")
            outer_figure.add_content(includegraphics)
            if self.caption is not None:
                outer_figure.add_content(Macro("caption", arguments = self.caption))
            if self.label is not None:
                if self.caption is None:
                    # Empty caption to show figure number
                    outer_figure.add_content(Macro("caption", arguments = ""))
                outer_figure.add_content(Macro("label", arguments = self.label))

        else:
            if self.centered:
                center = Environment("center")
                container.add_content(center)
                center.add_content(includegraphics)
            else:
                container.add_content(includegraphics)
        return str(container)

class KWArgs:

    def __init__(self, args: dict = None):
        """``KWArgs`` is a helper class for storing key-value paris of LaTeX arguments, and 
        simplifying the process of converting them to LaTeX markup. ``KWArgs`` will throw an error
        if an argument is passed which is not a string or an instance of ``Arg`` (or by extension 
        ``OptArg``).

        Parameters
        ----------
        args : dict, optional, default ``None``
            An initial dictionary of arguments to add to the ``KWArgs`` object. The value of each
            key-value pair should be a string, or an instance of ``Arg``.
        """        
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


    def add_argument(self, key: str, value: str):
        """Add an argument to the ``KWArgs`` object. The value of the argument should be a string,
        or an instance of ``Arg``.

        Parameters
        ----------

        key : str
            The name of the argument.
        value : str
            The value of the argument. This should be a string, or an instance of ``Arg``.
        """
        self.args[key] = value
        self._check_values()
    
    def set_argument(self, key: str, value: str):
        """Set an argument in the ``KWArgs`` object. If the argument does not already exist, it
        will be added. The value of the argument should be a string, or an instance of ``Arg``.

        Parameters
        ----------
        key : str
            The name of the argument.
        value : str
            The value of the argument. This should be a string, or an instance of ``Arg``.
        """        
        self.add_argument(key, value)

    def remove_argument(self, key: str):
        """Remove an argument from the ``KWArgs`` object.

        Parameters
        ----------

        key : str
            The name of the argument to remove.
        """
        del self.args[key]

    def set_arguments(self, new_values: dict):
        """Set multiple key-value pairs simultaneously. The values of the arguments should be strings,
        or instances of ``Arg``. Any keys which already exist will be overwritten.

        Parameters
        ----------
        new_values : dict
            A dictionary of key-value pairs to add to the ``KWArgs`` object.
        """        
        self.args = {**self.args, **new_values}
        self._check_values()

    def remove_arguments(self, keys: List[str]):
        """Remove multiple arguments from the ``KWArgs`` object.

        Parameters
        ----------
        keys : List[str]
            A list of the names of the arguments to remove.
        """        
        for key in keys:
            self.remove_argument(key)

    def __str__(self):
        arg_strings = []
        for key, value in self.args.items():
            if isinstance(value, Arg):
                arg_strings.append(f"{key} = {value}")
            else:
                arg_strings.append(f"{key} = {{{value}}}")
        return ", ".join(arg_strings)

    def is_empty(self) -> bool:
        """Returns ``True`` if the ``KWArgs`` object is empty, ``False`` otherwise.

        Returns
        -------
        bool
            ``True`` if the ``KWArgs`` object is empty, ``False`` otherwise.
        """        
        return len(self.args) == 0

class Arg:

    brackets = ("{", "}")

    def __init__(self, value: str | List[str | KWArgs] | KWArgs = None):
        """``Arg`` is a helper class for storing LaTeX arguments, and simplifying the process of
        converting them to LaTeX markup. Argument values can only be strings, lists of strings, or
        ``KWArgs`` instances.

        Parameters
        ----------
        value : str | List[str | KWArgs] | KWArgs, optional, default ``None``
            The value of the argument. This should be a string, list of strings, or ``KWArgs`` instance(s).
        """        
        self.set_values(value)
    
    def set_values(self, new_values: str | List[str | KWArgs] | KWArgs = None):
        """Set the value(s) of the argument. This will replace any existing values.

        Parameters
        ----------
        new_values : str | List[str | KWArgs] | KWArgs, optional, default ``None``
            The new value(s) to be stored in the argument.

        Raises
        ------
        TypeError
            If a nested list is passed as an argument value.
        """        
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

    def add_value(self, value: str | KWArgs):
        """Append a single value to the argument.

        Parameters
        ----------
        value : str | KWArgs
            Value to be added to the argument.

        Raises
        ------
        TypeError
            If the new value is not a string or ``KWArgs`` instance.
        """        
        if isinstance(value, dict):
            value = KWArgs(value)
            self.value.append(value)
            return
        if not isinstance(value, str) and not isinstance(value, KWArgs):
            raise TypeError(f"Value must be a string, dictionary, or ``KWArgs`` instance.")
        self.value.append(value)
    
    def set_value(self, value: str | KWArgs, index: int):
        """Set one of the values of the argument at a given index.

        Parameters
        ----------
        value : str | KWArgs
            The new value to be stored in the argument.
        index : int
            The which should be replaced.

        Raises
        ------
        IndexError
            If the index is out of range for the number of values in the argument
        TypeError
            If the new value is not a string or ``KWArgs`` instance.
        """         
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
    
    def insert_value(self, value: str | KWArgs, index: int):
        """Insert a new value into the argument at a given index.

        Parameters
        ----------
        value : str | KWArgs
            The new value to be stored in the argument.
        index : int
            The index at which the value should be inserted.

        Raises
        ------
        IndexError
            If the index is out of range for the number of values in the argument.
        TypeError
            If the new value is not a string or ``KWArgs`` instance.
        """        
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
        """Remove the value at a given index from the argument.

        Parameters
        ----------
        index : int
            The index of the value to be removed.

        Raises
        ------
        IndexError
            If the index is out of range for the number of values in the argument.
        """        
        # check if index is in range
        if index >= len(self.value):
            raise IndexError(f"Cannot remove value, index {index} is out of range.")
        del self.value[index]
    
    def __str__(self):
        return self.brackets[0] + ", ".join([str(v) for v in self.value]) + self.brackets[1]

    def __repr__(self):
        return f"Args({self.value})"

class OptArg(Arg):
    """``OptArg`` extends ``Arg`` to represent optional arguments. It is identical in all aspects
    except that it uses square brackets instead of curly braces when converting to LaTeX markup.
    """    

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
        """Add an argument to the macro or environment.

        Parameters
        ----------
        argument : Arg | OptArg | str
            Argument to add
        optional : bool, optional, default ``False``
            If ``True`` and the ``argument`` is a string, it will be converted to an ``OptArg``. If
            ``False`` and the ``argument`` is a string, it will be converted to an ``Arg``.
        """        
        if not isinstance(argument, Arg) and not isinstance(argument, OptArg):
            if optional:
                argument = OptArg(argument)
            else:
                argument = Arg(argument)
        self.arguments.append(argument)
    
    def set_argument(self, argument: Arg | OptArg | str, index: int, optional: bool = False):
        """Set an argument at a given index.

        Parameters
        ----------
        argument : Arg | OptArg | str
            The new argument to be stored.
        index : int
            The index of the argument to be replaced.
        optional : bool, optional, default ``False``
            If ``True`` and the ``argument`` is a string, it will be converted to an ``OptArg``. If
            ``False`` and the ``argument`` is a string, it will be converted to an ``Arg``.

        Raises
        ------
        IndexError
            If the index is out of range for the number of arguments in the macro or environment.
        """         
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
        """Insert an argument at a given index, without replacing any existing arguments.

        Parameters
        ----------
        argument : Arg | OptArg | str
            The new argument to be stored.
        index : int
            The index at which the argument should be inserted.
        optional : bool, optional, default ``False``
            If ``True`` and the ``argument`` is a string, it will be converted to an ``OptArg``. If
            ``False`` and the ``argument`` is a string, it will be converted to an ``Arg``.

        Raises
        ------
        IndexError
            If the index is out of range for the number of arguments in the macro or environment.
        """        
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
        """Remove the argument at a given index.

        Parameters
        ----------
        index : int
            The index of the argument to be removed.

        Raises
        ------
        IndexError
            If the index is out of range for the number of arguments in the macro or environment.
        """        
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
        """``Macro`` is a helper class for storing and outputting LaTeX macros with (ordered) 
        optional and required arguments.

        Parameters
        ----------
        name : str
            Name fo the macro as a string, without the leading ``\\``.
        arguments : Arg | OptArg | str | List[str  |  Arg  |  OptArg], optional, default ``None``
            A list of arguments to be passed to the macro. Each element should be a string, 
            ``Arg``, or ``OptArg`` instance. ``KWArgs`` instances must be wrapped in an ``Arg``
            or ``OptArg`` instance. If a single argument is passed, it will be wrapped in a list.
        """    
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
        """A helper class for storing LaTeX environments and their arguments, possibly in a nested 
        structure.

        Parameters
        ----------
        name : str
            The name of the environment, which will be rendered as ``\\begin{name}`` and
            ``\\end{name}``.
        arguments : Arg | OptArg | str | List[str  |  Arg  |  OptArg], optional, default ``None``
            Argument or list of arguments for the environment. Each element should be a string,
            ``Arg``, or ``OptArg`` instance. ``KWArgs`` instances must be wrapped in an ``Arg``
            or ``OptArg`` instance. If a single argument is passed, it will be wrapped in a list.
        content : str | Table | Figure | Macro | Environment | List[ str  |  Table  |  Figure Macro | Environment], optional, default ``None``
            The content to be stored in and rendered in the environment. Any ``lapyx.components`` 
            class is acceptable, except those derived from ``Arg`` or ``KWArgs``, including 
            other Environments. A list of the same is also acceptable. These will be rendered in 
            the order in which they are added.

            .. warning::
                Be careful not to add an ``Environment`` to its own content or that of its
                children. Recursion is not checked, and will result in an infinite loop.  
        """        
        super().__init__(name, arguments)
        
        if content is None:
            self.content = []
        elif not isinstance(content, list):
            self.content = [content]
        else:
            self.content = content
    
    def add_content(self, content: str | Table | Figure | Macro):
        """Add content to the end of the environment.

        Parameters
        ----------
        content : str | Table | Figure | Macro | Environment
            The new content to be added. Any ``lapyx.components`` class is acceptable, except
            those derived from ``Arg`` or ``KWArgs``, including other Environments. A list of 
            the same is also acceptable and will be added in order. This will be appended as the 
            last item within the environment.
        """        
        # content can also be Environment or list of Environments, but for type hints only in python >= 3.11   
        if isinstance(content, list) or isinstance(content, tuple):
            self.content.extend(content)
        else:
            self.content.append(content)

    def set_content(self, content: str | Table | Figure | Macro, index: int):
        """Set the content at a given index.

        Parameters
        ----------
        content : str | Table | Figure | Macro | Environment
            The new content to be stored. Any ``lapyx.components`` class is acceptable, except
            those derived from ``Arg`` or ``KWArgs``, including other Environments.
        index : int
            The index of the content to be replaced.

        Raises
        ------
        IndexError
            If the index is out of range for the number of content items in the environment.
        """        
        # content can also be Environment or list of Environments, but for type hints only in python >= 3.11   
        # Set an option at a specific index. If the index is out of range, raise an error
        if index >= len(self.content):
            raise IndexError(f"Cannot set content: index {index} is out of range for content list of length {len(self.content)}")
        self.content[index] = content
    
    def insert_content(self, content: str | Table | Figure | Macro, index: int):
        """Insert content at a given index, without replacing any existing content.

        Parameters
        ----------
        content : str | Table | Figure | Macro | Environment
            The new content to be stored. Any ``lapyx.components`` class is acceptable, except
            those derived from ``Arg`` or ``KWArgs``, including other Environments.
        index : int
            The index at which the content should be inserted.

        Raises
        ------
        IndexError
            If the index is out of range for the number of content items in the environment.
        """        
        # content can also be Environment or list of Environments, but for type hints only in python >= 3.11   
        # Insert an option at a specific index. If the index is out of range, raise an error, unless the index is the length of the array in which case just append
        if index > len(self.content):
            raise IndexError(f"Cannot insert content: index {index} is out of range for content list of length {len(self.content)}")
        self.content.insert(index, content)
    
    def remove_content(self, index: int):
        """Remove the content at a given index.

        Parameters
        ----------
        index : int
            The index of the content to be removed.

        Raises
        ------
        IndexError
            If the index is out of range for the number of content items in the environment.
        """        
        # Remove an option at a specific index. If the index is out of range, raise an error
        if index >= len(self.content):
            raise IndexError(f"Cannot remove content: index {index} is out of range for content list of length {len(self.content)}")
        del self.content[index]

    def set_parent(self, other):
        """Adds this environment to the content of another environment.

        Parameters
        ----------
        other : Environment
            The environment to which this environment should be appended as content.

        Raises
        ------
        TypeError
            If the other object is not an ``Environment`` instance.
        """        
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
    """``EmptyEnvironment`` is a convenience class for creating an ``Environment`` object which 
    will not be rendered in the final output, but **will** render its content. This is useful 
    for consistency within Python, but has exactly the same effect as passing each element of
    ``content`` to ``export()`` directly.

    Parameters
    ----------
    content : str | Table | Figure | Macro | Environment | List[ str  |  Table  |  Figure Macro | Environment], optional, default ``None``
        The content to be stored in and rendered in the environment. Any ``lapyx.components`` 
        class is acceptable, except those derived from ``Arg`` or ``KWArgs``, including 
        other Environments. A list of the same is also acceptable. These will be rendered in 
        the order in which they are added.
    """        
    def __init__(self, content: str | Table | Figure | List[ str | Table | Figure] = None):
        super().__init__(name = None, content = content)

    def __str__(self):
        return "\n".join([str(item) for item in self.content])

class Itemize(Environment):
    def __init__(
            self, 
            content: str | Table | Figure | List[ str | Table | Figure]  = None,
            arguments:  Arg | OptArg | str | List[str | Arg | OptArg] = None
        ):
        """``Itemize`` is a convenience class for creating unordered lists in LaTeX.

        Parameters
        ----------
        content : str | Table | Figure | Environment | List[ str | Table | Figure | Environment] , optional, default ``None``
            The content to be added to the ``itemize`` environment. Any ``lapyx.components``
            class is acceptable, except those derived from ``Arg`` or ``KWArgs``, including
            other Environments. A list of the same is also acceptable. Unlike other 
            ``Environments``, a nested list is also acceptable, with each list being rendered as a
            nested ``itemize`` environment. These will be rendered in the order in which they are 
            added.
        arguments :  Arg | OptArg | str | List[str | Arg | OptArg] , optional, default ``None``
            The arguments to be passed to the ``itemize`` environment. 
        """        
        super().__init__(name = "itemize", arguments = arguments)
        
        if content is not None:
            self.add_content(content)
    
    def add_content(self, content: str | Table | Figure | Macro | Environment | List[str | Table | Figure | Macro | Environment]):
        """Append content to the ``itemize`` environment.

        Parameters
        ----------
        content : str | Table | Figure | Macro | Environment | List[str | Table | Figure | Macro | Environment]
            The new content to be added. Any ``lapyx.components`` class is acceptable, except
            those derived from ``Arg`` or ``KWArgs``, including other Environments. A list of the
            same is also acceptable. Unlike other ``Environments``, a nested list is also
            acceptable, with each list being rendered as a nested ``itemize`` environment. 
        """        
        if isinstance(content, list) or isinstance(content, tuple):
            for item in content:
                if isinstance(item, list) or isinstance(item, tuple):
                    self.add_content(self.__class__(content = item))
                else:
                    self.content.append(item)
        else:
            self.content.append(content)
    
    def set_content(self, content: str | Table | Figure | Macro | Environment | List[str | Table | Figure | Macro | Environment], index: int):
        """Set the content at a given index, replacing the existing content.

        Parameters
        ----------
        content : str | Table | Figure | Macro | Environment | List[str | Table | Figure | Macro | Environment]
            The new content to be added. Any ``lapyx.components`` class is acceptable, except
            those derived from ``Arg`` or ``KWArgs``, including other Environments. A list of the
            same is also acceptable. Unlike other ``Environments``, a nested list is also
            acceptable, with each list being rendered as a nested ``itemize`` environment.
        index : int
            The index of the content to be replaced.

        Raises
        ------
        IndexError
            If the index is out of range for the number of content items in the environment.
        """        
        if index >= len(self.content):
            raise IndexError(f"Cannot set content: index {index} is out of range for content list of length {len(self.content)}")
        
        if isinstance(content, list) or isinstance(content, tuple):
            self.content[index] = self.__class__(content = content)
        else:
            self.content[index] = content

    def insert_content(self, content: str | Table | Figure | Macro | Environment | List[str | Table | Figure | Macro | Environment], index: int):
        """Insert content at a given index, shifting the existing content to the right.

        Parameters
        ----------
        content : str | Table | Figure | Macro | Environment | List[str | Table | Figure | Macro | Environment]
            The new content to be added. Any ``lapyx.components`` class is acceptable, except
            those derived from ``Arg`` or ``KWArgs``, including other Environments. A list of the
            same is also acceptable. Unlike other ``Environments``, a nested list is also
            acceptable, with each list being rendered as a nested ``itemize`` environment.
        index : int
            The index at which the content should be inserted.

        Raises
        ------
        IndexError
            If the index is out of range for the number of content items in the environment.
        """        
        if index > len(self.content):
            raise IndexError(f"Cannot insert content: index {index} is out of range for content list of length {len(self.content)}")
        
        if isinstance(content, list) or isinstance(content, tuple):
            self.content.insert(index, self.__class__(content = content))
        else:
            self.content.insert(index, content)

    def __str__(self):
        # start_line = f"\\begin{{{self.name}}}{''.join([str(o) for o in self.arguments])}"
        start_line = str(Macro("begin", [self.name] + self.arguments))
        # end_line = f"\\end{{{self.name}}}"
        end_line = str(Macro("end", [self.name]))
        mid_lines = "\n".join([("\\item " if not isinstance(item, Itemize) else '') + str(item) for item in self.content])
        # indent each of mid_lines by one tab
        mid_lines = "\n".join(["\t" + line for line in mid_lines.split("\n")])
        return start_line + "\n" + mid_lines + "\n" + end_line

class Enumerate(Itemize):
    """Extends the ``Itemize`` class to create an ``enumerate`` environment, which will render an
    ordered list. Any automatically generated ``Environment`` s arising from nested lists will also
    be ``Enumerate`` instances instead of ``Itemize`` instances.
    """

    def __init__(
        self, 
        content: List = None,
        arguments: List = None
    ):
        super().__init__(arguments = arguments, content = content)
        self.name = "enumerate"


class Subfigure(Figure):
    """Extends the ``Figure`` class for correct formatting of subfigures with the ``subcaption``
    package. The ``subcaption`` package must be loaded in the preamble for this class to work
    correctly.
    """   
    def __init__(
        self,
        figure: mplFigure | str | Figure = None,
        *args,
        **kwargs
    ):
        if figure is not None:
            if isinstance(figure, Figure):
                self.from_Figure(figure)
            else:
                super().__init__(figure = figure, *args, **kwargs)
        else:
            super().__init__(*args, **kwargs)
        
        self.floating = True
        self.centered = True
        self.alignment = None
        self.base_dir = None
        self.temp_dir = None

    
    def float(self, *args, **kwargs):
        print("Warning: subfigures must be floating")
        
    def center(self, *args, **kwargs):
        print("Warning: subfigures are always centered")
    
    def __str__(self, **kwargs) -> str:
        if self.base_dir is None or self.temp_dir is None:
            raise ValueError("Cannot convert subfigure to LaTeX: base_dir and temp_dir must be set")
        fig = Environment("subfigure")
        figure_file_name = Path(self.base_dir, self.figure_name)
        if not self.using_file:
            # if we have a figure, save it to {temp_dir}/lapyx_figures/{id}.pdf
            # create {temp_dir}/lapyx_figures if it doesn't exist
            if not Path(self.temp_dir, "lapyx_figures").exists():
                Path(self.temp_dir, "lapyx_figures").mkdir()
            if self.figure is not None:
                figure_file_name = self.temp_dir / "lapyx_figures" / f"{self.figure_name}.{kwargs['extension'] if 'extension' in kwargs else 'pdf'}"
                self.figure.savefig(
                    figure_file_name, 
                    bbox_inches='tight',
                    **kwargs
                )


        includegraphics_opts = KWArgs()
        if self.size["width"] is not None:
            fig.add_argument(self.size["width"])
            includegraphics_opts.add_argument("width", "\\textwidth")
        else:
            # we *must* have a width, so default to 0.45\\textwidth
            fig.add_argument("0.45\\textwidth")
            includegraphics_opts.add_argument("width", "\\textwidth")
        if self.size["height"] is not None:
            includegraphics_opts.add_argument("height", self.size["height"])
        if self.size["scale"] is not None:
            includegraphics_opts.add_argument("scale", self.size["scale"])
        
        includegraphics = Macro("includegraphics")
        if not includegraphics_opts.is_empty():
            includegraphics.add_argument(OptArg(includegraphics_opts))
        includegraphics.add_argument(figure_file_name)

        if self.alignment is not None:
            fig.insert_argument(self.alignment, optional = True, index = 0)
        else:
            fig.insert_argument("b", optional = True, index = 0) # default to aligning by baseline

        fig.add_content(Macro("centering"))
        fig.add_content(includegraphics)
        if self.caption is not None:
            fig.add_content(Macro("caption", arguments = self.caption))
        else:
            fig.add_content(Macro("caption", arguments = ""))
        if self.label is not None:
            fig.add_content(Macro("label", arguments = self.label))
        
        return str(fig)
    
    def set_alignment(self, alignment: str = None):
        """Set the vertical alignment of the subfigures within the outer ``figure`` LaTeX 
        environment. 

        Parameters
        ----------
        alignment : str, optional, default ``None``
            The alignment optional argument to the ``subfigure`` environment. 
        """        
        self.alignment = None

    def from_Figure(self, figure: Figure):
        """Create a ``Subfigure`` instance from a ``Figure`` instance. 

        Parameters
        ----------
        figure : Figure
            The source ``Figure`` to be converted.
        """        
        self.figure = figure.figure
        self.figure_name = figure.figure_name
        self.caption = figure.caption
        self.label = figure.label
        self.size = figure.size
        self.using_file = figure.using_file
        self.id = figure.id

class Subfigures():
    def __init__(
        self, 
        figures: List[Subfigure | Figure] = None, 
        alignment: str = None,
        floating_pos: str = None,
        caption: str = None,
        label: str = None,
        gap: str = None
    ):
        """Create a ``Subfigures`` instance, which will render a ``figure`` environment with
        multiple ``subfigure`` s using the ``subcaption`` package. The ``subcaption`` package must
        be loaded in the preamble for this class to work correctly.

        Parameters
        ----------
        figures : List[Subfigure  |  Figure], optional, default ``None``
            A list of figures to be included. These must be ``lapyx.components.Figure`` or
            ``lapyx.components.Subfigure`` instances, not ``matplotlib.figure.Figure`` instances.
        alignment : str, optional, default ``None``
            Alignment of the subfigures within the outer ``figure`` LaTeX environment.
        floating_pos : str, optional, default ``None``
            The optional positional argument to be passed to the ``figure`` environment if the 
            figure is floating. Setting this does not set ``floating`` to ``True``.
        caption : str, optional, default ``None``
            The caption to be used for the outer ``figure`` environment. Setting this sets
            ``floating`` to ``True``.
        label : str, optional, default ``None``
            The label to be used for the outer ``figure`` environment. Setting this sets
            ``floating`` to ``True``, and forces an empty caption if ``caption`` is ``None``.
        gap : str, optional, default ``None``
            The horizontal gap between each subfigure. This must be a valid LaTeX length.

        Raises
        ------
        TypeError
            If any element of ``figures`` is not a ``lapyx.components.Figure`` or
            ``lapyx.components.Subfigure`` instance.
        """        
        self.figures_list = []

        if figures is not None:
            if not isinstance(figures, list) and not isinstance(figures, tuple):
                figures = [figures]
            for f in figures:
                if isinstance(f, Subfigure):
                    self.figures_list.append(f)
                elif isinstance(f, Figure):
                    self.figures_list.append(Subfigure(figure = f))
                else:
                    raise TypeError(f"Subfigures must be a list of Subfigure objects, not {type(f)}")
        
        
            
        self.caption = caption
        self.label = label
        self.floating_pos = floating_pos
        self.alignment = alignment
        self.gap = gap

    def set_alignment(self, alignment: str = None):
        """Set the vertical alignment of the subfigures within the outer ``figure`` LaTeX
        environment.

        Parameters
        ----------
        alignment : str, optional, default ``None``
            The alignment optional argument to the ``subfigure`` environment.
        """        
        self.alignment = alignment
        for f in self.figures_list:
            f.set_alignment(alignment)
    
    def set_floating_pos(self, floating_pos: str = None):
        """Set the position of the outer ``figure`` LaTeX environment.

        Parameters
        ----------
        floating_pos : str, optional, default ``None``
            The optional position argument passed to the ``figure`` environment.
        """        
        self.floating_pos = floating_pos

    def set_caption(self, caption: str = None):
        """Set the caption of the outer ``figure`` LaTeX environment.

        Parameters
        ----------
        caption : str, optional, default ``None``
            The caption to be used for the outer ``figure`` environment.
        """
        self.caption = caption

    def set_label(self, label: str = None):
        """Set the label of the outer ``figure`` LaTeX environment.

        Parameters
        ----------
        label : str, optional, default ``None``
            The label to be used for the outer ``figure`` environment.
        """        
        self.label = label
    
    def add_figure(self, figure: Subfigure | Figure):
        """Append a new figure to the list of figures.

        Parameters
        ----------
        figure : Subfigure | Figure
            The figure to be added. This must be a ``lapyx.components.Figure`` or
            ``lapyx.components.Subfigure`` instance, not a ``matplotlib.figure.Figure`` instance.
            
        Raises
        ------
        TypeError
            If ``figure`` is not a ``lapyx.components.Figure`` or ``lapyx.components.Subfigure``
            instance.
        """        
        if isinstance(figure, Subfigure):
            self.figures_list.append(figure)
        elif isinstance(figure, Figure):
            self.figures_list.append(Subfigure(figure = figure))
        else:
            raise TypeError(f"Subfigures must be a list of Subfigure objects, not {type(figure)}")
    
    def add_figures(self, figures: List[Subfigure | Figure]):
        """Append multiple figures to the list of figures.

        Parameters
        ----------
        figures : List[Subfigure  |  Figure]
            The new figures to be added. These must be ``lapyx.components.Figure`` or
            ``lapyx.components.Subfigure`` instances, not ``matplotlib.figure.Figure`` instances.

        Raises
        ------
        TypeError
            If any element of ``figures`` is not a ``lapyx.components.Figure`` or
            ``lapyx.components.Subfigure`` instance.
        """        
        if not isinstance(figures, list) and not isinstance(figures, tuple):
            figures = [figures]
        for f in figures:
            if isinstance(f, Subfigure):
                self.figures_list.append(f)
            elif isinstance(f, Figure):
                self.figures_list.append(Subfigure(figure = f))
            else:
                raise TypeError(f"Subfigures must be a list of Subfigure objects, not {type(f)}")
        
    def insert_figure(self, figure: Subfigure | Figure, index: int):
        """Insert a new figure into the list of figures at the specified index, shifting all
        subsequent figures to the right.

        Parameters
        ----------
        figure : Subfigure | Figure
            The new figure to be inserted. This must be a ``lapyx.components.Figure`` or
            ``lapyx.components.Subfigure`` instance, not a ``matplotlib.figure.Figure`` instance.
        index : int
            The index at which to insert the new figure.

        Raises
        ------
        IndexError
            If the index is out of range for the number of figures.
        TypeError
            If ``figure`` is not a ``lapyx.components.Figure`` or ``lapyx.components.Subfigure``
            instance.
        """        
        if index >= len(self.figures_list):
            raise IndexError(f"Could not insert figure. Index {index} out of range for list of length {len(self.figures_list)}")
        if isinstance(figure, Subfigure):
            self.figures_list.insert(index, figure)
        elif isinstance(figure, Figure):
            self.figures_list.insert(index, Subfigure(figure = figure))
        else:
            raise TypeError(f"Subfigures must be a list of Subfigure objects, not {type(figure)}")
            
    def insert_figures(self, figures: List[Subfigure | Figure], index: int):
        """Insert multiple new figures into the list of figures at the specified index, shifting
        all subsequent figures to the right.

        Parameters
        ----------
        figures : List[Subfigure  |  Figure]
            The new figures to be inserted. These must be ``lapyx.components.Figure`` or
            ``lapyx.components.Subfigure`` instances, not ``matplotlib.figure.Figure`` instances.
        index : int
            The index at which to insert the new figures.

        Raises
        ------
        IndexError
            If the index is out of range for the number of figures.
        TypeError
            If any element of ``figures`` is not a ``lapyx.components.Figure`` or
            ``lapyx.components.Subfigure`` instance.
        """        
        if index >= len(self.figures_list):
            raise IndexError(f"Could not insert figure. Index {index} out of range for list of length {len(self.figures_list)}")
        if not isinstance(figures, list) and not isinstance(figures, tuple):
            figures = [figures]
        for f in figures[::-1]:
            if isinstance(f, Subfigure):
                self.figures_list.insert(index, f)
            elif isinstance(f, Figure):
                self.figures_list.insert(index, Subfigure(figure = f))
            else:
                raise TypeError(f"Subfigures must be a list of Subfigure objects, not {type(f)}")
    
    def set_figure(self, figure: Subfigure | Figure, index: int):
        """Replace the figure at the specified index with a new figure.

        Parameters
        ----------
        figure : Subfigure | Figure
            The new figure to be inserted. This must be a ``lapyx.components.Figure`` or
            ``lapyx.components.Subfigure`` instance, not a ``matplotlib.figure.Figure`` instance.
        index : int
            The index of the figure to be replaced.

        Raises
        ------
        IndexError
            If the index is out of range for the number of figures. 
        TypeError
            If ``figure`` is not a ``lapyx.components.Figure`` or ``lapyx.components.Subfigure``
            instance.
        """        
        if index >= len(self.figures_list):
            raise IndexError(f"Could not insert figure. Index {index} out of range for list of length {len(self.figures_list)}")
        if isinstance(figure, Subfigure):
            self.figures_list[index] = figure
        elif isinstance(figure, Figure):
            self.figures_list[index] = Subfigure(figure = figure)
        else:
            raise TypeError(f"Subfigures must be a list of Subfigure objects, not {type(figure)}")

    def remove_figure(self, index: int):
        """Remove the figure at the specified index.

        Parameters
        ----------
        index : int
            The index of the figure to be removed.

        Raises
        ------
        IndexError
            If the index is out of range for the number of figures.
        """        
        if index >= len(self.figures_list):
            raise IndexError(f"Could not insert figure. Index {index} out of range for list of length {len(self.figures_list)}")
        self.figures_list.pop(index)
    
    # No `remove_figures` method to make it more difficult to accidentally remove more than intended.
        
    def __getitem__(self, key):
        if isinstance(key, int):
            return self.figures_list[key]
        elif isinstance(key, slice):
            return self.figures_list[key]
        else:
            raise TypeError("Subfigures must be indexed with an integer or slice")
        
    # def get_figures(self) -> List[Subfigure]:
    #     """Return a list of the figures in the subfigure group

    #     Returns
    #     -------
    #     List[:class:`lapyx.components.Subfigure`]
    #         The figures associated with this subfigure group.
    #     """        
    #     return self.figures_list
        
    def to_latex(self, base_dir: str, temp_dir: str) -> str:
        """Export the ``Subfigures`` object to valid LaTeX markup, paying attention to all 
        formatting options which have been applied. Each ``Subfigure`` object within the 
        ``Subfigures`` instance will be exported according to  
        ``lapyx.components.Figure.to_latex``, saving the matplotlib figures to a temporary
        file. 

        .. warning::
            It is advised that you do not call this method directly, and instead pass the ``Figure`` 
            object to ``export()`` directly. This will ensure that ``base_dir`` and ``temp_dir`` are
            correctly set, and temporary files can be cleaned after compilation.

        Parameters
        ----------
        base_dir : str
            The base directory of the LaTeX document. This will be supplied automatically by the
            ``export()`` function.
        temp_dir : str
            The temporary directory and prefix for the figure file. This will be supplied automatically
            by the ``export()`` function.

        Returns
        -------
        str
            The complete LaTeX markup for the figure and subfigures.

        Raises
        ------
        ValueError
            If the ``Subfigures`` object has no figures.
        TypeError
            If the gap cannot be converted to a valid LaTeX length.
        """        
        
        
        if len(self.figures_list) == 0:
            raise ValueError("Subfigures must contain at least one figure before being exported")
        
        fig = Environment("figure")
        if self.floating_pos is not None:
            fig.add_argument(self.floating_pos, optional = True)
        else:
            fig.add_argument("ht!", optional = True)
        
        fig.add_content(Macro("centering"))

        gaptext = ""
        if self.gap is not None:
            if isinstance(self.gap, int):
                if self.gap == 0:
                    gaptext = r"\hspace{0pt}"
                else:
                    # assume cm
                    gaptext = rf"\hspace{{{self.gap}cm}}"
            elif isinstance(self.gap, str):
                if not self.gap.startswith(r"\hspace{"):
                    gaptext = r"\hspace{" + self.gap + "}"
                else:
                    gaptext = self.gap
            elif isinstance(self.gap, Macro):
                gaptext = str(self.gap)
            else:
                raise TypeError(f"Gap must be an int, str, or Macro, not {type(self.gap)}")
        else:
            gaptext = "\\hfill"
        
        for f in self.figures_list:
            f.base_dir = base_dir
            f.temp_dir = temp_dir

        fig.add_content(self.figures_list[0])
            
        if len(self.figures_list) > 1:
            for figure in self.figures_list[1:]:
                fig.add_content(gaptext)
                fig.add_content(figure)
        
        if self.caption is not None:
            fig.add_content(Macro("caption", self.caption))
        elif self.label is not None:
            fig.add_content(Macro("caption", ""))

        if self.label is not None:
            fig.add_content(Macro("label", self.label))
        
        return str(fig)
        
        