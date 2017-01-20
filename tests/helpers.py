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
        self.temp_grid = None

def load_snapshot(filename):
    with open(filename, 'rb') as f:
        disk = pickle.load(f)
        return disk

def _process_snapshot(stars, gas, mass_factor, nbins, limits):
    disk = processed_data()
   
    slab_mask = select_slab2D(stars.pos, *limits)
    x, y = stars.pos[:, 0][slab_mask], stars.pos[:, 1][slab_mask]
    mass, disk.x_grid, disk.y_grid = bin2d(x, y, nbins, weights=stars.mass[slab_mask])
    mass *= mass_factor
    bin_area = 1.0e6 * (2.0 * limits[0]) * (2.0 * limits[1]) / (1.0 * nbins * nbins)  # pc^2
    disk.stellar_smd = mass / bin_area
    
    if gas:
        slab_mask = select_slab2D(gas.pos, *limits)
        x, y = gas.pos[:, 0][slab_mask], gas.pos[:, 1][slab_mask]
        mass = bin2d(x, y, nbins, weights=gas.mass[slab_mask])[0]
        mass *= mass_factor
        disk.gas_smd = mass / bin_area
        
        temp = bin2d(x, y, nbins, weights=gas.temp[slab_mask])[0]
        disk.temp_grid = temp / bin_area
    
    return disk

def process_changa_snapshot(input_file, output_file, limits, nbins=512, is_xdr=True):
    if os.path.isfile(output_file):
        return load_snapshot(output_file)

    from astropy import units as u
    from astropy.constants import G as G_u
    unitlength = 1.0 * u.kpc
    unitvelocity = 1.0 * u.km / u.s
    unittime = (unitlength / unitvelocity).to(u.s)
    mass_factor = float((unitlength.to(u.m) ** 3 / unittime ** 2 / G_u).to(u.Msun) / u.Msun)

    with tipsy.File(input_file, is_xdr=is_xdr) as snap:
        disk = _process_snapshot(snap.stars, snap.gas, mass_factor, nbins, limits)
        disk.time = snap.header.time
    
    with open(output_file, 'wb') as f:
        pickle.dump(disk, f, pickle.HIGHEST_PROTOCOL)
    
    return disk

def process_gadget_snapshot(input_file, output_file, limits, nbins=512):
    if os.path.isfile(output_file):
        return load_snapshot(output_file)
    
    mass_factor = 1e10
    
    with gadget.File(input_file) as snap:
        disk = _process_snapshot(snap.disk, snap.gas, mass_factor, nbins, limits)
        disk.time = snap.header.time
    
    with open(output_file, 'wb') as f:
        pickle.dump(disk, f, pickle.HIGHEST_PROTOCOL)
    
    return disk

