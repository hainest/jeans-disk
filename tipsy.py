import tipsy_xdr
import tipsy_native

class File():
    """A simple wrapper around a read-only Tipsy file."""
    def __init__(self, filename, is_xdr=True):
        if is_xdr:
            self.file = tipsy_xdr.File(filename)
        else:
            self.file = tipsy_native.File(filename)

    def close(self):
        self.file.close()

    def __enter__(self):
        return self.file
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.file.close()
        return False  # always re-raise exceptions

class streaming_writer():
    """A simple wrapper around a write-only Tipsy file."""
    def __init__(self, filename, mode='wb', is_xdr=True):
        if not 'b' in mode:
            raise ValueError('Files must be binary')
        if not mode in ['wb', 'r+b']:
            raise ValueError("Mode must be one of 'wb' or 'r+b'")
        
        if is_xdr:
            self.file = tipsy_xdr.streaming_writer(filename, mode)
        else:
            self.file = tipsy_native.streaming_writer(filename, mode)

    def close(self):
        self.file.close()

    def __enter__(self):
        return self.file
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.file.close()
        return False  # always re-raise exceptions            
