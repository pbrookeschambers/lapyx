``Table``
^^^^^^^^^

.. include:: /lapyx/components/Table_extras.rst

``Figure``
^^^^^^^^^^

.. include:: /lapyx/components/Figure_extras.rst


``Subfigures``
^^^^^^^^^^^^^^

.. include:: /lapyx/components/Subfigures_extras.rst

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

Additional Classes
^^^^^^^^^^^^^^^^^^

In addition to the above, LaPyX provides a few more general helper classes:

:codelink:`Macro`
#################

A simple class for making the programmatic generation of macros easier, especially the handling of their arguments.

:codelink:`Environment`
#######################

A class for containing, managing, and exporting LaTeX environments in a nestable, DOM-like way.

:codelink:`EmptyEnvironment`
############################

An extension of :codelink:`Environment` for managing content without adding any LaTeX markup to the content.

:codelink:`KWArgs`
##################

A class for managing LaTeX key-value pairs to be passed to macros and environments.

:codelink:`Arg`
###############

A class for consistent handling of arguments to be passed to macros and environments. This class will mostly be used internally, but is publicly available.

:codelink:`OptArg`
##################

An extension of :codelink:`Arg` for optional arguments. This class will mostly be used internally, but is publicly available.
