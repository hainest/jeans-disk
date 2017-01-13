import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import plotting
import helpers
import matplotlib as mpl
import matplotlib.colors as colors
import tipsy
import gadget

limits = (20.0, 20.0) # kpc

changa_snaps = ['ChaNGa/nogas/nogas.out.000050.tipsy', 'ChaNGa/nogas/nogas.out.000300.tipsy', 'ChaNGa/nogas/nogas.out.000500.tipsy']
gadget_snaps = ['Gadget3/nogas/nogas_000.hdf5', 'Gadget3/nogas/nogas_007.hdf5', 'Gadget3/nogas/nogas_010.hdf5']

for f in changa_snaps:
    helpers.process_changa_snapshot(f, helpers.get_output_file(f), limits)

for f in gadget_snaps:
    helpers.process_gadget_snapshot(f, helpers.get_output_file(f), limits)

snapshots = [x for p in zip(changa_snaps, gadget_snaps) for x in p]

def titles(i):
    if i == 0:
        return 'ChaNGa'
    if i == 1:
        return 'Gadget3'
    return None

dims = (len(changa_snaps), 2)
figure_size = (1.8, 1.8)

fig, grid = plotting.make_fig_grid(x=dims[1], y=dims[0], size=figure_size, cbar_location='right',
                                   share_all=True, add_all=True, direction='row', cbar_mode='edge',
                                   cbar_pad='2.5%')
plotting.text_sizes['label'] *= 1.2

cmap = mpl.cm.get_cmap('Greys')
vrange = (0.1, 200.0)
cmap.set_under(cmap(vrange[0]))
cmap.set_over(cmap(vrange[1]))

for i in range(0, len(snapshots)):
    file = '{0:s}.pickle'.format(helpers.get_output_file(snapshots[i]))
    disk = helpers.load_snapshot(file)
    plotting.mesh(grid[i], disk.x_grid, disk.y_grid, disk.stellar_smd, vrange, cmap=cmap, cbar_ax=grid.cbar_axes[i],
                  xlabel=r'$x/R_s$', ylabel=r'$y/R_s$', cbar_label=r'$\Sigma_*$', norm=colors.LogNorm(),
                  title=titles(i) if i < 2 else None)
    if i%2 == 0:
        grid[i].text(-5.0, 15.0, r'$t=' + '{0:.2f}'.format(disk.time) + r'\,\rm{Gyrs}$', fontsize=9)

plotting.save_fig(fig, 'nogas.png')
