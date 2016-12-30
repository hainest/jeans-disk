import ctypes
import numpy as np
import numpy.ctypeslib as npct

"""
    The mapping between the C and Python type interfaces for Tipsy.
    This is the lowest level of the Tipsy-Python interface. It is
    not intended for general use.' 
"""

_native_float32_dtype = np.dtype('=f')
_array_1d_float32 = npct.ndpointer(dtype=_native_float32_dtype, ndim=1, flags=('C','O','W','A'))
_array_2d_float32 = npct.ndpointer(dtype=_native_float32_dtype, ndim=2, flags=('C','O','W','A'))

def _convert_array(x):
    return np.require(x, dtype=_native_float32_dtype, requirements=['C_CONTIGUOUS', 'ALIGNED', 'WRITEABLE', 'OWNDATA', 'ENSUREARRAY'])

def _make_array(size, ndims=1, zero=False):
    if ndims == 1:
#         return np.empty(size, dtype=_native_float32_dtype) if not zero else np.zeros(size, dtype=_native_float32_dtype)
        return np.zeros(size, dtype=_native_float32_dtype) 
    if ndims == 2:
#         return np.empty((size, 3), dtype=_native_float32_dtype) if not zero else np.zeros((size, 3), dtype=_native_float32_dtype)
        return np.zeros((size, 3), dtype=_native_float32_dtype)
    raise ValueError("tipsy only supports 1d and 2d arrays")

def _pretty_print(obj, attrs):
    repr = []
    for k in attrs:
        a = getattr(obj, k)
        repr.append('{0:10s}: {1:s}'.format(k, str(a.shape) if isinstance(a, np.ndarray) else str(a)))
    return '\n'.join(repr)

class header():
    class struct(ctypes.Structure):
        _fields_ = [
            ('time'   , ctypes.c_double),
            ('nbodies', ctypes.c_uint),
            ('ndim'   , ctypes.c_int),
            ('ngas'   , ctypes.c_uint),
            ('ndark'  , ctypes.c_uint),
            ('nstar'  , ctypes.c_uint)
        ]

        @classmethod
        def from_external(cls, hdr):
            self = cls()
            self.time = hdr.time
            self.nbodies = hdr.nbodies
            self.ndim = hdr.ndim
            self.ngas = hdr.ngas
            self.ndark = hdr.ndark
            self.nstar = hdr.nstar
            return self

    def __init__(self):
        self.c_data = header.struct()

    def __str__(self):
        return _pretty_print(self, ['time','nbodies','ngas','ndark','nstar'])
    
    @property
    def time(self):
        return self.c_data.time
    @time.setter
    def time(self, rhs):
        self.c_data.time = rhs
    @property
    def nbodies(self):
        return self.c_data.nbodies
    @nbodies.setter
    def nbodies(self, rhs):
        self.c_data.nbodies = rhs
    @property
    def ngas(self):
        return self.c_data.ngas
    @ngas.setter
    def ngas(self, rhs):
        self.c_data.ngas = rhs
    @property
    def ndark(self):
        return self.c_data.ndark
    @ndark.setter
    def ndark(self, rhs):
        self.c_data.ndark = rhs
    @property
    def nstar(self):
        return self.c_data.nstar
    @nstar.setter
    def nstar(self, rhs):
        self.c_data.nstar = rhs

    @classmethod
    def from_external(cls, time, ngas, ndark, nstar):
        self = cls()
        self.time = float(time)
        self.nbodies = int(ngas) + int(ndark) + int(nstar)
        self.ndim = 3
        self.ngas = int(ngas)
        self.ndark = int(ndark)
        self.nstar = int(nstar)
        self.c_data = header.struct.from_external(self)
        return self

class gas_data():
    class struct(ctypes.Structure):
        _fields_ = [
            ('mass'   , _array_1d_float32),
            ('pos'    , _array_2d_float32),
            ('vel'    , _array_2d_float32),
            ('rho'    , _array_1d_float32),
            ('temp'   , _array_1d_float32),
            ('hsmooth', _array_1d_float32),
            ('metals' , _array_1d_float32),
            ('phi'    , _array_1d_float32),
            ('size'   , ctypes.c_size_t)
        ]
        
        def __init__(self):
            super().__init__()
    
        @classmethod
        def from_external(cls, other):
            self = cls()
            self.mass = other.mass.ctypes.data_as(_array_1d_float32)
            self.pos = other.pos.ctypes.data_as(_array_2d_float32)
            self.vel = other.vel.ctypes.data_as(_array_2d_float32)
            self.rho = other.rho.ctypes.data_as(_array_1d_float32)
            self.temp = other.temp.ctypes.data_as(_array_1d_float32)
            self.metals = other.metals.ctypes.data_as(_array_1d_float32)
            self.hsmooth = other.hsmooth.ctypes.data_as(_array_1d_float32)
            self.phi = other.phi.ctypes.data_as(_array_1d_float32)
            self.size = other.size
            return self

    def __init__(self):
        self.size = 0
        self.c_data = None
    
    def __str__(self):
        if self.c_data is not None:
            return _pretty_print(self, [k[0] for k in self.c_data._fields_])

    @classmethod
    def from_size(cls, size):
        self = cls()
        self.mass = _make_array(size)
        self.pos = _make_array(size, ndims=2)
        self.vel = _make_array(size, ndims=2)
        self.rho = _make_array(size)
        self.temp = _make_array(size)
        self.metals = _make_array(size)
        self.hsmooth = _make_array(size)
        self.phi = _make_array(size)
        self.size = size
        self.c_data = gas_data.struct.from_external(self)
        return self

    @classmethod
    def from_external(cls, mass, pos, vel, rho, temp, hsmooth, metals, phi, size):
        self = cls()
        self.mass = _convert_array(mass)
        self.pos = _convert_array(pos)
        self.vel = _convert_array(vel)
        self.rho = _convert_array(rho)
        self.temp = _convert_array(temp)
        self.hsmooth = _convert_array(hsmooth)
        self.metals = _convert_array(metals)
        self.phi = _convert_array(phi)
        self.size = size
        self.c_data = gas_data.struct.from_external(self)
        return self

