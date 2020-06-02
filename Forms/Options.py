#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

if __name__ == "__main__":
    import os
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    import Forms.OptionsPanels as OptionsPanels
else:
    from . import OptionsPanels

from PySide.QtCore import QSettings
from PySide.QtGui import (
    QApplication, QDialog, QDialogButtonBox, QIcon, QPushButton,
    QTabWidget, QVBoxLayout)

import Lib
from Config import Config, Gopt, Gconf
from Const import IndentKind, LanguageKind


@Lib.updatable_tooltips
class Form(QDialog):

    def __init__(self, state, parent=None):
        super().__init__(parent)
        Lib.prepareModalDialog(self)
        self.state = state
        self.config = Config()
        enable = bool(self.state.model)
        if enable:
            self.config = self.state.model.configs()
        self.setWindowTitle("Options — {}".format(
                            QApplication.applicationName()))
        self.createWidgets()
        self.layoutWidgets()
        self.createConnections()
        for widget in (self.generalPanel.thisLanguageComboBox,
                       self.rulesPanel.thisSortAsRulesBox,
                       self.rulesPanel.thisPageRangeRulesBox):
            widget.setEnabled(enable)
        settings = QSettings()
        self.updateToolTips(bool(int(settings.value(
            Gopt.Key.ShowDialogToolTips, Gopt.Default.ShowDialogToolTips))))


    def createWidgets(self):
        self.generalPanel = OptionsPanels.General.Panel(self.state,
                                                        self.config, self)
        self.rulesPanel = OptionsPanels.Rules.Panel(self.state,
                                                    self.config, self)
        self.displayPanel = OptionsPanels.Display.Panel(self.state,
                                                        self.config, self)
        self.tabWidget = QTabWidget()
        self.tabWidget.addTab(self.generalPanel, "&1  General")
        self.tabWidget.addTab(self.rulesPanel, "&2  Rules")
        self.tabWidget.addTab(self.displayPanel, "&3  Display")
        self.helpButton = QPushButton(QIcon(":/help.svg"), "Help")
        self.tooltips.append((self.helpButton,
                              "Help on the Options dialog"))
        self.closeButton = QPushButton(QIcon(":/dialog-close.svg"),
                                       "&Close")
        self.tooltips.append((self.closeButton, """<p><b>Close</b></p>
<p>Close the dialog, and apply any changes to the index.</p>"""))


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
        self.state.help("xix_ref_dlg_options.html")


    def accept(self, *args):
        self.setEnabled(False)
        config = self._acceptOptions()
        if bool(self.state.model):
            model = self.state.model
            model.setConfigs(config)
        super().accept(*args)


    def _acceptOptions(self): # No need to restore focus widget
        config = Config()
        settings = QSettings()

        creator = self.generalPanel.creatorLineEdit.text().strip()
        settings.setValue(Gopt.Key.Creator, creator)
        config.Creator = creator

        initials = self.generalPanel.initialsLineEdit.text().strip()
        settings.setValue(Gopt.Key.Initials, initials)
        config.Initials = initials

        config.PadDigits = self.rulesPanel.thisPadDigitsSpinBox.value()
        config.IgnoreSubFirsts = bool(
            self.rulesPanel.thisIgnoreSubFirstsCheckBox.isChecked())
        config.SuggestSpelled = bool(
            self.rulesPanel.thisSuggestSpelledCheckBox.isChecked())

        highest = self.config.get(Gconf.Key.HighestPageNumber)
        config.HighestPageNumber = (
            self.generalPanel.highestPageSpinBox.value())
        largest = self.config.get(Gconf.Key.LargestPageRange)
        config.LargestPageRange = (
            self.generalPanel.largestPageRangeSpinBox.value())
        most = self.config.get(Gconf.Key.MostPages)
        config.MostPages = self.generalPanel.mostPagesSpinBox.value()

        index = self.rulesPanel.thisSortAsRulesBox.currentIndex()
        name = self.rulesPanel.thisSortAsRulesBox.itemData(index)
        if self.rulesPanel.thisSortAsRules != name:
            with Lib.DisableUI(self):
                self.state.setSortAsRules(name, "Updating Sort As texts",
                                          self.state.window.reportProgress)

        index = self.rulesPanel.thisPageRangeRulesBox.currentIndex()
        name = self.rulesPanel.thisPageRangeRulesBox.itemData(index)
        if self.rulesPanel.thisPageRangeRules != name:
            with Lib.DisableUI(self):
                self.state.setPageRangeRules(
                    name, "Updating Pages texts",
                    self.state.window.reportProgress)

        if (highest != config.HighestPageNumber or
                largest != config.LargestPageRange or
                most != config.MostPages):
            self.state.viewFilteredPanel.requery()

        return config


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
            config.PageRangeRules = "pageRangeCMS16"
            config.Created = "2015-06-15 13:06:35"
            config.Creator = "Mark Summerfield"
            config.Indent = IndentKind.FOUR_SPACES
            config.Initials = "MS"
            config.Language = LanguageKind.AMERICAN
            config.MonoFont = "DejaVu Sans Mono"
            config.MonoFontSize = 12
            config.Opened = 139
            config.StdFont = "Times New Roman"
            config.StdFontSize = 13
            config.SortAsRules = "wordByWordCMS16"
            config.Updated = "2015-06-22 10:01:37"
            config.Worktime = 7325
            return config
        def setConfig(self, what, value):
            print("setConfig {} [{}]".format(what, value))
        def setConfigs(self, config):
            for key, value in config:
                self.setConfig(key, value)
    class FakeHighlighter:
        def rehighlight(self):
            pass
    class FakePanel:
        def __init__(self):
            self.spellHighlighter = FakeHighlighter()
    class FakeView:
        def requery(self):
            pass
    class FakeState:
        def __init__(self):
            self.model = FakeModel()
            self.window = FakeWindow()
            self.user = "mark"
            self.stdFontFamily = "Times New Roman"
            self.stdFontSize = 13
            self.altFontFamily = "Arial"
            self.altFontSize = 13
            self.monoFontFamily = "Courier New"
            self.monoFontSize = 12
            self.window = None
            self.entryPanel = FakePanel()
            self.helpForm = None
            self.viewFilteredPanel = FakeView()
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
