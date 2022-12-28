..
    extra content for lapyx.components.Subfigures

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

                .. image:: /assets/figures/light/random_walk_left.svg
                
                left
        
            .. container:: latex-subfigure

                .. image:: /assets/figures/light/random_walk_up.svg
                
                up

            .. container:: latex-subfigure

                .. image:: /assets/figures/light/random_walk_right.svg
                
                right
        
            .. container:: latex-subfigure

                .. image:: /assets/figures/light/random_walk_down.svg
                
                down

            Random walks with differing biases


        .. container:: latex subfigures

            .. container:: latex-subfigure

                .. image:: /assets/figures/dark/random_walk_left.svg
                
                left
        
            .. container:: latex-subfigure

                .. image:: /assets/figures/dark/random_walk_up.svg
                
                up

            .. container:: latex-subfigure

                .. image:: /assets/figures/dark/random_walk_right.svg
                
                right
        
            .. container:: latex-subfigure

                .. image:: /assets/figures/dark/random_walk_down.svg
                
                down

            Random walks with differing biases