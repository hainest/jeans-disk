import numpy as np
import numpy.ctypeslib as npct
import ctypes

array_1d_float = npct.ndpointer(dtype=np.float32, ndim=1, flags='CONTIGUOUS')
array_2d_float = npct.ndpointer(dtype=np.float32, ndim=2, flags='CONTIGUOUS')

def print_struct(s):
    repr = []
    for f in s._fields_:
        a = getattr(s, f[0])
        repr.append('{0:10s}: {1:s}'.format(f[0], str(a.shape) if isinstance(a, np.ndarray) else str(a)))
    return '\n'.join(repr)

class tipsy_header(ctypes.Structure):
    _fields_ = [('time'    , ctypes.c_double),
                ('nbodies' , ctypes.c_int),
                ('ndim'    , ctypes.c_int),
                ('ngas'    , ctypes.c_int),
                ('ndark'   , ctypes.c_int),
                ('nstar'   , ctypes.c_int)
                ]
    
    def __str__(self):
        return print_struct(self)

class tipsy_gas_data(ctypes.Structure):
    _fields_ = [('mass'  , array_1d_float),
               ('pos'    , array_2d_float),
               ('vel'    , array_2d_float),
               ('rho'    , array_1d_float),
               ('temp'   , array_1d_float),
               ('metals' , array_1d_float),
               ('hsmooth', array_1d_float),
               ('phi'    , array_1d_float),
               ('soft'   , ctypes.c_float),
               ('size'   , ctypes.c_size_t)
              ]
    
    def __str__(self):
        return print_struct(self)

class tipsy_dark_data(ctypes.Structure):
    _fields_ = [('mass'   , array_1d_float),
                ('pos'    , array_2d_float),
                ('vel'    , array_2d_float),
                ('phi'    , array_1d_float),
                ('soft'   , ctypes.c_float),
                ('size'   , ctypes.c_size_t)
                ]
    
    def __str__(self):
        return print_struct(self)

class tipsy_star_data(ctypes.Structure):
    _fields_ = [('mass'   , array_1d_float),
                ('pos'    , array_2d_float),
                ('vel'    , array_2d_float),
                ('metals' , array_1d_float),
                ('tform'  , array_1d_float),
                ('phi'    , array_1d_float),
                ('soft'   , ctypes.c_float),
                ('size'   , ctypes.c_size_t)
                ]
    
    def __str__(self):
        return print_struct(self)

class tipsy_blackhole_data(ctypes.Structure):
    _fields_ = [('mass'   , array_1d_float),
                ('pos'    , array_2d_float),
                ('vel'    , array_2d_float),
                ('phi'    , array_1d_float),
                ('soft'   , ctypes.c_float),
                ('size'   , ctypes.c_size_t)
               ]
    
    def __str__(self):
        return print_struct(self)

def load_tipsy():
    """Load the tipsy module. For internal use only """
    
    if load_tipsy.is_loaded:
        return
    
    def decode_err(err):
        if err < 0:
            # Tipsy error
            raise IOError(lib.tipsy_strerror(err).decode('utf-8'))
        
        if err > 0:
            # system error
            raise IOError('{0:s}: {1:s}'.format(
                    lib.tipsy_get_last_system_error().decode('utf-8'),
                    lib.tipsy_strerror(err).decode('utf-8')
                ))
    
    lib = npct.load_library("libtipsy", "")
    
    # Force parameter type-checking and return-value error checking
    lib.tipsy_get_last_system_error.restype = ctypes.c_char_p
    lib.tipsy_get_last_system_error.argtypes = []
    
    lib.tipsy_strerror.restype = ctypes.c_char_p
    lib.tipsy_strerror.argtypes = [ctypes.c_int]
    
    lib.tipsy_open_file.restype = None
    lib.tipsy_open_file.argtypes = [ctypes.c_char_p]
    
    lib.tipsy_close_file.restype = None
    lib.tipsy_close_file.argtypes = []
    
    lib.tipsy_write_header.restype = decode_err
    lib.tipsy_write_header.argtypes = [ctypes.POINTER(tipsy_header)]
    
    lib.tipsy_write_star_particles.restype = decode_err
    lib.tipsy_write_star_particles.argtypes = [ctypes.POINTER(tipsy_star_data)]
    
    lib.tipsy_write_dark_particles.restype = decode_err
    lib.tipsy_write_dark_particles.argtypes = [ctypes.POINTER(tipsy_dark_data)]
    
    lib.tipsy_write_gas_particles.restype = decode_err
    lib.tipsy_write_gas_particles.argtypes = [ctypes.POINTER(tipsy_gas_data)]
  
    lib.tipsy_read_header.restype = decode_err
    lib.tipsy_read_header.argtypes = [ctypes.POINTER(tipsy_header)]
    
    lib.tipsy_read_star_particles.restype = decode_err
    lib.tipsy_read_star_particles.argtypes = [ctypes.POINTER(tipsy_star_data)]
    
    lib.tipsy_read_dark_particles.restype = decode_err
    lib.tipsy_read_dark_particles.argtypes = [ctypes.POINTER(tipsy_dark_data)]
    
    lib.tipsy_read_gas_particles.restype = decode_err
    lib.tipsy_read_gas_particles.argtypes = [ctypes.POINTER(tipsy_gas_data)]
    
    load_tipsy.is_loaded = True
    return lib
load_tipsy.is_loaded = False