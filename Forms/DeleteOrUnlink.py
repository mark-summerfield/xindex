#!/usr/bin/env python3
# Copyright © 2016-20 Qtrac Ltd. All rights reserved.

if __name__ == "__main__":
    import os
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from PySide.QtCore import QSettings
from PySide.QtGui import (
    QApplication, QDialog, QDialogButtonBox, QHBoxLayout, QIcon, QLabel,
    QPushButton, QRadioButton, QVBoxLayout)

import Forms.Util
import Lib
from Config import Gopt


@Lib.updatable_tooltips
class Form(QDialog):

    def __init__(self, what, gid, state, parent=None):
        super().__init__(parent)
        Lib.prepareModalDialog(self)
        self.what = what
        self.gid = gid
        self.state = state
        self.setWindowTitle("{} Linked Group — XindeX".format(what))
        self.createWidgets()
        self.layoutWidgets()
        self.createConnections()
        self.updateUi()
        settings = QSettings()
        self.updateToolTips(bool(int(settings.value(
            Gopt.Key.ShowDialogToolTips, Gopt.Default.ShowDialogToolTips))))


    def createWidgets(self):
        gname = self.state.model.nameForGid(self.gid)
        self.whatLabel = QLabel("{} Linked Group “{}” and".format(self.what,
                                                                  gname))
        self.leaveRadioButton = QRadioButton(
            "&Leave every entry in the group's pages intact")
        self.leaveRadioButton.setChecked(True)
        eids = list(self.state.model.eidsForGid(self.gid))
        self.addXrefRadioButton = QRadioButton(
            "&Add see cross-references to")
        if not eids:
            self.addXrefRadioButton.setEnabled(False)
        self.membersComboBox = Forms.Util.createTermsComboBox(self.state,
                                                              eids)
        self.membersComboBox.setEnabled(False)
        self.label = QLabel("""<p>from all the other entries in the
“{}” linked group, and delete their pages, leaving only the selected
(shown above) entry's pages intact</p>""".format(gname))
        self.label.setWordWrap(True)
        self.label.setIndent(self.label.fontMetrics().width("WW"))

        self.buttonBox = QDialogButtonBox()
        if self.what.lower() == "delete":
            self.doButton = QPushButton(QIcon(":/delete.svg"), "&Delete")
        else:
            self.doButton = QPushButton(QIcon(":/groups.svg"), "&Unlink")
        self.buttonBox.addButton(self.doButton,
                                 QDialogButtonBox.AcceptRole)
        self.closeButton = QPushButton(QIcon(":/dialog-close.svg"),
                                       "&Cancel")
        self.tooltips.append((self.closeButton, """<p><b>Cancel</b></p>
<p>Close the dialog without making any changes to the index.</p>"""))
        self.buttonBox.addButton(self.closeButton,
                                 QDialogButtonBox.RejectRole)
        self.helpButton = QPushButton(QIcon(":/help.svg"), "Help")
        self.tooltips.append(
            (self.helpButton, "Help on the {} linked group dialog".format(
             self.what)))
        self.buttonBox.addButton(self.helpButton,
                                 QDialogButtonBox.HelpRole)


    def layoutWidgets(self):
        layout = QVBoxLayout()
        layout.addWidget(self.whatLabel)
        layout.addWidget(self.leaveRadioButton)
        hbox = QHBoxLayout()
        hbox.setSpacing(0)
        hbox.addWidget(self.addXrefRadioButton)
        hbox.addWidget(self.membersComboBox)
        layout.addLayout(hbox)
        layout.addWidget(self.label)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)


    def createConnections(self):
        self.buttonBox.accepted.connect(self.deleteOrUnlink)
        self.buttonBox.rejected.connect(self.reject)
        self.helpButton.clicked.connect(self.help)
        self.leaveRadioButton.toggled.connect(self.updateUi)
        self.addXrefRadioButton.toggled.connect(self.updateUi)
        self.addXrefRadioButton.toggled.connect(self.moveFocus)
        self.membersComboBox.currentIndexChanged[int].connect(
            self.memberChanged)


    def memberChanged(self):
        self.addXrefRadioButton.setChecked(True)
        self.updateUi()


    def moveFocus(self):
        if self.addXrefRadioButton.isChecked():
            self.membersComboBox.setFocus()


    def updateUi(self):
        self.membersComboBox.setEnabled(self.membersComboBox.count())


    def help(self):
        self.state.help("xix_ref_dlg_unlink.html")


    def deleteOrUnlink(self):
        eid = None
        if self.addXrefRadioButton.isChecked():
            eid = self.membersComboBox.itemData(
                self.membersComboBox.currentIndex())
        if self.what.lower() == "delete":
            self.state.model.deleteGroup(self.gid, targetEid=eid)
        else:
            self.state.model.unlinkGroup(self.gid, targetEid=eid)
        self.accept()


if __name__ == "__main__":
    import collections
    import random
    import sys
    import Qrc # noqa
    import HelpForm
    Entry = collections.namedtuple("Entry", "eid term peid")
    class FakeModel:
        def nameForGid(self, gid):
            return "scene selection"
        def eidsForGid(self, gid):
            for eid in (20, 31, 72):
                yield eid
        def entry(self, eid):
            if eid == 100:
                return Entry(eid, "Selected Entry", peid=0)
            elif eid == 300:
                return Entry(eid, "Filtered Entry", peid=0)
            elif eid == 500:
                return Entry(eid, "Circled Entry", peid=300)
            else:
                return Entry(eid, "Recent Entry #{}".format(eid), peid=0)
        def term(self, eid):
            return self.entry(eid)[1]
        def termPath(self, eid):
            return self.entry(eid).term
        def deleteGroup(self, gid, *, targetEid=None):
            print("unlinkGroup gid={} eid={}".format(gid, targetEid))
        def unlinkGroup(self, gid, *, targetEid=None):
            print("unlinkGroup gid={} eid={}".format(gid, targetEid))
    class FakeView:
        def __init__(self, eid):
            self.selectedEid = eid
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
            self.gotoEids = []
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
    form = Form(random.choice(("Delete", "Unlink")), 14, state)
    state.window = form
    form.show()
    app.exec_()
