#!/usr/bin/env python3
# Copyright © 2016-20 Qtrac Ltd. All rights reserved.

if __name__ == "__main__":
    import os
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from PySide.QtCore import QSettings, Qt
from PySide.QtGui import (
    QApplication, QDialog, QDialogButtonBox, QIcon, QListWidget,
    QListWidgetItem, QVBoxLayout)

import Lib
from Config import Gopt


@Lib.updatable_tooltips
class Form(QDialog):

    def __init__(self, state, parent=None):
        super().__init__(parent)
        Lib.prepareModalDialog(self)
        self.state = state
        self.groups = set()
        self.createWidgets()
        self.layoutWidgets()
        self.createConnections()
        self.setWindowTitle("Choose Normal Group(s) — {}".format(
                            QApplication.applicationName()))
        settings = QSettings()
        self.updateToolTips(bool(int(settings.value(
            Gopt.Key.ShowDialogToolTips, Gopt.Default.ShowDialogToolTips))))


    def createWidgets(self):
        self.listWidget = QListWidget()
        for row, (gid, name) in enumerate(self.state.model.normalGroups()):
            item = QListWidgetItem(name)
            item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsUserCheckable |
                          Qt.ItemIsEnabled)
            item.setBackground(self.palette().base() if row % 2 else
                               self.palette().alternateBase())
            item.setCheckState(Qt.Unchecked)
            item.setData(Qt.UserRole, gid)
            item.setIcon(QIcon(":/groups.svg"))
            self.listWidget.addItem(item)
        self.tooltips.append((self.listWidget, "List of Normal Groups"))
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok |
                                        QDialogButtonBox.Cancel)


    def layoutWidgets(self):
        layout = QVBoxLayout()
        layout.addWidget(self.listWidget)
        layout.addWidget(self.buttons)
        self.setLayout(layout)


    def createConnections(self):
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)


    def accept(self):
        self.groups = set()
        for row in range(self.listWidget.count()):
            item = self.listWidget.item(row)
            if item.checkState() == Qt.Checked:
                self.groups.add(int(item.data(Qt.UserRole))) # gid
        super().accept()


    def reject(self):
        self.groups = set()
        super().reject()


    def help(self):
        pass


if __name__ == "__main__":
    import collections
    import Qrc # noqa
    import HelpForm
    Entry = collections.namedtuple("Entry", "eid term peid")
    app = QApplication([])
    app.setOrganizationName("Qtrac Ltd.")
    app.setOrganizationDomain("qtrac.eu")
    app.setApplicationName("XindeX-Test")
    app.setApplicationVersion("1.0.0")
    entries = {100: "term #1", 200: "term #2", 300: "term #3"}
    groups = {3: "scene selection", 5: "code generation",
              4: "special method", 6: "ttk widget"}
    class FakeModel:
        def normalGroups(self):
            for gid, name in sorted(groups.items(), key=lambda p: p[1]):
                yield gid, name
    class FakeState:
        def __init__(self):
            self.model = FakeModel()
            self.helpForm = None
            self.window = None
        def help(self, page=None):
            if self.helpForm is None:
                self.helpForm = HelpForm.Form("xix_help.html", self.window)
            if page is not None:
                self.helpForm.changePage(page)
            self.helpForm.show()
            self.helpForm.raise_()
            self.helpForm.activateWindow()
    state = FakeState()
    form = Form(state)
    state.window = form
    form.show()
    app.exec_()
    print(form.groups)
