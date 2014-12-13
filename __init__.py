import common
import stream
import decoding
import encoding

def load(fd, transform=common.default_transform_dec):
    stream = stream.ReadStream(fd, transform)
    return decoding.file(stream)

def dump(contents, fd, transform=common.default_transform_enc):
    stream = stream.WriteStream(fd, transform)
    return encoding.file(stream, contents)
