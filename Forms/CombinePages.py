#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

if __name__ == "__main__":
    import os
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from PySide.QtCore import QSettings, Qt
from PySide.QtGui import (
    QApplication, QDialog, QDialogButtonBox, QFormLayout, QIcon, QLabel,
    QPushButton)

import Lib
import Saf
import Pages
import Widgets
from Config import Gopt
from Const import EntryDataKind, FilterKind, say, SAY_TIMEOUT, UNLIMITED

_BG_SAME = "background-color: #EEFFEE;"
_BG_DIFFERENT = "background-color: #FFEEEE;"


@Lib.updatable_tooltips
class Form(QDialog):

    def __init__(self, state, parent=None):
        super().__init__(parent)
        Lib.prepareModalDialog(self)
        self.state = state
        self.setWindowTitle("Combine Overlapping Pages — {}".format(
                            QApplication.applicationName()))
        self.createWidgets()
        self.layoutWidgets()
        self.createConnections()
        self.entry = None
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            self.eids = list(self.state.model.filteredEntries(
                filter=FilterKind.HAS_OVERLAPPING_PAGES, match=None,
                offset=0, limit=UNLIMITED, entryData=EntryDataKind.EID))
        finally:
            QApplication.restoreOverrideCursor()
        self.eidIndex = -1 if self.eids else None
        if self.eids:
            self.skip()
            self.combineButton.setFocus()
            say("Found {:,} entries with overlapping pages".format(
                len(self.eids)), SAY_TIMEOUT)
        else:
            say("No overlapping pages found", SAY_TIMEOUT)
        self.updateUi()
        settings = QSettings()
        self.updateToolTips(bool(int(settings.value(
            Gopt.Key.ShowDialogToolTips, Gopt.Default.ShowDialogToolTips))))


    def createWidgets(self):
        self.termLabelLabel = QLabel("Term")
        self.termLabel = Widgets.Label.HtmlLabel()
        self.originalPagesLabel = Widgets.Label.HtmlLabel()
        self.originalPagesLabel.setStyleSheet(_BG_SAME)
        self.combinedPagesLabel = Widgets.Label.HtmlLabel()
        self.combinedPagesLabel.setStyleSheet(_BG_SAME)

        self.buttonBox = QDialogButtonBox()
        self.combineButton = QPushButton(QIcon(":/combinepages.svg"),
                                         "Co&mbine")
        self.tooltips.append((self.combineButton, """\
<p><b>Combine</b></p>
<p>Combine overlapping pages as shown, and move to the next term with
overlapping pages.</p>"""))
        self.buttonBox.addButton(self.combineButton,
                                 QDialogButtonBox.ActionRole)
        self.skipButton = QPushButton(QIcon(":/skip.svg"), "S&kip")
        self.tooltips.append((self.skipButton, """\
<p><b>Skip</b></p>
<p>Skip this term's overlapping pages, and move to the next term with
overlapping pages.</p>"""))
        self.buttonBox.addButton(self.skipButton,
                                 QDialogButtonBox.ActionRole)
        self.closeButton = QPushButton(QIcon(":/dialog-close.svg"),
                                       "&Close")
        self.tooltips.append((self.closeButton, """<p><b>Close</b></p>
<p>Close the dialog.</p>"""))
        self.buttonBox.addButton(self.closeButton,
                                 QDialogButtonBox.RejectRole)
        self.helpButton = QPushButton(QIcon(":/help.svg"), "Help")
        self.tooltips.append((
            self.helpButton,
            "Help on the Combine Overlapping Pages dialog"))
        self.buttonBox.addButton(self.helpButton,
                                 QDialogButtonBox.HelpRole)


    def layoutWidgets(self):
        layout = QFormLayout()
        layout.addRow(self.termLabelLabel, self.termLabel)
        layout.addRow("Pages", self.originalPagesLabel)
        layout.addRow("Pages if Combined", self.combinedPagesLabel)
        layout.addRow(self.buttonBox)
        self.setLayout(layout)


    def createConnections(self):
        self.buttonBox.rejected.connect(self.reject)
        self.combineButton.clicked.connect(self.combine)
        self.skipButton.clicked.connect(self.skip)
        self.helpButton.clicked.connect(self.help)


    def help(self):
        self.state.help("xix_ref_dlg_combpages.html")


    def updateUi(self):
        if bool(self.eids) and self.eidIndex < len(self.eids):
            enableReplace = (self.combinedPagesLabel.text() !=
                             self.originalPagesLabel.text())
            self.combineButton.setEnabled(enableReplace)
            self.skipButton.setEnabled(True)
            if enableReplace:
                self.combineButton.setFocus()
            else:
                self.skipButton.setFocus()
        else:
            self.combineButton.setEnabled(False)
            self.skipButton.setEnabled(False)


    def combine(self):
        pages = self.combinedPagesLabel.text()
        if pages != self.originalPagesLabel.text():
            with Lib.BlockSignals(self.state.model):
                self.state.model.editEntry(
                    self.entry, self.entry.saf, self.entry.sortas,
                    self.entry.term, pages)
        self.skip()


    def skip(self):
        self.eidIndex += 1
        while 0 <= self.eidIndex < len(self.eids):
            self.entry = self.state.model.entry(self.eids[self.eidIndex])
            self.termLabelLabel.setText("Term ({:,} of {:,})".format(
                                        self.eidIndex + 1, len(self.eids)))
            self.termLabel.setText(Lib.elidePatchHtml(self.entry.term,
                                                      self.state))
            self.originalPagesLabel.setText(self.entry.pages)
            pages = Pages.combinedOverlappingPages(self.entry.pages)
            self.combinedPagesLabel.setText(pages)
            self.combinedPagesLabel.setStyleSheet(
                _BG_DIFFERENT if pages != self.entry.pages else _BG_SAME)
            if pages != self.entry.pages:
                break
            self.eidIndex += 1
        self.updateUi()


    def reject(self):
        message = "Combine overlapping pages"
        if self.state.model.canUndo:
            self.state.model.can_undo.emit(True, message)
        if self.state.model.canRedo:
            self.state.model.can_redo.emit(True, message)
        self.state.updateUi()
        super().accept() # Because this is Close not Cancel


