#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

import Lib
import Sql
from ._Command import ( # noqa (for importers)
    AddGroup, RenameGroup, DeleteGroup, LinkGroup, UnlinkGroup,
    AddToGroup, RecreateGrouped, RemoveFromGroup)
from Const import Query, ROOT, XrefKind


def eids_for_command(command):
    gid = getattr(command, "gid", None)
    if gid is not None:
        return None, None, gid
    eid1 = getattr(command, "eid", None)
    if eid1 is None:
        eid1 = getattr(command, "from_eid", None)
        if eid1 is None:
            eid1 = getattr(command, "eid1", None)
            if eid1 is None:
                entry = getattr(command, "entry", None)
                if entry is not None:
                    eid1 = entry.eid
    eid2 = getattr(command, "eid", None)
    if eid2 is None:
        eid2 = getattr(command, "to_eid", None)
        if eid2 is None:
            eid2 = getattr(command, "eid2", None)
    return eid1, eid2, None


class AddEntry(Lib.Command.Command):

    def __init__(self, saf, sortas, term, pages=None, notes=None,
                 peid=ROOT, *, name="add"):
        super().__init__()
        self.eid = None
        self.saf = saf
        self.sortas = sortas
        self.term = term
        self.pages = pages
        self.notes = notes
        self.peid = peid
        sub = "sub" if self.peid != ROOT else ""
        self.description = "{} {}entry “{}”".format(name, sub,
                                                    Lib.elide(term))


    def do(self):
        params = dict(saf=self.saf, sortas=self.sortas, term=self.term,
                      pages=self.pages, notes=self.notes, peid=self.peid)
        if self.eid is None:
            sql = Sql.INSERT_ENTRY
        else:
            params["eid"] = self.eid # redo
            sql = Sql.REINSERT_ENTRY
        return Query(sql, params)


    def undo(self):
        return Query(Sql.UNINSERT_ENTRY, dict(eid=self.eid))


class SyncPages(Lib.Command.Command):

    def __init__(self, eid, term, oldPages, pages):
        super().__init__()
        self.eid = eid
        self.oldPages = oldPages
        self.pages = pages
        self.description = "update pages for “{}”".format(Lib.elide(term))


    def do(self):
        return Query(Sql.SYNC_PAGES, dict(eid=self.eid, pages=self.pages))


    def undo(self):
        return Query(Sql.SYNC_PAGES, dict(eid=self.eid,
                                          pages=self.oldPages))


class EditEntry(AddEntry):

    def __init__(self, entry, saf, sortas, term, pages, notes, name="edit"):
        super().__init__(saf, sortas, term, pages, notes, entry.peid,
                         name=name)
        self.entry = entry


    def do(self):
        return Query(Sql.UPDATE_ENTRY, dict(eid=self.entry.eid,
                     saf=self.saf, sortas=self.sortas, term=self.term,
                     pages=self.pages, notes=self.notes))


    def undo(self):
        return Query(Sql.UPDATE_ENTRY, dict(eid=self.entry.eid,
                     saf=self.entry.saf, sortas=self.entry.sortas,
                     term=self.entry.term, pages=self.entry.pages,
                     notes=self.entry.notes))


# Must only be created in the context of a macro and only done if the
# entry has no subentries or xrefs or generic_xrefs
class DeleteEntry(AddEntry):

    def __init__(self, eid, saf, sortas, term, pages, notes, peid):
        super().__init__(saf, sortas, term, pages, notes, peid,
                         name="delete")
        self.eid = eid


    def do(self):
        return Query(Sql.DELETE_ENTRY, dict(eid=self.eid))


    def undo(self):
        params = dict(eid=self.eid, saf=self.saf, sortas=self.sortas,
                      term=self.term, pages=self.pages, notes=self.notes,
                      peid=self.peid)
        return Query(Sql.UNDELETE_ENTRY, params)


class CopyEntry(AddEntry):

    def __init__(self, saf, sortas, term, pages, notes, peid):
        super().__init__(saf, sortas, term, pages, notes, peid, name="copy")


