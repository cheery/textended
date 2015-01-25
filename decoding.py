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

def legacy_sequence(stream):
    return [legacy_node(stream) for n in range(integer(stream))]

def nothing(stream):
    pass

def legacy_node(stream):
    tag = stream.read_ubyte()
    if tag == 0:
        return stream.transform(string(stream), None, '')
    ident = binary(stream) if tag & 0x80 else ''
    label = string(stream) if tag & 0x40 else u''
    return stream.transform(label, legacy_coders[tag & 3](stream), ident)

def node(stream):
    tag = stream.read_ubyte(safe_trunc=True)
    if tag == 255:
        raise StopIteration()
    ident = binary(stream) if tag & 0x80 else ''
    label = string(stream) if tag & 0x40 else u''
    return stream.transform(label, coders[tag & 3](stream), ident)

def file(stream):
    legacy_mode = header(stream)
    if legacy_mode:
        for node in legacy_sequence(stream):
            yield node
        footer(stream)
    else:
        try:
            while True:
                yield node(stream)
        except StopIteration:
            footer(stream)

def header(stream):
    magic = stream.read(len(common.magic))
    if magic == common.legacy_magic:
        return True
    assert common.magic == magic, "file header mismatch"

def footer(stream):
    crc = stream.crc & 0xFFFFFFFF
    assert crc == stream.read_uint(), "crc mismatch"

coders = {
    common.SYMBOL: nothing,
    common.STRING: string,
    common.BINARY: binary,
    common.LIST:   sequence,
}

legacy_coders = {
    common.SYMBOL: nothing,
    common.STRING: string,
    common.BINARY: binary,
    common.LIST:   legacy_sequence,
}

if __name__ == '__main__':
    import sys
    from stream import ReadStream
    stream = ReadStream(sys.stdin, common.default_transform_dec)
    for subj in file(stream):
        print subj
