#!/usr/bin/env python3

import sys

if sys.version_info.major < 3:
    print('python3 required!')
    exit()

import gadget
import ChaNGa
import tipsy
import argparse
import math
import numpy as np

parser = argparse.ArgumentParser(description='Convert GADGET2 files to ChaNGa files')
parser.add_argument('gadget_file', metavar='GADGET', help='GADGET2 HDF5 file to convert')
parser.add_argument('param_file', metavar='Parameter', help='GADGET2 parameter file to convert')
parser.add_argument('out_dir', metavar='out_dir', help='Location of output')
parser.add_argument('--preserve-boundary-softening', action='store_true', help='Preserve softening lengths for boundary particles')
parser.add_argument('--no-param-list', action='store_true', help='Do not store a complete list ChaNGa parameters in "param_file"')
parser.add_argument('--generations', type=int, help='Number of generations of stars each gas particle can spawn (see GENERATIONS in Gadget)')
parser.add_argument('--viscosity', action='store_true', help='Use artificial bulk viscosity')
args = parser.parse_args()

print("Converting {0:s}".format(args.gadget_file))

try:
    gadget_params = gadget.parameter_file(args.param_file)
except Exception as e:
    print('\nERROR: {0:s}\n\n'.format(str(e)))
    parser.print_help()
    exit()

gadget_file = gadget.File(args.gadget_file)
changa_params = ChaNGa.convert_parameter_file(gadget_params, args, gadget_file.gas is not None)
basename = args.out_dir + '/' + ChaNGa.get_input_file(args.gadget_file) + '.tipsy'

# Output the parameter file
with open(basename + '.ChaNGa.params', 'w') as f:
    for k in sorted(changa_params):
         f.write('{0:20s} = {1:s}\n'.format(k, str(changa_params[k])))

    if not args.no_param_list:
        f.write('\n# Complete parameter list below\n')
        f.write(ChaNGa.all_parameters)

##################################################################################
time = float(gadget_file.header.time)
is_cosmological = int(gadget_params['ComovingIntegrationOn']) == 1

# Gadget units have an extra sqrt(a) in the internal velocities
velocity_scale = math.sqrt(1.0 + float(gadget_file.header.redshift))

with tipsy.streaming_writer(basename) as file:
    ngas = ndark = nstar = 0
    
    # just a placeholder
    file.header(time, ngas, ndark, nstar)
    
    if gadget_file.gas is not None:
        gas = gadget_file.gas
        ngas += gas.size
        temp = gadget.convert_U_to_temperature(gas, gadget_params)
        gas.mass *= changa_params['dMsolUnit']
        gas.velocities *= velocity_scale
        metals = gas.metals if gas.metals is not None else np.zeros(gas.size)
        pot = gas.potential if gas.potential is not None else np.zeros(gas.size)
        file.gas(gas.mass, gas.positions, gas.velocities, gas.density, temp, gas.hsml, metals, pot, gas.size)
    
    if gadget_file.halo is not None:
        halo = gadget_file.halo
        ndark += halo.size
        halo.mass *= changa_params['dMsolUnit']
        halo.velocities *= velocity_scale
        pot = halo.potential if halo.potential is not None else np.zeros(halo.size)
        file.darkmatter(halo.mass, halo.positions, halo.velocities, gadget_params['SofteningHalo'], pot, halo.size)
        
    # In ChaNGa, cosmological simulations treat disk and bulge particles
    # as dark matter particles
    if is_cosmological:
        if gadget_file.disk is not None:
            disk = gadget_file.disk
            ndark += disk.size
            disk.mass *= changa_params['dMsolUnit']
            disk.velocities *= velocity_scale
            pot = disk.potential if disk.potential is not None else np.zeros(disk.size)
            file.darkmatter(disk.mass, disk.positions, disk.velocities, gadget_params['SofteningDisk'], pot, disk.size)
        
        if gadget_file.bulge is not None:
            bulge = gadget_file.bulge
            ndark += bulge.size
            bulge.mass *= changa_params['dMsolUnit']
            bulge.velocities *= velocity_scale
            pot = bulge.potential if bulge.potential is not None else np.zeros(bulge.size)
            file.darkmatter(bulge.mass, bulge.positions, bulge.velocities, gadget_params['SofteningBulge'], pot, bulge.size)
    
    # Convert boundary particles to dark matter particles
    if gadget_file.boundary is not None:
        boundary = gadget_file.boundary
        ndark += boundary.size
        boundary.mass *= changa_params['dMsolUnit']
        boundary.velocities *= velocity_scale
        eps = gadget_params['SofteningBndry'] if args.preserve_boundary_softening else gadget_params['SofteningHalo']
        pot = boundary.potential if boundary.potential is not None else np.zeros(boundary.size)
        file.darkmatter(boundary.mass, boundary.positions, boundary.velocities, eps, pot, boundary.size)
        
    if not is_cosmological:
        if gadget_file.disk is not None:
            disk = gadget_file.disk
            nstar += disk.size
            disk.mass *= changa_params['dMsolUnit']
            disk.velocities *= velocity_scale
            metals = np.zeros(disk.size)
            tform = np.zeros(disk.size)
            pot = disk.potential if disk.potential is not None else np.zeros(disk.size)
            file.stars(disk.mass, disk.positions, disk.velocities, metals, tform, gadget_params['SofteningDisk'],
                       pot, disk.size)
            metals = tform = None
        
        if gadget_file.bulge is not None:
            bulge = gadget_file.bulge
            nstar += bulge.size
            bulge.mass *= changa_params['dMsolUnit']
            bulge.velocities *= velocity_scale
            metals = bulge.metals if bulge.metals is not None else np.zeros(bulge.size)
            tform = bulge.t_form if bulge.t_form is not None else np.zeros(bulge.size)
            pot = bulge.potential if bulge.potential is not None else np.zeros(bulge.size)
            file.stars(bulge.mass, bulge.positions, bulge.velocities, metals, tform,
                       gadget_params['SofteningBulge'], pot, bulge.size)

    if gadget_file.stars is not None:
        star = gadget_file.stars
        nstar += star.size
        star.mass *= changa_params['dMsolUnit']
        star.velocities *= velocity_scale
        metals = star.metals if star.metals is not None else np.zeros(star.size)
        tform = star.t_form if star.t_form is not None else np.zeros(star.size)
        pot = star.potential if star.potential is not None else np.zeros(star.size)
        file.stars(star.mass, star.positions, star.velocities, metals, tform,
                   gadget_params['SofteningStars'], pot, star.size)

# update the header
with tipsy.streaming_writer(basename, 'r+b') as file:
    file.header(time, ngas, ndark, nstar)
