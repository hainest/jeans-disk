import h5py
import numpy as np
import astropy.units as apu
import astropy.constants as apc

def convert_U_to_temperature(gas_data, params=None):
    units = {}
    
    if params is not None:
        units['length'] = float(params['UnitLength_in_cm']) * apu.cm
        units['mass'] = float(params['UnitMass_in_g']) * apu.g
        units['velocity'] = float(params['UnitVelocity_in_cm_per_s']) * apu.cm / apu.s
    else:
        units['length'] = (1.0 * apu.kpc).to(apu.cm)
        units['mass'] = (1e10 * apu.Msun).to(apu.g)
        units['velocity'] = 1.0 * apu.km / apu.s

    units['time'] = units['length'] / units['velocity']
    units['density'] = units['mass'] / units['length'] ** 3.0
    units['pressure'] = units['mass'] / units['length'] / units['time'] ** 2.0

    boltzmann = apc.k_B.cgs.value
    protonmass = apc.m_p.cgs.value
    gamma_minus1 = (5.0 / 3.0) - 1.0
    h_massfrac = 0.76
    
    # Neutral gas
    mean_weight = 4.0 / (1.0 + 3.0 * h_massfrac)
    
    # Fully ionized gas
    if params is not None and float(params['InitGasTemp']) >= 1e4:
        mean_weight = 4.0 / (8.0 - 5.0 * (1.0 - h_massfrac))

    # Gas with metals
    if gas_data.metals is not None and gas_data.electron_density is not None:
        X = gas_data.metals / gas_data.mass
        mask = X > 0.0
        Y = np.zeros(X.shape)
        Y[mask] = (1.0 - X[mask]) / (4.0 * X[mask])
        mean_weight = (1.0 + 4.0 * Y) / (1.0 + Y + gas_data.electron_density)

    p = float(units['pressure'] / (apu.g / (apu.cm * apu.s ** 2.0)))
    d = float(units['density'] / (apu.g / apu.cm ** 3.0))
    u = gas_data.internal_energy * p / d
    temp = gamma_minus1 / boltzmann * u * protonmass * mean_weight

    # Enforce minimum temperature
    if params is not None:
        temp[temp < float(params['MinGasTemp'])] = float(params['MinGasTemp'])

    return temp

class basic_particle():
    def __init__(self, data, mass):
        self.positions = np.empty(data['Coordinates'].shape, data['Coordinates'].dtype)
        data['Coordinates'].read_direct(self.positions)
        
        self.velocities = np.empty(data['Velocities'].shape, data['Velocities'].dtype)
        data['Velocities'].read_direct(self.velocities)
        
        self.size = self.positions.shape[0]
        
        if (float(mass) <= 0.0):
            self.mass = np.empty(data['Masses'].shape, data['Masses'].dtype)
            data['Masses'].read_direct(self.mass)
        else:
            self.mass = float(mass) * np.ones(self.size, dtype=np.float32)
        
        self.potential = None
        if 'Potential' in data.keys():
            self.potential = np.empty(data['Potential'].shape, data['Potential'].dtype)
            data['Potential'].read_direct(self.potential)
        
        # Some useful aliases
        self.pos = self.positions
        self.vel = self.velocities
        self.pot = self.potential

class star_particle(basic_particle):
    def __init__(self, data, mass):
        super().__init__(data, mass)

        self.t_form = None
        if 'StellarFormationTime' in data.keys():
            self.t_form = np.empty(data['StellarFormationTime'].shape, data['StellarFormationTime'].dtype)
            data['StellarFormationTime'].read_direct(self.t_form)
        
        self.metals = None
        if 'Metallicity' in data.keys():
            self.metals = np.empty(data['Metallicity'].shape, data['Metallicity'].dtype)
            data['Metallicity'].read_direct(self.metals)

class gas_particle(basic_particle):
    def __init__(self, data, mass):
        super().__init__(data, mass)

        self.internal_energy = np.empty(data['InternalEnergy'].shape, data['InternalEnergy'].dtype)
        data['InternalEnergy'].read_direct(self.internal_energy)

        self.density = None   
        if 'Density' in data.keys():
            self.density = np.empty(data['Density'].shape, data['Density'].dtype)
            data['Density'].read_direct(self.density)

        self.hsml = None        
        if 'SmoothingLength' in data.keys():
            self.hsml = np.empty(data['SmoothingLength'].shape, data['SmoothingLength'].dtype)
            data['SmoothingLength'].read_direct(self.hsml)

        self.electron_density = None
        if 'ElectronAbundance' in data.keys():
            self.electron_density = np.empty(data['ElectronAbundance'].shape, data['ElectronAbundance'].dtype)
            data['ElectronAbundance'].read_direct(self.electron_density)
        
        self.sfr = None
        if 'StarFormationRate' in data.keys():
            self.sfr = np.empty(data['StarFormationRate'].shape, data['StarFormationRate'].dtype)
            data['StarFormationRate'].read_direct(self.sfr)
        
        self.metals = None
        if 'Metallicity' in data.keys():
            self.metals = np.empty(data['Metallicity'].shape, data['Metallicity'].dtype)
            data['Metallicity'].read_direct(self.metals)

        # Set temperature from internal energy
        # NOTE: This must be done _after_ reading metals and electron density
        self.temperature = convert_U_to_temperature(self)
        
        # Some useful aliases
        self.temp = self.temperature
        self.U = self.internal_energy
        self.rho = self.density
        self.Ne = self.electron_density

