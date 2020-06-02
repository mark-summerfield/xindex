#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

if __name__ == "__main__":
    import os
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import collections

import apsw
from PySide.QtCore import QSettings, Qt
from PySide.QtGui import (
    QApplication, QDialog, QHBoxLayout, QIcon, QListWidget,
    QListWidgetItem, QMessageBox, QPushButton, QVBoxLayout)

import Lib
from Config import Gopt


Info = collections.namedtuple(
    "Info", "name desc help db SELECT INSERT UPDATE DELETE")

ADDING = "NEW"


class ListWidgetItem(QListWidgetItem):

    info = None
    refresh = None

    def setData(self, role, value):
        oldText = self.text()
        super().setData(role, value)
        if role == Qt.EditRole:
            cursor = self.info.db.cursor()
            if oldText == ADDING:
                cursor.execute(self.info.INSERT, (value,))
            else:
                cursor.execute(self.info.UPDATE, (value, oldText))
            self.refresh(text=value) # Order might have changed


@Lib.updatable_tooltips
class Form(QDialog):

    def __init__(self, state, info, parent=None):
        super().__init__(parent)
        Lib.prepareModalDialog(self)
        self.state = state
        ListWidgetItem.info = info
        ListWidgetItem.refresh = self.refresh
        self.info = info
        self.helpPage = info.help
        self.createWidgets()
        self.layoutWidgets()
        self.setWindowTitle("{} — {}".format(
            self.info.name, QApplication.applicationName()))
        self.refresh()
        settings = QSettings()
        self.updateToolTips(bool(int(settings.value(
            Gopt.Key.ShowDialogToolTips, Gopt.Default.ShowDialogToolTips))))


    def createWidgets(self):
        self.listWidget = QListWidget()
        self.buttonLayout = QVBoxLayout()
        for icon, text, slot, tip in (
                (":/add.svg", "&Add", self.add, """\
<p><b>Add</b></p><p>Add an item to the {}
list.</p>""".format(self.info.name)),
                (":/edit.svg", "&Edit", self.edit, """\
<p><b>Edit</b></p><p>Edit the {} list's current
item.</p>""".format(self.info.name)),
                (":/delete.svg", "&Remove...", self.remove, """\
<p><b>Remove</b></p><p>Remove the {} list's current
item.</p>""".format(self.info.name)),
                (":/help.svg", "Help", self.help, """\
Help on the {} dialog""".format(self.info.name)),
                (":/dialog-close.svg", "&Close", self.accept, """\
<p><b>Close</b></p><p>Close the dialog.</p>""")):
            button = QPushButton(QIcon(icon), text)
            button.setFocusPolicy(Qt.NoFocus)
            if text in {"&Close", "Help"}:
                self.buttonLayout.addStretch()
            self.buttonLayout.addWidget(button)
            button.clicked.connect(slot)
            self.tooltips.append((button, tip))
        self.tooltips.append((self.listWidget, self.info.desc))


    def layoutWidgets(self):
        layout = QHBoxLayout()
        layout.addWidget(self.listWidget)
        layout.addLayout(self.buttonLayout)
        self.setLayout(layout)


    def refresh(self, *, text=None):
        self.listWidget.clear()
        cursor = self.info.db.cursor()
        for row, record in enumerate(cursor.execute(self.info.SELECT)):
            item = ListWidgetItem(record[0])
            item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEditable |
                          Qt.ItemIsEnabled)
            item.setBackground(self.palette().base() if row % 2 else
                               self.palette().alternateBase())
            self.listWidget.addItem(item)
        if self.listWidget.count():
            self.listWidget.setCurrentRow(0)
            if text is not None:
                for i in range(self.listWidget.count()):
                    if self.listWidget.item(i).text() == text:
                        self.listWidget.setCurrentRow(i)
                        break


    def add(self):
        item = ListWidgetItem(ADDING)
        item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEditable |
                      Qt.ItemIsEnabled)
        self.listWidget.insertItem(0, item)
        self.listWidget.setCurrentRow(0)
        self.listWidget.editItem(item)


    def edit(self):
        item = self.listWidget.currentItem()
        if item is not None:
            self.listWidget.editItem(item)


    def remove(self): # No need to restore focus widget
        row = self.listWidget.currentRow()
        item = self.listWidget.item(row)
        if item is None:
            return
        with Lib.Qt.DisableUI(self, forModalDialog=True):
            reply = QMessageBox.question(
                self, "Remove {} — {}".format(
                    self.info.name, QApplication.applicationName()),
                "Remove {} “{}”?".format(self.info.name, item.text()),
                QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            cursor = self.info.db.cursor()
            cursor.execute(self.info.DELETE, (item.text(),))
            item = self.listWidget.takeItem(row)
            del item


    def help(self):
        self.state.help(self.helpPage)


if __name__ == "__main__":
    import Qrc # noqa
    import HelpForm
    app = QApplication(sys.argv)
    app.setOrganizationName("Qtrac Ltd.")
    app.setOrganizationDomain("qtrac.eu")
    app.setApplicationName("XindeX-Test")
    app.setApplicationVersion("1.0.0")
    class FakeState:
        def __init__(self):
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
    fruit = [(x,) for x in (
        "Banana", "Apple", "Elderberry", "Clementine", "Fig", "Guava",
        "Mango", "Honeydew Melon", "Date", "Watermelon", "Tangerine",
        "Ugli Fruit", "Juniperberry", "Kiwi", "Lemon", "Nectarine",
        "Plum", "Raspberry", "Strawberry", "Orange")]
    db = apsw.Connection(":memory:")
    cursor = db.cursor()
    cursor.execute("""CREATE TABLE fruit (
word TEXT PRIMARY KEY UNIQUE NOT NULL) WITHOUT ROWID;""")
    cursor.executemany("INSERT INTO fruit (word) VALUES (?);", fruit)
    info = Info(
        "Fruit",
        "Manage Fruit",
        "xix_ref_dlg_subignore.html",
        db,
        "SELECT word FROM fruit ORDER BY LOWER(word);",
        "INSERT OR REPLACE INTO fruit (word) VALUES (?);",
        "UPDATE fruit SET word = ? WHERE word = ?;",
        "DELETE FROM fruit WHERE word = ?;",
        )
    state = FakeState()
    form = Form(state, info)
    form.exec_()
    cursor = db.cursor()
    for record in cursor.execute(info.SELECT):
        print(record[0])
