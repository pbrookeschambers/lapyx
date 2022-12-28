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

.. container:: latex center latex-table

    .. table::

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

    Some sample data

Installation
------------

Requirements
~~~~~~~~~~~~

LaPyX requires Python 3.10 or later. The following are necessary for some functionality:
  
* :codelink:`pandas <https://pandas.pydata.org>` for reading CSV files, and for including ``DataFrame`` objects in :codelink:`Table <lapyx.components.Table>` objects
* :codelink:`numpy <https://numpy.org/>` for reading CSV files when ``pandas`` is not available or wanted, and for including ``ndarray`` objects in :codelink:`Table` 
* :codelink:`matplotlib <https://matplotlib.org/>` for including ``matplotlib`` figures in :codelink:`Figure` objects. Otherwise, ``Figure`` objects will be restricted to local files only.
* A working ``pdflatex`` installation available on the system path. If this is not present, you must use the ``-C`` or ``--no-compile`` command line option.

LaPyX can be installed using pip:

.. note::

    Coming soon!

.. code-block:: bash

    pip install lapyx

On linux, you may wish to add an alias to your ``.bashrc`` or ``.zshrc`` file to make it easier to run LaPyX:

.. code-block:: bash

    alias lapyx="python3 -m lapyx"

In the following sections, it will be assumed that you have done this.

Usage
-----

For basic usage, simply run

.. code-block:: bash

    lapyx document.tex

This will process and compile the document, producing a final file ``document.pdf`` in the current directory. Any temporary files created will be removed once compilation is complete, including auxiliary files created by ``pdflatex``.

Command Line Arguments
~~~~~~~~~~~~~~~~~~~~~~

LaPyX can take a number of command line arguments:

.. container:: cli-arg

    ``-C``, ``--no-compile``

    Do not compile the document. All pre-processing will be done, and all temporary files will be removed, but the final document will not be compiled via ``pdflatex``. 

.. container:: cli-arg

    ``-o <path>``, ``--output <path>``

    Specify the output file path. If not specified, the output file will be the same as the input file, with the extension changed to ``.pdf``. A ``.pdf`` extension will be added if it's not already present.

.. container:: cli-arg

    ``-t <multipart/path>``, ``--temp <multipart/path>``

    Specifies the location for all temporary files. This may be  a directory, a file prefix, or both. Directories **must** include the trailing separator (``/`` on Unix, ``\\`` on Windows). For example,
    
    .. code-block:: bash

        lapyx -t ./temp/ document.tex
    
    will place all temporary files in a new directory ``temp`` (creating it recursively if necessary). Exactly the same without the trailing slash:

    .. code-block:: bash

        lapyx -t ./temp document.tex

    will instead place all temporary files in the current directory, with a prefix of ``temp``. These can of course be combined, for example:

    .. code-block:: bash

        lapyx -t ./temp/lapyx document.tex

    will place all temporary files in the ``temp`` directory, with a prefix of ``lapyx``.

.. container:: cli-arg

    ``-d``, ``--debug``

    Do not remove any temporary files, even on successful compilation. This is useful for debugging purposes, but also in combination with ``--no-compile`` if your LaTeX compiler is not available in the same environment as LaPyX, or you wish to use another LaTeX compiler.

.. container:: cli-arg

    ``-k``, ``--keep-figures``

    By default, any figures generated by LaPyX will be removed after compilation (*not* pre-existing figures included in the document, only those created by LaPyX using the :codelink:``Figure`` class). This option will prevent this from happening.

    .. note::

        This option is likely subject to change, as there are plans to implement some caching between runs to speed up compilation. This will likely involve a change to the default behaviour regarding temporary figure files.

.. container:: cli-arg

    ``-c <options>``, ``--compiler-options <options>``

    Any additional options to pass to ``pdflatex`` during compilation can be specified here. These must be specified as a single string, and will be passed to ``pdflatex`` as-is. The option ``-interaction=nonstopmode`` will always be added, so be careful not to override this.

