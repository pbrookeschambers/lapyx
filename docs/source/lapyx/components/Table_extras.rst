..
    extra content for lapyx.components.Table

Creating tables in LaTeX is notoriously annoying. To help alleviate this, LaPyX provides a :codelink:`Table` class which can hold and manipulate data before generating a (optionally floating) tabular environment, with a variety of formatting options. Data can be read form a CSV file, a ``pandas.DataFrame``, ``numpy.ndarray``, or a nested list, or added manually. The following example creates a table of random numbers, then adds a new column with any shared prime factors:

.. dropdown:: Table Example
    :class-container: example-dropdown
    :icon: code-square
    :animate: fade-in-slide-down
    
    .. code-block:: python

        \begin{python}
            import numpy as np
            from sympy.ntheory import primefactors

            # Create a list of random numbers:
            rnd = np.random.randint(100, size=(10, 2))

            # Create a table from rnd:
            table = Table(rnd, headers = ["$R_1$", "$R_2$"])

            # generate the list of prime factors (as strings)
            factors = []
            for r1, r2 in rnd:
                f1, f2 = primefactors(r1), primefactors(r2)
                # check for any shared factors
                shared = [str(f) for f in f1 if f in f2]
                if shared:
                    factors.append(", ".join(shared))
                else:
                    factors.append(r"\textit{none}")

            # Add the new column
            table.add_column(factors, column_name = "Shared Prime Factors")

            # Add a caption
            table.set_caption("Random numbers and their shared prime factors")

            # Export the table
            export(table)
        \end{python}

    .. container:: latex center latex-table

        .. table::

            +--------------+--------------+-----------------------+
            | :math:`R_1`  | :math:`R_2`  | Shared Prime Factors  |
            +==============+==============+=======================+
            | 65           | 93           | *none*                |
            +--------------+--------------+-----------------------+
            | 0            | 46           | *none*                |
            +--------------+--------------+-----------------------+
            | 80           | 16           | 2                     |
            +--------------+--------------+-----------------------+
            | 21           | 7            | 7                     |
            +--------------+--------------+-----------------------+
            | 56           | 36           | 2                     |
            +--------------+--------------+-----------------------+
            | 71           | 18           | *none*                |
            +--------------+--------------+-----------------------+
            | 67           | 89           | *none*                |
            +--------------+--------------+-----------------------+
            | 49           | 68           | *none*                |
            +--------------+--------------+-----------------------+
            | 42           | 18           | 2, 3                  |
            +--------------+--------------+-----------------------+
            | 74           | 48           | 2                     |
            +--------------+--------------+-----------------------+

        Random numbers and their shared prime factors