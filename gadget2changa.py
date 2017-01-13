#!/usr/bin/env python3

import sys

if sys.version_info.major < 3:
    print('python3 required!')
    exit()

import gadget
import ChaNGa
import tipsy
import argparse
import astropy.units as apu
import astropy.constants as apc
import math
import numpy as np

def convert_U_to_temperature(gadget_params, gadget_file, hubble):
    # TODO: Check these units wrt the mass conversion between GADGET and ChaNGa
    units = {}
    units['Length_in_cm'] = float(gadget_params['UnitLength_in_cm']) / hubble
    units['Mass_in_g'] = float(gadget_params['UnitMass_in_g']) / hubble
    units['Velocity_in_cm_per_s'] = float(gadget_params['UnitVelocity_in_cm_per_s'])
    units['Time_in_s'] = units['Length_in_cm'] / units['Velocity_in_cm_per_s']
    units['Energy_in_cgs'] = units['Mass_in_g'] * units['Length_in_cm'] ** 2 / units['Time_in_s'] ** 2
    
    constants = {
        'boltzmann'     : apc.k_B.cgs.value,
        'protonmass'    : apc.m_p.cgs.value,
        'gamma_minus1'  : (5.0 / 3.0) - 1.0,
        'h_massfrac'    : 0.76
    }
    
    # Convert temperature to Kelvin
    print('Converting internal energy to temperature assuming a neutral hydrogen-only gamma=5/3 gas and non-traditional SPH')
    
    # See GADGET3/density.c:1426  for details on these calculations
    mean_weight = 4.0 / (1.0 + 3.0 * constants['h_massfrac'])
    
    if gadget_file.gas.metals is not None and gadget_file.gas.electron_density is not None:
        X = gadget_file.gas.metals / gadget_file.gas.mass
        mask = X > 0.0
        Y = np.zeros(X.shape)
        Y[mask] = (1.0 - X[mask]) / (4.0 * X[mask])
        mean_weight = (1.0 + 4.0 * Y) / (1.0 + Y + gadget_file.gas.electron_density)
    
    gas_temp = constants['gamma_minus1'] / constants['boltzmann'] * gadget_file.gas.internal_energy / gadget_file.gas.mass
    gas_temp *= constants['protonmass'] * mean_weight * units['Energy_in_cgs'] / units['Mass_in_g']
    gas_temp[gas_temp < float(gadget_params['MinGasTemp'])] = float(gadget_params['MinGasTemp'])

    return gas_temp

#-----------------------------------------------------------------------------

parser = argparse.ArgumentParser(description='Convert GADGET2 files to ChaNGa files')
parser.add_argument('gadget_file', metavar='GADGET', help='GADGET2 HDF5 file to convert')
parser.add_argument('param_file', metavar='Parameter', help='GADGET2 parameter file to convert')
parser.add_argument('out_dir', metavar='out_dir', help='Location of output')
parser.add_argument('--preserve-boundary-softening', action='store_true', help='Preserve softening lengths for boundary particles')
parser.add_argument('--no-param-list', action='store_true', help='Do not store a complete list ChaNGa parameters in "param_file"')
parser.add_argument('--generations', type=int, help='Number of generations of stars each gas particle can spawn (see GENERATIONS in Gadget)')
parser.add_argument('--viscosity', action='store_true', help='Use artificial bulk viscosity')
args = parser.parse_args()

try:
    gadget_params = gadget.Parameter_file(args.param_file)
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

hubble = 1.0
if is_cosmological:
    hubble = float(gadget_params['HubbleParam'])
    if hubble == 0.0:
        hubble = 1.0

with tipsy.streaming_writer(basename) as file:
    ngas = ndark = nstar = 0
    
    # just a placeholder
    file.header(time, ngas, ndark, nstar)
    
    if gadget_file.gas is not None:
        gas = gadget_file.gas
        ngas += gas.size
        gas_temp = convert_U_to_temperature(gadget_params, gadget_file, hubble)
        gas.mass *= changa_params['dMsolUnit']
        gas.velocities *= velocity_scale
        metals = gas.metals if gas.metals is not None else np.zeros(gas.size)
        pot = gas.potential if gas.potential is not None else np.zeros(gas.size)
        file.gas(gas.mass, gas.positions, gas.velocities, gas.density, gas_temp, gas.hsml, metals, pot, gas.size)
    
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
