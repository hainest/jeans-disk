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
    def __init__(self, filename, is_xdr=True):
        """A simple wrapper around a write-only Tipsy file."""
        if is_xdr:
            self.file = tipsy_xdr.streaming_writer(filename)
        else:
            self.file = tipsy_native.streaming_writer(filename)

    def close(self):
        self.file.close()

    def __enter__(self):
        return self.file
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.file.close()
        return False  # always re-raise exceptions            
