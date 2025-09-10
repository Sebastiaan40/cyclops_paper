import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, BoundaryNorm

# plt.rcParams['text.usetex'] = True

def dcmap(cmap_name, n=9):
    """Discrete colormap with n bins"""
    cmap = plt.colormaps[cmap_name]
    cmaplist = [cmap(i) for i in np.linspace(0, 1, n)]
    return LinearSegmentedColormap.from_list("Custom cmap", cmaplist, n)

if __name__ == "__main__":
    n = 1
    vmin, vmax = -n, n

    data = np.linspace(vmin, vmax, 4).reshape((2, 2))

    cmap = dcmap('bwr', n=n*2+1)

    # bin edges & centers
    bounds = np.linspace(vmin-0.5, vmax+0.5, n*2+2)
    norm = BoundaryNorm(bounds, cmap.N)
    tick_centers = (bounds[:-1] + bounds[1:]) / 2

    # plot
    plt.imshow(data, cmap=cmap, norm=norm)

    # colorbar with Arial labels
    cbar = plt.colorbar(label="phase index", ticks=tick_centers)
    cbar.ax.minorticks_off()
    cbar.set_ticks(tick_centers)
    cbar.set_ticklabels([f"{tc:.0f}" for tc in tick_centers])

    plt.show()

    plt.imshow(np.linspace(-np.pi, np.pi, 4).reshape((2, 2)), cmap="viridis")
    cbar = plt.colorbar(label="phase")
    tick_centers = [-np.pi, -np.pi/2, 0, np.pi/2, np.pi]  # for example
    cbar.set_ticks(tick_centers)
    cbar.set_ticklabels([r"$-\pi$", r"$-\frac{\pi}{2}$", r"$0$", r"$\frac{\pi}{2}$", r"$\pi$"])  # LaTeX-style
    plt.show()