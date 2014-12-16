import common

def integer(stream, value):
    "http://en.wikipedia.org/wiki/Variable-length_quantity"
    output = []
    output.append(value & 0x7F)
    while value > 0x7F:
        value >>= 7
        output.append(0x80 | value & 0x7F)
    stream.write(''.join(map(chr, reversed(output))))

def binary(stream, value):
    integer(stream, len(value))
    stream.write(value)

def string(stream, value):
    binary(stream, value.encode('utf-8'))

def sequence(stream, nodes):
    integer(stream, len(nodes))
    for item in nodes:
        node(stream, item)

def node(stream, node):
    tag = 0
    node = stream.transform(node)
    if isinstance(node, (str, unicode)):
        stream.write_ubyte(tag | common.SYMBOL)
        return string(stream, node)
    ident, label, value = node
    tag |= 0x80 * (len(ident) > 0)
    tag |= 0x40 * (len(label) > 0)
    if isinstance(value, unicode):
        tag |= common.STRING
    elif isinstance(value, str):
        tag |= common.BINARY
    else:
        tag |= common.LIST
    stream.write_ubyte(tag)
    if len(ident) > 0:
        binary(stream, ident)
    if len(label) > 0:
        string(stream, label)
    coders[tag & 3](stream, value)

def file(stream, contents):
    stream.write(common.magic)
    sequence(stream, contents)
    stream.write_uint(stream.crc)

coders = {
    common.STRING: string,
    common.BINARY: binary,
    common.LIST:   sequence,
}

if __name__ == '__main__':
    import sys
    from stream import WriteStream
    stream = WriteStream(sys.stdout, common.default_transform_enc)
    file(stream, [
        "a",
        common.Node('#ref', u'', "b"),
        common.Node('', u'', u"cdefg"),
        common.Node('', u'call', []),
        common.Node('', u'', []),
    ])
