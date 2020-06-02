#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

import copy

from PySide.QtCore import QObject, Signal

import Lib
import Spell
import SortAs
from Config import Gconf, Gopt
from Const import (
    CountKind, EntryDataKind, FilterKind, ROOT, UNLIMITED, XrefKind)
from . import Command
from . import Xix
from . import Util
from . import _Model
from . import _Model2


class Model(QObject, _Model.Mixin, _Model2.Mixin):

    can_undo = Signal(bool, str)
    can_redo = Signal(bool, str)
    changed = Signal(int, str) # eid, message
    edited = Signal(int, str) # eid, message
    group_changed = Signal(int, str) # gid, message
    loaded = Signal()


    def __init__(self, username=None, parent=None):
        super().__init__(parent)
        self.username = username
        self.filename = None
        self._xix = None
        self._stack = Lib.Command.Stack()
        self._stack.can_undo.connect(self.can_undo)
        self._stack.can_redo.connect(self.can_redo)


    def __bool__(self):
        return self._xix is not None


    def open(self, filename, language, sortAsRules, pageRangeRules):
        self.close()
        self.filename = filename
        self._stack.clear()
        self._xix = Xix.Xix(filename, self.username, language, sortAsRules,
                            pageRangeRules)
        self._updateSpellWords(Spell.add, language.value)
        self.loaded.emit()


    def close(self):
        self.filename = None
        if self._xix is not None:
            self._updateSpellWords(
                Spell.remove, self.config(Gconf.Key.Language).value)
            self._xix.close()
            self._xix = None


    def importIndex(self, inFilename, filename, language, sortAsRules,
                    pageRangeRules):
        self.close()
        self.filename = filename
        self._stack.clear()
        self._xix = Xix.Xix(filename, self.username, language, sortAsRules,
                            pageRangeRules)
        ok = self._importIndex(inFilename)
        self._updateSpellWords(Spell.add, language.value)
        self.loaded.emit()
        return ok


    def _updateSpellWords(self, function, language):
        for word in self._xix.spellWords():
            function(word, language)


    def filteredEntries(self, *, filter=FilterKind.TERMS_MATCHING,
                        match="", offset=0, limit=UNLIMITED,
                        entryData=EntryDataKind.EID):
        for entry in self._xix.filteredEntries(
            filter=filter, match=match, offset=offset, limit=limit,
                entryData=entryData):
            yield entry


    def entries(self, *, offset=0, limit=UNLIMITED,
                entryData=EntryDataKind.INDENT_AND_EID, peid=ROOT):
        for entry in self._xix.entries(offset=offset, limit=limit,
                                       entryData=entryData, peid=peid):
            yield entry


    def addEntry(self, saf, sortas, term, *, pages=None, notes=None,
                 peid=ROOT):
        command = Command.AddEntry(saf, sortas, term, pages, notes, peid)
        self._stack.push(command) # Store, then do
        description = self._xix.doCommand(command)
        self.changed.emit(command.eid, description)
        return Util.Entry(command.eid, saf, sortas, term, pages, notes,
                          peid=peid)


    def editEntry(self, entry, saf, sortas, term, pages=None, notes=None,
                  description=None, name=None):
        gid = self.linkedGroup(entry.eid)
        eids = list(self.eidsForGid(gid)) if gid is not None else []
        command = Command.EditEntry(entry, saf, sortas, term, pages, notes,
                                    name="edit" if name is None else name)
        if not eids or entry.pages == pages:
            # Not linked or same pages
            self._stack.push(command) # Store, then do
            description = self._xix.doCommand(command)
            if entry.sortas != sortas:
                self.changed.emit(entry.eid, description)
            else:
                self.edited.emit(entry.eid, description)
        else: # Linked and different pages
            macro = Lib.Command.Macro("edit entry" if description is None
                                      else description)
            macro.eid = entry.eid
            macro.append(command) # The edit might be more than pages
            for eid in eids:
                if eid != entry.eid:
                    sentry = self.entry(eid)
                    command = Command.SyncPages(eid, sentry.term,
                                                sentry.pages, pages)
                    macro.append(command) # Sync all their pages with these
            self._stack.push(macro) # Store, then do
            description = self._xix.doCommand(macro)
            self.changed.emit(entry.eid, description)
        return Util.Entry(entry.eid, saf, sortas, term, pages, notes,
                          peid=entry.peid)


    def deleteEntry(self, eid, description=None):
        macro = Lib.Command.Macro("delete entry" if description is None
                                  else description)
        macro.eid = eid
        for eid in list(self.deletableEntries(eid)):
            self._deleteEntry(macro, eid)
        self._stack.push(macro) # Store, then do
        description = self._xix.doCommand(macro)
        self.changed.emit(macro.eid, description)


    def copyEntry(self, info):
        info.sanitize()
        if info.link:
            gid = self.linkedGroup(info.eid)
            if gid is None:
                gname = self._xix.uniqueGroupName(self._xix.term(info.eid))
                gid = self.addGroup(gname, link=True)
                self.addToGroup(info.eid, gid)
        newEid = self._copyEntry(info, top=(info.peid == ROOT))
        self.changed.emit(newEid, info.description)
        return newEid


    def _copyEntry(self, info, top=False, copied=None):
        if copied is None:
            copied = {info.eid}
        entry = self._xix.entry(info.eid)
        if top:
            term = self.deleteIgnoredFirstWords(entry.term)
            sortas = self.sortBy(term, entry.saf, False)
        else:
            term = entry.term
            sortas = entry.sortas
        pages = "" if info.withsee else entry.pages
        command = Command.CopyEntry(entry.saf, sortas, term, pages,
                                    entry.notes, info.peid)
        self._stack.push(command) # Store, then do
        self._xix.doCommand(command)
        newEid = command.eid # This is the copy's eid, not the original
        copied.add(newEid)
        if info.withsee:
            command = Command.AddXRef(term, newEid, term, info.eid,
                                      XrefKind.SEE)
            self._stack.push(command) # Store, then do
            self._xix.doCommand(command)
        else:
            subentries = (list(self.subentries(info.eid)) # Original's
                          if info.copysubentries else []) # subentries
            self._maybeCopyGroups(info, entry, newEid)
            self._maybeCopyXrefs(info, term, newEid)
            if info.copysubentries and subentries:
                for eid in subentries:
                    if eid not in copied:
                        subInfo = copy.copy(info)
                        subInfo.eid = eid
                        subInfo.peid = newEid
                        self._copyEntry(subInfo, copied=copied)
        return newEid


    def _maybeCopyGroups(self, info, entry, newEid):
        groups = (list(self._xix.groupsForEid(info.eid))
                  if info.copygroups else []) # Original's groups
        if info.copygroups and groups:
            macro = Lib.Command.Macro("copy groups")
            macro.eid = newEid
            for gid, name in groups:
                command = Command.AddToGroup(newEid, entry.term, gid, name)
                macro.append(command)
            self._stack.push(macro) # Store, then do
            self._xix.doCommand(macro)


    def _maybeCopyXrefs(self, info, term, newEid):
        xrefs = (list(self.all_xrefs(info.eid))
                 if info.copyxrefs else []) # Original's xrefs
        if info.copyxrefs and xrefs:
            macro = Lib.Command.Macro("copy cross-references")
            macro.eid = newEid
            for xref in xrefs:
                if xref.kind in {XrefKind.SEE, XrefKind.SEE_ALSO}:
                    if xref.to_eid in {info.eid, newEid}:
                        continue # No circular cross-references
                    to_term = self._xix.term(xref.to_eid)
                    command = Command.AddXRef(term, newEid, to_term,
                                              xref.to_eid, xref.kind)
                else:
                    command = Command.AddGenericXRef(term, newEid,
                                                     xref.term, xref.kind)
                macro.append(command)
            self._stack.push(macro) # Store, then do
            self._xix.doCommand(macro)


    def recreateEntry(self, oldEid, recreateSubentries):
        xrefs = list(self._xix.deletedXRefs(oldEid))
        generic_xrefs = list(self._xix.deletedGenericXRefs(oldEid))
        gids = list(self._xix.deletedGidsForEid(oldEid))
        entry = self._xix.deletedEntry(oldEid)
        subeids = (list(self._xix.deletedSubentries(oldEid))
                   if recreateSubentries else [])
        self.deleteDeletedEntry(oldEid) # Also deletes deleted_xrefs etc
        # Make subentry of original parent if that still exists, even if
        # it was recreated, (or make or leave as top-level entry).
        peid = self._xix.eidForEid(entry.peid)
        # Can't use a macro because we must first find out the new EID
        # Also, this means the user gets more fine-grained control,
        # i.e., they can undo the xrefs one by one if they want
        command = Command.RecreateEntry(
            entry.saf, entry.sortas, entry.term, entry.pages, entry.notes,
            peid)
        self._stack.push(command) # Store, then do
        description = self._xix.doCommand(command)
        eid = command.eid
        self._xix.setEidForEid(oldEid, eid)
        for xref in xrefs:
            from_eid = eid if xref.from_eid == oldEid else xref.from_eid
            to_eid = eid if xref.to_eid == oldEid else xref.to_eid
            if not self.hasEntry(from_eid) or not self.hasEntry(to_eid):
                continue # We only recreate valid xrefs and using new EID
            from_term = self.term(from_eid)
            to_term = self.term(to_eid)
            command = Command.RecreateXRef(from_term, from_eid, to_term,
                                           to_eid, xref.kind)
            self._stack.push(command) # Store, then do
            description = self._xix.doCommand(command)
        for generic_xref in generic_xrefs:
            from_eid = (eid if generic_xref.from_eid == oldEid else
                        generic_xref.from_eid)
            if not self.hasEntry(from_eid):
                continue # We only recreate valid xrefs and using new EID
            from_term = self.term(from_eid)
            command = Command.RecreateGenericXRef(
                from_term, from_eid, generic_xref.term,
                generic_xref.kind)
            self._stack.push(command) # Store, then do
            description = self._xix.doCommand(command)
        for gid in gids:
            name = self._xix.nameForGid(gid)
            if name is not None and not self._xix.isLinkedGroup(gid):
                # Group still exists and isn't linked (too dangerous)
                command = Command.RecreateGrouped(eid, entry.term, gid,
                                                  name)
                self._stack.push(command) # Store, then do
                description = self._xix.doCommand(command)
        for subeid in subeids:
            self.recreateEntry(subeid, True)
        sub = "sub" if peid != ROOT else ""
        description = "recreated {}entry “{}”".format(sub,
                                                      Lib.elide(entry.term))
        self.changed.emit(eid, description)


    def moveToTop(self, eid):
        entry = self.entry(eid)
        term = self.deleteIgnoredFirstWords(entry.term)
        if term == entry.term:
            command = Command.MoveToTop(term, entry.eid, entry.peid, ROOT)
            self._stack.push(command) # Store, then do
            description = self._xix.doCommand(command)
        else:
            macro = Lib.Command.Macro("move to be main entry")
            macro.eid = entry.eid
            sortas = self.sortBy(term, entry.saf, False)
            command = Command.EditEntry(entry, entry.saf, sortas, term,
                                        entry.pages, entry.notes)
            macro.append(command)
            command = Command.MoveToTop(term, entry.eid, entry.peid, ROOT)
            macro.append(command)
            self._stack.push(macro) # Store, then do
            description = self._xix.doCommand(macro)
        self.changed.emit(entry.eid, description)


    def moveUnder(self, eid, new_peid, name="move"):
        entry = self.entry(eid)
        command = Command.MoveUnder(entry.term, entry.eid, entry.peid,
                                    new_peid, name)
        self._stack.push(command) # Store, then do
        description = self._xix.doCommand(command)
        self.changed.emit(entry.eid, description)


    def addXRef(self, from_eid, to_eid, kind):
        from_term = self.term(from_eid)
        to_term = self.term(to_eid)
        command = Command.AddXRef(from_term, from_eid, to_term, to_eid,
                                  kind)
        self._stack.push(command) # Store, then do
        description = self._xix.doCommand(command)
        self.edited.emit(from_eid, description)


    def changeXRef(self, from_eid, to_eid, kind):
        from_term = self.term(from_eid)
        to_term = self.term(to_eid)
        command = Command.ChangeXRef(from_term, from_eid, to_term, to_eid,
                                     kind)
        self._stack.push(command) # Store, then do
        description = self._xix.doCommand(command)
        self.edited.emit(from_eid, description)


    def deleteXRef(self, from_eid, to_eid, kind):
        from_term = self.term(from_eid)
        to_term = self.term(to_eid)
        command = Command.DeleteXRef(from_term, from_eid, to_term, to_eid,
                                     kind)
        self._stack.push(command) # Store, then do
        description = self._xix.doCommand(command)
        self.edited.emit(from_eid, description)


    def addGenericXRef(self, from_eid, term, kind):
        from_term = self.term(from_eid)
        command = Command.AddGenericXRef(from_term, from_eid, term, kind)
        self._stack.push(command) # Store, then do
        description = self._xix.doCommand(command)
        self.edited.emit(from_eid, description)


    def changeGenericXRef(self, from_eid, term, kind):
        from_term = self.term(from_eid)
        command = Command.ChangeGenericXRef(from_term, from_eid, term, kind)
        self._stack.push(command) # Store, then do
        description = self._xix.doCommand(command)
        self.edited.emit(from_eid, description)


    def deleteGenericXRef(self, from_eid, term, kind):
        from_term = self.term(from_eid)
        command = Command.DeleteGenericXRef(from_term, from_eid, term, kind)
        self._stack.push(command) # Store, then do
        description = self._xix.doCommand(command)
        self.edited.emit(from_eid, description)


    def addBookmark(self, eid):
        term = self.term(eid)
        command = Command.AddBookmark(eid, term)
        self._stack.push(command) # Store, then do
        description = self._xix.doCommand(command)
        self.edited.emit(eid, description)


    def removeBookmark(self, eid):
        term = self.term(eid)
        command = Command.RemoveBookmark(eid, term)
        self._stack.push(command) # Store, then do
        description = self._xix.doCommand(command)
        self.edited.emit(eid, description)


    def redo(self):
        if not self.canRedo:
            return
        command = self._stack.getRedo()
        description = self._xix.doCommand(command)
        eid1, eid2, gid = Command.eids_for_command(command)
        if gid is not None:
            self.group_changed.emit(gid, description)
        if eid2 is not None:
            self.changed.emit(eid2, description)
        if eid1 is not None:
            self.changed.emit(eid1, description)
        return eid1


    def undo(self):
        if not self.canUndo:
            return
        command = self._stack.getUndo()
        description = self._xix.undoCommand(command)
        eid1, eid2, gid = Command.eids_for_command(command)
        if gid is not None:
            self.group_changed.emit(gid, description)
        if eid2 is not None:
            self.changed.emit(eid2, description)
        if eid1 is not None:
            self.changed.emit(eid1, description)
        return eid1


    def sortBy(self, term, saf, isSubentry):
        name = self.sortAsRules()
        sortBy = SortAs.RulesForName[name].function
        ignored = None
        if isSubentry and bool(self.config(Gconf.Key.IgnoreSubFirsts,
                                           Gopt.Default.IgnoreSubFirsts)):
            ignored = self.ignoredFirstsWords()
        pad_digits = self.config(Gconf.Key.PadDigits,
                                 Gopt.Default.PadDigits)
        return sortBy(term, saf, pad_digits=pad_digits, ignored=ignored)


    def sortByCandidates(self, term, isSubentry):
        name = self.sortAsRules()
        ignored = None
        if isSubentry and bool(self.config(Gconf.Key.IgnoreSubFirsts,
                                           Gopt.Default.IgnoreSubFirsts)):
            ignored = self.ignoredFirstsWords()
        pad_digits = self.config(Gconf.Key.PadDigits,
                                 Gopt.Default.PadDigits)
        suggest_spelled = self.config(Gconf.Key.SuggestSpelled,
                                      Gopt.Default.SuggestSpelled)
        return SortAs.candidatesFor(term, name, ignored, pad_digits,
                                    suggest_spelled)


    # Delegates

    def __getattr__(self, name): # Delegates everything except those below
        return getattr(self._xix, name)


    def __len__(self): # __getattr__ can't delegate special methods
        return self.count(CountKind.ENTRIES)


    def backup(self, filename, prefix, reportProgress):
        self._xix.backup(filename, prefix, reportProgress)


    @property
    def isUndoMacro(self):
        return self._stack.isUndoMacro


    @property
    def canUndo(self):
        return self._stack.canUndo


    @property
    def isRedoMacro(self):
        return self._stack.isRedoMacro


    @property
    def canRedo(self):
        return self._stack.canRedo