class RecreateEntry(AddEntry):

    def __init__(self, saf, sortas, term, pages, notes, peid):
        super().__init__(saf, sortas, term, pages, notes, peid,
                         name="recreate")


class ReparentEntry(Lib.Command.Command):

    def __init__(self, term, eid, old_peid, new_peid, *, name="reparent"):
        super().__init__()
        self.term = term
        self.eid = eid
        self.old_peid = old_peid
        self.new_peid = new_peid
        sub = "sub" if old_peid != ROOT else ""
        self.description = "{} {}entry “{}”".format(name, sub,
                                                    Lib.elide(term))


    def do(self):
        params = dict(eid=self.eid, peid=self.new_peid)
        return Query(Sql.REPARENT_ENTRY, params)


    def undo(self):
        params = dict(eid=self.eid, peid=self.old_peid)
        return Query(Sql.REPARENT_ENTRY, params)


class MoveToTop(ReparentEntry):

    def __init__(self, term, eid, old_peid, new_peid):
        super().__init__(term, eid, old_peid, new_peid,
                         name="move to be main")


class MoveUnder(ReparentEntry):

    def __init__(self, term, eid, old_peid, new_peid, name):
        super().__init__(term, eid, old_peid, new_peid, name=name)


class AddXRef(Lib.Command.Command):

    def __init__(self, from_term, from_eid, to_term, to_eid, kind, *,
                 name="add"):
        super().__init__()
        self.from_term = from_term
        self.eid = self.from_eid = from_eid
        self.to_term = to_term
        self.to_eid = to_eid
        self.kind = kind
        self.description = "{} cross-reference from “{}” to {} “{}”".format(
            name, Lib.elide(from_term),
            "see" if kind is XrefKind.SEE else "see also",
            Lib.elide(to_term))


    def do(self):
        return Query(Sql.INSERT_XREF, dict(from_eid=self.from_eid,
                     to_eid=self.to_eid, kind=self.kind))


    def undo(self):
        return Query(Sql.DELETE_XREF, dict(from_eid=self.from_eid,
                     to_eid=self.to_eid))


class ChangeXRef(AddXRef):

    def __init__(self, from_term, from_eid, to_term, to_eid, kind):
        super().__init__(from_term, from_eid, to_term, to_eid, kind)
        oldKind = "see also" if kind is XrefKind.SEE else "see"
        newKind = "see also" if kind is XrefKind.SEE_ALSO else "see"
        self.description = ("change cross-reference from “{}” {} to {} “{}”"
                            .format(Lib.elide(from_term), oldKind, newKind,
                                    Lib.elide(to_term)))


    def undo(self):
        kind = (XrefKind.SEE if self.kind is XrefKind.SEE_ALSO else
                XrefKind.SEE_ALSO)
        return Query(Sql.INSERT_XREF, dict(from_eid=self.from_eid,
                     to_eid=self.to_eid, kind=kind))


class DeleteXRef(AddXRef):

    def __init__(self, from_term, from_eid, to_term, to_eid, kind):
        super().__init__(from_term, from_eid, to_term, to_eid, kind,
                         name="delete")


    def do(self):
        return Query(Sql.DELETE_XREF, dict(from_eid=self.from_eid,
                     to_eid=self.to_eid))


    def undo(self):
        return Query(Sql.INSERT_XREF, dict(from_eid=self.from_eid,
                     to_eid=self.to_eid, kind=self.kind))


class RecreateXRef(AddXRef):

    def __init__(self, from_term, from_eid, to_term, to_eid, kind):
        super().__init__(from_term, from_eid, to_term, to_eid, kind,
                         name="recreate")


