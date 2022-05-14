"""Models used for packing and unpacking REST API payloads."""


class GeneSequence:
    def __init__(self, chrom=None, pos=None, id_=None, ref=None, alt=None, format_=None):
        self.chrom = chrom
        self.pos = pos
        self.id = id_
        self.ref = ref
        self.alt = alt
        self.format = format_