class Header():
    def __init__(self, attrs):
        self.numpart_thisfile = attrs['NumPart_ThisFile'][()]
        self.numpart_total = attrs['NumPart_Total'][()]
        self.numpart_total_highword = attrs['NumPart_Total_HighWord'][()]
        self.masstable = attrs['MassTable'][()]
        self.time = float(attrs['Time'])
        self.redshift = float(attrs['Redshift'])
        self.boxsize = float(attrs['BoxSize'])
        self.numfilespersnapshot = int(attrs['NumFilesPerSnapshot'])
        self.omega0 = float(attrs['Omega0'])
        self.omegalambda = float(attrs['OmegaLambda'])
        self.hubbleparam = float(attrs['HubbleParam'])
        self.flag_sfr = int(attrs['Flag_Sfr'])
        self.flag_cooling = int(attrs['Flag_Cooling'])
        self.flag_stellarage = int(attrs['Flag_StellarAge'])
        self.flag_metals = int(attrs['Flag_Metals'])
        self.flag_feedback = int(attrs['Flag_Feedback'])
        self.flag_doubleprecision = int(attrs['Flag_DoublePrecision'])
        self.flag_ic_info = int(attrs['Flag_IC_Info']) if 'Flag_IC_Info' in attrs else 0
    
    def __str__(self):
        return '\n'.join(['{0:s} => {1:s}'.format(x, str(getattr(self, x))) for x in self.__dict__])

class parameter_file():
    def __init__(self, filename=None):
        self.data = {}
        
        if filename is not None:
            with open(filename) as f:
                self.read_from_textfile(f)

    @classmethod
    def from_hdf5(cls, hdf5_file):
        c = cls()
        if not isinstance(hdf5_file, h5py.File):
            with h5py.File(hdf5_filename) as f:
                c.read_from_hdf5(f)
        else:
            c.read_from_hdf5(hdf5_file)
        return c
    
    def read_from_hdf5(self, hdf5_file):
        for x in hdf5_file['parameters']:
            self.data[x[0].decode('ascii')] = x[1].decode('ascii')
    
    def write_to_hdf5(self, hdf5_file):
        dt = h5py.special_dtype(vlen=bytes)
        params = [[str(k).encode('ascii'), str(v).encode('ascii')] for k, v in self.data.items()]
        hdf5_file.create_dataset('parameters', (len(params), 2), dtype=dt, data=params)
    
    def read_from_textfile(self, file):
        for line in file:
            line = line.strip()
            if line == '':
                continue
            name, value = (line.split())[:2]
            if '%' in name:
                continue
            self.data[name] = value
    
    def write_to_textfile(self, file):
        for k in sorted(self.data):
            file.write('{0:<40s}{1:s}\n'.format(k, str(self.data[k])))
    
    def __getitem__(self, key):
        return self.data[key]
    
    def items(self):
        return self.data.items()
    
    def __str__(self):
        return '\n'.join(['{0:s} => {1:s}'.format(k, str(v)) for k, v in self.data.items()])

class File:
    def __init__(self, fname, mode='r'):
        self.file = h5py.File(fname, mode)
        self.header = Header(self.file['Header'].attrs)
        self.gas_particles = None
        self.halo_particles = None
        self.disk_particles = None
        self.bulge_particles = None
        self.star_particles = None
        self.boundary_particles = None
        self._params = None

    def close(self):
        self.file.close()

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        return False  # always re-raise exceptions
    
    def to_hdf5(self):
        return self.file
    
    @property
    def params(self):
        if self._params is None:
            self._params = parameter_file.from_hdf5(self.file)
        return self._params
    
    @params.setter
    def params(self, p):
        self._params = p
    
    @property
    def gas(self):
        if self.gas_particles is None and 'PartType0' in self.file.keys():
            self.gas_particles = gas_particle(self.file['PartType0'], self.header.masstable[0])
        return self.gas_particles

    @property
    def halo(self):
        if self.halo_particles is None and 'PartType1' in self.file.keys():
            self.halo_particles = basic_particle(self.file['PartType1'], self.header.masstable[1])
        return self.halo_particles
    
    @property
    def disk(self):
        if self.disk_particles is None and 'PartType2' in self.file.keys():
            self.disk_particles = basic_particle(self.file['PartType2'], self.header.masstable[2])
        return self.disk_particles
        
    @property
    def bulge(self):
        if self.bulge_particles is None and 'PartType3' in self.file.keys():
            self.bulge_particles = star_particle(self.file['PartType3'], self.header.masstable[3])
        return self.bulge_particles
    
    @property
    def stars(self):
        if self.star_particles is None and 'PartType4' in self.file.keys():
            self.star_particles = star_particle(self.file['PartType4'], self.header.masstable[4])
        return self.star_particles

    @property
    def boundary(self):
        if self.boundary_particles is None and 'PartType5' in self.file.keys():
            self.boundary_particles = basic_particle(self.file['PartType5'], self.header.masstable[5])
        return self.boundary_particles

