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
* :codelink:`numpy <https://numpy.org/>` for reading CSV files when ``pandas`` is not available or wanted, and for including ``ndarray`` objects in :codelink:`Table` 
* :codelink:`matplotlib <https://matplotlib.org/>` for including ``matplotlib`` figures in :codelink:`Figure` objects. Otherwise, ``Figure`` objects will be restricted to local files only.
* A working ``pdflatex`` installation available on the system path. If this is not present, you must use the ``-C`` or ``--no-compile`` command line option.

LaPyX can be installed using pip:

.. code-block:: bash

    pip install lapyx

You may wish to add an alias to your ``.bashrc`` or ``.zshrc`` file to make it easier to run LaPyX:

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
            sum = 0
            for i in range(8):
                sum += np.random.randint(6) + 1
            export(f"I cast fireball for {sum} damage!")
        \end{python}

    results in

    .. container:: latex

        I cast fireball for 32 damage!

As you can see, code blocks can be indented uniformly (in addition to control flow indentation) and this will be removed during processing. This is based on the indentation of the first line of the block, so do not indent the first line more than the rest of the block.

Helper classes
~~~~~~~~~~~~~~

LaPyX provides a number of helper classes to make handling various LaTeX features easier and more programmatic. These are all imported by default, so you don't need to import them explicitly. Below are some simple examples of each. See the :codelink:`components` documentation for full detail.

``Table``
^^^^^^^^^

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

    .. container:: latex center

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

        **Table 1**: Random numbers and their shared prime factors

``Figure``
^^^^^^^^^^

The :codelink:`Figure` class helps to include `matplotlib` figures which are generated within the document, as well as pre-existing image files. The following example generates a random walk and plots it using ``matplotlib`` (with some appropriate styling applied):

.. dropdown:: Figure Example
    :class-container: example-dropdown
    :icon: code-square
    :animate: fade-in-slide-down
    

    .. code-block:: python

        \begin{python}
            import numpy as np
            import matplotlib.pyplot as plt

            # Generate a random walk
            steps = np.random.randint(0, 4, size=100)
            x = np.cumsum(np.where(steps == 0, -1, np.where(steps == 1, 1, 0)))
            y = np.cumsum(np.where(steps == 2, -1, np.where(steps == 3, 1, 0)))

            # Plot the walk
            fig, ax = plt.subplots()
            ax.plot(x, y)
            ax.set_aspect("equal")
            ax.set_title("Random Walk")

            # Create a figure object
            figure = Figure(fig, caption = "A random walk in 2D")

            # Export the figure
            export(figure)
        \end{python}


    .. container:: light-dark-mode

        .. container:: latex center latex-figure

            .. image:: assets/figures/light/random_walk.svg

            A random walk in 2D

        .. container:: latex center latex-figure

            .. image:: assets/figures/dark/random_walk.svg

            A random walk in 2D

``Subfigures``
^^^^^^^^^^^^^^

In addition to the ``Figure`` class, LaPyX provides the :codelink:`Subfigures` class for easier grouping and organising of multiple figures. A ``Subfigures`` instance keeps a list of figures (which should be ``Subfigure`` instances, though ``Figure`` instances will usually be converted automatically - see the :codelink:`Subfigure` documentation for more detail). This allows easy modifications to groups of figures, as well as access to the individual captions and group caption. The below example uses a ``Subfigures`` instance to create a :math:`2\times2` grid of random walks:

