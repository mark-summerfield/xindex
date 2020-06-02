#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

if __name__ == "__main__":
    import os
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from PySide.QtCore import QEvent, QSettings, Qt
from PySide.QtGui import (
    QApplication, QComboBox, QDialog, QDialogButtonBox, QGridLayout,
    QGroupBox, QHBoxLayout, QIcon, QLabel, QPushButton, QRadioButton,
    QVBoxLayout)

import Forms.Util
import Lib
import Widgets
import Widgets.LineEdit
from Config import Gopt
from Const import MAX_RECENT, say, SAY_TIMEOUT, XrefKind


@Lib.updatable_tooltips
class Form(QDialog):

    def __init__(self, state, parent=None):
        super().__init__(parent)
        Lib.prepareModalDialog(self)
        self.state = state
        self.setWindowTitle("Add Cross-reference — {}".format(
                            QApplication.applicationName()))
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
        self.entry1Label = QLabel("cross-reference from ")
        self.termLabel = Widgets.Label.HtmlLabel("“{}”".format(
            Lib.elidePatchHtml(self.selectedEntry.term, self.state)))
        self.entry2Label = QLabel(" to")
        self.seeRadioButton = QRadioButton("&See")
        self.seeRadioButton.setChecked(True)
        self.tooltips.append((self.seeRadioButton, """<p><b>See</b></p>
<p>Check to create a <i>see</i> cross-reference.</p>"""))
        self.alsoRadioButton = QRadioButton("See &Also")
        self.tooltips.append((self.alsoRadioButton, """<p><b>See
Also</b></p>
<p>Check to create a <i>see also</i> cross-reference.</p>"""))
        self.whichGroup = QGroupBox("Add")
        self.filteredEntry = self.circledEntry = None
        filteredEid = self.state.viewFilteredPanel.view.selectedEid
        if filteredEid is not None:
            self.filteredEntry = self.state.model.entry(filteredEid)
        circledEid = self.state.viewAllPanel.view.circledEid
        if circledEid is not None:
            self.circledEntry = self.state.model.entry(circledEid)
        self.filteredRadioButton = QRadioButton("&Filtered")
        self.circledRadioButton = QRadioButton("C&ircled")
        self.recentRadioButton = QRadioButton("&Recent")
        self.tooltips.append((
            self.recentRadioButton, """<p><b>Recent</b></p>
<p>Create a cross-reference to a recently visited entry.</p>"""))
        self.filteredLabel = Widgets.Label.HtmlLabel()
        self.circledLabel = Widgets.Label.HtmlLabel()
        seen = {selectedEid}
        buttons = (self.filteredRadioButton, self.circledRadioButton,
                   self.recentRadioButton)
        Forms.Util.setUpRadioButton(
            self, self.filteredEntry, self.filteredRadioButton,
            self.filteredLabel, buttons, seen, """<p><b>Filtered</b></p>
<p>Create a cross-reference to the filtered entry “{}”.</p>""")
        Forms.Util.setUpRadioButton(
            self, self.circledEntry, self.circledRadioButton,
            self.circledLabel, buttons, seen, """<p><b>Circled</b></p>
<p>Create a cross-reference to the circled entry “{}”.</p>""")
        self.recentComboBox = Forms.Util.createTermsComboBox(
            self.state, self.state.gotoEids, ignore=seen,
            maximum=MAX_RECENT)
        self.groupRadioButton = QRadioButton("All in &Group")
        self.groupComboBox = QComboBox()
        for i, (gid, name, linked) in enumerate(
                self.state.model.allGroups()):
            self.groupComboBox.addItem(
                QIcon(":/grouplink.svg" if linked else ":/groups.svg"),
                name, gid)
        if not self.groupComboBox.count():
            self.groupRadioButton.setEnabled(False)
            self.groupComboBox.setEnabled(False)
        self.eidGroup = QGroupBox()
        self.genericTermRadioButton = QRadioButton("Generic &Term")
        self.tooltips.append((self.genericTermRadioButton, """\
<p><b>Generic Term</b></p>
<p>Create a cross-reference to the given generic term.</p>"""))
        self.genericTermLineEdit = EnableOnClickLineEdit(
            self.state, self.genericTermRadioButton, self)
        self.tooltips.append((self.genericTermLineEdit, """\
<p><b>Generic Term text</b></p>
<p>The generic term text styled (e.g., <b>bold</b>, <i>italic</i>), as
it should appear in the final index.</p>"""))
        self.formatPanel = Widgets.FormatPanel.Panel(self.state, self)
        self.formatPanel.state.editors = [self.genericTermLineEdit]
        self.formatActions = self.formatPanel.formatActions
        self.buttonBox = QDialogButtonBox()
        self.addButton = QPushButton(QIcon(":/xref-add.svg"), "A&dd")
        self.tooltips.append((self.addButton, """<p><b>Add</b></p>
<p>Add the specified cross-reference to the <b>Entry</b> {}.</p>"""
                             .format(self.termLabel.text())))
        self.buttonBox.addButton(self.addButton,
                                 QDialogButtonBox.AcceptRole)
        self.closeButton = QPushButton(QIcon(":/dialog-close.svg"),
                                       "&Cancel")
        self.tooltips.append((self.closeButton, """<p><b>Cancel</b></p>
<p>Close the dialog without making any changes to the index.</p>"""))
        self.buttonBox.addButton(self.closeButton,
                                 QDialogButtonBox.RejectRole)
        self.helpButton = QPushButton(QIcon(":/help.svg"), "Help")
        self.tooltips.append((self.helpButton,
                              "Help on the Add Cross-reference dialog"))
        self.buttonBox.addButton(self.helpButton,
                                 QDialogButtonBox.HelpRole)
        if (not self.filteredRadioButton.isChecked() and
                not self.circledRadioButton.isChecked()):
            if self.recentComboBox.count():
                self.recentRadioButton.setChecked(True)
            else:
                self.genericTermRadioButton.setChecked(True)
                self.genericTermLineEdit.setFocus()


    def layoutWidgets(self):
        layout = QVBoxLayout()
        whichLayout = QHBoxLayout()
        whichLayout.addWidget(self.seeRadioButton)
        whichLayout.addWidget(self.alsoRadioButton)
        whichLayout.addStretch()
        self.whichGroup.setLayout(whichLayout)
        layout.addWidget(self.whichGroup)
        entryLayout = QHBoxLayout()
        entryLayout.setSpacing(0)
        entryLayout.addWidget(self.entry1Label)
        entryLayout.addWidget(self.termLabel)
        entryLayout.addWidget(self.entry2Label)
        entryLayout.addStretch()
        layout.addLayout(entryLayout)
        eidLayout = QVBoxLayout()
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
        hbox = QHBoxLayout()
        hbox.addWidget(self.groupRadioButton)
        hbox.addWidget(self.groupComboBox, 1)
        eidLayout.addLayout(hbox)
        grid = QGridLayout()
        grid.addWidget(self.formatPanel, 0, 0, 1, 2, Qt.AlignRight)
        grid.addWidget(self.genericTermRadioButton, 1, 0)
        grid.addWidget(self.genericTermLineEdit, 1, 1)
        eidLayout.addLayout(grid)
        eidLayout.addStretch()
        self.eidGroup.setLayout(eidLayout)
        layout.addWidget(self.eidGroup)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)


    def createConnections(self):
        self.buttonBox.accepted.connect(self.addXRef)
        self.buttonBox.rejected.connect(self.reject)
        self.helpButton.clicked.connect(self.help)
        self.filteredRadioButton.clicked.connect(self.updateUi)
        self.circledRadioButton.clicked.connect(self.updateUi)
        self.recentRadioButton.clicked.connect(self.updateUi)
        self.recentRadioButton.toggled.connect(self.moveFocus)
        self.recentComboBox.currentIndexChanged[int].connect(
            self.recentChanged)
        self.groupRadioButton.clicked.connect(self.updateUi)
        self.groupRadioButton.toggled.connect(self.moveFocus)
        self.groupComboBox.currentIndexChanged[int].connect(
            self.groupChanged)
        self.genericTermRadioButton.clicked.connect(self.updateUi)
        self.genericTermRadioButton.clicked.connect(
            self.genericTermLineEdit.setFocus)
        self.genericTermLineEdit.textChanged.connect(self.updateUi)
        self.genericTermLineEdit.enterPressed.connect(self.maybeAdd)


    def recentChanged(self):
        self.recentRadioButton.setChecked(True)
        self.updateUi()


    def groupChanged(self):
        self.groupRadioButton.setChecked(True)
        self.updateUi()


    def moveFocus(self):
        if self.recentRadioButton.isChecked():
            self.recentComboBox.setFocus()
        elif self.groupRadioButton.isChecked():
            self.groupComboBox.setFocus()


    def help(self):
        self.state.help("xix_ref_dlg_addxref.html")


    def updateUi(self):
        enable = (self.genericTermRadioButton.isChecked() or
                  (self.groupRadioButton.isChecked() and
                   self.groupComboBox.count()))
        for widget in (self.genericTermLineEdit, self.formatPanel):
            widget.setEnabled(enable)
        self.recentRadioButton.setEnabled(self.recentComboBox.count())
        self.recentComboBox.setEnabled(self.recentComboBox.count())
        enable = True
        if (self.filteredRadioButton.isChecked() and
                self.filteredEntry is None):
            enable = False
        if (self.circledRadioButton.isChecked() and
                self.circledEntry is None):
            enable = False
        if (self.recentRadioButton.isChecked() and
                self.recentComboBox.currentIndex() < 0):
            enable = False
        if (self.groupRadioButton.isChecked() and
                not self.groupComboBox.count()):
            enable = False
        if (self.genericTermRadioButton.isChecked() and
                self.genericTermLineEdit.isEmpty()):
            enable = False
        self.addButton.setEnabled(enable)


    def maybeAdd(self):
        if (self.genericTermRadioButton.isChecked() and not
                self.genericTermLineEdit.isEmpty()):
            self.addXRef()


    def addXRef(self):
        from_eid = self.selectedEntry.eid
        assert from_eid is not None
        kind = (XrefKind.SEE if self.seeRadioButton.isChecked() else
                XrefKind.SEE_ALSO)
        if self.groupRadioButton.isChecked():
            gid = int(self.groupComboBox.itemData(
                      self.groupComboBox.currentIndex()))
            for to_eid in tuple(self.state.model.eidsForGid(gid)):
                self.state.model.addXRef(from_eid, to_eid, kind)
        elif not self.genericTermRadioButton.isChecked():
            to_eid = None
            if self.filteredRadioButton.isChecked():
                to_eid = self.filteredEntry.eid
            elif self.circledRadioButton.isChecked():
                to_eid = self.circledEntry.eid
            elif self.recentRadioButton.isChecked():
                to_eid = self.recentComboBox.itemData(
                    self.recentComboBox.currentIndex())
            assert to_eid is not None
            self.state.model.addXRef(from_eid, to_eid, kind)
        else:
            term = self.genericTermLineEdit.toHtml()
            kind = (XrefKind.SEE_GENERIC if
                    self.seeRadioButton.isChecked() else
                    XrefKind.SEE_ALSO_GENERIC)
            self.state.model.addGenericXRef(from_eid, term, kind)
        say("Added cross-reference", SAY_TIMEOUT)
        self.accept()


