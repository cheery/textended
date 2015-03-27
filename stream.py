"""
    These objects calculate crc32 checksums.
    Additionally they provide convenience
    functions for binary processing.
"""
from binascii import crc32

class ReadStream(object):
    def __init__(self, fd, transform):
        self.fd = fd
        self.crc = 0
        self.transform = transform
        self.grammars = {}

    def read(self, count, safe_trunc=False):
        data = self.fd.read(count)
        if len(data) != count:
            raise FileTruncated(safe_trunc)
        self.crc = crc32(data, self.crc)
        return data

    def read_ubyte(self, safe_trunc=False):
        return ord(self.read(1, safe_trunc))

    def read_uint(self):
        return (self.read_ubyte() << 0 |
                self.read_ubyte() << 8 |
                self.read_ubyte() << 16 |
                self.read_ubyte() << 24)

class WriteStream(object):
    def __init__(self, fd, transform):
        self.fd = fd
        self.crc = 0
        self.transform = transform
        self.grammars = {}

    def write(self, data):
        self.crc = crc32(data, self.crc)
        self.fd.write(data)

    def write_ubyte(self, ubyte):
        return self.write(chr(ubyte))

    def write_uint(self, uint):
        self.write_ubyte(uint >> 0  & 0xFF)
        self.write_ubyte(uint >> 8  & 0xFF)
        self.write_ubyte(uint >> 16 & 0xFF)
        self.write_ubyte(uint >> 24 & 0xFF)

class FileTruncated(Exception):
    "'safe', as in the file was truncated from a fold and not from middle of record."
    def __init__(self, safe):
        self.safe = safe

    def __str__(self):
        return "safe={0.safe}".format(self)
