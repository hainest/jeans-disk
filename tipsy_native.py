import ctypes
import tipsy_c
import numpy.ctypeslib as npct

class File():
    """A read-only Tipsy native file."""
    def __init__(self, filename):
        self.lib = _load_tipsy()

        # fopen in tipsy_py_init_native fails without this here
        print()
        cfname = ctypes.c_char_p(bytes(filename, 'utf-8'))
        self.lib.tipsy_py_init_reader_native(cfname)
        
        self.hdr = tipsy_c.header()
        self.lib.tipsy_py_read_header_native(ctypes.byref(self.hdr.c_data))
        
        self.dark_particles = None
        self.star_particles = None
        self.gas_particles = None

    def close(self):
        self.lib.tipsy_py_destroy_native()

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        return False  # always re-raise exceptions

    @property
    def header(self):
        return self.hdr

    @property
    def gas(self):
        if self.hdr.ngas == 0:
            return None
        
        if self.gas_particles is None:
            self.gas_particles = tipsy_c.gas_data.from_size(self.hdr.ngas)
            self.lib.tipsy_py_read_gas_native(ctypes.byref(self.hdr.c_data),
                                              ctypes.byref(self.gas_particles.c_data))
        return self.gas_particles

    @property
    def darkmatter(self):
        if self.hdr.ndark == 0:
            return None

        if self.dark_particles is None:
            self.dark_particles = tipsy_c.dark_data.from_size(self.hdr.ndark)
            self.lib.tipsy_py_read_dark_native(ctypes.byref(self.hdr.c_data),
                                            ctypes.byref(self.dark_particles.c_data))
        return self.dark_particles

    @property
    def stars(self):
        if self.hdr.nstar == 0:
            return None
        
        if self.star_particles is None:
            self.star_particles = tipsy_c.star_data.from_size(self.hdr.nstar)
            self.lib.tipsy_py_read_star_native(ctypes.byref(self.hdr.c_data),
                                            ctypes.byref(self.star_particles.c_data))
        return self.star_particles
    
class streaming_writer():
    """A write-only Tipsy native file."""
    def __init__(self, filename, mode):
        self.lib = _load_tipsy()

        # fopen in tipsy_py_init_native fails without this here
        print()
        cfname = ctypes.c_char_p(bytes(filename, 'utf-8'))
        cmode = ctypes.c_char_p(bytes(mode, 'utf-8'))
        self.lib.tipsy_py_init_writer_native(cfname, cmode)
    
    def header(self, time, ngas, ndark, nstars):
        tmp = tipsy_c.header.from_external(time, ngas, ndark, nstars)
        self.lib.tipsy_py_write_header_native(ctypes.byref(tmp.c_data))

    def gas(self, mass, pos, vel, rho, temp, hsmooth, metals, phi, size):
        tmp = tipsy_c.gas_data.from_external(mass, pos, vel, rho, temp, hsmooth, metals, phi, size)
        self.lib.tipsy_py_write_gas_native(ctypes.byref(tmp.c_data))

    def darkmatter(self, mass, pos, vel, soft, phi, size):
        tmp = tipsy_c.dark_data.from_external(mass, pos, vel, soft, phi, size)
        self.lib.tipsy_py_write_dark_native(ctypes.byref(tmp.c_data))
    
    def stars(self, mass, pos, vel, metals, tform, soft, phi, size):
        tmp = tipsy_c.star_data.from_external(mass, pos, vel, metals, tform, soft, phi, size)
        self.lib.tipsy_py_write_star_native(ctypes.byref(tmp.c_data))

    def close(self):
        self.lib.tipsy_py_destroy_native()

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        return False  # always re-raise exceptions

def _load_tipsy():
    """Load the tipsy module. For internal use only """
    if _load_tipsy.lib is not None:
        return _load_tipsy.lib
    
    lib = npct.load_library("libtipsy", "")
    
    def decode_err(err):
        if int(err) != 0:
            raise IOError(lib.tipsy_strerror(err).decode('utf-8'))
    
    # Force parameter type-checking and return-value error checking
    lib.tipsy_strerror.restype = ctypes.c_char_p
    lib.tipsy_strerror.argtypes = [ctypes.c_int]
    
    lib.tipsy_py_init_reader_native.restype = decode_err
    lib.tipsy_py_init_reader_native.argtypes = [ctypes.c_char_p]
    
    lib.tipsy_py_init_writer_native.restype = decode_err
    lib.tipsy_py_init_writer_native.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
    
    lib.tipsy_py_destroy_native.restype = None
    lib.tipsy_py_destroy_native.argtypes = []
    
    lib.tipsy_py_read_header_native.restype = decode_err
    lib.tipsy_py_read_header_native.argtypes = [ctypes.POINTER(tipsy_c.header.struct)]

    lib.tipsy_py_read_gas_native.restype = decode_err
    lib.tipsy_py_read_gas_native.argtypes = [ctypes.POINTER(tipsy_c.header.struct),
                                             ctypes.POINTER(tipsy_c.gas_data.struct)]

    lib.tipsy_py_read_dark_native.restype = decode_err
    lib.tipsy_py_read_dark_native.argtypes = [ctypes.POINTER(tipsy_c.header.struct),
                                              ctypes.POINTER(tipsy_c.dark_data.struct)]
             
    lib.tipsy_py_read_star_native.restype = decode_err
    lib.tipsy_py_read_star_native.argtypes = [ctypes.POINTER(tipsy_c.header.struct),
                                              ctypes.POINTER(tipsy_c.star_data.struct)]

    lib.tipsy_py_write_header_native.restype = decode_err
    lib.tipsy_py_write_header_native.argtypes = [ctypes.POINTER(tipsy_c.header.struct)]

    lib.tipsy_py_write_gas_native.restype = decode_err
    lib.tipsy_py_write_gas_native.argtypes = [ctypes.POINTER(tipsy_c.gas_data.struct)]

    lib.tipsy_py_write_dark_native.restype = decode_err
    lib.tipsy_py_write_dark_native.argtypes = [ctypes.POINTER(tipsy_c.dark_data.struct)]
    
    lib.tipsy_py_write_star_native.restype = decode_err
    lib.tipsy_py_write_star_native.argtypes = [ctypes.POINTER(tipsy_c.star_data.struct)]
     
    _load_tipsy.lib = lib
    return lib
_load_tipsy.lib = None

