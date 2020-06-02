#!/usr/bin/env python3
# Copyright © 2014-20 Qtrac Ltd. All rights reserved.

import logging
import os
import pathlib
import re

from PySide.QtCore import QDir, QSettings, Qt
from PySide.QtGui import (
    QApplication, QFileDialog, QKeySequence, QMessageBox, QPrintDialog,
    QPrinter)

import Forms
import Lib
import Output
from Config import Gopt
from Const import (
    error, EXPORT_EXTENSIONS, EXTENSION, IMPORT_EXTENSIONS, PaperSizeKind,
    say)


EXTENSION_EXTRACT_RX = re.compile(r"^.*?(\.[^)]+)\)$")


class Actions:

    def __init__(self, window):
        self.window = window
        self.state = self.window.state
        self.printer = None
        self.newAction = Lib.createAction(
            window, ":/document-new.svg", "&New Index...", self.new,
            QKeySequence.New, tooltip="""
<p><b>File→New Index</b> ({})</p>
<p>Create a new empty index with all options set to their default values.
</p>""".format(QKeySequence(QKeySequence.New).toString()))
        self.newEmptyCopyAction = Lib.createAction(
            window, ":/document-new.svg", "New &Empty Copy...",
            self.newEmptyCopy, tooltip="""
<p><b>File→New Empty Copy</b></p>
<p>Create a new empty index with all options set to the values in the
current index (except where specified otherwise).</p>""")
        self.openAction = Lib.createAction(
            window, ":/document-open.svg", "&Open...", self.open,
            QKeySequence.Open, """
<p><b>File→Open</b> ({})</p>
<p>Open an existing index.</p>""".format(QKeySequence(
                                         QKeySequence.Open).toString()))
        self.openRecentAction = Lib.createAction(
            window, ":/document-open.svg", "Open Re&cent", tooltip="""
<p><b>File→Open Recent</b></p>
<p>Open a recently opened index.</p>""")
        self.importAction = Lib.createAction(
            window, ":/document-open.svg", "&Import...", self.importIndex,
            tooltip="""
<p><b>File→Import</b></p>
<p>Import an index from a file in standard <tt>.ixml</tt> (indexdata) or
in {}'s own <tt>.ximl</tt> XML interchange format.</p>""".format(
                QApplication.applicationName()))
        self.backupAction = Lib.createAction(
            window, ":/filesave.svg", "&Backup...", self.backup,
            tooltip="""
<p><b>File→Backup</b></p>
<p>Save a backup of this index with a number added to the filename.""")
        self.saveAction = Lib.createAction(
            window, ":/filesave.svg", "&Save", self.state.maybeSave,
            QKeySequence.Save, tooltip="""
<p><b>File→Save</b> ({})</p>
<p>Save any unsaved changes. {} is very diligent about saving, so this
action is never really needed.""".format(
                QKeySequence(QKeySequence.Save).toString(),
                QApplication.applicationName()))
        self.saveAsAction = Lib.createAction(
            window, ":/filesaveas.svg", "Save &As...", self.saveAs,
            QKeySequence.SaveAs, """
<p><b>File→Save As</b> ({})</p>
<p>Save this index under a new name, then close the index under the old
name (with the index left intact) and open the index under its new name."""
            .format(QKeySequence(QKeySequence.SaveAs).toString()))
        self.saveGroupedAsAction = Lib.createAction(
            window, ":/filesaveas.svg", "Save &Grouped As...",
            self.saveGroupedAs, tooltip="""
<p><b>File→Save Grouped As</b></p>
<p>Save this index under a new name&mdash;but including only those
entries in the specified Normal Groups&mdash;then close the index under
the old name (with the index left intact) and open the index under its
new name.""")
        self.outputRtfAction = Lib.createAction(
            window, ":/exportrtf.svg", "Output As .&rtf", self.outputRtf,
            tooltip="""
<p><b>File→Output as .rtf</b></p>
<p>Output the index using its current name and folder, but formatted as
a Rich Text Format file with a .rtf extension.</p>""")
        self.outputDocxAction = Lib.createAction(
            window, ":/exportdocx.svg", "Output As .&docx", self.outputDocx,
            tooltip="""
<p><b>File→Output As .docx</b></p>
<p>Output the index using its current name and folder, but formatted as
a Word Office Open XML (OOXML) file with a .docx extension.</p>""")
        self.outputAsAction = Lib.createAction(
            window, ":/export.svg", "Ou&tput As...", self.outputIndexAs,
            tooltip="""
<p><b>File→Output As</b></p>
<p>Output the index in one of {}'s supported output
formats.</p>""".format(QApplication.applicationName()))
        self.printAction = Lib.createAction(
            window, ":/fileprint.svg", "&Print...", self.printIndex,
            QKeySequence.Print, """
<p><b>File→Print</b> ({})</p>
<p>Print the index.</p>""".format(QKeySequence(
                                  QKeySequence.Print).toString()))
        self.quitAction = Lib.createAction(
            window, ":/shutdown.svg", "&Quit", self.quit,
            # Can't use QKeySequence.Quit since it is blank on Windows
            QKeySequence(Qt.CTRL + Qt.Key_Q), """
<p><b>File→Quit</b> ({})</p>
<p>Save any unsaved changes and then close {}.</p>""".format(
                QKeySequence(Qt.CTRL + Qt.Key_Q).toString(),
                QApplication.applicationName()))


    def forMenu(self):
        return (self.newAction, self.newEmptyCopyAction, self.openAction,
                self.openRecentAction, self.importAction, None,
                self.backupAction, self.saveAction, self.saveAsAction,
                self.saveGroupedAsAction, self.outputRtfAction,
                self.outputDocxAction, self.outputAsAction, None,
                self.printAction, None, self.quitAction)


    def forToolbar(self):
        return (self.newAction, self.openAction, self.saveAction, None,
                self.outputRtfAction, self.outputDocxAction)


    def updateUi(self):
        enable = bool(self.state.model)
        for action in (self.newEmptyCopyAction, self.backupAction,
                       self.saveAction, self.saveAsAction,
                       self.saveGroupedAsAction, self.printAction,
                       self.outputRtfAction, self.outputDocxAction,
                       self.outputAsAction):
            action.setEnabled(enable)


    def new(self, filename=None):
        if filename is None:
            filename = self._new_or_open("New", QFileDialog.getSaveFileName)
        if filename:
            if not filename.casefold().endswith(EXTENSION):
                filename += EXTENSION
            if os.path.exists(filename):
                try:
                    os.remove(filename)
                except OSError as err:
                    error(err)
            self.window.newXix(filename)


    def newEmptyCopy(self): # No need to restore focus widget
        with Lib.Qt.DisableUI(*self.window.widgets(), forModalDialog=True):
            form = Forms.EmptyCopy.Form(self.state, self.window)
            form.exec_()


    def open(self, filename=None):
        if filename is None or not os.path.exists(filename):
            filename = self._new_or_open("Open",
                                         QFileDialog.getOpenFileName)
        if filename:
            if not filename.casefold().endswith(EXTENSION):
                filename += EXTENSION
            self.window.openXix(filename)


    def _new_or_open(self, word, getter): # No need to restore focus widget
        with Lib.Qt.DisableUI(*self.window.widgets(), forModalDialog=True):
            filename, _ = getter(self.window, "{} Index — {}".format(
                word, QApplication.applicationName()),
                self.state.indexPath, "{} index (*{})".format(
                    QApplication.applicationName(), EXTENSION))
        if filename and not filename.casefold().endswith(EXTENSION):
            filename += EXTENSION
        if filename:
            self.state.indexPath = os.path.dirname(filename)
        return filename


    def importIndex(self): # No need to restore focus widget
        extensions = []
        for extension, desc in IMPORT_EXTENSIONS.items():
            extensions.append("{} (*{})".format(desc, extension))
        with Lib.Qt.DisableUI(*self.window.widgets(), forModalDialog=True):
            inFilename, _ = QFileDialog.getOpenFileName(
                self.window, "Import Index — {}".format(
                    QApplication.applicationName()),
                self.state.importPath, ";;".join(extensions))
        if inFilename:
            for extension in IMPORT_EXTENSIONS:
                break # Just want the first (i.e., .ximl)
            if not inFilename.casefold().endswith(
                    tuple(EXPORT_EXTENSIONS.keys())):
                inFilename += extension
            with Lib.Qt.DisableUI(*self.window.widgets(),
                                  forModalDialog=True):
                filename, _ = QFileDialog.getSaveFileName(
                    self.window, "Save Imported Index As — {}".format(
                        QApplication.applicationName()),
                    self.state.indexPath,
                    "{} index (*{})".format(
                        QApplication.applicationName(), EXTENSION))
            if filename and not filename.casefold().endswith(EXTENSION):
                filename += EXTENSION
            if inFilename and filename:
                self.state.importPath = os.path.dirname(inFilename)
                self.state.indexPath = os.path.dirname(filename)
                self.window.importIndex(filename, inFilename)


    def backup(self):
        model = self.state.model
        if not model:
            return
        widget = QApplication.focusWidget()
        filename = Lib.incrementedFilename(model.filename)
        with Lib.Qt.DisableUI(*self.window.widgets(), forModalDialog=True):
            filename, _ = QFileDialog.getSaveFileName(
                self.window, "Backup Index — {}".format(
                    QApplication.applicationName()), filename,
                "{} index (*{})".format(
                    QApplication.applicationName(), EXTENSION))
        if filename:
            with Lib.Qt.DisableUI(*self.window.widgets(),
                                  forModalDialog=True):
                self.state.saving = True
                try:
                    self.state.maybeSave()
                    if not filename.endswith(EXTENSION):
                        filename += EXTENSION
                    say("Backing up to “{}”...".format(
                        QDir.toNativeSeparators(filename)))
                    model.optimize()
                    model.backup(filename, "Backing up",
                                 self.window.reportProgress)
                    say("Backed up to “{}”".format(QDir.toNativeSeparators(
                                                   filename)))
                finally:
                    self.state.saving = False
        Lib.restoreFocus(widget)


    def saveAs(self): # No need to restore focus widget
        filename = self._getSaveAsFilename()
        if filename:
            # Do a backup to the new filename, then open it
            say("Saving to “{}”...".format(
                QDir.toNativeSeparators(filename)))
            self.state.model.backup(filename, "Saving",
                                    self.window.reportProgress)
            self.window.openXix(filename)


    def saveGroupedAs(self): # No need to restore focus widget
        model = self.state.model
        if not model:
            return
        with Lib.Qt.DisableUI(*self.window.widgets(), forModalDialog=True):
            form = Forms.ChooseGroups.Form(self.state, self.window)
            form.exec_()
            groups = form.groups
            del form
        if groups:
            filename = self._getSaveAsFilename("Save Grouped As")
            if filename:
                Lib.remove_file(filename)
                self.state.model.saveGrouped(filename, groups)
                self.state.window.openXix(filename)


    def _getSaveAsFilename(self, title="Save As"):
        model = self.state.model
        if not model:
            return
        with Lib.Qt.DisableUI(*self.window.widgets(), forModalDialog=True):
            filename, _ = QFileDialog.getSaveFileName(
                self.window, "{} — {}".format(
                    title, QApplication.applicationName()),
                self.state.indexPath, "{} index (*{})".format(
                    QApplication.applicationName(), EXTENSION))
        if filename:
            self.state.maybeSave()
            if not filename.endswith(EXTENSION):
                filename += EXTENSION
            if filename != model.filename:
                self.state.indexPath = os.path.dirname(filename)
            return filename


    def outputRtf(self):
        widget = QApplication.focusWidget()
        self._outputIndex(Lib.replace_extension(self.state.model.filename,
                                                ".rtf"), widget)


    def outputDocx(self):
        widget = QApplication.focusWidget()
        self._outputIndex(Lib.replace_extension(self.state.model.filename,
                                                ".docx"), widget)


    def outputIndexAs(self):
        widget = QApplication.focusWidget()
        extensions = []
        for extension, desc in EXPORT_EXTENSIONS.items():
            extensions.append("{} (*{})".format(desc, extension))
        with Lib.Qt.DisableUI(*self.window.widgets(), forModalDialog=True):
            form = QFileDialog(self.window, "Output As — {}".format(
                               QApplication.applicationName()))
            form.setNameFilters(extensions)
            form.setAcceptMode(QFileDialog.AcceptSave)
            form.setDirectory(self.state.outputPath)
            form.selectFile(str(pathlib.Path(
                                self.state.model.filename).stem))
            if form.exec_():
                filename = form.selectedFiles()[0]
                extension = form.selectedNameFilter()
                if filename: # Must have some extension
                    if not re.match(r"^.*[.].+$", filename):
                        if extension:
                            filename += EXTENSION_EXTRACT_RX.sub(
                                r"\1", extension)
                        else:
                            filename += ".rtf"
                    self._outputIndex(filename, widget)
        Lib.restoreFocus(widget)


    def _outputIndex(self, filename, widget):
        monitor = Lib.MonitorFile(filename)
        self.state.outputPath = os.path.dirname(filename)
        nativeFilename = QDir.toNativeSeparators(filename)
        try:
            say("Outputting to “{}”…".format(nativeFilename))
            with Lib.DisableUI(*self.state.window.widgets()):
                config = self.state.model.configs().copy()
                config.Filename = filename
                Output.outputEntries(self.state.model, config, "Outputting",
                                     self.window.reportProgress)

            self._reportOnOutput(
                monitor,
                "Output to “{}”".format(nativeFilename),
                "Output Failed",
                "Failed to output to “{}”".format(nativeFilename))
        except Output.Error as err:
            self._reportOnOutput(
                monitor,
                "Output to “{}”".format(nativeFilename),
                "Output Failed",
                "Failed to output to “{}”: {}".format(nativeFilename, err))
        Lib.restoreFocus(widget)


    def _reportOnOutput(self, monitor, goodMessage, badTitle, badMessage):
        if monitor.changed:
            say(goodMessage)
        else:
            QMessageBox.warning(
                self.window, "{} — {}".format(
                    badTitle, QApplication.applicationName()), """\
<p>{}</p><p>{} cannot write a file if the file is open in another
application or if you don't have access permission to write the file (or
to write in the file's folder).</p>
<p><b>Try using a different filename and/or folder.</b></p>""".format(
                    badMessage, QApplication.applicationName()))


    def printIndex(self):
        widget = QApplication.focusWidget()
        if self.state.printer is None:
            self.state.printer = QPrinter(QPrinter.HighResolution)
            self.state.printer.setColorMode(QPrinter.GrayScale)
            settings = QSettings()
            size = PaperSizeKind(int(settings.value(Gopt.Key.PaperSize,
                                 Gopt.Default.PaperSize)))
            self.state.printer.setPaperSize(
                QPrinter.Letter if size is PaperSizeKind.LETTER else
                QPrinter.A4)
        with Lib.Qt.DisableUI(*self.window.widgets(), forModalDialog=True):
            form = QPrintDialog(self.state.printer, self.state.window)
            form.setWindowTitle("Print Index")
            if form.exec_():
                try:
                    with Lib.DisableUI(*self.window.widgets()):
                        config = self.state.model.configs().copy()
                        config.Filename = "print.$$$"
                        config.Printer = self.state.printer
                        Output.outputEntries(
                            self.state.model, config, "Printing",
                            self.window.reportProgress)
                    say("Printed")
                except Output.Error as err:
                    say("Failed to print: {}".format(err))
                    logging.error("printIndex failed: {}".format(err))
        Lib.restoreFocus(widget)


    def quit(self):
        QApplication.closeAllWindows()
