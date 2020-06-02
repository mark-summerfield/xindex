#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

from Const import STRIP_AT_RX


class _Base:

    def __repr__(self):
        items = []
        for key, value in sorted(vars(self).items()):
            items.append("{}={!r}".format(key, value))
        return "{}({})".format(self.__class__.__name__, ", ".join(items))


class Start(_Base):

    def __init__(self, title=None, note=None):
        self.title = title
        self.note = note


class Section(_Base):

    def __init__(self, line=""):
        self.line = line


class End(_Base):
    pass


class Entry(_Base):

    def __init__(self, indent, eid, term, pages, sortas, xrefs=None,
                 childcount=None):
        self.indent = indent
        self.eid = eid
        self.term = term
        self.pages = (STRIP_AT_RX.sub("", pages) if pages is not None else
                      pages)
        self.sortas = sortas
        self.xrefs = xrefs
        self.childcount = childcount


    @property
    def istoplevel(self):
        return self.indent == 0


    @property
    def haschildren(self):
        return bool(self.childcount)


class _XRef(_Base):

    def __init__(self, toterm, totermparent):
        self.toterm = toterm
        self.totermparent = totermparent


class See(_XRef):
    pass


class SeeAlso(_XRef):
    pass


class SeeGeneric(_XRef):
    pass


class SeeAlsoGeneric(_XRef):
    pass
