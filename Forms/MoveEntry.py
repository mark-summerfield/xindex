#!/usr/bin/env python3
# Copyright © 2016-20 Qtrac Ltd. All rights reserved.

if __name__ == "__main__":
    import os
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from PySide.QtCore import QSettings
from PySide.QtGui import (
    QApplication, QDialog, QDialogButtonBox, QGroupBox, QHBoxLayout,
    QIcon, QLabel, QPushButton, QRadioButton, QVBoxLayout)

import Lib
import Widgets
import Widgets.LineEdit
import Forms.Util
from Config import Gopt
from Const import MAX_RECENT, ROOT, say, SAY_TIMEOUT


@Lib.updatable_tooltips
class Form(QDialog):

    def __init__(self, state, parent=None):
        super().__init__(parent)
        Lib.prepareModalDialog(self)
        self.state = state
        self.setWindowTitle("Move Entry — {}".format(
                            QApplication.applicationName()))
        self.message = None
        self.createWidgets()
        self.layoutWidgets()
        self.createConnections()
        self.updateUi()
        settings = QSettings()
        self.updateToolTips(bool(int(settings.value(
            Gopt.Key.ShowDialogToolTips, Gopt.Default.ShowDialogToolTips))))


    def createWidgets(self):
        selectedEid = self.state.viewAllPanel.view.selectedEid
        self.selectedEntry = self.state.model.entry(selectedEid)
        self.entryLabel = QLabel("Move ")
        self.termLabel = Widgets.Label.HtmlLabel("“{}”".format(
            Lib.elidePatchHtml(self.selectedEntry.term, self.state)))

        self.eidGroup = QGroupBox()

        parentEid = self.selectedEntry.peid
        self.moveToTopRadioButton = QRadioButton("to be a &Main Entry")
        self.grandParentEntry = None
        grandParentEid = None
        if parentEid != ROOT:
            grandParentEid = self.state.model.parentOf(parentEid)
            if grandParentEid != ROOT:
                self.grandParentEntry = self.state.model.entry(
                    grandParentEid)
        self.grandParentRadioButton = QRadioButton("up under &Grandparent")

        self.filteredEntry = self.circledEntry = None
        filteredEid = self.state.viewFilteredPanel.view.selectedEid
        if filteredEid is not None:
            self.filteredEntry = self.state.model.entry(filteredEid)
        circledEid = self.state.viewAllPanel.view.circledEid
        if circledEid is not None:
            self.circledEntry = self.state.model.entry(circledEid)
        self.filteredRadioButton = QRadioButton("under &Filtered")
        self.circledRadioButton = QRadioButton("under C&ircled")
        self.recentRadioButton = QRadioButton("under &Recent")
        self.tooltips.append((
            self.recentRadioButton, """<p><b>under Recent</b></p>
<p>Move the current entry under a recently visited entry.</p>"""))

        self.grandParentLabel = Widgets.Label.HtmlLabel()
        self.filteredLabel = Widgets.Label.HtmlLabel()
        self.circledLabel = Widgets.Label.HtmlLabel()

        self.moveToTopRadioButton.setEnabled(parentEid != ROOT)
        self.moveToTopRadioButton.setChecked(parentEid != ROOT)
        seen = {selectedEid, self.selectedEntry.peid}
        self.buttons = (self.moveToTopRadioButton,
                        self.grandParentRadioButton,
                        self.filteredRadioButton,
                        self.circledRadioButton, self.recentRadioButton)
        Forms.Util.setUpRadioButton(
            self, self.grandParentEntry, self.grandParentRadioButton,
            self.grandParentLabel, self.buttons, seen,
            """<p><b>under Grandparent</b></p>
<p>Move the current entry up under its grandparent “{}”.</p>""")
        Forms.Util.setUpRadioButton(
            self, self.filteredEntry, self.filteredRadioButton,
            self.filteredLabel, self.buttons, seen,
            """<p><b>under Filtered</b></p>
<p>Move the current entry under the filtered entry “{}”.</p>""")
        Forms.Util.setUpRadioButton(
            self, self.circledEntry, self.circledRadioButton,
            self.circledLabel, self.buttons, seen,
            """<p><b>under Circled</b></p>
<p>Move the current entry under the circled entry “{}”.</p>""")
        self.recentComboBox = Forms.Util.createTermsComboBox(
            self.state, self.state.gotoEids, ignore=seen,
            maximum=MAX_RECENT)
        if self.recentComboBox.count() and all(not radio.isChecked()
                                               for radio in self.buttons):
            self.recentRadioButton.setChecked(True)
            self.recentComboBox.setFocus()

        self.buttonBox = QDialogButtonBox()
        self.moveButton = QPushButton(QIcon(":/move.svg"), "M&ove")
        self.tooltips.append((self.moveButton, """<p><b>Move</b></p>
<p>Move the “{}” entry.</p>""".format(self.termLabel.text())))
        self.buttonBox.addButton(self.moveButton,
                                 QDialogButtonBox.AcceptRole)
        self.closeButton = QPushButton(QIcon(":/dialog-close.svg"),
                                       "&Cancel")
        self.tooltips.append((self.closeButton, """<p><b>Cancel</b></p>
<p>Close the dialog without making any changes to the index.</p>"""))
        self.buttonBox.addButton(self.closeButton,
                                 QDialogButtonBox.RejectRole)
        self.helpButton = QPushButton(QIcon(":/help.svg"), "Help")
        self.tooltips.append((self.helpButton,
                              "Help on the Move Entry dialog"))
        self.buttonBox.addButton(self.helpButton,
                                 QDialogButtonBox.HelpRole)


    def layoutWidgets(self):
        layout = QVBoxLayout()
        entryLayout = QHBoxLayout()
        entryLayout.setSpacing(0)
        entryLayout.addWidget(self.entryLabel)
        entryLayout.addWidget(self.termLabel)
        entryLayout.addStretch()
        layout.addLayout(entryLayout)
        eidLayout = QVBoxLayout()
        eidLayout.addWidget(self.moveToTopRadioButton)
        hbox = QHBoxLayout()
        hbox.setSpacing(0)
        hbox.addWidget(self.grandParentRadioButton)
        hbox.addWidget(self.grandParentLabel, 1)
        eidLayout.addLayout(hbox)
        hbox = QHBoxLayout()
        hbox.setSpacing(0)
        hbox.addWidget(self.filteredRadioButton)
        hbox.addWidget(self.filteredLabel, 1)
        eidLayout.addLayout(hbox)
        hbox = QHBoxLayout()
        hbox.setSpacing(0)
        hbox.addWidget(self.circledRadioButton)
        hbox.addWidget(self.circledLabel, 1)
        eidLayout.addLayout(hbox)
        hbox = QHBoxLayout()
        hbox.setSpacing(0)
        hbox.addWidget(self.recentRadioButton)
        hbox.addWidget(self.recentComboBox, 1)
        eidLayout.addLayout(hbox)
        eidLayout.addStretch()
        self.eidGroup.setLayout(eidLayout)
        layout.addWidget(self.eidGroup)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)


    def createConnections(self):
        self.buttonBox.accepted.connect(self.move)
        self.buttonBox.rejected.connect(self.reject)
        self.helpButton.clicked.connect(self.help)
        self.recentRadioButton.toggled.connect(self.moveFocus)
        self.recentComboBox.currentIndexChanged[int].connect(
            self.recentChanged)


    def recentChanged(self):
        self.recentRadioButton.setChecked(True)
        self.updateUi()


    def moveFocus(self):
        if self.recentRadioButton.isChecked():
            self.recentComboBox.setFocus()


    def updateUi(self):
        self.recentRadioButton.setEnabled(self.recentComboBox.count())
        self.recentComboBox.setEnabled(self.recentComboBox.count())
        self.moveButton.setEnabled(any(button.isChecked()
                                   for button in self.buttons))


    def help(self):
        self.state.help("xix_ref_dlg_move.html")


    def move(self):
        self.state.maybeSave()
        eid = self.selectedEntry.eid
        if self.moveToTopRadioButton.isChecked():
            self.state.model.moveToTop(eid)
        else:
            peid = None
            if self.grandParentRadioButton.isChecked():
                peid = self.grandParentEntry.eid
                message = "move up"
            elif self.filteredRadioButton.isChecked():
                peid = self.filteredEntry.eid
                message = "move under filtered"
            elif self.circledRadioButton.isChecked():
                peid = self.circledEntry.eid
                message = "move under circled"
            elif self.recentRadioButton.isChecked():
                peid = self.recentComboBox.itemData(
                    self.recentComboBox.currentIndex())
                message = "move under recently visited"
            if peid is not None: # Should always be True
                self.state.model.moveUnder(eid, peid, message)
                term = Lib.htmlToPlainText(self.state.model.term(eid))
                if peid == ROOT:
                    message = "Moved “{}” to be a main entry".format(term)
                else:
                    message = "Moved “{}” under “{}”".format(
                        term,
                        Lib.htmlToPlainText(self.state.model.term(peid)))
                say(message, SAY_TIMEOUT)
        self.accept()