class EnableOnClickLineEdit(Widgets.LineEdit.HtmlLineEdit):

    def __init__(self, state, button, parent=None):
        super().__init__(state, parent)
        self.button = button


    def event(self, event):
        if not self.isEnabled() and event.type() == QEvent.MouseButtonPress:
            event.accept()
            self.button.click()
            self.setEnabled(True)
            self.setFocus()
            self.selectAll()
            return True
        return super().event(event)


if __name__ == "__main__":
    import collections
    import sys
    import Qrc # noqa
    import HelpForm
    Entry = collections.namedtuple("Entry", "eid term")
    class FakeModel:
        def entry(self, eid):
            if eid == 100:
                return Entry(eid, "Selected Entry")
            elif eid == 300:
                return Entry(eid, "Filtered Entry")
            elif eid == 500:
                return Entry(eid, "Circled Entry")
            else:
                return Entry(eid, "Recent Entry #{}".format(eid))
        def term(self, eid):
            return self.entry(eid)[1]
        def termPath(self, eid):
            return self.entry(eid).term
        def addGenericXRef(self, from_eid, term, kind):
            print("addGenericXRef from={} term={!r} kind={}".format(
                  from_eid, term, kind.name))
        def addXRef(self, from_eid, to_eid, kind):
            print("addXRef from={} to={} kind={}".format(from_eid, to_eid,
                  kind.name))
        def allGroups(self):
            for t in ((1, "Unlinked 1", False), (2, "Unlinked 2", False),
                      (3, "Linked", True)):
                yield t
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
        state.gotoEids = [500, 600]
    form = Form(state)
    state.window = form
    form.show()
    app.exec_()
