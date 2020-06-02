#!/usr/bin/env python3
# Copyright © 2014-20 Qtrac Ltd. All rights reserved.

import functools
import os
import tempfile

from PySide.QtCore import Qt, QTimer
from PySide.QtGui import QApplication, QKeySequence, QMenu

import Check
import Forms
import Lib
import Sql
from Config import Gconf
from Const import FilterKind, say, SAY_TIMEOUT, UUID


CHECK_TIMEOUT = 10000 # 10 secs


class Actions:

    TmpCount = 0

    def __init__(self, window):
        self.window = window
        self.state = self.window.state
        self.keepCheckFormsAlive = set()
        self.doingAllChecks = False
        self.checkCount = 0

        self.undoAction = Lib.createAction(
            window, ":/edit-undo.svg", "&Undo", self.state.undo,
            QKeySequence(Qt.Key_F9), tooltip="""\
<p><b>Index→Undo</b></p>
<p>Undo the last entry or index action if possible.</p>""".format(
                QKeySequence(Qt.Key_F9)))
        self.redoAction = Lib.createAction(
            window, ":/edit-redo.svg", "&Redo", self.state.redo,
            QKeySequence(Qt.CTRL + Qt.Key_F9), tooltip="""\
<p><b>Index→Redo</b></p>
<p>Redo the last entry or index action that was undone if possible.</p>"""
            .format(QKeySequence(Qt.CTRL + Qt.Key_F9)))
        self.combinePagesAction = Lib.createAction(
            window, ":/combinepages.svg", "&Combine Overlapping Pages...",
            self.combinePages, tooltip="""\
<p><b>Index→Combine Overlapping Pages</b></p>
<p>Combine overlapping pages where possible.</p>""")
        self.renumberPagesAction = Lib.createAction(
            window, ":/renumberpages.svg", "Renumber &Pages...",
            self.renumberPages, tooltip="""\
<p><b>Index→Renumber Pages</b></p>
<p>Renumber all or a selected range of pages.</p>""")
        self.ignoredFirstsAction = Lib.createAction(
            window, ":/format-justify-right.svg",
            "Ignored &Subentry Function Words...",
            self.editSubentryIgnoreFirsts, tooltip="""\
<p><b>Index→Ignored Subentry Function Words</b></p>
<p>Edit the function words to be ignored when sorting subentries if the
<b>Index→Options</b>, <b>Rules</b>, <b>Ignore Subentries Function
Words</b> checkbox is checked.</p>""")
        self.optionsAction = Lib.createAction(
            window, ":/preferences-system.svg", "&Options...", self.options,
            tooltip="""\
<p><b>Index→Options</b></p>
<p>Set options for {} and for the current index.""".format(
                QApplication.applicationName()))
        self.outputOptionsAction = Lib.createAction(
            window, ":/preferences-system.svg", "Ou&tput Options...",
            self.outputOptions, tooltip="""\
<p><b>Index→Output Options</b></p>
<p>Set {}'s output and print options.</p>""".format(
                QApplication.applicationName()))
        self.checkActions = Lib.createAction(
            window, ":/check.svg", "Chec&k", tooltip="""\
<p><b>Index→Check</b></p>
<p>Check various aspects of the index.</p>""")

        menu = QMenu(window)
        action = Lib.createAction(
            window, ":/check.svg", "&All the Checks", self.allChecks,
            tooltip="""\
<p><b>Index→Check→All the Checks</b></p>
<p>Perform all the checks.</p>""")
        menu.addAction(action)
        menu.addSeparator()
        action = Lib.createAction(
            window, ":/check.svg", "&Same Term Texts",
            lambda: self.check(FilterKind.SAME_TERM_TEXTS), tooltip="""\
<p><b>Index→Check→Same Term Texts</b></p>
<p>Check to see if any entries at the same level have the same term
texts irrespective of formatting or case and regardless of their Sort As
texts.</p>""")
        menu.addAction(action)
        action = Lib.createAction(
            window, ":/check.svg", "&Overlapping Pages",
            lambda: self.check(FilterKind.HAS_OVERLAPPING_PAGES),
            tooltip="""\
<p><b>Index→Check→Overlapping Pages</b></p>
<p>Check to see if any entries have overlapping pages.</p>""")
        menu.addAction(action)
        action = Lib.createAction(
            window, ":/check.svg", "Too &High Page Number",
            lambda: self.check(FilterKind.TOO_HIGH_PAGE),
            tooltip="""\
<p><b>Index→Check→Too High Page Number</b></p>
<p>Check to see if any entries have page numbers exceeding the limit set
in the Index→Options General tab's Publisher's Limits.</p>""")
        menu.addAction(action)
        action = Lib.createAction(
            window, ":/check.svg", "Too &Large Page Range",
            lambda: self.check(FilterKind.TOO_LARGE_PAGE_RANGE),
            tooltip="""\
<p><b>Index→Check→Too Large Page Range</b></p>
<p>Check to see if any entries have page ranges spanning more page
number than the the limit set in the Index→Options General tab's
Publisher's Limits.</p>""")
        menu.addAction(action)
        action = Lib.createAction(
            window, ":/check.svg", "Too &Many Pages",
            lambda: self.check(FilterKind.TOO_MANY_PAGES),
            tooltip="""\
<p><b>Index→Check→Too Many Pages</b></p>
<p>Check to see if any entries have more pages than the the limit set in
the Index→Options General tab's Publisher's Limits.</p>""")
        menu.addAction(action)
        action = Lib.createAction(
            window, ":/check.svg", "&Unindexed Pages",
            self.unindexedPages, tooltip="""\
<p><b>Index→Check→Unindexed Pages</b></p>
<p>Check to see if there are any (decimal) pages that have no index
entries. (This checks pages between 1 and the highest page limit set in
the Index→Options General tab's Publisher's Limits.)</p>""")
        menu.addAction(action)

        self.checkActions.setMenu(menu)
        self.customMarkupAction = Lib.createAction(
            window, ":/markup.svg", "Custom &Markup...",
            self.customMarkup, tooltip="""\
<p><b>Index→Custom Markup</b></p>
<p>Create, edit, or delete custom plain-text markup.</p>""")
        self.infoAction = Lib.createAction(
            window, ":/about.svg", "&Information...", self.info,
            tooltip="""\
<p><b>Index→Information</b></p>
<p>Show some basic information about the current index.</p>""")
        self.showSuggestionsAction = Lib.createAction(
            window, ":/showpanel.svg", "Show Suggestions and &Groups",
            self.state.window.showSuggestions, tooltip="""
<p><b>Index→Show Suggestions and Groups</b></p>
<p>Show the Suggestions and Groups panels if they aren't visible.</p>""")
        self.showToobarsAction = Lib.createAction(
            window, ":/preferences-desktop.svg", "Sho&w Toolbars",
            self.showToobars, tooltip="""\
<p><b>Index→Show Toolbars</b></p>
<p>Show all {}'s toolbars; useful if they have all been hidden.</p>
""".format(QApplication.applicationName()))


    def forMenu(self):
        return (self.undoAction, self.redoAction, None, self.checkActions,
                self.optionsAction, self.outputOptionsAction,
                self.ignoredFirstsAction, None, self.customMarkupAction,
                None, self.combinePagesAction, self.renumberPagesAction,
                None, self.infoAction, None, self.showSuggestionsAction,
                self.showToobarsAction)


    def forToolbar(self):
        return (self.undoAction, self.redoAction)


    def updateUndo(self, canUndo,
                   description="Undo the last entry action if possible."):
        self.undoAction.setEnabled(canUndo)
        self.undoAction.setToolTip("<p><b>Index→Undo</b></p><p>{}</p>"
                                   .format(description))


    def updateRedo(self, canRedo,
                   description="Redo the last entry action that was "
                   "undone if possible."):
        self.redoAction.setEnabled(canRedo)
        self.redoAction.setToolTip("<p><b>Index→Redo</b></p><p>{}</p>"
                                   .format(description))


    def editSubentryIgnoreFirsts(self):
        desc = """<p>
Manage the current index's list of function words and phrases that
should be ignored when sorting if they appear at the beginning of a
subentry (providing the <b>Index→Options</b>, <b>Rules</b>, <b>Ignore
Subentries Function Words</b> checkbox is checked).</p>
<p>
All words and phrases in this list are case-folded (lower-cased) and
have any accents stripped.</p>
"""
        info = Forms.List.Info(
            "Ignored Subentry Function Words", desc,
            "xix_ref_dlg_subignore.html", self.state.model._xix.db,
            Sql.SORTED_IGNORED_FIRSTS_WORDS, Sql.INSERT_IGNORED_FIRSTS_WORD,
            Sql.UPDATE_IGNORED_FIRSTS_WORD, Sql.DELETE_IGNORED_FIRSTS_WORD)
        widget = QApplication.focusWidget()
        with Lib.Qt.DisableUI(*self.window.widgets(), forModalDialog=True):
            form = Forms.List.Form(self.state, info, self.window)
            form.exec_()
        self.state.model.ignoredFirstsWords.cache_clear()
        Lib.restoreFocus(widget)


    def combinePages(self):
        widget = QApplication.focusWidget()
        say("Looking for overlapping pages…")
        with Lib.Qt.DisableUI(*self.window.widgets(), forModalDialog=True):
            form = Forms.CombinePages.Form(self.state, self.window)
            form.exec_()
        Lib.restoreFocus(widget)


    def renumberPages(self):
        widget = QApplication.focusWidget()
        with Lib.Qt.DisableUI(*self.window.widgets(), forModalDialog=True):
            form = Forms.RenumberPages.Form(self.state, self.window)
            form.exec_()
        Lib.restoreFocus(widget)


    def options(self):
        widget = QApplication.focusWidget()
        with Lib.Qt.DisableUI(*self.window.widgets(), forModalDialog=True):
            form = Forms.Options.Form(self.state, self.window)
            form.exec_()
        Lib.restoreFocus(widget)


    def outputOptions(self):
        widget = QApplication.focusWidget()
        with Lib.Qt.DisableUI(*self.window.widgets(), forModalDialog=True):
            form = Forms.OutputOptions.Form(self.state, self.window)
            form.exec_()
        Lib.restoreFocus(widget)


    def customMarkup(self):
        widget = QApplication.focusWidget()
        with Lib.Qt.DisableUI(*self.window.widgets(), forModalDialog=True):
            form = Forms.CustomMarkup.Form(self.state, self.window)
            form.exec_()
        Lib.restoreFocus(widget)


    def info(self):
        widget = QApplication.focusWidget()
        with Lib.Qt.DisableUI(*self.window.widgets(), forModalDialog=True):
            form = Forms.Info.Form(self.state, self.window)
            form.exec_()
        Lib.restoreFocus(widget)


    def showToobars(self):
        for toolbar in (self.window.fileToolBar, self.window.editToolBar,
                        self.window.spellingToolBar,
                        self.window.formatToolBar,
                        self.window.indexToolBar,
                        self.window.entryToolBar1,
                        self.window.entryToolBar2,
                        self.window.modifyToolBar,
                        self.window.gotoToolBar1,
                        self.window.gotoToolBar2,
                        self.window.gotoToolBar3,
                        self.window.gotoToolBar4):
            toolbar.show()


    def unindexedPages(self):
        if bool(self.state.model):
            config = self.state.model.configs()
            highestPage = config.get(Gconf.Key.HighestPageNumber,
                                     Gconf.Default.HighestPageNumber)
            pages = self.state.model.unindexedPages(highestPage)
            if pages:
                message = ("<p><font color=darkgreen>Unindexed Pages "
                           "between 1 and {:,} inclusive:</font></p><p>"
                           .format(highestPage))
                message += ", ".join("{:,}".format(page) for page in pages)
                message += ".</p>"
            else:
                message = ("There are no unindexed pages between 1 and "
                           "{:,}".format(highestPage))
            form = Forms.ModelessInfo.Form("Check “Unindexed Pages”",
                                           message)
            form.show()
            self.keepCheckFormsAlive.add(form)


    def allChecks(self):
        if bool(self.state.model):
            self.doingAllChecks = True
            self.checkCount = 5 # Number of checks using temp file
            filename = self._checkCreateTempFile()
            self.check(FilterKind.SAME_TERM_TEXTS, filename=filename)
            self.check(FilterKind.HAS_OVERLAPPING_PAGES, filename=filename)
            self.check(FilterKind.TOO_HIGH_PAGE, filename=filename)
            self.check(FilterKind.TOO_LARGE_PAGE_RANGE, filename=filename)
            self.check(FilterKind.TOO_MANY_PAGES, filename=filename)
            self.unindexedPages()
            say("Doing All the Checks — will report each one when done",
                SAY_TIMEOUT)


    def check(self, filter, match="", filename=None):
        if bool(self.state.model):
            uuid = self.state.model.config(UUID)
            if filename is None:
                filename = self._checkCreateTempFile()
            say("Checking “{}” — will report when done".format(filter.text),
                SAY_TIMEOUT)
            asyncResult = Check.filteredEntries(filename=filename,
                                                filter=filter, match=match)
            slot = functools.partial(
                self.checkDone, asyncResult=asyncResult,
                filename=filename, uuid=uuid, name=filter.text)
            QTimer.singleShot(CHECK_TIMEOUT, slot)


    def _checkCreateTempFile(self):
        filename = os.path.join(tempfile.gettempdir(),
                                "tmp-{}.xix".format(Actions.TmpCount))
        Actions.TmpCount += 1
        Lib.remove_file(filename)
        self.state.model.backup(filename, "Saving temporary copy",
                                self.window.reportProgress)
        return filename


    def checkDone(self, *, asyncResult, filename, uuid, name):
        if not asyncResult.ready():
            slot = functools.partial(
                self.checkDone, asyncResult=asyncResult,
                filename=filename, uuid=uuid, name=name)
            QTimer.singleShot(CHECK_TIMEOUT, slot)
        else:
            if self.doingAllChecks:
                self.checkCount -= 1
            if not self.doingAllChecks or not self.checkCount:
                self.doingAllChecks = False
                Lib.remove_file(filename)
            eids = asyncResult.get()
            form = Forms.Check.Form(self.state, eids, uuid, name)
            form.requestGotoEid.connect(self.requestGotoEid)
            form.show()
            self.keepCheckFormsAlive.add(form)


    def requestGotoEid(self, uuid, eid):
        if not bool(self.state.model):
            say("No index is open")
            return
        if uuid != self.state.model.config(UUID):
            say("Can't goto an entry in a different index")
            return
        if not self.state.model.hasEntry(eid):
            say("Can't goto an entry that no longer exists")
            return
        self.window.gotoActions.gotoEid(eid)