.. container:: cli-arg

    ``-l``, ``--latex-comments``

    If specified, any lines within Python blocks which start with ``%`` will be treated as comments. This is convenient so that comments can be consistent within the LaTeX file, but can cause issues if you are using line continuations, modulo functions, string formatting, etc. and so should be used with caution.

.. container:: cli-arg

    ``-v``, ``--verbose``

    Print additional information to the console during compilation, most notably all output from ``pdflatex`` will be printed to the console.

.. container:: cli-arg

    ``-q``, ``--quiet``

    Print nothing to the console except in the event of an error.

.. container:: cli-arg

    ``-h``, ``--help``

    Print a help message and exit.

Within LaTeX Documents
~~~~~~~~~~~~~~~~~~~~~~

Since LaPyX is a separate pre-processor, the LaTeX document doesn't require any special packages or modifications, and the compiler will be completely unaware that the document contained Python code. All that is needed is to include some Python code. There are two ways to do this.

For short, inline code snippets, you can use the ``\py`` macro:


.. dropdown:: ``\py{}`` Example
    :class-container: example-dropdown
    :icon: code-square
    :animate: fade-in-slide-down
    :open:

    .. code-block:: latex

        I rolled 1d6 and got \py{numpy.random.randint(6) + 1}.

    .. container:: latex

        I rolled 1d6 and got 4.

The above example won't actually work usually, since the ``numpy`` module is not imported by default. Although ``\py{}`` is intended for one-liners and short snippets, it can contain multiple statements delimited by ``;``:


.. dropdown:: Multi-Statement ``\py{}`` Example
    :open:
    :class-container: example-dropdown
    :icon: code-square
    :animate: fade-in-slide-down

    .. code-block:: latex

        I rolled 1d6 and got \py{import numpy as np;np.random.randint(6) + 1}.

    .. container:: latex

        I rolled 1d6 and got 2.

.. .. sidebar::

..     LaPyX has memory! all Python code is run as though it were in a single script, so variables and modules persist between blocks. We don't need to import ``numpy`` again, since it was imported in the previous block.

In the above examples, LaPyX is assuming that you want to output the result of the last statement. To be more explicit, we should pass the result to the :codelink:`export()` function:


.. dropdown:: ``export()`` Example
    :open:
    :class-container: example-dropdown
    :icon: code-square
    :animate: fade-in-slide-down

    .. code-block:: latex

        I rolled 1d6 and got \py{export(np.random.randint(6) + 1)}.

    .. container:: latex

        I rolled 1d6 and got 5.

This is also how to handle multiple outputs; simply pass everything you wish to output to :codelink:`export()`. If you don't want to automatically output the result of the last statement, you can either end the final statement with a trailing semicolon (inline ``\py{}`` only), or use the :codelink:`no_export()` function, which suppresses all subsequent output (including those triggered by ``export()``) until the end of the block.

For longer blocks of code, a ``python`` environment is provided. For example,

.. dropdown:: ``python`` Environment Example
    :open:
    :class-container: example-dropdown
    :icon: code-square
    :animate: fade-in-slide-down

    .. code-block:: python

        \begin{python}
            import numpy as np
            total = 0
            for i in range(8):
                total += np.random.randint(6) + 1
            export(f"I cast fireball for {total} damage!")
        \end{python}

    results in

    .. container:: latex

        I cast fireball for 32 damage!

As you can see, code blocks can be indented uniformly (in addition to control flow indentation) and this will be removed during processing. This is based on the indentation of the first line of the block, so do not indent the first line more than the rest of the block.

Helper classes
~~~~~~~~~~~~~~

LaPyX provides a number of helper classes to make handling various LaTeX features easier and more programmatic. These are all imported by default, so you don't need to import them explicitly. Below are some simple examples of each. See the :codelink:`components` documentation for full detail.

.. include:: lapyx/helper_classes.rst


Coming Soon
-----------

The following features are planned for future releases:

* Some caching of output to minimize the overhead added by LaPyX on repeated runs.
* Following of ``\input`` and ``\include`` commands to allow for the use of external files.
* Detection of verbatim input and listings to avoid parsing unwanted content.
* Similar ``markdown`` environment for parsing Markdown content (*potentially; this may be outside the scope of this project*).