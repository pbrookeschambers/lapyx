..
    extra content for lapyx.components.Table.add_row

Examples
--------
.. dropdown:: ``Table.add_row()`` Example
    :open:
    :class-container: example-dropdown
    :icon: code-square
    :animate: fade-in-slide-down

    .. code-block:: python

        \begin{python}
            # some sample data
            headers = ['Name', 'Age (Yr)', 'Height (m)']
            data = [
                ['John', 20, 1.8],
                ['Mary', 21, 1.7],
                ['Peter', 22, 1.9],
            ]
            
            t = Table(data, headers = headers, caption = 'Sample table')
            t.add_row(['Sam', 23, 1.6])

            export(t)
        \end{python}

    .. container:: latex center latex-table

        .. table::

            +---------+------------+--------------+
            | Name    | Age (Yr)   | Height (m)   |
            +=========+============+==============+
            | John    | 20         | 1.8          |
            +---------+------------+--------------+
            | Mary    | 21         | 1.7          |
            +---------+------------+--------------+
            | Peter   | 22         | 1.9          |
            +---------+------------+--------------+
            | Sam     | 23         | 1.6          |
            +---------+------------+--------------+

        Sample Table