class AddGenericXRef(Lib.Command.Command):

    def __init__(self, from_term, from_eid, term, kind, *, name="add"):
        super().__init__()
        self.from_term = from_term
        self.eid = from_eid
        self.term = term
        self.kind = kind
        self.description = (
            "{} generic {} cross-reference from “{}” to “{}”".format(
                name, "see" if kind is XrefKind.SEE_GENERIC else
                "see also", Lib.elide(from_term), Lib.elide(term)))


    def do(self):
        return Query(Sql.INSERT_GENERIC_XREF, dict(from_eid=self.eid,
                     term=self.term, kind=self.kind))


    def undo(self):
        return Query(Sql.DELETE_GENERIC_XREF, dict(from_eid=self.eid,
                     term=self.term, kind=self.kind))


class ChangeGenericXRef(AddGenericXRef):

    def __init__(self, from_term, from_eid, term, kind):
        super().__init__(from_term, from_eid, term, kind)
        oldKind = "see also" if kind is XrefKind.SEE_GENERIC else "see"
        newKind = "see also" if kind is XrefKind.SEE_ALSO_GENERIC else "see"
        self.description = (
            "change generic cross-reference from “{}” {} to {} “{}”".format(
                Lib.elide(from_term), oldKind, newKind, Lib.elide(term)))


    def undo(self):
        kind = (XrefKind.SEE_GENERIC if self.kind is
                XrefKind.SEE_ALSO_GENERIC else
                XrefKind.SEE_ALSO_GENERIC)
        return Query(Sql.INSERT_GENERIC_XREF, dict(from_eid=self.eid,
                     term=self.term, kind=kind))


class DeleteGenericXRef(AddGenericXRef):

    def __init__(self, from_term, from_eid, term, kind):
        super().__init__(from_term, from_eid, term, kind, name="delete")


    def do(self):
        return Query(Sql.DELETE_GENERIC_XREF, dict(from_eid=self.eid,
                     term=self.term, kind=self.kind))


    def undo(self):
        return Query(Sql.INSERT_GENERIC_XREF, dict(from_eid=self.eid,
                     term=self.term, kind=self.kind))


class RecreateGenericXRef(AddGenericXRef):

    def __init__(self, from_term, from_eid, term, kind):
        super().__init__(from_term, from_eid, term, kind, name="recreate")


class SwapTerms(Lib.Command.Command):

    def __init__(self, eid1, term1, sortas1, saf1, eid2, term2,
                 sortas2, saf2):
        super().__init__()
        self.eid1 = eid1
        self.term1 = term1
        self.sortas1 = sortas1
        self.saf1 = saf1
        self.eid2 = eid2
        self.term2 = term2
        self.sortas2 = sortas2
        self.saf2 = saf2
        self.description = "swap term “{}” with “{}”".format(
            Lib.elide(term1), Lib.elide(term2))


    def do(self):
        return Query(Sql.SWAP_TERMS, dict(
                     eid1=self.eid1, term1=self.term1,
                     sortas1=self.sortas1, saf1=self.saf1, eid2=self.eid2,
                     term2=self.term2, sortas2=self.sortas2,
                     saf2=self.saf2))


    def undo(self):
        return Query(Sql.SWAP_TERMS, dict(
                     eid1=self.eid2, term1=self.term1,
                     sortas1=self.sortas1, saf1=self.saf1, eid2=self.eid1,
                     term2=self.term2, sortas2=self.sortas2,
                     saf2=self.saf2))


class AddBookmark(Lib.Command.Command):

    def __init__(self, eid, term):
        super().__init__()
        self.eid = eid
        self.term = term
        self.description = "add bookmark to “{}”".format(term)


    def do(self):
        return Query(Sql.ADD_BOOKMARK, dict(eid=self.eid))


    def undo(self):
        return Query(Sql.REMOVE_BOOKMARK, dict(eid=self.eid))


class RemoveBookmark(Lib.Command.Command):

    def __init__(self, eid, term):
        super().__init__()
        self.eid = eid
        self.term = term
        self.description = "remove bookmark to “{}”".format(term)


    def do(self):
        return Query(Sql.REMOVE_BOOKMARK, dict(eid=self.eid))


    def undo(self):
        return Query(Sql.ADD_BOOKMARK, dict(eid=self.eid))
