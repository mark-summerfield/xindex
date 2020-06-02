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
    QApplication, QDialog, QHBoxLayout, QIcon, QMessageBox, QPushButton,
    QTableWidget, QTableWidgetItem, QVBoxLayout)

import Lib
import Sql
from Config import Gopt


Info = collections.namedtuple(
    "Info", "name desc help key value db SELECT EDIT DELETE COUNT")

Flags = Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsEnabled


class TableWidgetItem(QTableWidgetItem):

    info = None
    refresh = None

    def setData(self, role, value):
        if role == Qt.EditRole:
            oldText = self.text()
            cursor = self.info.db.cursor()
            if self.column() == 0: # Word
                cursor.execute(self.info.DELETE, dict(word=oldText))
                word = value
                replacement = self.tableWidget().item(self.row(), 1).text()
            else: # Replacement
                word = self.tableWidget().item(self.row(), 0).text()
                replacement = value
            cursor.execute(self.info.EDIT, dict(word=word,
                                                replacement=replacement))
            self.refresh(key=word) # Order might have changed
        else:
            super().setData(role, value)


@Lib.updatable_tooltips
class Form(QDialog):

    def __init__(self, state, info, parent=None):
        super().__init__(parent)
        Lib.prepareModalDialog(self)
        self.state = state
        TableWidgetItem.info = info
        TableWidgetItem.refresh = self.refresh
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
        self.tableWidget = QTableWidget()
        self.buttonLayout = QVBoxLayout()
        for icon, text, slot, tip in (
                (":/add.svg", "&Add", self.add, """\
<p><b>Add</b></p><p>Add a {} and {} to the {}
list.</p>""".format(self.info.key, self.info.value, self.info.name)),
                (":/edit.svg", "&Edit", self.edit, """\
<p><b>Edit</b></p><p>Edit the {} list's current
{} or {}.</p>""".format(self.info.name, self.info.key, self.info.value)),
                (":/delete.svg", "&Remove...", self.remove, """\
<p><b>Remove</b></p><p>Remove the {} list's current
{} and {}.</p>""".format(self.info.name, self.info.key, self.info.value)),
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
        self.tooltips.append((self.tableWidget, self.info.desc))


    def layoutWidgets(self):
        layout = QHBoxLayout()
        layout.addWidget(self.tableWidget)
        layout.addLayout(self.buttonLayout)
        self.setLayout(layout)


    def refresh(self, *, key=None):
        cursor = self.info.db.cursor()
        self._prepareTable(cursor)
        for row, record in enumerate(cursor.execute(self.info.SELECT)):
            word, replacement = record
            bg = (self.palette().base() if row % 2 else
                  self.palette().alternateBase())
            item = TableWidgetItem(record[0])
            item.setFlags(Flags)
            item.setBackground(bg)
            self.tableWidget.setItem(row, 0, item)
            item = TableWidgetItem(record[1])
            item.setFlags(Flags)
            item.setBackground(bg)
            self.tableWidget.setItem(row, 1, item)
        self.tableWidget.resizeColumnsToContents()
        if key is None and self.tableWidget.rowCount():
            self.tableWidget.setCurrentCell(0, 0)
        else:
            for row in range(self.tableWidget.rowCount()):
                if self.tableWidget.item(row, 0).text() == key:
                    self.tableWidget.setCurrentCell(row, 0)
                    break

    def _prepareTable(self, cursor):
        self.tableWidget.clear()
        count = Sql.first(cursor, self.info.COUNT, default=0)
        self.tableWidget.setRowCount(count)
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setHorizontalHeaderLabels([self.info.key,
                                                    self.info.value])


    def add(self):
        self.tableWidget.insertRow(0)
        edit = item = TableWidgetItem("$TEXT")
        item.setFlags(Flags)
        item.setBackground(self.palette().base())
        self.tableWidget.setItem(0, 0, item)
        item = TableWidgetItem("REPLACEMENT")
        item.setFlags(Flags)
        item.setBackground(self.palette().base())
        self.tableWidget.setItem(0, 1, item)
        self.tableWidget.setCurrentCell(0, 0)
        self.tableWidget.editItem(edit)


    def edit(self):
        item = self.tableWidget.currentItem()
        if item is not None:
            self.tableWidget.editItem(item)


    def remove(self): # No need to restore focus widget
        row = self.tableWidget.currentRow()
        if row < 0:
            return
        word = self.tableWidget.item(row, 0).text()
        replacement = self.tableWidget.item(row, 1).text()
        with Lib.Qt.DisableUI(self, forModalDialog=True):
            reply = QMessageBox.question(
                self, "Remove {} — {}".format(
                    self.info.name, QApplication.applicationName()),
                "Remove {}<br>“{}”→“{}”?".format(self.info.name, word,
                                                 replacement),
                QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            cursor = self.info.db.cursor()
            cursor.execute(self.info.DELETE, (word,))
            self.tableWidget.removeRow(row)


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
    data = [("$fbi", "Federal Bureau of Investigation"),
            ("$eu", "European Union"),
            ("$gs", "garden city"),
            ("$po", "Post Office"),
            ]
    db = apsw.Connection(":memory:")
    cursor = db.cursor()
    cursor.execute("""CREATE TABLE auto_replace (
word TEXT PRIMARY KEY UNIQUE NOT NULL,
replacement TEXT NOT NULL) WITHOUT ROWID;""")
    for word, replacement in data:
        cursor.execute(Sql.EDIT_AUTO_REPLACE,
                       dict(word=word, replacement=replacement))
    info = Info(
        "Auto Replace",
        "Manage Auto Replace",
        "xix_ref_dlg_autorep.html",
        "Text",
        "Replacement",
        db,
        Sql.SORTED_AUTO_REPLACE,
        Sql.EDIT_AUTO_REPLACE,
        Sql.DELETE_AUTO_REPLACE,
        Sql.AUTO_REPLACE_COUNT,
        )
    state = FakeState()
    form = Form(state, info)
    form.exec_()
    cursor = db.cursor()
    for record in cursor.execute(info.SELECT):
        print(record)
