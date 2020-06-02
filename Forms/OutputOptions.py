#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

if __name__ == "__main__":
    import os
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    import Forms.OutputPanels as OutputPanels
else:
    from . import OutputPanels

from PySide.QtCore import QSettings
from PySide.QtGui import (
    QApplication, QDialog, QDialogButtonBox, QIcon, QPrinter,
    QPushButton, QTabWidget, QVBoxLayout)

import Lib
from Config import Config, Gopt
from Const import (
    IndentKind, LanguageKind, PaperSizeKind, SeeAlsoPositionKind,
    StyleKind, XRefToSubentryKind)


@Lib.updatable_tooltips
class Form(QDialog):

    def __init__(self, state, parent=None):
        super().__init__(parent)
        Lib.prepareModalDialog(self)
        self.state = state
        self.config = Config()
        if bool(self.state.model):
            self.config = self.state.model.configs()
        self.setWindowTitle("Output Options — {}".format(
                            QApplication.applicationName()))
        self.createWidgets()
        self.layoutWidgets()
        self.createConnections()
        settings = QSettings()
        self.updateToolTips(bool(int(settings.value(
            Gopt.Key.ShowDialogToolTips, Gopt.Default.ShowDialogToolTips))))


    def createWidgets(self):
        self.tabWidget = QTabWidget()
        self.generalOutputPanel = OutputPanels.GeneralOutput.Panel(
            self.state, self.config, self)
        self.entryXRefOutputPanel = OutputPanels.EntryXRefOutput.Panel(
            self.state, self.config, self)
        self.subentryXRefOutputPanel = (
            OutputPanels.SubentryXRefOutput.Panel(self.state, self.config,
                                                  self))
        self.specificOutputPanel = OutputPanels.SpecificOutput.Panel(
            self.state, self.config, self)
        self.tabWidget.addTab(self.generalOutputPanel, "&1 General")
        self.tabWidget.addTab(self.entryXRefOutputPanel,
                              "&2 Entry Cross-references")
        self.tabWidget.addTab(self.subentryXRefOutputPanel,
                              "&3 Subentry Cross-references")
        self.tabWidget.addTab(self.specificOutputPanel,
                              "&4 Format Specific")
        self.helpButton = QPushButton(QIcon(":/help.svg"), "Help")
        self.tooltips.append((self.helpButton,
                              "Help on the Output Options dialog"))
        self.closeButton = QPushButton(QIcon(":/dialog-close.svg"),
                                       "&Close")
        self.tooltips.append((self.closeButton, """<p><b>Close</b></p>
<p>Close the dialog.</p>"""))


    def layoutWidgets(self):
        layout = QVBoxLayout()
        layout.addWidget(self.tabWidget)
        layout.addStretch()
        buttonBox = QDialogButtonBox()
        buttonBox.addButton(self.helpButton, QDialogButtonBox.HelpRole)
        buttonBox.addButton(self.closeButton, QDialogButtonBox.AcceptRole)
        layout.addWidget(buttonBox)
        self.setLayout(layout)


    def createConnections(self):
        self.helpButton.clicked.connect(self.help)
        self.closeButton.clicked.connect(self.accept)


    def help(self):
        self.state.help("xix_ref_dlg_output.html")


    def accept(self, *args):
        self.setEnabled(False)
        self._acceptOptions()
        if bool(self.state.model):
            self._acceptConfig()
        super().accept(*args)


    def _acceptOptions(self):
        settings = QSettings()
        size = PaperSizeKind.A4
        if self.specificOutputPanel.letterRadioButton.isChecked():
            size = PaperSizeKind.LETTER
        settings.setValue(Gopt.Key.PaperSize, int(size))
        if self.state.printer is not None:
            self.state.printer.setPaperSize(
                QPrinter.A4 if size is PaperSizeKind.A4 else
                QPrinter.Letter)


    def _acceptConfig(self):
        model = self.state.model
        config = Config()
        config.Title = self.generalOutputPanel.titleTextEdit.toHtml()
        config.Note = self.generalOutputPanel.noteTextEdit.toHtml()
        config.SectionPreLines = (self.generalOutputPanel
                                  .blankBeforeSpinBox.value())
        config.SectionPostLines = (self.generalOutputPanel
                                   .blankAfterSpinBox.value())
        config.SectionTitles = (self.generalOutputPanel
                                .sectionTitlesCheckBox.isChecked())
        config.MonoFontAsStrikeout = (
            self.generalOutputPanel.monoFontAsStrikeoutCheckbox.isChecked())
        index = self.generalOutputPanel.styleComboBox.currentIndex()
        config.Style = StyleKind(self.generalOutputPanel.styleComboBox
                                 .itemData(index))
        config.RunInSeparator = (self.generalOutputPanel
                                 .runInSepTextEdit.toHtml())
        config.SectionSpecialTitle = (
            self.generalOutputPanel.sectionSpecialTitleTextEdit.toHtml())
        config.TermPagesSeparator = (self.generalOutputPanel
                                     .termPagesSepTextEdit.toHtml())
        config.SeePrefix = (self.entryXRefOutputPanel
                            .seePrefixTextEdit.toHtml())
        config.See = self.entryXRefOutputPanel.seeTextEdit.toHtml()
        config.SeeSeparator = (self.entryXRefOutputPanel
                               .seeSepTextEdit.toHtml())
        config.SeeSuffix = (self.entryXRefOutputPanel
                            .seeSuffixTextEdit.toHtml())
        config.SeeAlsoPrefix = (self.entryXRefOutputPanel
                                .seeAlsoPrefixTextEdit.toHtml())
        config.SeeAlso = self.entryXRefOutputPanel.seeAlsoTextEdit.toHtml()
        config.SeeAlsoSeparator = (self.entryXRefOutputPanel
                                   .seeAlsoSepTextEdit.toHtml())
        config.SeeAlsoSuffix = (self.entryXRefOutputPanel
                                .seeAlsoSuffixTextEdit.toHtml())
        index = (self.entryXRefOutputPanel.seeAlsoPositionComboBox
                 .currentIndex())
        config.SeeAlsoPosition = (
            self.entryXRefOutputPanel.seeAlsoPositionComboBox.itemData(
                index))
        config.GenericConjunction = (
            self.entryXRefOutputPanel.genericConjunctionTextEdit.toHtml())
        index = (self.entryXRefOutputPanel.xrefToSubentryComboBox
                 .currentIndex())
        config.XRefToSubentry = (
            self.entryXRefOutputPanel.xrefToSubentryComboBox.itemData(
                index))
        config.SubSeePrefix = (self.subentryXRefOutputPanel
                               .seePrefixTextEdit.toHtml())
        config.SubSee = self.subentryXRefOutputPanel.seeTextEdit.toHtml()
        config.SubSeeSeparator = (self.subentryXRefOutputPanel
                                  .seeSepTextEdit.toHtml())
        config.SubSeeSuffix = (self.subentryXRefOutputPanel
                               .seeSuffixTextEdit.toHtml())
        config.SubSeeAlsoPrefix = (self.subentryXRefOutputPanel
                                   .seeAlsoPrefixTextEdit.toHtml())
        config.SubSeeAlso = (self.subentryXRefOutputPanel
                             .seeAlsoTextEdit.toHtml())
        config.SubSeeAlsoSeparator = (self.subentryXRefOutputPanel
                                      .seeAlsoSepTextEdit.toHtml())
        config.SubSeeAlsoSuffix = (self.subentryXRefOutputPanel
                                   .seeAlsoSuffixTextEdit.toHtml())
        index = (self.subentryXRefOutputPanel.seeAlsoPositionComboBox
                 .currentIndex())
        config.SubSeeAlsoPosition = (
            self.subentryXRefOutputPanel.seeAlsoPositionComboBox
            .itemData(index))
        model.setConfigs(config)


