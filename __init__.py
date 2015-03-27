import common
import stream
import decoding
import encoding

def load(fd, transform=(lambda tag, ident, contents: (tag, ident, contents))):
    rd = stream.ReadStream(fd, transform)
    return decoding.file(rd)

def dump(contents, fd, transform=(lambda x: x)):
    wr = stream.WriteStream(fd, transform)
    encoding.file(wr, contents)
