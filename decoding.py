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

def legacy_sequence2(stream):
    return [legacy_node2(stream) for n in range(integer(stream))]

def struct(stream):
    grammar = stream.grammars[integer(stream)]
    label = string(stream)
    return sequence(stream), label, grammar

def legacy_node(stream):
    tag = stream.read_ubyte()
    if tag == 0:
        return stream.transform(common.SYMBOL, "", string(stream))
    ident = binary(stream) if tag & 0x80 else ''
    label = string(stream) if tag & 0x40 else u''
    if len(label) > 0 and tag & 3 == common.LIST:
        return stream.transform(common.STRUCT, ident, (legacy_coders[tag & 3](stream), label, ""))
    return stream.transform(tag & 3, ident, legacy_coders[tag & 3](stream))

def legacy_node2(stream):
    tag = stream.read_ubyte(safe_trunc=True)
    if tag == 255:
        raise StopIteration()
    ident = binary(stream) if tag & 0x80 else ''
    label = string(stream) if tag & 0x40 else u''
    if tag & 3 == common.SYMBOL:
        return stream.transform(tag & 3, ident, label)
    if len(label) > 0 and tag & 3 == common.LIST:
        return stream.transform(common.STRUCT, ident, (legacy_coders2[tag & 3](stream), label, ""))
    return stream.transform(tag & 3, ident, legacy_coders2[tag & 3](stream))

def node(stream):
    tag = stream.read_ubyte(safe_trunc=True)
    if tag == 255:
        raise StopIteration()
    if tag == common.GRAMMAR:
        stream.grammars[len(stream.grammars)] = string(stream)
        return node(stream)
    ident = binary(stream) if tag & 0x80 else ''
    return stream.transform(tag & 15, ident, coders[tag & 15](stream))

def file(stream):
    legacy_mode = header(stream)
    if legacy_mode == 1:
        for subj in legacy_sequence(stream):
            yield subj
        footer(stream)
    elif legacy_mode == 2:
        try:
            while True:
                yield legacy_node2(stream)
        except StopIteration:
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
        return 1
    if magic == common.legacy_magic2:
        return 2
    assert common.magic == magic, "file header mismatch"
    return 0

def footer(stream):
    crc = stream.crc & 0xFFFFFFFF
    assert crc == stream.read_uint(), "crc mismatch"

coders = {
    common.SYMBOL: string,
    common.STRING: string,
    common.BINARY: binary,
    common.LIST:   sequence,
    common.STRUCT: struct,
}

legacy_coders = {
    common.STRING: string,
    common.BINARY: binary,
    common.LIST:   legacy_sequence,
}

legacy_coders2 = {
    common.STRING: string,
    common.BINARY: binary,
    common.LIST:   legacy_sequence2,
}

if __name__ == '__main__':
    import sys
    from stream import ReadStream
    stream = ReadStream(sys.stdin, lambda tag, ident, contents: (tag, ident, contents))
    for subj in file(stream):
        print subj
