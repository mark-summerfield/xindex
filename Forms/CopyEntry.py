#!/usr/bin/env python3
# Copyright © 2016-20 Qtrac Ltd. All rights reserved.

if __name__ == "__main__":
    import os
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import collections
import re

from PySide.QtCore import QSettings
from PySide.QtGui import (
    QApplication, QCheckBox, QDialog, QDialogButtonBox, QGroupBox,
    QHBoxLayout, QIcon, QLabel, QPushButton, QRadioButton, QVBoxLayout)

import Forms.Util
import Lib
import Widgets
import Widgets.LineEdit
from Config import Gopt
from Const import MAX_RECENT, ROOT, say, SAY_TIMEOUT


@Lib.updatable_tooltips
class Form(QDialog):

    def __init__(self, state, parent=None):
        super().__init__(parent)
        Lib.prepareModalDialog(self)
        self.state = state
        self.setWindowTitle("Copy Entry — {}".format(
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
        self.entryLabel = QLabel("Copy ")
        termText = Lib.elidePatchHtml(self.selectedEntry.term, self.state)
        self.termLabel = Widgets.Label.HtmlLabel("“{}”".format(termText))

        self.eidGroup = QGroupBox()

        self.copyToTopRadioButton = QRadioButton("to be a &Main Entry")
        self.tooltips.append((self.copyToTopRadioButton, """\
<p><b>to be a Main Entry</b></p>
<p>Copy the original entry to be a Main Entry (even if it is
already).</p>"""))
        self.subentryRadioButton = QRadioButton(
            "to be a &Subentry of itself")
        self.tooltips.append((self.subentryRadioButton, """\
<p><b>to be a Subentry of itself</b></p>
<p>Copy the original entry to be a subentry of the original entry.</p>"""))
        self.siblingRadioButton = QRadioButton(
            "to be a Si&bling of itself")
        self.tooltips.append((self.subentryRadioButton, """\
<p><b>to be a Sibling of itself</b></p>
<p>Copy the original entry to be a sibling of itself, i.e., to be a
subentry of the original entry's parent.</p>"""))

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
<p>Copy the current entry under a recently visited entry.</p>"""))

        self.filteredLabel = Widgets.Label.HtmlLabel()
        self.circledLabel = Widgets.Label.HtmlLabel()

        self.copyToTopRadioButton.setChecked(True)
        seen = {selectedEid}
        self.buttons = (self.copyToTopRadioButton,
                        self.subentryRadioButton,
                        self.filteredRadioButton,
                        self.circledRadioButton, self.recentRadioButton)
        Forms.Util.setUpRadioButton(
            self, self.filteredEntry, self.filteredRadioButton,
            self.filteredLabel, self.buttons, seen,
            """<p><b>under Filtered</b></p>
<p>Copy the current entry under the filtered entry “{}”.</p>""")
        Forms.Util.setUpRadioButton(
            self, self.circledEntry, self.circledRadioButton,
            self.circledLabel, self.buttons, seen,
            """<p><b>under Circled</b></p>
<p>Copy the current entry under the circled entry “{}”.</p>""")
        self.recentComboBox = Forms.Util.createTermsComboBox(
            self.state, self.state.gotoEids, ignore=seen,
            maximum=MAX_RECENT)

        self.optionsGroup = QGroupBox()
        self.copyAllCheckBox = QCheckBox("Copy &All:")
        self.tooltips.append((self.copyAllCheckBox, """\
<p><b>Copy All</b></p>
<p>If you check this checkbox, the other Copy checkboxes are checked in
one go.</p>"""))
        self.copyXrefsCheckBox = QCheckBox("Cross-r&eferences")
        self.tooltips.append((self.copyXrefsCheckBox, """\
<p><b>Cross-references</b></p>
<p>Copy cross-references from the original entry(ies) to the copied
entry(ies).</p>"""))
        self.copyGroupsCheckBox = QCheckBox("&Groups")
        self.tooltips.append((self.copyGroupsCheckBox, """\
<p><b>Groups</b></p>
<p>Copy groups from the original entry(ies) to the copied
entry(ies).</p>
<p>If you check the <b>Link Pages...</b> checkbox, this checkbox will be
both checked and disabled, since linking is achieved by copying a linked
group (creating one if necessary).</p>"""))
        self.copySubentriesCheckBox = QCheckBox("S&ubentries")
        self.tooltips.append((self.copySubentriesCheckBox, """\
<p><b>Subentries</b></p>
<p>Copy the copied entry's subentries, subsubentries, and so on.</p>"""))
        self.linkPagesCheckBox = QCheckBox("&Link Pages between")
        self.linkLabel = Widgets.Label.HtmlLabel("“{}” and its copy".format(
            termText))
        self.tooltips.append((self.linkPagesCheckBox, """\
<p><b>Link Pages</b></p>
<p>If the original entry belongs to a linked group, its copy is added to
that linked group. If the original doesn't belong to a linked group, a
new linked group is created with the name of the original's term, and
both the original and its copy are added to this new linked group.</p>
<p>If you check the this checkbox, the <b>Copy Groups</b> checkbox will be
both checked and disabled, since linking is achieved by copying a linked
group (creating one if necessary).</p>"""))
        self.withSeeCheckBox = QCheckBox("A&dd a")
        self.withSeeLabel1 = Widgets.Label.HtmlLabel(
            "<i>see</i> cross-reference from the copy to “{}”"
            .format(termText))
        self.withSeeLabel2 = Widgets.Label.HtmlLabel(
            "and <i>don't</i> copy the pages")
        self.withSeeLabel2.setIndent(self.fontMetrics().width("WW"))

        self.buttonBox = QDialogButtonBox()
        self.copyButton = QPushButton(QIcon(":/copy.svg"), "C&opy")
        self.tooltips.append((self.copyButton, """<p><b>Copy</b></p>
<p>Copy the “{}” entry.</p>""".format(self.termLabel.text())))
        self.buttonBox.addButton(self.copyButton,
                                 QDialogButtonBox.AcceptRole)
        self.closeButton = QPushButton(QIcon(":/dialog-close.svg"),
                                       "&Cancel")
        self.tooltips.append((self.closeButton, """<p><b>Cancel</b></p>
<p>Close the dialog without making any changes to the index.</p>"""))
        self.buttonBox.addButton(self.closeButton,
                                 QDialogButtonBox.RejectRole)
        self.helpButton = QPushButton(QIcon(":/help.svg"), "Help")
        self.tooltips.append((self.helpButton,
                              "Help on the Copy Entry dialog"))
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
        eidLayout.addWidget(self.copyToTopRadioButton)
        eidLayout.addWidget(self.subentryRadioButton)
        eidLayout.addWidget(self.siblingRadioButton)
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
        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        hbox.addWidget(self.copyAllCheckBox)
        hbox.addWidget(self.copyXrefsCheckBox)
        hbox.addWidget(self.copyGroupsCheckBox)
        hbox.addWidget(self.copySubentriesCheckBox)
        hbox.addStretch()
        vbox.addLayout(hbox)
        hbox = QHBoxLayout()
        hbox.setSpacing(0)
        hbox.addWidget(self.linkPagesCheckBox)
        hbox.addWidget(self.linkLabel)
        hbox.addStretch()
        vbox.addLayout(hbox)
        hbox = QHBoxLayout()
        hbox.setSpacing(0)
        hbox.addWidget(self.withSeeCheckBox)
        hbox.addWidget(self.withSeeLabel1)
        hbox.addStretch()
        vbox.addLayout(hbox)
        vbox.addWidget(self.withSeeLabel2)
        self.optionsGroup.setLayout(vbox)
        layout.addWidget(self.optionsGroup)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)


    def createConnections(self):
        self.buttonBox.accepted.connect(self.copy)
        self.buttonBox.rejected.connect(self.reject)
        self.helpButton.clicked.connect(self.help)
        self.copyXrefsCheckBox.toggled.connect(self.updateUi)
        self.copyGroupsCheckBox.toggled.connect(self.updateUi)
        self.copySubentriesCheckBox.toggled.connect(self.updateUi)
        self.linkPagesCheckBox.toggled.connect(self.updateUi)
        self.withSeeCheckBox.toggled.connect(self.updateUi)
        self.copyAllCheckBox.toggled.connect(self.copyAll)
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
        enable = not self.withSeeCheckBox.isChecked()
        for widget in (self.copyAllCheckBox, self.copyXrefsCheckBox,
                       self.copyGroupsCheckBox,
                       self.copySubentriesCheckBox, self.linkPagesCheckBox):
            if not enable:
                widget.setChecked(False)
            widget.setEnabled(enable)
        self.linkLabel.setEnabled(enable)
        if enable:
            if self.linkPagesCheckBox.isChecked():
                self.copyGroupsCheckBox.setChecked(True)
                self.copyGroupsCheckBox.setEnabled(False)
            else:
                self.copyGroupsCheckBox.setEnabled(True)
            self.copyAllCheckBox.setChecked(
                all(widget.isChecked() for widget in (
                    self.copyXrefsCheckBox, self.copyGroupsCheckBox,
                    self.copySubentriesCheckBox)))


    def copyAll(self, checked):
        if checked:
            for widget in (self.copyXrefsCheckBox, self.copyGroupsCheckBox,
                           self.copySubentriesCheckBox):
                widget.setChecked(True)


    def help(self):
        self.state.help("xix_ref_dlg_copy.html")


    def copy(self):
        self.state.maybeSave()
        eid = self.selectedEntry.eid
        peid = None
        if self.copyToTopRadioButton.isChecked():
            peid = ROOT
            description = "copy “{}” to be main entry"
        elif self.subentryRadioButton.isChecked():
            peid = eid
            description = "copy “{}” to be subentry of itself"
        elif self.siblingRadioButton.isChecked():
            peid = self.selectedEntry.peid
            description = "copy “{}” to be sibling of itself"
        elif self.filteredRadioButton.isChecked():
            peid = self.filteredEntry.eid
            description = "copy “{}” under filtered"
        elif self.circledRadioButton.isChecked():
            peid = self.circledEntry.eid
            description = "copy “{}” under circled"
        elif self.recentRadioButton.isChecked():
            peid = self.recentComboBox.itemData(
                self.recentComboBox.currentIndex())
            description = "copy “{}” under recently visited"
        if peid is not None: # Should always be True
            description = description.format(Lib.elidePatchHtml(
                self.selectedEntry.term, self.state))
            self.state.model.copyEntry(Lib.CopyInfo(
                eid, peid, self.copyXrefsCheckBox.isChecked(),
                self.copyGroupsCheckBox.isChecked(),
                self.copySubentriesCheckBox.isChecked(),
                self.linkPagesCheckBox.isChecked(),
                self.withSeeCheckBox.isChecked(), description))
            say(re.sub(r"^copy", "Copied", Lib.htmlToPlainText(
                description)), SAY_TIMEOUT)
        self.accept()


if __name__ == "__main__":
    import sys
    import Qrc # noqa
    import HelpForm
    Entry = collections.namedtuple("Entry", "eid term peid")
    class FakeModel:
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
        def addGenericXRef(self, from_eid, term, kind):
            print("addGenericXRef {} [{}] {}".format(from_eid, term, kind))
        def addXRef(self, from_eid, to_eid, kind):
            print("addXRef {} {} {}".format(from_eid, to_eid, kind))
        def allGroups(self):
            for t in ((1, "Unlinked 1", False), (2, "Unlinked 2", False),
                      (3, "Linked", True)):
                yield t
        def copyEntry(self, info):
            print("copyEntry", ascii(info))
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
            self.gotoEids = []
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
        state.gotoEids = [500, 600]
    form = Form(state)
    state.window = form
    form.show()
    app.exec_()
