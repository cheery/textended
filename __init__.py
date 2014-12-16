import common
import stream
import decoding
import encoding

def load(fd, transform=common.default_transform_dec):
    rd = stream.ReadStream(fd, transform)
    return decoding.file(rd)

def dump(contents, fd, transform=common.default_transform_enc):
    wr = stream.WriteStream(fd, transform)
    encoding.file(wr, contents)
