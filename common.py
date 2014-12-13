"""
    'magic' imitates the PNG identification string.
    Additionally it holds the version number. Newer
    versions will be incompatible by default.

    It's this way because the internal model of
    the format was settled down when I designed it.
    Newer versions would introduce changes to the
    encoding of the same data, rather than extend
    the possible forms of the data.

    Each function with same name in 'decoding'
    decodes what 'encoding' encodes. This kind of
    functional composition and isomorphism is in
    itself very compact and readable description of
    the file format.

    This format has been meant to extend text
    representation with a structure. It has been
    meant for pleasant and layered structured
    programming.

    Smarter might notice that symbols are redundant
    and could be represented by strings. They are
    there to make the format uniform while
    eliminating hard to represent forms, such as
    list as labels or labelled symbols.

    Symbols have a different encoding due to their
    atomicity. They are the only construct capable
    of being promoted as a label for an another.
    Besides they always appear within a list, so
    you can access them by index, or by symbol if
    they're unique.

    This is a stream format. Additionally it is
    meant to become a data-interchange format. It
    was designed after json, but inspired by lisp
    and unix.

    As a NIH counterargument, I considered all JSON,
    CBOR and BSON before settling to design my own
    format. JSON was not compatible with my
    use case. CBOR sets too permissive tone for
    "extensions" of the format. There's no point
    in data-interchange format that cannot be
    parsed otherwise than being corrupted. BSON's
    byte-length fields sacrifise streamability and
    writability to favor quicker read, But those
    in need of random-access would be better off
    using a database.
"""
magic = "\211t+\r\n\032\n\000"
SYMBOL = 0
STRING = 1
BINARY = 2
LIST = 3

class Node(object):
    def __init__(self, ident, label, contents):
        self.contents = contents
        self.ident = ident
        self.label = label

    def __getitem__(self, index):
        return self.contents[index]
    
    def __len__(self):
        return len(self.contents)

    def __repr__(self):
        if len(self.ident) > 0:
            label = "{0.label}#{0.ident}".format(self)
        else:
            label = self.label
        return "({}){!r}".format(label, self.contents)

def default_transform_enc(node):
    if isinstance(node, (str, unicode)):
        return node
    if isinstance(node, Node):
        return (node.ident, node.label, node.contents)

def default_transform_dec(obj):
    if isinstance(obj, tuple):
        return Node(*obj)
    return obj
