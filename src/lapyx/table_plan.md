# Table

Ideas:
- Separate class for storing the data
    - Keeps functions for data manipulation separate to functions for formatting
    - *Could* use a pandas dataframe:
        - Pros:
            - Already well established
        - Cons:
            - annoying to deal with arbitrary types
            - reliance on column names could be annoying
            - no native ability to insert rather than append
    - List of lists
        - Pros:
            - easy to insert
            - easy to access
            - No need to worry about types
        - Cons:
            - No easy way to access columns without looping through rows
            - No type verification
            - Have to manually enforce rows being the same length

Using pandas DataFrame. We'll just have to deal with the annoyance of insertion etc. 

## Data Manipulation

Want to be able to:
- [x] Read from file and/or string
    - csv, tsv, json (column names), excel/xlsx, html, markdown, latex
    - Separate parsers for each format.
- [x] Read from numpy array or pandas dataframe
- [x] Add row(s)
    - Append *and* insert
- [x] Add column(s)
    - Append *and* insert
- [x] Remove row(s)
- [x] Remove column(s)
- [x] modify cell(s) by index
- [x] transpose


# Table Object

Contains a TableData object, and passes any data-related function calls to it.

Also handles all formatting.

Want to be able to:
- set the table as a float
- add a:
    - caption
    - label
- specify some footer row
- specify some header row (via the TableData object)
- Formatting for header row
- Formatting for footer row
- formatting per column:
    - python format specifier
    - callable - takes a single argument and returns a string
    - None - no formatting, just uses the `str()` function
- set as a longtable
- set as a tabularx
- split into multiple tables
    - by number of tables
    - by max number of rows
- Set column widths and alignments


