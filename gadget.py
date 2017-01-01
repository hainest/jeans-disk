import numpy as np
import h5py

class basic_particle():
    def __init__(self, data, mass, header):
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

class particle_with_metals(basic_particle):
    def __init__(self, data, mass, header):
        super().__init__(data, mass, header)
        self.t_form = None
        if header.Flag_Sfr and header.Flag_StellarAge:
            if 'StellarFormationTime' in data.keys():
                self.t_form = np.empty(data['StellarFormationTime'].shape, data['StellarFormationTime'].dtype)
                data['StellarFormationTime'].read_direct(self.t_form)
            else:
                print('Stellar evolution enabled, but StellarFormationTime is not present. Skipping...')
        
        self.metals = None
        if header.Flag_Sfr and header.Flag_Metals:
            if 'Metallicity' in data.keys():
                self.metals = np.empty(data['Metallicity'].shape, data['Metallicity'].dtype)
                data['Metallicity'].read_direct(self.metals)
            else:
                print('Star formation and metals enabled, but no stellar metals found. Skipping...')

class gas_particle(particle_with_metals):
    def __init__(self, data, mass, header):
        super().__init__(data, mass, header)

        self.internal_energy = np.empty(data['InternalEnergy'].shape, data['InternalEnergy'].dtype)
        data['InternalEnergy'].read_direct(self.internal_energy)
        
        self.density = np.empty(data['Density'].shape, data['Density'].dtype)
        data['Density'].read_direct(self.density)
        
        self.hsml = np.empty(data['SmoothingLength'].shape, data['SmoothingLength'].dtype)
        data['SmoothingLength'].read_direct(self.hsml)

        self.electron_density = None
        if header.Flag_Cooling:
            self.electron_density = np.empty(data['ElectronAbundance'].shape, data['ElectronAbundance'].dtype)
            data['ElectronAbundance'].read_direct(self.electron_density)
        
        self.sfr = None
        if header.Flag_Sfr:
            self.sfr = np.empty(data['StarFormationRate'].shape, data['StarFormationRate'].dtype)
            data['StarFormationRate'].read_direct(self.sfr)

class Header():
    def __init__(self, attrs):
        self.NumPart_ThisFile        = attrs['NumPart_ThisFile'][()]
        self.NumPart_Total           = attrs['NumPart_Total'][()]
        self.NumPart_Total_HighWord  = attrs['NumPart_Total_HighWord'][()]
        self.MassTable               = attrs['MassTable'][()]
        self.Time                    = float(attrs['Time'])
        self.Redshift                = float(attrs['Redshift'])
        self.BoxSize                 = float(attrs['BoxSize'])
        self.NumFilesPerSnapshot     = int(attrs['NumFilesPerSnapshot'])
        self.Omega0                  = float(attrs['Omega0'])
        self.OmegaLambda             = float(attrs['OmegaLambda'])
        self.HubbleParam             = float(attrs['HubbleParam'])
        self.Flag_Sfr                = int(attrs['Flag_Sfr'])
        self.Flag_Cooling            = int(attrs['Flag_Cooling'])
        self.Flag_StellarAge         = int(attrs['Flag_StellarAge'])
        self.Flag_Metals             = int(attrs['Flag_Metals'])
        self.Flag_Feedback           = int(attrs['Flag_Feedback'])
        self.Flag_DoublePrecision    = int(attrs['Flag_DoublePrecision'])
        self.Flag_IC_Info            = int(attrs['Flag_IC_Info'])
    
    def __str__(self):
        return '\n'.join(['{0:s} => {1:s}'.format(x, str(getattr(self, x))) for x in self.__dict__])

class File:
    def __init__(self, fname):
        self.file = h5py.File(fname, 'r')
        self.header = Header(self.file['Header'].attrs)
        self.gas_particles = None
        self.halo_particles = None
        self.disk_particles = None
        self.bulge_particles = None
        self.star_particles = None
        self.boundary_particles = None

    def close(self):
        self.file.close()

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        return False  # always re-raise exceptions
    
    @property
    def gas(self):
        if self.gas_particles is None and 'PartType0' in self.file.keys():
            self.gas_particles = gas_particle(self.file['PartType0'], self.header.MassTable[0], self.header)
        return self.gas_particles

    @property
    def halo(self):
        if self.halo_particles is None and 'PartType1' in self.file.keys():
            self.halo_particles = basic_particle(self.file['PartType1'], self.header.MassTable[1], self.header)
        return self.halo_particles
    
    @property
    def disk(self):
        if self.disk_particles is None and 'PartType2' in self.file.keys():
            self.disk_particles = basic_particle(self.file['PartType2'], self.header.MassTable[2], self.header)
        return self.disk_particles
        
    @property
    def bulge(self):
        if self.bulge_particles is None and 'PartType3' in self.file.keys():
            self.bulge_particles = particle_with_metals(self.file['PartType3'], self.header.MassTable[3], self.header)
        return self.bulge_particles
    
    @property
    def stars(self):
        if self.star_particles is None and 'PartType4' in self.file.keys():
            self.star_particles = particle_with_metals(self.file['PartType4'], self.header.MassTable[4], self.header)
        return self.star_particles

    @property
    def boundary(self):
        if self.boundary_particles is None and 'PartType5' in self.file.keys():
            self.boundary_particles = basic_particle(self.file['PartType5'], self.header.MassTable[5], self.header)
        return self.boundary_particles

class Parameter_file():
    def __init__(self, fname):
        self.data = {}
        with open(fname, 'r') as file:
            for line in file:
                line = line.strip()
                if line == '':
                    continue
                name, value = (line.split())[:2]
                if '%' in name:
                    continue
                self.data[name] = value
    
    def __getitem__(self, key):
        return self.data[key]
    
    def items(self):
        return self.data.items()
