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

def struct(stream, (contents, label, grammar)):
    integer(stream, stream.grammars[grammar])
    string(stream, label)
    sequence(stream, contents)

def node(stream, node):
    tag, ident, contents = stream.transform(node)
    tag |= 0x80 * (len(ident) > 0)
    if tag & 15 == common.STRUCT and contents[2] not in stream.grammars:
        stream.write_ubyte(common.GRAMMAR)
        string(stream, contents[2])
        stream.grammars[contents[2]] = len(stream.grammars)
    stream.write_ubyte(tag)
    if len(ident) > 0:
        binary(stream, ident)
    coders[tag & 15](stream, contents)

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
    common.SYMBOL: string,
    common.STRING: string,
    common.BINARY: binary,
    common.LIST:   sequence,
    common.STRUCT: struct,
}

if __name__ == '__main__':
    import sys
    from stream import WriteStream
    from common import Node
    stream = WriteStream(sys.stdout, lambda x: x)
    file(stream, [
        (common.SYMBOL, "1", u"a"),
        (common.STRING, "2", u"lol"),
        (common.LIST,   "3", [
        ]),
        (common.STRUCT, "4", ([
        ], "foo", "bar")),
    ])