if __name__ == "__main__":
    import collections
    import Qrc # noqa
    import HelpForm
    Entry = collections.namedtuple("Entry", "eid saf sortas term pages")
    class FakeModel:
        def __init__(self):
            class E:
                def emit(self, *args):
                    pass
            self.can_undo = E()
            self.can_redo = E()
        def entry(self, eid):
            if eid == 100:
                return Entry(eid, Saf.AUTO, "one", "One", "11, 21-25, 22")
            if eid == 200:
                return Entry(eid, Saf.AUTO, "two", "Two", "11, 21-25, 22t")
            if eid == 300:
                return Entry(eid, Saf.AUTO, "three", "Three",
                             "2–11, 41–46, 97, 123, 262, 265f, "
                             "380–88, 382–89, 390–92, 479, 489–94")
            if eid == 400:
                return Entry(eid, Saf.AUTO, "four", "Four",
                             "15, 37, 211, 223–26, 359, 372, 372, 386, "
                             "396, 448–54, 484")
            if eid == 500:
                return Entry(eid, Saf.AUTO, "five", "Five",
                             "94, 163–69, 164, 180, 190, 238–47, 260, "
                             "262, 316–20, 372–79, 429<b>t</b>")
        def filteredEntries(self, *args, **kwargs):
            for eid in (100, 200, 300, 400, 500):
                yield eid
        def editEntry(self, *args):
            print("editEntry", args)
        def blockSignals(self, *args):
            print("blockSignals", args)
        def canUndo(self):
            return False
        def canRedo(self):
            return False
    class FakeView:
        def __init__(self):
            self.selectedEid = 88
        def gotoEid(self, eid):
            print("gotoEid", eid)
    class FakePanel:
        def __init__(self):
            self.view = FakeView()
    class FakeState:
        def __init__(self):
            self.model = FakeModel()
            self.viewAllPanel = FakePanel()
            self.stdFontFamily = "Times New Roman"
            self.stdFontSize = 13
            self.altFontFamily = "Arial"
            self.altFontSize = 13
            self.monoFontFamily = "Courier New"
            self.monoFontSize = 12
            self.window = None
            self.helpForm = None
        def updateUi(self):
            pass
        def help(self, page=None):
            if self.helpForm is None:
                self.helpForm = HelpForm.Form("xix_help.html", self.window)
            if page is not None:
                self.helpForm.changePage(page)
            self.helpForm.show()
            self.helpForm.raise_()
            self.helpForm.activateWindow()
    app = QApplication([])
    app.setOrganizationName("Qtrac Ltd.")
    app.setOrganizationDomain("qtrac.eu")
    app.setApplicationName("XindeX-Test")
    app.setApplicationVersion("1.0.0")
    state = FakeState()
    form = Form(state)
    state.window = form
    form.show()
    app.exec_()