class dark_data():
    class struct(ctypes.Structure):
        _fields_ = [
            ('mass', _array_1d_float32),
            ('pos' , _array_2d_float32),
            ('vel' , _array_2d_float32),
            ('soft', _array_1d_float32),
            ('phi' , _array_1d_float32),
            ('size', ctypes.c_size_t)
        ]
    
        def __init__(self):
            super().__init__()
    
        @classmethod
        def from_external(cls, other):
            self = cls()
            self.mass = other.mass.ctypes.data_as(_array_1d_float32)
            self.pos = other.pos.ctypes.data_as(_array_2d_float32)
            self.vel = other.vel.ctypes.data_as(_array_2d_float32)
            self.phi = other.phi.ctypes.data_as(_array_1d_float32)
            self.soft = other.soft.ctypes.data_as(_array_1d_float32)
            self.size = other.size
            return self

    def __init__(self):
        self.size = 0
        self.c_data = None
    
    def __str__(self):
        if self.c_data is not None:
            return _pretty_print(self, [k[0] for k in self.c_data._fields_])
    
    @classmethod
    def from_size(cls, size):
        self = cls()
        self.mass = _make_array(size)
        self.pos = _make_array(size, ndims=2)
        self.vel = _make_array(size, ndims=2)
        self.phi = _make_array(size)
        self.soft = _make_array(size)
        self.size = size
        self.c_data = dark_data.struct.from_external(self)
        return self
    
    @classmethod
    def from_external(cls, mass, pos, vel, soft, phi, size):
        self = cls()
        self.mass = _convert_array(mass)
        self.pos = _convert_array(pos)
        self.vel = _convert_array(vel)
        self.phi = _convert_array(phi)
        
        if np.isscalar(soft):
            self.soft = _make_array(size, zero=True)
            self.soft += soft
        else:
            self.soft = _convert_array(soft)
        
        self.size = size
        self.c_data = dark_data.struct.from_external(self)
        return self

class star_data():
    class struct(ctypes.Structure):
        _fields_ = [
            ('mass'  , _array_1d_float32),
            ('pos'   , _array_2d_float32),
            ('vel'   , _array_2d_float32),
            ('metals', _array_1d_float32),
            ('tform' , _array_1d_float32),
            ('soft'  , _array_1d_float32),
            ('phi'   , _array_1d_float32),
            ('size'  , ctypes.c_size_t)
        ]
        
        def __init__(self):
            super().__init__()

        @classmethod
        def from_external(cls, other):
            self = cls()
            self.mass = other.mass.ctypes.data_as(_array_1d_float32)
            self.pos = other.pos.ctypes.data_as(_array_2d_float32)
            self.vel = other.vel.ctypes.data_as(_array_2d_float32)
            self.metals = other.metals.ctypes.data_as(_array_1d_float32)
            self.tform = other.tform.ctypes.data_as(_array_1d_float32)
            self.phi = other.phi.ctypes.data_as(_array_1d_float32)
            self.soft = other.soft.ctypes.data_as(_array_1d_float32)
            self.size = other.size
            return self

    def __init__(self):
        self.size = 0
        self.c_data = None
    
    def __str__(self):
        if self.c_data is not None:
            return _pretty_print(self, [k[0] for k in self.c_data._fields_])
    
    @classmethod
    def from_size(cls, size):
        self = cls()
        self.mass = _make_array(size)
        self.pos = _make_array(size, ndims=2)
        self.vel = _make_array(size, ndims=2)
        self.metals = _make_array(size)
        self.tform = _make_array(size)
        self.phi = _make_array(size)
        self.soft = _make_array(size)
        self.size = size
        self.c_data = star_data.struct.from_external(self)
        return self

    @classmethod
    def from_external(cls, mass, pos, vel, metals, tform, soft, phi, size):
        self = cls()
        self.mass = _convert_array(mass)
        self.pos = _convert_array(pos)
        self.vel = _convert_array(vel)
        self.metals = _convert_array(metals)
        self.tform = _convert_array(tform)
        self.phi = _convert_array(phi)
        
        if np.isscalar(soft):
            self.soft = _make_array(size, zero=True)
            self.soft += soft
        else:
            self.soft = _convert_array(soft)
        
        self.size = size
        self.c_data = star_data.struct.from_external(self)
        return self

