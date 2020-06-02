#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

if __name__ == "__main__":
    import os
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import collections
import os

from PySide.QtCore import QSettings
from PySide.QtGui import (
    QApplication, QCheckBox, QDialog, QDialogButtonBox, QFileDialog,
    QFrame, QGridLayout, QGroupBox, QHBoxLayout, QIcon, QLabel,
    QPushButton, QVBoxLayout)

import Lib
from Config import Gopt
from Const import EXTENSION, LanguageKind, ModeKind


CopyInfo = collections.namedtuple(
    "CopyInfo", ("oldname", "newname", "copyconfig", "copymarkup",
                 "copyspelling", "copyignored", "copyautoreplace",
                 "copygroups", "username", "language", "sortasrules",
                 "pagerangerules"))


@Lib.updatable_tooltips
class Form(QDialog):

    def __init__(self, state, parent=None):
        super().__init__(parent)
        Lib.prepareModalDialog(self)
        self.state = state
        self.setWindowTitle("New Empty Copy — {}".format(
                            QApplication.applicationName()))
        self.createWidgets()
        self.layoutWidgets()
        self.createConnections()
        self.updateUi()
        settings = QSettings()
        self.updateToolTips(bool(int(settings.value(
            Gopt.Key.ShowDialogToolTips, Gopt.Default.ShowDialogToolTips))))


    def createWidgets(self):
        self.filenameLabelLabel = QLabel("New Filename")
        self.filenameLabel = QLabel()
        self.filenameLabel.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        self.filenameButton = QPushButton("C&hoose...")
        self.tooltips.append((self.filenameButton, """\
<p><b>Choose</b></p>
<p>Choose the {} <tt>.xix</tt> file to copy the current index's options,
spelling words, etc., to.</p>""".format(QApplication.applicationName())))
        self.copyGroupBox = QGroupBox("Copy")
        self.configCheckBox = QCheckBox("&Options")
        self.tooltips.append((self.configCheckBox, """\
<p><b>Options</b></p>
<p>If checked, copy all the current index's option and output option
settings (language, sort as and page range rules, display preferences,
fonts, output style, etc.) to the new empty copy.</p>"""))
        self.spellWordsCheckBox = QCheckBox("&Spelling Words")
        self.tooltips.append((self.spellWordsCheckBox, """\
<p><b>Spelling Words</b></p>
<p>If checked, copy all the current index's spelling words to the new
empty copy.</p>"""))
        self.ignoredFirstWordsCheckBox = QCheckBox(
            "&Ignored Subentry Function Words")
        self.tooltips.append((self.ignoredFirstWordsCheckBox, """\
<p><b>Ignored Subentry Function Words</b></p>
<p>If checked, copy all the current index's ignored subentry function
words words to the new empty copy.</p>"""))
        self.customMarkupCheckBox = QCheckBox("Custom &Markup")
        self.tooltips.append((self.customMarkupCheckBox, """\
<p><b>Custom Markup</b></p>
<p>If checked, copy all the current index's custom markup to the new
empty copy.</p>"""))
        self.groupsCheckBox = QCheckBox("&Groups")
        self.tooltips.append((self.groupsCheckBox, """\
<p><b>Groups</b></p>
<p>If checked, copy all the current index's groups to the new empty
copy.</p>"""))
        self.autoReplaceCheckBox = QCheckBox("&Auto Replacements")
        self.tooltips.append((self.autoReplaceCheckBox, """\
<p><b>Auto Replacements</b></p>
<p>If checked, copy all the current index's auto replacements to the new
empty copy.</p>"""))
        for checkbox in (self.configCheckBox, self.spellWordsCheckBox,
                         self.ignoredFirstWordsCheckBox,
                         self.customMarkupCheckBox, self.groupsCheckBox,
                         self.autoReplaceCheckBox):
            checkbox.setChecked(True)
        self.helpButton = QPushButton(QIcon(":/help.svg"), "Help")
        self.tooltips.append((self.helpButton,
                              "Help on the New Empty Copy dialog"))
        self.newCopyButton = QPushButton(QIcon(":/document-new.svg"),
                                         "&New Empty Copy")
        self.tooltips.append((self.newCopyButton, """\
<p><b>New Empty Copy</b></p>
<p>Create a new empty index and copy the options, spelling words,
etc.&mdash;providing they have been checked&mdash;into the new
index.</p>"""))
        self.cancelButton = QPushButton(QIcon(":/dialog-close.svg"),
                                        "&Cancel")
        self.tooltips.append((self.cancelButton, """<p><b>Cancel</b></p>
<p>Close the dialog without making a new empty copy.</p>"""))


    def layoutWidgets(self):
        layout = QVBoxLayout()
        hbox = QHBoxLayout()
        hbox.addWidget(self.filenameLabelLabel)
        hbox.addWidget(self.filenameLabel, 1)
        hbox.addWidget(self.filenameButton)
        layout.addLayout(hbox)
        grid = QGridLayout()
        grid.addWidget(self.configCheckBox, 0, 0)
        grid.addWidget(self.autoReplaceCheckBox, 0, 1)
        grid.addWidget(self.spellWordsCheckBox, 1, 0)
        grid.addWidget(self.ignoredFirstWordsCheckBox, 1, 1)
        grid.addWidget(self.groupsCheckBox, 2, 0)
        grid.addWidget(self.customMarkupCheckBox, 2, 1)
        hbox = QHBoxLayout()
        hbox.addLayout(grid)
        hbox.addStretch()
        self.copyGroupBox.setLayout(hbox)
        layout.addWidget(self.copyGroupBox)
        layout.addStretch()
        buttonBox = QDialogButtonBox()
        buttonBox.addButton(self.newCopyButton, QDialogButtonBox.AcceptRole)
        buttonBox.addButton(self.cancelButton, QDialogButtonBox.RejectRole)
        buttonBox.addButton(self.helpButton, QDialogButtonBox.HelpRole)
        layout.addWidget(buttonBox)
        self.setLayout(layout)


    def createConnections(self):
        self.newCopyButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)
        self.helpButton.clicked.connect(self.help)
        self.filenameButton.clicked.connect(self.setFilename)


    def updateUi(self):
        filename = self.filenameLabel.text()
        self.newCopyButton.setEnabled(
            bool(filename) and
            filename != os.path.normpath(self.state.model.filename))


    def setFilename(self): # No need to restore focus widget
        with Lib.Qt.DisableUI(self, forModalDialog=True):
            filename, _ = QFileDialog.getSaveFileName(
                self, "New Empty Index — {}".format(
                    QApplication.applicationName()),
                self.state.indexPath,
                "{} index (*{})".format(QApplication.applicationName(),
                                        EXTENSION))
        if filename and not filename.casefold().endswith(EXTENSION):
            filename += EXTENSION
        if filename:
            self.state.indexPath = os.path.dirname(filename)
            self.filenameLabel.setText(os.path.normpath(filename))
            self.updateUi()


    def help(self):
        self.state.help("xix_ref_dlg_newcopy.html")


    def accept(self):
        settings = QSettings()
        language = LanguageKind(settings.value(Gopt.Key.Language,
                                               Gopt.Default.Language))
        if self.configCheckBox.isChecked():
            sortasrules = Gopt.Default.SortAsRules
            pagerangerules = Gopt.Default.PageRangeRules
        else:
            sortasrules = self.state.model.sortAsRules()
            pagerangerules = self.state.model.pageRangeRules()
        copyInfo = CopyInfo(self.state.model.filename,
                            self.filenameLabel.text(),
                            self.configCheckBox.isChecked(),
                            self.customMarkupCheckBox.isChecked(),
                            self.spellWordsCheckBox.isChecked(),
                            self.ignoredFirstWordsCheckBox.isChecked(),
                            self.autoReplaceCheckBox.isChecked(),
                            self.groupsCheckBox.isChecked(),
                            self.state.model.username, language,
                            sortasrules, pagerangerules)
        self.state.window.closeXix()
        self.state.model.copyEmpty(copyInfo)
        self.state.window.openXix(copyInfo.newname)
        self.state.entryPanel.clearForm()
        self.state.setMode(ModeKind.VIEW)
        super().accept()



