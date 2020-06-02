#!/usr/bin/env python3
# Copyright © 2016-20 Qtrac Ltd. All rights reserved.

if __name__ == "__main__":
    import os
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from PySide.QtCore import QSettings, Qt
from PySide.QtGui import (
    QApplication, QDialog, QHBoxLayout, QIcon, QListWidget,
    QListWidgetItem, QMessageBox, QPushButton, QVBoxLayout)

import Forms
import Lib
from Config import Gopt


class ListWidgetItem(QListWidgetItem):

    model = None
    refresh = None

    def __init__(self, text, parent=None, *, adding=False):
        super().__init__(text, parent)
        self.adding = adding


    def setData(self, role, value):
        super().setData(role, value)
        if role == Qt.EditRole:
            if self.adding:
                self.adding = False
                gid = self.model.addGroup(value)
                super().setData(Qt.UserRole, gid)
            else:
                gid = self.data(int(Qt.UserRole))
                self.model.renameGroup(gid, value)
            self.refresh(text=value) # Order might have changed


@Lib.updatable_tooltips
class Form(QDialog):

    def __init__(self, term, state, parent=None):
        super().__init__(parent)
        Lib.prepareModalDialog(self)
        self.addingText = term
        self.state = state
        ListWidgetItem.model = state.model
        ListWidgetItem.refresh = self.refresh
        self.buttons = []
        self.createWidgets()
        self.layoutWidgets()
        self.createConnections()
        self.setWindowTitle("Edit Groups — {}".format(
                            QApplication.applicationName()))
        self.refresh()
        settings = QSettings()
        self.updateToolTips(bool(int(settings.value(
            Gopt.Key.ShowDialogToolTips, Gopt.Default.ShowDialogToolTips))))


    def createWidgets(self):
        self.listWidget = QListWidget()
        self.buttonLayout = QVBoxLayout()
        self.linkButton = None
        for icon, text, slot, tip in (
                (":/add.svg", "&Add", self.add, """\
<p><b>Add</b> (Alt+A)</p><p>Add a new Normal Group.</p>"""),
                (":/edit.svg", "&Rename", self.rename, """\
<p><b>Rename</b> (Alt+R)</p><p>Rename the current Group.</p>"""),
                (":/grouplink.svg", "&Link", self.link, """\
<p><b>Link</b> (Alt+L)</p><p>Change the current group into a Linked
Group.</p>
<p>This means that the pages of every entry in this group will be merged
and synchronized, and any future changes to the pages of any entries in
this group will be propagated to all the other entries in this
group to keep them all synchronized.</p>"""),
                (":/groups.svg", "&Unlink", self.unlink, """\
<p><b>Unlink</b> (Alt+U)</p><p>Change the current group into a Normal
(unlinked) Group. If the linked group
has entries, the <b>Delete Linked Group</b> dialog will pop up.</p>"""),
                (":/groupset.svg", "&View", self.viewGroup, """\
<p><b>View</b> (Alt+V)</p><p>View the current group in the Filtered
View.</p>"""),
                (":/delete.svg", "&Delete", self.delete, """\
<p><b>Delete</b> (Alt+D)</p><p>Remove entries from the current normal group
and then delete the group. If the current group is a linked group that
has entries, the <b>Delete Linked Group</b> dialog will pop up.</p>"""),
                (":/help.svg", "Help", self.help, """\
Help on the Groups dialog"""),
                (":/dialog-close.svg", "&Close", self.accept, """\
<p><b>Close</b></p><p>Close the dialog.</p>""")):
            button = QPushButton(QIcon(icon), text)
            button.setFocusPolicy(Qt.NoFocus)
            if text in {"&Close", "Help"}:
                self.buttonLayout.addStretch()
            else:
                self.buttons.append(button)
            self.buttonLayout.addWidget(button)
            button.clicked.connect(slot)
            self.tooltips.append((button, tip))
            if text == "&Link":
                self.linkButton = button
                button.setEnabled(False)
            elif text == "&Unlink":
                self.unlinkButton = button
                button.setEnabled(False)
        self.tooltips.append((self.listWidget, "List of Groups"))


    def layoutWidgets(self):
        layout = QHBoxLayout()
        layout.addWidget(self.listWidget)
        layout.addLayout(self.buttonLayout)
        self.setLayout(layout)


    def createConnections(self):
        self.listWidget.currentRowChanged.connect(self.updateUi)


    def updateUi(self):
        for button in self.buttons:
            button.setEnabled(True)
        item = self.listWidget.currentItem()
        if item is not None:
            gid = item.data(Qt.UserRole)
            self.linkButton.setEnabled(self.state.model.safeToLinkGroup(
                                       gid))
            self.unlinkButton.setEnabled(self.state.model.isLinkedGroup(
                                         gid))


    def refresh(self, *, text=None, index=None):
        self.listWidget.clear()
        for row, (gid, name, linked) in enumerate(
                self.state.model.allGroups()):
            item = ListWidgetItem(name)
            item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEditable |
                          Qt.ItemIsEnabled)
            item.setBackground(self.palette().base() if row % 2 else
                               self.palette().alternateBase())
            item.setData(Qt.UserRole, gid)
            item.setIcon(QIcon(":/grouplink.svg" if linked else
                               ":/groups.svg"))
            self.listWidget.addItem(item)
        if self.listWidget.count():
            self.listWidget.setCurrentRow(0)
            if index is not None:
                self.listWidget.setCurrentRow(index)
            elif text is not None:
                for i in range(self.listWidget.count()):
                    if self.listWidget.item(i).text() == text:
                        self.listWidget.setCurrentRow(i)
                        break
        self.updateUi()


    def add(self):
        item = ListWidgetItem(self.addingText, adding=True)
        item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEditable |
                      Qt.ItemIsEnabled)
        self.listWidget.insertItem(0, item)
        self.listWidget.setCurrentRow(0)
        for button in self.buttons:
            button.setEnabled(False)
        self.listWidget.editItem(item)


    def rename(self):
        item = self.listWidget.currentItem()
        if item is not None:
            for button in self.buttons:
                button.setEnabled(False)
            self.listWidget.editItem(item)


    def link(self):
        item = self.listWidget.currentItem()
        if item is not None:
            gid = item.data(Qt.UserRole)
            if not self.state.model.safeToLinkGroup(gid):
                return # Should never happen
            self.state.model.linkGroup(gid)
            self.refresh(index=self.listWidget.currentRow())


    def unlink(self):
        item = self.listWidget.currentItem()
        if item is not None:
            gid = item.data(Qt.UserRole)
            if not self.state.model.groupMemberCount(gid):
                self.state.model.unlinkGroup(gid)
            else:
                with Lib.Qt.DisableUI(self, forModalDialog=True):
                    form = Forms.DeleteOrUnlink.Form("Unlink", gid,
                                                     self.state, self)
                    form.exec_()
            self.refresh(index=self.listWidget.currentRow())


    def viewGroup(self):
        item = self.listWidget.currentItem()
        if item:
            self.state.viewFilteredPanel.setGroup(item)


    def delete(self): # No need to restore focus widget
        row = self.listWidget.currentRow()
        item = self.listWidget.item(row)
        if item is None:
            return
        gid = item.data(Qt.UserRole)
        for button in self.buttons:
            button.setEnabled(False)
        deleteItem = False
        if (not self.state.model.isLinkedGroup(gid) or
                not self.state.model.groupMemberCount(gid)):
            with Lib.Qt.DisableUI(self, forModalDialog=True):
                reply = QMessageBox.question(
                    self, "Delete Group — {}".format(
                        QApplication.applicationName()),
                    "<p>Delete Group “{}”?</p>".format(item.text()),
                    QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.state.model.deleteGroup(gid)
                deleteItem = True
        else:
            with Lib.Qt.DisableUI(self, forModalDialog=True):
                form = Forms.DeleteOrUnlink.Form("Delete", gid, self.state,
                                                 self)
                deleteItem = form.exec_()
        if deleteItem:
            item = self.listWidget.takeItem(row)
            del item
        self.updateUi()


    def help(self):
        self.state.help("xix_ref_dlg_groups.html")


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
        def safeToLinkGroup(self, gid):
            return not self.isLinkedGroup(gid)
        def isLinkedGroup(self, gid):
            return gid % 2
        def allGroups(self):
            for gid, name in sorted(groups.items(), key=lambda p: p[1]):
                yield gid, name, gid % 2
        def nameForGid(self, gid):
            return groups[gid]
        def eidsForGid(self, gid):
            if gid in {5, 6}:
                return ()
            return entries.keys()
        def term(self, eid):
            return entries[eid]
        def linkGroup(self, gid):
            print("linkGroup", gid)
        def unlinkGroup(self, gid, *, eid=None):
            print("unlinkGroup", gid, eid)
        def deleteGroup(self, gid, *, eid=None):
            print("deleteGroup", gid, eid)
        def groupMemberCount(self, gid):
            if gid in {5, 6}:
                return 0
            return len(entries)
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
    form = Form("scene selection", state)
    state.window = form
    form.show()
    app.exec_()
