#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

if __name__ == "__main__":
    import os
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from PySide.QtCore import QSettings, Qt
from PySide.QtGui import (
    QApplication, QCheckBox, QDialog, QDialogButtonBox, QIcon,
    QListWidgetItem, QMessageBox, QPushButton, QVBoxLayout)

import Lib
import Widgets
from Config import Gopt
from Const import MAIN_INDICATOR, ROOT, say, SAY_TIMEOUT, SUB_INDICATOR


@Lib.updatable_tooltips
class Form(QDialog):

    def __init__(self, state, parent=None):
        super().__init__(parent)
        Lib.prepareModalDialog(self)
        self.state = state
        self.setWindowTitle("Recreate Entries — {}".format(
                            QApplication.applicationName()))
        self.createWidgets()
        self.layoutWidgets()
        self.populate()
        self.updateUi()
        self.createConnections()
        settings = QSettings()
        self.updateToolTips(bool(int(settings.value(
            Gopt.Key.ShowDialogToolTips, Gopt.Default.ShowDialogToolTips))))


    def createWidgets(self):
        self.listWidget = Widgets.List.HtmlListWidget(self.state)
        self.tooltips.append((self.listWidget, """\
<p><b>Recreatable Entries view</b></p>
<p>The list of this index's recreatable entries.</p>"""))
        self.recreateSubentriesCheckBox = QCheckBox("Recreate &Subentries")
        self.recreateSubentriesCheckBox.setChecked(True)
        self.tooltips.append((self.recreateSubentriesCheckBox, """\
<p><b>Recreate Subentries</b></p>
<p>If checked, when an entry or subentry is recreated, all of its
subentries, and their subentries, and so on (if any), will also be
recrected if possible.</p>"""))
        self.recreateButton = QPushButton(QIcon(":/recreate.svg"),
                                          "&Recreate")
        self.recreateButton.setDefault(True)
        self.recreateButton.setAutoDefault(True)
        self.tooltips.append((self.recreateButton, """\
<p><b>Recreate</b></p>
<p>Recreate the current entry or subentry (and its subentries and their
subentries, and so on, if the <b>Recreate Subentries</b> checkbox is
checked), and then close the dialog.</p>
<p>Note that it is possible to get rid of the recreated entries by
clicking <b>Index→Undo</b> immediately after the dialog closes. (Or, at
any later time by simply deleting them.)"""))
        self.deleteButton = QPushButton(QIcon(":/delete.svg"), "&Delete...")
        self.tooltips.append((self.deleteButton, """\
<p><b>Delete</b></p>
<p>Permanently delete the current recreatable entry or subentry from
this index's list of recreatable entries.</p>"""))
        self.helpButton = QPushButton(QIcon(":/help.svg"), "Help")
        self.tooltips.append((self.helpButton,
                              "Help on the Recreate Entries dialog"))
        self.closeButton = QPushButton(QIcon(":/dialog-close.svg"),
                                       "&Close")
        self.tooltips.append((self.closeButton, """<p><b>Close</b></p>
<p>Close the dialog.</p>"""))


    def layoutWidgets(self):
        buttonBox = QDialogButtonBox()
        buttonBox.addButton(self.recreateButton,
                            QDialogButtonBox.ActionRole)
        buttonBox.addButton(self.deleteButton, QDialogButtonBox.ActionRole)
        buttonBox.addButton(self.closeButton, QDialogButtonBox.AcceptRole)
        buttonBox.addButton(self.helpButton, QDialogButtonBox.HelpRole)
        layout = QVBoxLayout()
        layout.addWidget(self.listWidget)
        layout.addWidget(self.recreateSubentriesCheckBox)
        layout.addWidget(buttonBox)
        self.setLayout(layout)


    def createConnections(self):
        self.recreateButton.clicked.connect(self.recreate)
        self.deleteButton.clicked.connect(self.delete)
        self.closeButton.clicked.connect(self.reject)
        self.helpButton.clicked.connect(self.help)


    def help(self):
        self.state.help("xix_ref_dlg_recreate.html")


    def updateUi(self):
        enable = self.listWidget.currentRow() > -1
        self.recreateButton.setEnabled(enable)
        self.deleteButton.setEnabled(enable)


    def populate(self):
        self.listWidget.clear()
        for entry in self.state.model.deletedEntries():
            pages = ""
            if entry.pages:
                pages = ", {}".format(entry.pages)
            top = MAIN_INDICATOR if entry.peid == ROOT else SUB_INDICATOR
            item = QListWidgetItem("{} {}{}".format(
                top, Lib.elidePatchHtml(entry.term, self.state),
                Lib.elidePatchHtml(pages, self.state)))
            item.setData(Qt.UserRole, entry.eid)
            self.listWidget.addItem(item)
        if self.listWidget.count():
            self.listWidget.setCurrentRow(0)


    def recreate(self): # No need to restore focus widget
        item = self.listWidget.currentItem()
        if item:
            eid = item.data(Qt.UserRole)
            subentries = self.recreateSubentriesCheckBox.isChecked()
            with Lib.DisableUI(self):
                self.state.model.recreateEntry(eid, subentries)
            say("Recreated", SAY_TIMEOUT)
        self.accept()


    def delete(self):
        widget = QApplication.focusWidget()
        item = self.listWidget.currentItem()
        if item:
            eid = item.data(Qt.UserRole)
            if self.state.model.hasDeletedEntry(eid):
                with Lib.Qt.DisableUI(self, forModalDialog=True):
                    reply = QMessageBox.question(
                        self, "Delete Revivable Entry — {}".format(
                            QApplication.applicationName()),
                        "<p>Permanently delete revivable entry<br>“{}”?"
                        .format(item.text()),
                        QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                if reply == QMessageBox.Yes:
                    with Lib.DisableUI(self):
                        self.state.model.deleteDeletedEntry(eid)
                        self.populate()
                    self.updateUi()
        Lib.restoreFocus(widget)


if __name__ == "__main__":
    import collections
    import Qrc # noqa
    import HelpForm
    DeletedEntry = collections.namedtuple("DeletedEntry",
                                          "eid term pages peid")
    data = {}
    for eid, term in enumerate((
        "X-Ray", "Delta", "Alpha", "Kilo", "Echo", "Juliet", "Uniform",
        "Oscar", "Tango", "Foxtrot", "Hotel", "Golf", "Victor", "Romeo",
        "Papa", "Lima", "India", "Mike", "November", "Sierra", "Whisky",
        "Bravo", "Charlie", "Zulu", "Quebec", "Yankee",),
            1):
        data[eid] = term
    class FakeModel:
        def deletedEntries(self):
            for eid, term in sorted(data.items(),
                                    key=lambda i: (i[0] % 5, i[1])):
                yield DeletedEntry(eid, term, str(eid), eid % 5)
        def hasDeletedEntry(self, eid):
            return eid in data
        def deleteDeletedEntry(self, eid):
            del data[eid]
    class FakeState:
        def __init__(self):
            self.model = FakeModel()
            self.stdFontFamily = "Times New Roman"
            self.stdFontSize = 13
            self.altFontFamily = "Arial"
            self.altFontSize = 13
            self.monoFontFamily = "Courier New"
            self.monoFontSize = 12
            self.window = None
            self.helpForm = None
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
    form.show()
    app.exec_()
