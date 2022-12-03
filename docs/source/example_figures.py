import numpy as np
import qoplots
import matplotlib.pyplot as plt
import os
import matplotlib

figures_dir = "./assets/figures"

def light_dark(func):
    global figures_dir

    def get_figures(func, variant):
        figs, base_names = func()
        for fig, base_name in zip(figs, base_names):
            figure_file = os.path.join(figures_dir, variant, f"{base_name}.svg")
            print(f"Generating figure {figure_file}")
            fig.savefig(figure_file)

    qoplots.init(scheme = "catppuccinlatte", dark = False)
    matplotlib.rcParams['savefig.facecolor'] = '#00000000'
    get_figures(func, "light")

    qoplots.init(scheme = "catppuccin", dark = True)
    matplotlib.rcParams['savefig.facecolor'] = '#00000000'
    get_figures(func, "dark")


def main_figure_example():

    # Generate a random walk
    steps = np.random.randint(0, 4, size=200)
    x = np.cumsum(np.where(steps == 0, -1, np.where(steps == 1, 1, 0)))
    y = np.cumsum(np.where(steps == 2, -1, np.where(steps == 3, 1, 0)))

    # plot the random walk
    fig, ax = plt.subplots()
    ax.plot(x, y)
    ax.set_title("Random Walk")
    return [fig], ["random_walk"]


def main_subfigures_example():
    def random_walk(steps: int, bias: int, strength: float):
        # Generate a random walk of `steps` steps with a `strength`% chance of moving in the `bias` direction
        step_dirs = np.random.randint(0, 4, size = steps)
        bias_mask = np.random.random(size = steps) < strength
        step_dirs[bias_mask] = bias
        # Convert the step directions into x and y coordinates. left: 0, up: 1, right: 2, down: 3
        x = np.cumsum(np.where(step_dirs == 0, -1, np.where(step_dirs == 2, 1, 0)))
        y = np.cumsum(np.where(step_dirs == 3, -1, np.where(step_dirs == 1, 1, 0)))
        return x, y

    dirs = ["left", "up", "right", "down"]

    figs = []
    xlims = [0,0]
    ylims = [0,0]
    for i, dir in enumerate(dirs):
        fig = plt.figure()
        figs.append(fig)
        for j in range(4):
            x, y = random_walk(500, i, 0.1)
            xlims = [min(xlims[0], x.min()), max(xlims[1], x.max())]
            ylims = [min(ylims[0], y.min()), max(ylims[1], y.max())]
            fig.gca().plot(x, y, label = f"Walk {j + 1}", linewidth = 0.75)
        fig.gca().legend()

    xlims = [xlims[0] - 10, xlims[1] + 10]
    ylims = [ylims[0] - 10, ylims[1] + 10]
    for fig in figs:
        fig.gca().set_ylim(ylims)
        fig.gca().set_xlim(xlims)

    return figs, [f"random_walk_{dir}" for dir in dirs]

if __name__ == "__main__":
    light_dark(main_figure_example)
    light_dark(main_subfigures_example)