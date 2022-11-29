..
    extra content for lapyx


.. role:: codelink
    :class: codelink



.. note::

    This is a work in progress. The documentation especially is incomplete and may contain inconsistencies. 


LaPyX is a preprocessor for LaTeX which allows for the embedding of Python code in LaTeX documents with their output included in the final document as though it were native LaTeX markup. It also contains several useful classes for generating LaTeX objects like tables, figures and subfigures, and nested lists.

For example, including the following in a LaTeX document (with a suitable sample CSV file)

.. code-block:: python

    \begin{python}
        Table("data.csv", caption = "Some sample data", label = "tab:sample", centered = True)
    \end{python}

will result in the following table being included in the compiled document, where the column headings were automatically taken from the first row of the CSV file.

.. container:: latex center

    .. table::
        :widths: 40 20 20 20

        +---------------------------------+----------------------+----------------------+----------------------+
        | :math:`\theta` (:math:`^\circ`) | :math:`\sin(\theta)` | :math:`\cos(\theta)` | :math:`\tan(\theta)` |
        +=================================+======================+======================+======================+
        | 0                               | 0                    | 1                    | 0                    |
        +---------------------------------+----------------------+----------------------+----------------------+
        | 45                              | 0.7071               | 0.7071               | 1                    |
        +---------------------------------+----------------------+----------------------+----------------------+
        | 90                              | 1                    | 0                    | Undefined            |
        +---------------------------------+----------------------+----------------------+----------------------+
        | 135                             | 0.7071               | -0.7071              | -1                   |
        +---------------------------------+----------------------+----------------------+----------------------+
        | 180                             | 0                    | -1                   | 0                    |
        +---------------------------------+----------------------+----------------------+----------------------+

Installation
------------

Requirements
~~~~~~~~~~~~

LaPyX requires Python 3.10 or later. The following are necessary for some functionality:
  
* :codelink:`pandas <https://pandas.pydata.org>` for reading CSV files, and for including ``DataFrame`` objects in :codelink:`Table <lapyx.components.Table>` objects
* :codelink:`numpy <https://numpy.org/>` for reading CSv files when ``pandas`` is not available or wanted, and for including ``ndarray`` objects in :codelink:`Table` 
* :codelink:`matplotlib <https://matplotlib.org/>` for including ``matplotlib`` figures in :codelink:`Figure` objects. Otherwise, ``Figure`` objects will be restricted to local files only.
* A working ``pdflatex`` installation available on the system path. If this is not present, you must use the ``-C`` or ``--no-compile`` command line option.

LaPyX can be installed using pip:

.. code-block:: bash

    pip install lapyx