if __name__ == "__main__":
    import Qrc # noqa
    import HelpForm
    class FakeWindow:
        def setIndexViewPosition():
            print("setIndexViewPosition")
    class FakeModel:
        def __bool__(self):
            return True
        def config(self, what, default=None):
            if what == "Language":
                return LanguageKind.AMERICAN
            elif what == "Indent":
                return IndentKind.FOUR_SPACES
            elif what == "StdFont":
                return "Times New Roman"
            elif what == "StdFontSize":
                return 13
            elif what == "AltFont":
                return "Arial"
            elif what == "AltFontSize":
                return 13
            elif what == "MonoFont":
                return "Courier New"
            elif what == "MonoFontSize":
                return 12
        def configs(self):
            config = Config()
            config.AltFont = "Arial"
            config.AltFontSize = 13
            config.Created = "2015-06-15 13:06:35"
            config.Creator = "Mark Summerfield"
            config.Indent = IndentKind.FOUR_SPACES
            config.Title = '<span style="font-size: 14pt;">Index</span>'
            config.Note = "Note"
            config.Language = LanguageKind.AMERICAN
            config.MonoFont = "DejaVu Sans Mono"
            config.MonoFontSize = 12
            config.MonoFontAsStrikeout = False
            config.Opened = 139
            config.See = "<i>see</i> "
            config.SeeAlso = "<i>see also</i> "
            config.SeeAlsoPosition = SeeAlsoPositionKind.AFTER_PAGES
            config.SeeAlsoPrefix = ". "
            config.SeeAlsoSeparator = "; "
            config.SeeAlsoSuffix = ""
            config.SeePrefix = ". "
            config.SeeSeparator = "; "
            config.SeeSuffix = ""
            config.GenericConjunction = " and "
            config.SubSee = "<i>see</i> "
            config.SubSeeAlso = "<i>see also</i> "
            config.SubSeeAlsoPosition = SeeAlsoPositionKind.AFTER_PAGES
            config.SubSeeAlsoPrefix = ". "
            config.SubSeeAlsoSeparator = "; "
            config.SubSeeAlsoSuffix = ""
            config.SubSeePrefix = ". "
            config.SubSeeSeparator = "; "
            config.SubSeeSuffix = ""
            config.StdFont = "Times New Roman"
            config.StdFontSize = 13
            config.TermPagesSeparator = ", "
            config.SortAsRules = "wordByWordCMS16"
            config.Updated = "2015-06-22 10:01:37"
            config.Worktime = 7325
            config.XRefToSubentry = XRefToSubentryKind.COLON
            config.SectionPreLines = 1
            config.SectionPostLines = 1
            config.SectionTitles = True
            config.SectionSpecialTitle = """<span style="font-size: \
10pt; font-family: 'Arial';"><b>Symbols &amp; Numbers</b>"""
            config.Style = StyleKind.INDENTED
            config.RunInSeparator = "; "
            return config
        def setConfig(self, what, value):
            print("setConfig {} [{}]".format(what, value))
        def setConfigs(self, config):
            for key, value in config:
                self.setConfig(key, value)
    class FakeState:
        def __init__(self):
            self.model = FakeModel()
            self.window = FakeWindow()
            self.printer = None
            self.user = "mark"
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
        def setSortAsRules(self, name, *args):
            print("FAKE setSortAsRules", name)
        def setPageRangeRules(self, name, *args):
            print("FAKE setPageRangeRules", name)
        def updateDisplayFonts(self):
            print("updateDisplayFonts")
    app = QApplication([])
    app.setOrganizationName("Qtrac Ltd.")
    app.setOrganizationDomain("qtrac.eu")
    app.setApplicationName("XindeX-Test")
    app.setApplicationVersion("1.0.0")
    state = FakeState()
    form = Form(state)
    form.show()
    app.exec_()
