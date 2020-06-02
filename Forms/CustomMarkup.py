#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

if __name__ == "__main__":
    import os
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    import Forms.CustomMarkupPanels as CustomMarkupPanels
else:
    from . import CustomMarkupPanels

from PySide.QtCore import QSettings, Qt
from PySide.QtGui import (
    QApplication, QComboBox, QDialog, QDialogButtonBox, QHBoxLayout,
    QIcon, QInputDialog, QLabel, QMessageBox, QPushButton, QTabWidget,
    QVBoxLayout)

import Lib
import Output.Markup
from Config import Gopt
from Const import FileKind, UTF8


@Lib.updatable_tooltips
class Form(QDialog): # Only use if there's a model present

    def __init__(self, state, parent=None):
        super().__init__(parent)
        Lib.prepareModalDialog(self)
        self.state = state
        self.formatActions = None
        self.extension = None
        self.markup = None
        self.dirty = False
        self.setWindowTitle("Custom Markup — {}".format(
                            QApplication.applicationName()))
        self.createWidgets()
        self.layoutWidgets()
        self.createConnections()
        self.refresh()
        settings = QSettings()
        self.updateToolTips(bool(int(settings.value(
            Gopt.Key.ShowDialogToolTips, Gopt.Default.ShowDialogToolTips))))


    def createWidgets(self):
        self.extensionLabel = QLabel("&Extension")
        self.extensionComboBox = QComboBox()
        for markup in self.state.model.markups():
            self.extensionComboBox.addItem(markup)
        self.tooltips.append((self.extensionComboBox, """\
<p><b>Extension</b></p>
<p>Choose the file extension to view and edit its custom markup.</p>"""))
        self.extensionLabel.setBuddy(self.extensionComboBox)
        self.helpButton = QPushButton(QIcon(":/help.svg"), "Help")
        self.tooltips.append((self.helpButton,
                              "Help on the Custom Markup dialog"))
        self.addButton = QPushButton(QIcon(":/add.svg"), "&Add...")
        self.tooltips.append((self.addButton, """\
<p><b>Add</b></p>
<p>Add a new custom markup to the index.</p>"""))
        self.deleteButton = QPushButton(QIcon(":/delete.svg"), "&Delete...")
        self.tooltips.append((self.deleteButton, """\
<p><b>Delete</b></p>
<p>Permanently delete the custom markup from the index's <tt>.xix</tt>
file. (Note that <tt>.ucp</tt> custom markup cannot be deleted.)</p>"""))
        self.closeButton = QPushButton(QIcon(":/dialog-close.svg"),
                                       "&Close")
        self.tooltips.append((self.closeButton, """<p><b>Close</b></p>
<p>Close the dialog.</p>"""))
        self.tabWidget = QTabWidget()
        self.documentPanel = CustomMarkupPanels.Document.Panel(self.state,
                                                               self)
        self.characterPanel = CustomMarkupPanels.Character.Panel(self.state,
                                                                 self)
        self.tabWidget.addTab(self.documentPanel, "D&ocument")
        self.tabWidget.addTab(self.characterPanel, "C&haracter")


    def layoutWidgets(self):
        buttonBox = QDialogButtonBox()
        buttonBox.addButton(self.helpButton, QDialogButtonBox.HelpRole)
        buttonBox.addButton(self.addButton, QDialogButtonBox.ActionRole)
        buttonBox.addButton(self.deleteButton, QDialogButtonBox.ActionRole)
        buttonBox.addButton(self.closeButton, QDialogButtonBox.AcceptRole)
        hbox = QHBoxLayout()
        hbox.addWidget(self.extensionLabel)
        hbox.addWidget(self.extensionComboBox)
        hbox.addStretch()
        hbox.addWidget(buttonBox)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addWidget(self.tabWidget, 1)

        self.setLayout(vbox)


    def createConnections(self):
        self.helpButton.clicked.connect(self.help)
        self.extensionComboBox.currentIndexChanged.connect(self.refresh)
        self.addButton.clicked.connect(self.add)
        self.deleteButton.clicked.connect(self.delete)
        self.closeButton.clicked.connect(self.accept)
        self.documentPanel.changed.connect(self.setDirty)
        self.characterPanel.changed.connect(self.setDirty)


    def help(self):
        self.state.help("xix_ref_dlg_markup.html")


    def setDirty(self):
        self.dirty = True


    def refresh(self):
        self.save()
        self.extension = self.extensionComboBox.currentText()
        if self.extension not in self.state.model.markups():
            self.markup = Output.Markup.user_markup()
        else:
            self.markup = self.state.model.markup(self.extension)
        self.documentPanel.populateFromMarkup(self.markup)
        self.characterPanel.populateFromMarkup(self.markup)
        self.deleteButton.setEnabled(self.extension != ".ucp")


    def save(self):
        if self.dirty and self.extension is not None:
            self.documentPanel.updateMarkup(self.markup)
            self.characterPanel.updateMarkup(self.markup)
            self.state.model.updateMarkup(self.extension, self.markup)
        self.dirty = False


    def add(self): # No need to restore focus widget
        self.save()
        with Lib.DisableUI(self, forModalDialog=True):
            extension, ok = QInputDialog.getText(
                self, "Add Custom Markup -— {}".format(
                    QApplication.applicationName()), "Extension")
        if ok and extension and extension.strip():
            extension = extension.strip()
            if not extension.startswith("."):
                extension = "." + extension
            index = self.extensionComboBox.findText(extension,
                                                    Qt.MatchExactly)
            if index != -1:
                self.extensionComboBox.setCurrentIndex(index)
            else:
                self.extension = extension
                self.markup = Output.Markup.user_markup()
                self.state.model.updateMarkup(self.extension, self.markup)
                self.extensionComboBox.addItem(extension)
                self.extensionComboBox.setCurrentIndex(
                    self.extensionComboBox.count() - 1)


    def delete(self): # No need to restore focus widget
        index = self.extensionComboBox.currentIndex()
        if index == -1:
            return
        with Lib.Qt.DisableUI(self, forModalDialog=True):
            extension = self.extensionComboBox.currentText()
            reply = QMessageBox.question(
                self, "Delete Custom Markup — {}".format(
                    QApplication.applicationName()), """<p>Delete “{}”?<p>
<font color=red>Warning: deleting custom markup cannot be undone.</font>"""
                .format(extension),
                QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.extensionComboBox.removeItem(index)
            if index < self.extensionComboBox.count():
                self.extensionComboBox.setCurrentIndex(index)
            else:
                self.extensionComboBox.setCurrentIndex(max(0, index - 1))
            self.state.model.deleteMarkup(extension)


    def reject(self):
        self.accept()


    def accept(self):
        self.save()
        super().accept()


if __name__ == "__main__":
    import Qrc # noqa
    import HelpForm
    class FakeModel:
        def updateMarkup(self, extension, markup):
            print(extension)
            markup._dump()
        def markups(self):
            yield ".ucp"
        def markup(self, extension):
            markup = Output.Markup.Markup(FileKind.USER)
            markup.escapefunction = "ucp"
            markup.DocumentStart = ""
            markup.DocumentEnd = ""
            markup.Note = ""
            markup.SectionStart = ""
            markup.SectionEnd = "{nl}"
            markup.MainStart = "    <p>"
            markup.MainEnd = "</p>{nl}"
            markup.Sub1Start = "<h1>"
            markup.Sub1End = "</>{nl}"
            markup.Sub2Start = "<h2>"
            markup.Sub2End = "</>{nl}"
            markup.Sub3Start = "<h3>"
            markup.Sub3End = "</>{nl}"
            markup.Sub4Start = "<h4>"
            markup.Sub4End = "</>{nl}"
            markup.Sub5Start = "<h5>"
            markup.Sub5End = "</>{nl}"
            markup.Sub6Start = "<h6>"
            markup.Sub6End = "</>{nl}"
            markup.Sub7Start = "<h7>"
            markup.Sub7End = "</>{nl}"
            markup.Sub8Start = "<h8>"
            markup.Sub8End = "</>{nl}"
            markup.Sub9Start = "<h9>"
            markup.Sub9End = "</>{nl}"
            markup.Encoding = UTF8
            markup.RangeSeparator = "<#8211>"
            markup.Tab = "\t"
            markup.Newline = "\n"
            markup.AltFontStart = ""
            markup.AltFontEnd = ""
            markup.MonoFontStart = ""
            markup.MonoFontEnd = ""
            markup.StdFontStart = ""
            markup.StdFontEnd = ""
            markup.BoldStart = "<e1>"
            markup.BoldEnd = "</e1>"
            markup.ItalicStart = "<i>"
            markup.ItalicEnd = "</i>"
            markup.SubscriptEnd = "</sub>"
            markup.SubscriptStart = "<sub>"
            markup.SuperscriptEnd = "</sup>"
            markup.SuperscriptStart = "<sup>"
            markup.UnderlineStart = ""
            markup.UnderlineEnd = ""
            markup.StrikeoutStart = ""
            markup.StrikeoutEnd = ""
            return markup
    class FakeWindow:
        def __init__(self):
            self.formatActions = None
    class FakeState:
        def __init__(self):
            self.model = FakeModel()
            self.stdFontFamily = "Times New Roman"
            self.stdFontSize = 13
            self.altFontFamily = "Arial"
            self.altFontSize = 13
            self.monoFontFamily = "Courier New"
            self.monoFontSize = 12
            self.window = FakeWindow()
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
    state.window = form
    form.show()
    app.exec_()