.. dropdown:: Subfigures Example
    :class-container: example-dropdown
    :icon: code-square
    :animate: fade-in-slide-down
        
    .. code-block:: python

        \begin{python}
            import numpy as np
            import matplotlib.pyplot as plt
            
            def random_walk(steps: int, bias: int, strength: float):
                # Generate a random walk of `steps` steps with a `strength`% 
                # chance of moving in the `bias` direction
                step_dirs = np.random.randint(0, 4, size = steps)
                bias_mask = np.random.random(size = steps) < strength
                step_dirs[bias_mask] = bias
                # Convert the step directions into x and y coordinates. left: 0, up: 1, right: 2, down: 3
                x = np.cumsum(np.where(step_dirs == 0, -1, np.where(step_dirs == 2, 1, 0)))
                y = np.cumsum(np.where(step_dirs == 3, -1, np.where(step_dirs == 1, 1, 0)))
                return x, y
            
            # Create the parent Subfigures object
            parent = Subfigures(caption = "Random walks with differing biases", label = "fig:random_walks")

            figs = []
            xlims = [0,0]
            ylims = [0,0]
            dirs = ["left", "up", "right", "down"]
            for bias in range(4):
                mpl_fig = plt.figure()
                fig = Figure(mpl_fig)
                for i in range(4):
                    x, y = random_walk(500, bias, 0.1)
                    xlims = [min(xlims[0], x.min()), max(xlims[1], x.max())]
                    ylims = [min(ylims[0], y.min()), max(ylims[1], y.max())]
                    fig.plot(x, y, label = f"Walk {i + 1}")
                fig.set_caption(dirs[bias])
                fig.legend()
                figs.append(fig)
            
            # Add the subfigures to the parent
            parent.add_figures(figs)

            # set appropriate axis limits
            xlims = [xlims[0] - 10, xlims[1] + 10]
            ylims = [ylims[0] - 10, ylims[1] + 10]
            for fig in parent:
                fig.xlim(xlims)
                fig.ylim(ylims)

            parent.set_caption("Random walks with differing biases")

            export(parent)
        \end{python}

    .. container:: light-dark-mode

        .. container:: latex subfigures
            
            .. container:: latex-subfigure

                .. image:: assets/figures/light/random_walk_left.svg
                
                left
        
            .. container:: latex-subfigure

                .. image:: assets/figures/light/random_walk_up.svg
                
                up

            .. container:: latex-subfigure

                .. image:: assets/figures/light/random_walk_right.svg
                
                right
        
            .. container:: latex-subfigure

                .. image:: assets/figures/light/random_walk_down.svg
                
                down

            Random walks with differing biases


        .. container:: latex subfigures

            .. container:: latex-subfigure

                .. image:: assets/figures/dark/random_walk_left.svg
                
                left
        
            .. container:: latex-subfigure

                .. image:: assets/figures/dark/random_walk_up.svg
                
                up

            .. container:: latex-subfigure

                .. image:: assets/figures/dark/random_walk_right.svg
                
                right
        
            .. container:: latex-subfigure

                .. image:: assets/figures/dark/random_walk_down.svg
                
                down

            Random walks with differing biases

``Itemize`` and ``Enumerate``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Two other simple helper classes are included, :codelink:`Itemize` and :codelink:`Enumerate`. These serve to generate and modify unordererd and ordered lists respectively, including nested lists. See their documentation (:codelink:`Itemize`, :codelink:`Enumerate`) for more detailed examples, but the below example shows a simple ordered list, and a nested unordered list.

.. note::

    These will soon be able to take a dictionary as input for nested lists, but for now must take a ``list`` instance.

.. dropdown:: Itemize Example
    :class-container: example-dropdown
    :icon: code-square
    :animate: fade-in-slide-down
    
    .. code-block:: python

        The following is a list of colours:
        \begin{python}
            # create the list of colors:
            colors = ["Red", "Green", "Blue", "Yellow", "Orange", "Purple", "Black", "White"]
            export(Itemize(colors))
        \end{python}

    .. container:: latex

        The following is a list of colours:

        * Red
        * Green
        * Blue
        * Yellow
        * Orange
        * Purple
        * Black
        * White

.. dropdown:: Enumerate Example
    :class-container: example-dropdown
    :icon: code-square
    :animate: fade-in-slide-down

    .. code-block:: python

        The following is a list of colours by shade:
        \begin{python}
            # create the list of colors:
            colors = [
                "Red", 
                    ["Cherry", "Crimson", "Scarlet"],
                "Orange",
                    ["Coral", "Tangerine", "Gold"],
                "Yellow",
                    ["Lemon", "Mustard"],
                "Green",
                    ["Emerald", "Forest", "Mint"],
                "Blue",
                    ["Navy"],
                "Purple",
                    ["Lavender"],
                "Black",
                "White"
            ]
            export(Enumerate(colors))
        \end{python}

    .. container:: latex

        The following is a list of colours by shade:

        #. Red

           #. Cherry

           #. Crimson

           #. Scarlet

        #. Orange

           #. Coral

           #. Tangerine

           #. Gold

        #. Yellow

           #. Lemon

           #. Mustard

        #. Green

           #. Emerald

           #. Forest

           #. Mint

        #. Blue

           #. Navy

        #. Purple

           #. Lavender

        #. Black

        #. White