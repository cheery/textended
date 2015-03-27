"""
    This stream format has been meant for pleasant
    and layered structured programming. It extends
    text representation with a tree structure.
    Additionally it is able to function as a
    data-interchange format. It has been inspired
    by json, lisp and unix systems.

    A valid file starts with the header, ends with
    0xff and crc-32 field. Between there may be zero
    or more nodes.

    'magic' imitates the PNG identification string.
    Additionally it holds the version number. Newer
    versions will be incompatible by default. Internal
    model of the format was settled down when I
    designed it. Newer versions would introduce changes
    to the encoding of the same data, rather than
    extend the possible forms of the data.

    The node is a triplet, consisting of an identifier
    label and contents. The identifier&label portion
    is considered as a symbol.
    
    Each function with same name in 'decoding' -module
    decodes what 'encoding' encodes. This kind of
    functional composition and isomorphism is in 
    itself very compact and readable description of
    the file format.

    As a NIH counterargument, I considered all JSON,
    CBOR and BSON before settling to design my own
    format.
    
     * JSON was not compatible with my use case.
     * CBOR sets too permissive tone for "extensions"
    of the format. If you do not know the 'schema'
    of the file, you can't parse it at all.
     * BSON's byte-length fields sacrifise streamability
    and writability to favor quicker read.
"""
magic = "\211t+\r\n\032\n\002"
legacy_magic2 = "\211t+\r\n\032\n\001"
legacy_magic = "\211t+\r\n\032\n\000"
SYMBOL = 0
STRING = 1
BINARY = 2
LIST = 3
STRUCT = 4
GRAMMAR = 5
