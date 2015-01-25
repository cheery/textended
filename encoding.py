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

def nothing(stream, value):
    pass

def node(stream, node):
    label, contents, ident = stream.transform(node)
    tag = 0
    tag |= 0x80 * (len(ident) > 0)
    tag |= 0x40 * (len(label) > 0)
    if contents is None:
        tag |= common.SYMBOL
    elif isinstance(contents, unicode):
        tag |= common.STRING
    elif isinstance(contents, str):
        tag |= common.BINARY
    else:
        tag |= common.LIST
    stream.write_ubyte(tag)
    if len(ident) > 0:
        binary(stream, ident)
    if len(label) > 0:
        string(stream, label)
    coders[tag & 3](stream, contents)

def file(stream, contents):
    header(stream)
    for subj in contents:
        node(stream, subj)
    footer(stream)

def header(stream):
    stream.write(common.magic)

def footer(stream):
    stream.write_ubyte(255)
    stream.write_uint(stream.crc)

coders = {
    common.SYMBOL: nothing,
    common.STRING: string,
    common.BINARY: binary,
    common.LIST:   sequence,
}

if __name__ == '__main__':
    import sys
    from stream import WriteStream
    from common import Node
    stream = WriteStream(sys.stdout, common.default_transform_enc)
    file(stream, [
        Node(u"a"),
        Node(u'', "b", '#ref'),
        u"cdefg",
        Node(u'call', []),
        [],
    ])