if __name__ == "__main__":
    import collections
    import Qrc # noqa
    import HelpForm
    data = {}
    for eid, term in enumerate((
        "X-Ray", "Delta", "Alpha", "Kilo", "Echo", "Juliet", "Uniform",
        "Oscar", "Tango", "Foxtrot", "Hotel", "Golf", "Victor", "Romeo",
        "Papa", "Lima", "India", "Mike", "November", "Sierra", "Whisky",
        "Bravo", "Charlie", "Zulu", "Quebec", "Yankee",),
            1):
        data[eid] = term
    class FakeModel:
        def __init__(self):
            self.filename = "/tmp/1.xix"
            self.username = "mark"
        def sortAsRules(self):
            return "wordByWordISO999en"
        def pageRangeRules(self):
            return "pageRangeCMS16"
        def copyEmpty(self, copyInfo):
            print("copyEmpty", copyInfo)
    class FakeWindow:
        def closeXix(self):
            print("closeXix")
        def openXix(self, filename):
            print("openXix", filename)
    class FakeEntryPanel:
        def clearForm(self):
            pass
    class FakeState:
        def __init__(self):
            self.model = FakeModel()
            self.window = FakeWindow()
            self.helpForm = None
            self.indexPath = "/tmp"
            self.entryPanel = FakeEntryPanel()
        def setMode(self, kind):
            pass
        def help(self, page=None):
            if self.helpForm is None:
                self.helpForm = HelpForm.Form("xix_help.html")
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
