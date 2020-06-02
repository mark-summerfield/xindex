#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

import re

import HtmlReplacer
import Lib
import Pages
from . import Command
from Const import DELETE_IGNORED_FIRSTS_TEMPLATE, XrefKind


class Mixin:


    def _deleteEntry(self, macro, eid):
        for generic_xref in list(self._xix.deletableGenericXRefs(eid)):
            from_term = self.term(generic_xref.from_eid)
            command = Command.DeleteGenericXRef(
                from_term, generic_xref.from_eid, generic_xref.term,
                generic_xref.kind)
            macro.append(command) # Delete generic_xrefs first
        for xref in list(self._xix.deletableXRefs(eid)):
            from_term = self.term(xref.from_eid)
            to_term = self.term(xref.to_eid)
            command = Command.DeleteXRef(from_term, xref.from_eid, to_term,
                                         xref.to_eid, xref.kind)
            macro.append(command) # Delete xrefs second
        entry = self.entry(eid)
        if self.bookmarked(eid):
            command = Command.RemoveBookmark(eid, entry.term)
            macro.append(command) # Delete bookmark
        for gid, name in list(self.groupsForEid(eid)):
            command = Command.RemoveFromGroup(entry.eid, entry.term, gid,
                                              name)
            macro.append(command) # Remove from group
        command = Command.DeleteEntry(
            entry.eid, entry.saf, entry.sortas, entry.term, entry.pages,
            entry.notes, entry.peid)
        macro.append(command) # Delete this entry


    def reparentAndDeleteChild(self, macro, peid, parent, ceid, child):
        # Reparent all the child's immediate children to the parent
        name = "move under “{}”".format(parent.term)
        for eid in list(self.subentries(ceid)):
            entry = self.entry(eid)
            command = Command.MoveUnder(entry.term, entry.eid, entry.peid,
                                        peid, name)
            macro.append(command)
        # Delete the child
        command = Command.DeleteEntry(
            ceid, child.saf, child.sortas, child.term, child.pages,
            child.notes, child.peid)
        macro.append(command)


    def moveXRef(self, macro, new_eid, old_eid, xref):
        # Delete the old xref
        if xref.kind in {XrefKind.SEE, XrefKind.SEE_ALSO}:
            command = Command.DeleteXRef(
                self.term(xref.from_eid), xref.from_eid,
                self.term(xref.to_eid), xref.to_eid, xref.kind)
        else:
            command = Command.DeleteGenericXRef(
                self.term(xref.from_eid), xref.from_eid, xref.term,
                xref.kind)
        macro.append(command)
        # Add the new xref
        command = None
        from_eid = xref.from_eid
        if from_eid == old_eid:
            from_eid = new_eid
        if xref.kind in {XrefKind.SEE, XrefKind.SEE_ALSO}:
            to_eid = xref.to_eid
            if to_eid == old_eid:
                to_eid = new_eid
            if from_eid != to_eid:
                command = Command.AddXRef(
                    self.term(from_eid), from_eid, self.term(to_eid),
                    to_eid, xref.kind)
        else:
            command = Command.AddGenericXRef(
                self.term(from_eid), from_eid, xref.term, xref.kind)
        if command is not None:
            macro.append(command)


    def addGroup(self, name, link=False):
        gid = self.gidForName(name)
        if gid is not None: # Don't add duplicates
            return gid
        command = Command.AddGroup(name, link=link)
        self._stack.push(command) # Store, then do
        description = self._xix.doCommand(command)
        self.group_changed.emit(command.gid, description)
        return command.gid


    def renameGroup(self, gid, name):
        oldname = self.nameForGid(gid)
        if name == oldname or self.gidForName(name) is not None:
            return # Don't allow renaming to an existing name
        command = Command.RenameGroup(gid, name, oldname)
        self._stack.push(command) # Store, then do
        description = self._xix.doCommand(command)
        self.group_changed.emit(gid, description)


    # NOTE: It is the caller's responsibility to ensure that none of
    # this group's entries are in another linked group. See safeToLink().
    def linkGroup(self, gid):
        name = self.nameForGid(gid)
        macro = Lib.Command.Macro("link group “{}”".format(name))
        macro.gid = gid
        command = Command.LinkGroup(gid, name)
        macro.append(command)
        eids = list(self.eidsForGid(gid))
        self._syncPages(macro, eids)
        self._stack.push(macro) # Store, then do
        description = self._xix.doCommand(macro)
        self.group_changed.emit(gid, description)


    def _syncPages(self, macro, eids):
        terms = []
        pages = []
        for eid in eids:
            entry = self.entry(eid)
            terms.append(entry.term)
            pages.append(entry.pages)
        pageRange = Pages.RulesForName[self.pageRangeRules()].function
        newPages = Pages.mergedPages(*pages, pageRange=pageRange)
        for eid, term, pages in zip(eids, terms, pages):
            command = Command.SyncPages(eid, term, pages, newPages)
            macro.append(command)


    def deleteGroup(self, gid, *, targetEid=None):
        name = self.nameForGid(gid)
        macro = Lib.Command.Macro("delete group “{}”".format(name))
        macro.gid = gid
        self._replacePagesWithCrossRef(name, macro, gid, targetEid,
                                       removeFromGroup=True)
        if self.isLinkedGroup(gid):
            command = Command.UnlinkGroup(gid, name)
            macro.append(command)
        command = Command.DeleteGroup(gid, name)
        macro.append(command)
        self._stack.push(macro) # Store, then do
        description = self._xix.doCommand(macro)
        if targetEid is not None:
            self.edited.emit(targetEid, "delete “{}” entry's group".format(
                             Lib.elide(self.term(targetEid))))
        self.group_changed.emit(gid, description)


    def unlinkGroup(self, gid, *, targetEid=None):
        name = self.nameForGid(gid)
        unlinkCommand = Command.UnlinkGroup(gid, name)
        if targetEid is None:
            self._stack.push(unlinkCommand) # Store, then do
            description = self._xix.doCommand(unlinkCommand)
        else:
            macro = Lib.Command.Macro("unlink group “{}”".format(name))
            macro.gid = gid
            self._replacePagesWithCrossRef(name, macro, gid, targetEid)
            macro.append(unlinkCommand)
            self._stack.push(macro) # Store, then do
            description = self._xix.doCommand(macro)
            self.edited.emit(targetEid, "unlink “{}” entry's group".format(
                             Lib.elide(self.term(targetEid))))
        self.group_changed.emit(gid, description)


    def _replacePagesWithCrossRef(self, name, macro, gid, targetEid, *,
                                  removeFromGroup=False):
        for eid in list(self.eidsForGid(gid)):
            entry = self.entry(eid)
            if removeFromGroup:
                command = Command.RemoveFromGroup(eid, entry.term, gid,
                                                  name)
                macro.append(command)
            if targetEid is not None and targetEid != eid:
                command = Command.EditEntry(entry, entry.saf, entry.sortas,
                                            entry.term, "", entry.notes)
                macro.append(command) # Delete pages
                command = Command.AddXRef(
                    entry.term, eid, self.term(targetEid), targetEid,
                    XrefKind.SEE)
                macro.append(command) # Add see cross-reference


    # NOTE: It is the caller's responsibility to ensure that any given
    # eid is added to at most one linked group. (There's no limit to how
    # many unlinked groups an entry can belong to.) See safeToAddToGroup().
    def addToGroup(self, eid, gid):
        name = self.nameForGid(gid)
        entry = self.entry(eid)
        if self.isLinkedGroup(gid):
            macro = Lib.Command.Macro("add to group “{}”".format(name))
            macro.gid = gid
            macro.eid = eid
            command = Command.AddToGroup(eid, entry.term, gid, name)
            macro.append(command)
            eids = [eid] + list(self.eidsForGid(gid))
            self._syncPages(macro, eids)
            self._stack.push(macro) # Store, then do
            description = self._xix.doCommand(macro)
            self.group_changed.emit(gid, description)
            self.edited.emit(eid, description)
            for eid in reversed(eids):
                self.edited.emit(eid, description)
        else:
            command = Command.AddToGroup(eid, entry.term, gid, name)
            self._stack.push(command) # Store, then do
            description = self._xix.doCommand(command)
            self.group_changed.emit(eid, description)
            self.edited.emit(eid, description)


    def removeFromGroup(self, eid, gid):
        term = self.term(eid)
        name = self.nameForGid(gid)
        command = Command.RemoveFromGroup(eid, term, gid, name)
        self._stack.push(command) # Store, then do
        description = self._xix.doCommand(command)
        self.group_changed.emit(eid, description)
        self.edited.emit(eid, description)


    def deleteIgnoredFirstWords(self, term): # term is HTML
        ignore = self.ignoredFirstsWords()
        if ignore:
            return HtmlReplacer.sub(DELETE_IGNORED_FIRSTS_TEMPLATE.format(
                "|".join(re.escape(word) for word in ignore)), "", term)
        return term
    # See also: SortAs/Common.py delete_ignored_firsts()
