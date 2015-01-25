import common

def integer(stream):
    "http://en.wikipedia.org/wiki/Variable-length_quantity"
    output = 0
    ubyte = stream.read_ubyte()
    while ubyte & 0x80:
        output |= ubyte & 0x7F
        output <<= 7
        ubyte = stream.read_ubyte()
    output |= ubyte
    return output

def binary(stream):
    return stream.read(integer(stream))

def string(stream):
    return binary(stream).decode('utf-8')

def sequence(stream):
    return [node(stream) for n in range(integer(stream))]

def nothing(stream):
    pass

def node(stream):
    tag = stream.read_ubyte(safe_trunc=True)
    if tag == 255:
        raise StopIteration()
    ident = binary(stream) if tag & 0x80 else ''
    label = string(stream) if tag & 0x40 else u''
    return stream.transform(label, coders[tag & 3](stream), ident)

def file(stream):
    header(stream)
    try:
        while True:
            yield node(stream)
    except StopIteration:
        footer(stream)

def header(stream):
    assert common.magic == stream.read(len(common.magic)), "file header mismatch"

def footer(stream):
    crc = stream.crc & 0xFFFFFFFF
    assert crc == stream.read_uint(), "crc mismatch"

coders = {
    common.SYMBOL: nothing,
    common.STRING: string,
    common.BINARY: binary,
    common.LIST:   sequence,
}

if __name__ == '__main__':
    import sys
    from stream import ReadStream
    stream = ReadStream(sys.stdin, common.default_transform_dec)
    for subj in file(stream):
        print subj