if __name__ == "__main__":
    import collections
    import sys
    import Qrc # noqa
    import HelpForm
    Entry = collections.namedtuple("Entry", "eid term peid")
    letters = list("ABCDEFGHIJK")
    class FakeModel:
        def entry(self, eid):
            if eid == 100:
                return Entry(eid, "Selected Entry", peid=0)
            elif eid == 300:
                return Entry(eid, "Filtered Entry", peid=0)
            elif eid == 500:
                return Entry(eid, "Circled Entry", peid=300)
            else:
                return Entry(eid, "{} Recent Entry #{}".format(
                             letters.pop(), eid), peid=0)
        def term(self, eid):
            return self.entry(eid)[1]
        def termPath(self, eid):
            return self.entry(eid).term
        def addGenericXRef(self, from_eid, term, kind):
            print("addGenericXRef {} [{}] {}".format(from_eid, term, kind))
        def addXRef(self, from_eid, to_eid, kind):
            print("addXRef {} {} {}".format(from_eid, to_eid, kind))
        def allGroups(self):
            for t in ((1, "Unlinked 1", False), (2, "Unlinked 2", False),
                      (3, "Linked", True)):
                yield t
        def moveUnder(self, eid, peid, message):
            print("moveUnder eid={} peid={}".format(eid, peid))
    class FakeView:
        def __init__(self, eid):
            self.selectedEid = eid
            self.circledEid = 500
    class FakePanel:
        def __init__(self, eid):
            self.view = FakeView(eid)
    class FakeState:
        def __init__(self):
            self.viewFilteredPanel = FakePanel(300)
            self.viewAllPanel = FakePanel(100)
            self.model = FakeModel()
            self.stdFontFamily = "Times New Roman"
            self.stdFontSize = 13
            self.altFontFamily = "Arial"
            self.altFontSize = 13
            self.monoFontFamily = "Courier New"
            self.monoFontSize = 12
            self.window = None
            self.helpForm = None
            self.gotoEids = [100, 300, 500, 11, 15, 21, 37]
        def maybeSave(self):
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
    if len(sys.argv) > 1:
        state.gotoEids = []
    form = Form(state)
    state.window = form
    form.show()
    app.exec_()
