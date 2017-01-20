import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import plotting
import helpers
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import tipsy
import gadget
import numpy as np

limits = (20.0, 20.0) # kpc

changa_snaps = ['ChaNGa/gas/gas.tipsy', 'ChaNGa/gas/gas.out.000050.tipsy', 'ChaNGa/gas/gas.out.000150.tipsy', 'ChaNGa/gas/gas.out.000250.tipsy']
gadget_snaps = ['Gadget3/gas/gas.hdf5', 'Gadget3/gas/gas_000.hdf5', 'Gadget3/gas/gas_002.hdf5', 'Gadget3/gas/gas_004.hdf5']

for f in changa_snaps:
    helpers.process_changa_snapshot(f, f+'.pickle', limits)

for f in gadget_snaps:
    helpers.process_gadget_snapshot(f, f+'.pickle', limits)
snapshots = [x for p in zip(changa_snaps, gadget_snaps) for x in p]

def titles(i):
    if i == 0:
        return 'ChaNGa'
    if i == 1:
        return 'Gadget3'
    return None

def plot_hist(data, label, xlims, ylims, filename):
    fig, grid = plt.subplots(2, 2, figsize=(figure_size[1]*2, figure_size[0]*2), dpi=400)
    grid = grid.flatten()
    fig.subplots_adjust(hspace=0.15, wspace=0.10)

    def _hist(axis, snap_name, color, label):
        file = '{0:s}.pickle'.format(snap_name)
        disk = helpers.load_snapshot(file)
        x = data(disk).ravel()
        axis.hist(x, bins=100, normed=True, color=color, histtype='step', label=label)
        axis.set_xlim(xlims)
        axis.set_ylim(ylims)
        ymin, ymax = ylims
        xmin, xmax = xlims
        axis.text(xmin + 0.6*(xmax-xmin), ymin + 0.7*(ymax-ymin), r'$t=' + '{0:.2f}'.format(disk.time) + r'\,\rm{Gyrs}$', fontsize=5)
        
    for i in range(0, len(changa_snaps)):
        _hist(grid[i], changa_snaps[i], 'red', 'ChaNGa')
        _hist(grid[i], gadget_snaps[i], 'blue', 'Gadget3')
        grid[i].tick_params(axis='x', labelsize=plotting.text_sizes['axis']*0.9)
        grid[i].tick_params(axis='y', labelsize=plotting.text_sizes['axis']*0.9, pad=0.5)
        grid[i].set_xlabel(label, fontsize=plotting.text_sizes['label'], labelpad=0.55)
        if i == 0:
            grid[i].legend(fontsize=plotting.text_sizes['annotation'], loc='upper right', frameon=False)
    
    plotting.save_fig(fig, filename+'.png')
    
def plot_mesh(data, cmap, cbar_label, filename):
    fig, grid = plotting.make_fig_grid(x=dims[1], y=dims[0], size=figure_size, cbar_location='right',
                                        add_all=True, direction='row', cbar_mode='edge', share_all=True,
                                        cbar_pad='2.5%')

    for i in range(0, len(snapshots)):
        file = '{0:s}.pickle'.format(snapshots[i])
        disk = helpers.load_snapshot(file)
        
        vrange = [np.min(data(disk)), np.max(data(disk))]
        vrange[0] = 0.1 if vrange[0] < 0.1 else vrange[0]
        cmap.set_under(cmap(vrange[0]))
        cmap.set_over(cmap(vrange[1]))
        
        plotting.mesh(grid[i], disk.x_grid, disk.y_grid, data(disk), vrange, cmap=cmap,
                      cbar_ax=grid.cbar_axes[i] if i%2==1 else None,
                      xlabel=r'$x/R_s$' if i%2==1 else None,
                      ylabel=r'$y/R_s$' if i%2==1 else None,
                      title=titles(i) if i < 2 else None,
                      cbar_label=cbar_label,
                      norm=colors.LogNorm())
        grid[i].text(-5.0, 15.0, r'$t=' + '{0:.2f}'.format(disk.time) + r'\,\rm{Gyrs}$', fontsize=9)
    plotting.save_fig(fig, filename+'.png')
#--------------------------------------------------------------------------------------------------------------------------
plotting.text_sizes['label'] *= 1.2
dims = (len(changa_snaps), 2)
figure_size = (1.8, 1.8)

cmap = mpl.cm.get_cmap('Greys')
plot_mesh(lambda x: x.stellar_smd, cmap, r'$\Sigma_{\star}$', 'gas_stars')
plot_hist(lambda x: x.stellar_smd, r'$\Sigma_{\star}$', (1.25, 50.0), (0.0, 0.03), 'gas_stars_hist')

cmap = mpl.cm.get_cmap('Blues')
plot_mesh(lambda x: x.gas_smd, cmap, r'$\Sigma_{\rm{gas}}$', 'gas_gas') 
plot_hist(lambda x: x.gas_smd, r'$\Sigma_{\rm{gas}}$', (1.25, 30.0), (0.0, 0.06), 'gas_gas_hist')
 
cmap = mpl.cm.get_cmap('Oranges')
plot_mesh(lambda x: x.temp_grid, cmap, r'$T\,\rm\left(\rm{K}\right)$', 'gas_temp') 
plot_hist(lambda x: x.temp_grid, r'$T\,\rm\left(\rm{K}\right)$', (0.0, 40.0), (0.0, 0.1), 'gas_temp_hist')
