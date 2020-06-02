#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

import roman

import Lib
import Pages
import Sql
import Xix
from Const import say
from . import Command


class Mixin:


    def swapEntries(self, eid1, eid2):
        entry1 = self.entry(eid1)
        entry2 = self.entry(eid2)
        peid1 = entry1.peid
        peid2 = entry2.peid
        macro = Lib.Command.Macro("swap entry “{}” with “{}”".format(
            Lib.elide(entry1.term), Lib.elide(entry2.term)))
        macro.eid = eid1
        # Move eid1's immediate children under eid2
        for ceid in list(self.subentries(eid1)):
            if ceid == eid2:
                continue
            entry = self.entry(ceid)
            command = Command.MoveUnder(
                entry.term, entry.eid, entry.peid, eid2,
                "move under “{}”".format(entry2.term))
            macro.append(command)
        # Move eid2's immediate children under eid1
        for ceid in list(self.subentries(eid2)):
            if ceid == eid1:
                continue
            entry = self.entry(ceid)
            command = Command.MoveUnder(
                entry.term, entry.eid, entry.peid, eid1,
                "move under “{}”".format(entry1.term))
            macro.append(command)
        # Move eid1 under eid2's parent, unless that parent is eid1 in
        # which case move eid1 under eid2
        peid = term = None
        if eid1 == peid2:
            peid = eid2
            term = entry2.term
        else:
            peid = peid2
            term = self.term(peid2)
        command = Command.MoveUnder(
            entry1.term, entry1.eid, entry1.peid, peid,
            "move under “{}”".format(term))
        macro.append(command)
        # Move eid2 under eid1's parent, unless that parent is eid2 in
        # which case move eid2 under eid1
        peid = term = None
        if eid2 == peid1:
            peid = eid1
            term = entry1.term
        else:
            peid = peid1
            term = self.term(peid1)
        command = Command.MoveUnder(
            entry2.term, entry2.eid, entry2.peid, peid,
            "move under “{}”".format(term))
        macro.append(command)
        # Do macro
        self._stack.push(macro) # Store, then do
        description = self._xix.doCommand(macro)
        self.changed.emit(macro.eid, description)


    def swapTerms(self, eid1, eid2):
        entry1 = self.entry(eid1)
        entry2 = self.entry(eid2)
        command = Command.SwapTerms(
            eid1, entry1.term, entry1.sortas, entry1.saf,
            eid2, entry2.term, entry2.sortas, entry2.saf)
        self._stack.push(command) # Store, then do
        description = self._xix.doCommand(command)
        self.changed.emit(eid1, description)


    def mergeIntoParent(self, eid, peid):
        ceid = eid
        child = self.entry(ceid)
        parent = self.entry(peid)
        term = parent.term
        pageRange = Pages.RulesForName[self.pageRangeRules()].function
        pages = Pages.mergedPages(parent.pages, child.pages,
                                  pageRange=pageRange)
        notes = parent.notes or ""
        if child.notes:
            notes += "<p>{}".format(child.notes)
        notes += "<p>Merged from “{}”.".format(child.term)
        macro = Lib.Command.Macro("merge “{}” into parent “{}”".format(
            Lib.elide(child.term), Lib.elide(parent.term)))
        macro.eid = peid
        # Merge the child's term and pages into the parent's term
        command = Command.EditEntry(parent, parent.saf, parent.sortas, term,
                                    pages, notes)
        macro.append(command)
        # Move all the child's xrefs to the parent
        for xref in list(self.all_xrefs(ceid)):
            self.moveXRef(macro, peid, eid, xref)
        # Reparent all the child's immediate children to the parent and
        # delete the child
        self.reparentAndDeleteChild(macro, peid, parent, ceid, child)
        self._stack.push(macro) # Store, then do
        description = self._xix.doCommand(macro)
        self.changed.emit(macro.eid, description)


    def mergeSubentries(self, eid):
        parent = self.entry(eid)
        pages = [parent.pages]
        notes = [parent.notes or ""]
        cterms = []
        macro = Lib.Command.Macro("merge subentries into “{}”".format(
                                  Lib.elide(parent.term)))
        macro.eid = eid
        for ceid in list(self.subentries(eid)):
            child = self.entry(ceid)
            pages.append(child.pages)
            if child.notes:
                notes.append(child.notes)
            cterms.append(child.term)
            # Move all the child's xrefs to the parent
            for xref in list(self.all_xrefs(ceid)):
                self.moveXRef(macro, eid, ceid, xref)
            # Reparent all the child's immediate children to the parent
            # and delete the child
            self.reparentAndDeleteChild(macro, eid, parent, ceid, child)
        pageRange = Pages.RulesForName[self.pageRangeRules()].function
        pages = Pages.mergedPages(*pages, pageRange=pageRange)
        notes = "<p>".join(notes)
        if len(cterms) == 1:
            notes += "<p>Merged “{}”.".format(cterms[0])
        else:
            notes += "<p>Merged " + (", ".join("“{}”".format(cterm)
                                     for cterm in cterms))
        command = Command.EditEntry(parent, parent.saf, parent.sortas,
                                    parent.term, pages, notes)
        macro.append(command)
        self._stack.push(macro) # Store, then do
        description = self._xix.doCommand(macro)
        self.changed.emit(macro.eid, description)


    def copyEmpty(self, copyInfo):
        with Xix.Xix.Xix(copyInfo.newname, copyInfo.username,
                         copyInfo.language, copyInfo.sortasrules,
                         copyInfo.pagerangerules) as xix:
            cursor = xix.db.cursor()
            try:
                cursor.execute("ATTACH ? AS original;", (copyInfo.oldname,))
                if copyInfo.copyconfig:
                    cursor.execute(Sql.COPY_CONFIG)
                if copyInfo.copymarkup:
                    cursor.execute(Sql.COPY_MARKUP)
                if copyInfo.copyspelling:
                    cursor.execute(Sql.COPY_SPELLING)
                if copyInfo.copyignored:
                    cursor.execute(Sql.COPY_IGNORED_FIRSTS)
                if copyInfo.copyautoreplace:
                    cursor.execute(Sql.COPY_AUTO_REPLACE)
                if copyInfo.copygroups:
                    cursor.execute(Sql.COPY_GROUPS)
            finally:
                cursor.execute("DETACH original;")


    def saveGrouped(self, filename, groups):
        with Xix.Xix.Xix(filename, self.username, self.config("Language"),
                         self.sortAsRules(), self.pageRangeRules()) as xix:
            cursor = xix.db.cursor()
            try:
                cursor.execute("ATTACH ? AS original;", (self.filename,))
                cursor.execute(Sql.COPY_CONFIG)
                cursor.execute(Sql.COPY_MARKUP)
                cursor.execute(Sql.COPY_SPELLING)
                cursor.execute(Sql.COPY_IGNORED_FIRSTS)
                cursor.execute(Sql.COPY_AUTO_REPLACE)
                cursor.execute(Sql.COPY_GROUPS)
                cursor.execute(Sql.COPY_GROUPED.format(
                    gids=",".join(str(group) for group in groups)))
            finally:
                cursor.execute("DETACH original;")


    def renumber(self, options, reportProgress):
        description = "renumber "
        if options.romanchange:
            description += "{}\u2013{} {:+}".format(
                roman.toRoman(options.romanfrom),
                roman.toRoman(options.romanto), options.romanchange)
            if options.decimalchange:
                description += "; "
        if options.decimalchange:
            description += "{:,}\u2013{:,} {:+}".format(
                options.decimalfrom, options.decimalto,
                options.decimalchange)
        percents = set()
        total = len(self)
        entries = list(self.allEntriesWithPages())
        if entries:
            macro = Lib.Command.Macro(description)
            for i, entry in enumerate(entries, 1):
                percent = int(min(100, i * 100 // total))
                if percent not in percents: # report every 1% done
                    reportProgress("Renumbering {}%".format(percent))
                    percents.add(percent)
                pages = Pages.renumbered(entry.pages, options)
                command = Command.EditEntry(entry, entry.saf, entry.sortas,
                                            entry.term, pages, entry.notes)
                macro.append(command)
            self._stack.push(macro) # Store, then do
            description = self._xix.doCommand(macro)
            self.changed.emit(command.eid, description)
        else:
            say("No pages in range for renumbering")
