import matplotlib as mpl
# mpl.use('agg')
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import ImageGrid

text_sizes = {'axis':4, 'label':6, 'title':8, 'annotation':5}
dpi = 400

def make_fig(size = (6.0, 6.0)):
    fig, ax = plt.subplots(1, 1, figsize=size, dpi=dpi)
    fig.subplots_adjust(left=0.05, right=0.95)
    ax.tick_params(axis='x', labelsize=text_sizes['axis'])
    ax.tick_params(axis='y', labelsize=text_sizes['axis'])
    return fig, ax

def make_fig_grid(x, y, size, **kwargs):
    defaults = {'cbar_mode': 'each', 'cbar_size': '4%', 'cbar_pad':'1%'}
    for k,v in defaults.items():
        if k not in kwargs.keys():
            kwargs[k] = v

    fig = plt.figure(figsize=(float(x) * size[0], float(y) * size[1]), dpi=dpi)
    fig.subplots_adjust(left=0.05, right=0.95)
    grid = ImageGrid(fig, 111, nrows_ncols=(y, x), **kwargs)
    
    for i in range(x * y):
        grid[i].tick_params(axis='x', labelsize=text_sizes['axis'])
        grid[i].tick_params(axis='y', labelsize=text_sizes['axis'])
    return fig, grid

def save_fig(fig, name):
    fig.savefig(name, dpi=dpi, bbox_inches='tight', pad_inches=0.02)
    plt.close()

def mesh(ax, x, y, z, scale, norm=None, cbar_ax=None, cmap='jet', xlabel=None, ylabel=None, title=None, cbar_label=None):
    qmap = ax.pcolormesh(x, y, z, norm=norm, vmin=scale[0], vmax=scale[1], cmap=cmap, axes=ax)
    
    ax.axis([np.min(x), np.max(x), np.min(y), np.max(y)])
    ax.tick_params(axis='x', labelsize=text_sizes['axis'])
    ax.tick_params(axis='y', labelsize=text_sizes['axis'])
    
    if xlabel is not None:
        ax.xaxis.set_label_coords(0.5, -0.08)
        ax.set_xlabel(xlabel, fontsize=text_sizes['label'])

    if ylabel is not None:
        ax.yaxis.set_label_coords(-0.08, 0.5)
        ax.set_ylabel(ylabel, fontsize=text_sizes['label'])

    title_pos = 1.0
    if cbar_ax is not None:
        cbar = cbar_ax.colorbar(qmap)
        cbar_ax.tick_params(labelsize=text_sizes['axis'])
        if cbar_label is not None:
            cbar.ax.set_ylabel(cbar_label, fontsize=text_sizes['label'], labelpad=-0.5)
    
    if title is not None:
        ax.set_title(title, fontsize=text_sizes['title'], y=title_pos)

    return qmap

