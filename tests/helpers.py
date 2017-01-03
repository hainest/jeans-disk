import os
import pickle
import gadget
import tipsy
import numpy as np

def get_output_file(file_name):
    input_dir, input_name = os.path.split(file_name)
    input_file_basename = os.path.splitext(input_name)[0]
    
    if input_dir != '':
        input_dir += '/'
    
    return input_dir + input_file_basename

def bin2d(x, y, nbins, weights=None, center=True):
    hist, X, Y = np.histogram2d(x, y, bins=nbins, weights=weights)
    x_grid, y_grid = np.meshgrid(X, Y)
    
    if center:
        x_grid = (x_grid[1:, 1:] + x_grid[:-1, :-1]) / 2.0
        y_grid = (y_grid[1:, 1:] + y_grid[:-1, :-1]) / 2.0

    return hist, x_grid, y_grid

def select_slab2D(pos, x_lim, y_lim):
    x_mask = (np.abs(pos[:, 0]) <= x_lim)
    y_mask = (np.abs(pos[:, 1]) <= y_lim)
    return x_mask & y_mask

class processed_data:
    def __init__(self):
        self.time = None
        self.x_grid = None
        self.y_grid = None
        self.stellar_smd = None
        self.gas_smd = None

def load_snapshot(filename):
    with open(filename, 'rb') as f:
        disk = pickle.load(f)
        return disk

def process_changa_snapshot(input_file, output_file, limits, nbins=512):
    pickle_file = '{0:s}.pickle'.format(output_file)
    if os.path.isfile(pickle_file):
        return load_snapshot(pickle_file)

    mass_factor = 1e10 / 2.3245560928778488e-05
    disk = processed_data()
    
    with tipsy.File(input_file) as snap:
        disk.time = snap.header.time

        slab_mask = select_slab2D(snap.stars.pos, *limits)
        x, y = snap.stars.pos[:, 0][slab_mask], snap.stars.pos[:, 1][slab_mask]
        mass, disk.x_grid, disk.y_grid = bin2d(x, y, nbins, weights=snap.stars.mass[slab_mask])
        mass *= mass_factor
        bin_area = 1.0e6 * (2.0 * limits[0]) * (2.0 * limits[1]) / (1.0 * nbins * nbins)  # pc^2
        disk.stellar_smd = mass / bin_area
        
        if snap.gas:
            mass = bin2d(x, y, nbins, weights=snap.gas.mass[slab_mask])
            mass *= mass_factor
            disk.gas_smd = mass / bin_area
    
    with open(pickle_file, 'wb') as f:
        pickle.dump(disk, f, pickle.HIGHEST_PROTOCOL)
    
    return disk

def process_gadget_snapshot(input_file, output_file, limits, nbins=512):
    pickle_file = '{0:s}.pickle'.format(output_file)
    if os.path.isfile(pickle_file):
        with open(pickle_file, 'rb') as f:
            disk = pickle.load(f)
            return disk

    disk = processed_data()
    
    with gadget.File(input_file) as snap:
        disk.time = snap.header.time
    
        slab_mask = select_slab2D(snap.disk.positions, *limits)
        x, y = snap.disk.positions[:, 0][slab_mask], snap.disk.positions[:, 1][slab_mask]
        mass, disk.x_grid, disk.y_grid = bin2d(x, y, nbins, weights=snap.disk.mass[slab_mask])
        mass *= 1e10
        bin_area = 1.0e6 * (2.0 * limits[0]) * (2.0 * limits[1]) / (1.0 * nbins * nbins)  # pc^2
        disk.stellar_smd = mass / bin_area
        
        if snap.gas:
            mass = bin2d(x, y, nbins, weights=snap.gas.mass[slab_mask])
            mass *= 1e10
            disk.gas_smd = mass / bin_area
    
    with open(pickle_file, 'wb') as f:
        pickle.dump(disk, f, pickle.HIGHEST_PROTOCOL)
    
    return disk

