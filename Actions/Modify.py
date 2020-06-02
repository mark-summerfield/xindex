#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

from PySide.QtCore import Qt
from PySide.QtGui import QKeySequence

import Lib
import Pages
from Const import ROOT


MERGE_PAGES_TIP = """<p><b>Modify→Merge Pages</b> (F6)</p>
<p>Merge the most recently added or edited pages into the
current entry's pages, and combine any pages that overlap.</p>"""
COPY_PAGES_TIP = """<p><b>Modify→Copy Pages</b> (Shift+F6)</p>
<p>Copy the most recently added or edited pages into the
current entry's pages&mdash;replacing any existing pages.</p>"""


class Actions:

    def __init__(self, window):
        self.window = window
        self.state = self.window.state

        self.swapAcronymAction = Lib.createAction(
            window, ":/swapacronym.svg", "Swap &Acronym",
            self.swapAcronym, QKeySequence(Qt.CTRL + Qt.Key_J), """
<p><b>Modify→Swap Acronym</b> ({})</p>
<p>Swap the current entry's term's acronym.</p>
<p>For example, if the term is
<font color=navy>Return on Investment (ROI)</font>, using this action
will produce
<font color=navy>ROI (Return on Investment)</font>&mdash;or vice versa.
</p>""".format(QKeySequence(QKeySequence(Qt.CTRL + Qt.Key_J)).toString()))

        self.mergePagesAction = Lib.createAction(
            window, ":/mergepages.svg", "Merge &Pages", self.mergePages,
            QKeySequence(Qt.Key_F6), MERGE_PAGES_TIP)
        self.copyPagesAction = Lib.createAction(
            window, ":/copypages.svg", "C&opy Pages", self.copyPages,
            QKeySequence(Qt.SHIFT + Qt.Key_F6), COPY_PAGES_TIP)

        self.combinePagesAction = Lib.createAction(
            window, ":/combinepages.svg", "&Combine Pages",
            self.combinePages, QKeySequence(Qt.CTRL + Qt.Key_F6), """
<p><b>Modify→Combine Pages</b> ({})</p>
<p>Combine any overlapping pages in the current entry where possible.</p>
""".format(QKeySequence(QKeySequence(Qt.CTRL + Qt.Key_F6)).toString()))

        self.swapTermWithFilteredAction = Lib.createAction(
            window, ":/swap-term-with-found.svg",
            "Swap Term with &Filtered", self.swapTermWithFiltered,
            tooltip="""\
<p><b>Modify→Swap Term with Filtered</b></p>
<p>Swap the current entry's term text (and sort as text) with the current
filtered entry's.</p>
<p>This leaves the pages and subentries as-is; to swap them too, use
one of the <b>Modify→Swap Entry</b> actions.</p>
""")
        self.swapTermWithCircledAction = Lib.createAction(
            window, ":/swap-term-with-circled.svg",
            "Swap &Term with Circled", self.swapTermWithCircled,
            tooltip="""\
<p><b>Modify→Swap Term with Circled</b></p>
<p>Swap the current entry's term text (and sort as text) with the circled
entry's.</p>
<p>This leaves the pages and subentries as-is; to swap them too, use
one of the <b>Modify→Swap Entry</b> actions.</p>
""")

        self.swapEntryWithFilteredAction = Lib.createAction(
            window, ":/swap-entry-with-found.svg",
            "Swap &Entry with Filtered", self.swapEntryWithFiltered,
            tooltip="""\
<p><b>Modify→Swap Entry with Filtered</b></p>
<p>Swap the current entry with the current filtered entry.</p>
<p>This also means that the current entry will have the current filtered
entry's subentries and vice versa. To just swap the term texts use one
of the <b>Modify→Swap Term</b> actions.</p>
""")
        self.swapEntryWithCircledAction = Lib.createAction(
            window, ":/swap-entry-with-circled.svg",
            "&Swap Entry with Circled", self.swapEntryWithCircled,
            tooltip="""\
<p><b>Modify→Swap Entry with Circled</b></p>
<p>Swap the current entry with the circled entry.</p>
<p>This also means that the current entry will have the circled entry's
subentries and vice versa. To just swap the term texts use one of the
<b>Modify→Swap Term</b> actions.</p>
""")

        self.mergeIntoParentAction = Lib.createAction(
            window, ":/merge-into-parent.svg", "Merge &into Parent",
            self.mergeIntoParent,
            tooltip="""\
<p><b>Modify→Merge into Parent</b></p>
<p>Merge the current entry with its immediate parent entry, and then
delete the current entry.</p>""")
        self.mergeSubentriesAction = Lib.createAction(
            window, ":/merge-sub-entries.svg", "&Merge Subentries",
            self.mergeSubentries,
            tooltip="""\
<p><b>Modify→Merge Subentries</b></p>
<p>Merge all the current entry's subentries' pages, cross-references,
and their subentries into the current entry.</p>""")


    def forMenu(self):
        return (self.swapAcronymAction, None, self.mergePagesAction,
                self.copyPagesAction, self.combinePagesAction, None,
                self.swapTermWithFilteredAction,
                self.swapTermWithCircledAction,
                self.swapEntryWithCircledAction,
                self.swapEntryWithFilteredAction, None,
                self.mergeIntoParentAction, self.mergeSubentriesAction)


    def forToolbar(self):
        return (self.swapAcronymAction, None, self.mergePagesAction,
                self.copyPagesAction, self.combinePagesAction, None,
                self.swapTermWithFilteredAction,
                self.swapTermWithCircledAction,
                self.swapEntryWithFilteredAction,
                self.swapEntryWithCircledAction)


    def updateUi(self):
        eid = self.state.viewAllPanel.view.selectedEid
        filteredEid = self.state.viewFilteredPanel.view.selectedEid
        circledEid = self.state.viewAllPanel.view.circledEid

        self.window.gotoActions.gotoCircledAction.setEnabled(
            circledEid is not None)
        hasModel = bool(self.state.model)
        hasFiltered = (eid is not None and filteredEid is not None and
                       eid != filteredEid)
        hasCircled = (eid is not None and circledEid is not None and
                      eid != circledEid)
        enabled = eid is not None and hasModel
        for action in (self.swapAcronymAction, self.combinePagesAction):
            action.setEnabled(enabled)
        self.copyPagesAction.setEnabled(enabled and
                                        bool(self.state.pagesCache))
        self._updateCopyOrMergeActionTip(self.copyPagesAction,
                                         COPY_PAGES_TIP, "copied")
        self.mergePagesAction.setEnabled(enabled and
                                         bool(self.state.pagesCache))
        self._updateCopyOrMergeActionTip(self.mergePagesAction,
                                         MERGE_PAGES_TIP, "merged")
        self.swapTermWithFilteredAction.setEnabled(hasFiltered)
        self.swapTermWithCircledAction.setEnabled(hasCircled)
        self.swapEntryWithFilteredAction.setEnabled(hasFiltered)
        self.swapEntryWithCircledAction.setEnabled(hasCircled)
        self.mergeIntoParentAction.setEnabled(
            eid is not None and hasModel and
            self.state.model.parentOf(eid) != ROOT)
        self.mergeSubentriesAction.setEnabled(
            eid is not None and hasModel and
            self.state.model.hasSubentry(eid))


    def _updateCopyOrMergeActionTip(self, action, tip, word):
        if action.isEnabled():
            tip += "<p>The pages that will be {} are:<br>{}</p>".format(
                word, self.state.pagesCache)
        action.setToolTip(tip)


    def swapAcronym(self):
        self.state.maybeSave()
        oldText = self.state.entryPanel.termEdit.toHtml()
        newText = Lib.swapAcronym(oldText)
        if oldText != newText:
            self.state.entryPanel.termEdit.setHtml(newText)
            self.state.save(name="swap acronym in")


    def mergePages(self):
        self.state.maybeSave()
        oldPages = self.state.entryPanel.pagesEdit.toHtml()
        if oldPages != self.state.pagesCache and self.state.pagesCache:
            pageRange = Pages.RulesForName[
                self.state.model.pageRangeRules()].function
            merged = Pages.mergedPages(oldPages, self.state.pagesCache,
                                       pageRange=pageRange)
            self.state.entryPanel.pagesEdit.setHtml(merged)
            self.state.save(name="merge pages to")


    def copyPages(self):
        self.state.maybeSave()
        oldPages = self.state.entryPanel.pagesEdit.toHtml()
        if oldPages != self.state.pagesCache and self.state.pagesCache:
            self.state.entryPanel.pagesEdit.setHtml(self.state.pagesCache)
            self.state.save(name="copy pages to")


    def combinePages(self):
        self.state.maybeSave()
        oldPages = self.state.entryPanel.pagesEdit.toHtml()
        pageRange = Pages.RulesForName[
            self.state.model.pageRangeRules()].function
        newPages = Pages.combinedOverlappingPages(oldPages, pageRange)
        if oldPages != newPages:
            self.state.entryPanel.pagesEdit.setHtml(newPages)
            self.state.save(name="combine pages in")


    def swapTermWithFiltered(self):
        self.state.maybeSave()
        eid = self.state.entryPanel.entry.eid
        if eid is None:
            return # Should never happen
        filteredEid = self.state.viewFilteredPanel.view.selectedEid
        if filteredEid is None:
            return # Should never happen
        self.state.model.swapTerms(eid, filteredEid)


    def swapTermWithCircled(self):
        self.state.maybeSave()
        eid = self.state.entryPanel.entry.eid
        if eid is None:
            return # Should never happen
        circledEid = self.state.viewAllPanel.view.circledEid
        if circledEid is None:
            return # Should never happen
        self.state.model.swapTerms(eid, circledEid)


    def swapEntryWithFiltered(self):
        self.state.maybeSave()
        eid = self.state.entryPanel.entry.eid
        if eid is None:
            return # Should never happen
        filteredEid = self.state.viewFilteredPanel.view.selectedEid
        if filteredEid is None:
            return # Should never happen
        self.state.model.swapEntries(eid, filteredEid)


    def swapEntryWithCircled(self):
        self.state.maybeSave()
        eid = self.state.entryPanel.entry.eid
        if eid is None:
            return # Should never happen
        circledEid = self.state.viewAllPanel.view.circledEid
        if circledEid is None:
            return # Should never happen
        self.state.model.swapEntries(eid, circledEid)


    def mergeIntoParent(self):
        self.state.maybeSave()
        eid = self.state.entryPanel.entry.eid
        if eid is None:
            return # Should never happen
        peid = self.state.model.parentOf(eid)
        if peid != ROOT: # Should always be True
            self.state.model.mergeIntoParent(eid, peid)


    def mergeSubentries(self):
        self.state.maybeSave()
        eid = self.state.entryPanel.entry.eid
        if eid is None:
            return # Should never happen
        self.state.model.mergeSubentries(eid)
