#!/usr/bin/env python3
# Copyright © 2014-20 Qtrac Ltd. All rights reserved.

from PySide.QtCore import Qt
from PySide.QtGui import (
    QApplication, QInputDialog, QKeySequence, QMessageBox, QTextCursor)

import Forms
import Lib
import Xix
from Const import CountKind, ModeKind, ROOT, XrefKind


class Actions:

    def __init__(self, window):
        self.window = window
        self.state = self.window.state

        self.addTopAction = Lib.createAction(
            window, ":/add-toplevel.svg", "Add &Main Entry",
            self.addToplevelEntry, QKeySequence(Qt.Key_F7), """\
<p><b>Entry→Add Main Entry</b> ({})</p>
<p>Add a new main entry (after saving any unsaved add or edit).</p>
<p>Use the <b>Modify→Move</b> menu options to change an entry's
parent.</p>""".format(QKeySequence(Qt.Key_F7).toString()))
        self.addChildAction = Lib.createAction(
            window, ":/add-child.svg", "Add &Subentry", self.addSubEntry,
            QKeySequence(Qt.SHIFT + Qt.Key_F7), """\
<p><b>Entry→Add Subentry</b> ({})</p>
<p>Add a new subentry under the current entry (after saving any unsaved
add or edit).</p>
<p>Use the <b>Modify→Move</b> menu options to change an entry's
parent.</p>""".format(QKeySequence(Qt.SHIFT + Qt.Key_F7).toString()))
        self.addSiblingAction = Lib.createAction(
            window, ":/add.svg", "Add Sibling &Entry", self.addSiblingEntry,
            QKeySequence(Qt.CTRL + Qt.Key_F7), """\
<p><b>Entry→Add Sibling Entry</b> ({})</p>
<p>Add a new entry as a sibling of the current entry (after saving any
unsaved add or edit).</p>
<p>Use the <b>Modify→Move</b> menu options to change an entry's
parent.</p>""".format(QKeySequence(Qt.CTRL + Qt.Key_F7).toString()))

        self.cancelAddAction = Lib.createAction(
            window, ":/canceladd.svg", "Ca&ncel Add", self.cancelAdd,
            QKeySequence(Qt.CTRL + Qt.Key_0), tooltip="""\
<p><b>Entry→Cancel Add</b> ({})</p>
<p>Cancel adding a new entry.</p>""".format(
                QKeySequence(Qt.CTRL + Qt.Key_0).toString()))

        self.copyAction = Lib.createAction(
            window, ":/copy.svg", "&Copy...", self.copy,
            QKeySequence(Qt.Key_F8), tooltip="""\
<p><b>Entry→Copy</b> ({})</p>
<p>Create a copy of the current entry, optionally with its groups,
optionally with its subentries, and optionally with its pages
linked.</p>""".format(QKeySequence(Qt.Key_F8).toString()))
        self.moveAction = Lib.createAction(
            window, ":/move.svg", "Mo&ve...", self.move,
            QKeySequence(Qt.SHIFT + Qt.Key_F8), tooltip="""\
<p><b>Entry→Move</b> ({})</p>
<p>Move the current entry and all it subentries.</p>""".format(
                QKeySequence(Qt.Key_F8).toString()))

        self.recreateAction = Lib.createAction( # Must not have shortcut
            window, ":/recreate.svg", "Recrea&te...", self.recreate,
            tooltip="""\
<p><b>Entry→Recreate</b></p>
<p>Recreate a deleted entry.</p>
<p>Note that an entry that has <i>just</i> been deleted, can be undeleted
using <b>Index→Undo</b>.</p>""")
        self.deleteAction = Lib.createAction(
            window, ":/delete.svg", "&Delete...", self.delete,
            tooltip="""\
<p><b>Entry→Delete</b></p>
<p>Delete the current entry.</p>""")

        self.circleAction = Lib.createAction(
            window, ":/circle.svg", "C&ircle", self.circle,
            QKeySequence(Qt.CTRL + Qt.Key_L), tooltip="""\
<p><b>Entry→Circle</b> ({})</p>
<p>“Circle” or <i>un</i>-circle the current entry. A circled entry is
marked for this session. Circling has no effect on output, and can be useful
because some actions involve two entries&mdash;e.g., circled entry and the
current entry. (Although in most cases the current entry and the
filtered or a recent entry is sufficient.)</p>""".format(
                QKeySequence(Qt.CTRL + Qt.Key_L).toString()))
        self.addToNormalGroupAction = Lib.createAction(
            window, ":/groupaddto.svg", "Add to Normal &Group...",
            self.addToNormalGroup, QKeySequence(Qt.Key_F5), tooltip="""\
<p><b>Entry→Add to Normal Group</b> ({})</p>
<p>Add the current entry to a normal (unlinked) group.</p>""".format(
                QKeySequence(Qt.Key_F5).toString()))
        self.addToLinkedGroupAction = Lib.createAction(
            window, ":/groupaddtolink.svg", "Add to &Linked Group...",
            self.addToLinkedGroup, QKeySequence(Qt.SHIFT + Qt.Key_F5),
            tooltip="""\
<p><b>Entry→Add to Linked Group</b> ({})</p>
<p>Add the current entry to a linked group.</p>""".format(
                QKeySequence(Qt.SHIFT + Qt.Key_F5).toString()))
        self.removeFromGroupAction = Lib.createAction(
            window, ":/groupremovefrom.svg", "&Remove from Group",
            self.removeFromGroup, tooltip="""\
<p><b>Entry→Remove from Group</b></p>
<p>Remove the current entry from the highlighted group.</p>""")
        self.setGroupAction = Lib.createAction(
            window, ":/groupset.svg", "&Filter by Group",
            self.state.viewFilteredPanel.setGroup, tooltip="""\
<p><b>Entry→Filter by Group</b></p>
<p>Set the Filtered panel's filter to Group and the group to the current
group.</p>""")
        self.editGroupsAction = Lib.createAction(
            window, ":/groups.svg", "Edit Gro&ups...", self.editGroups,
            QKeySequence(Qt.CTRL + Qt.Key_F5), tooltip="""\
<p><b>Entry→Edit Groups</b> ({})</p>
<p>Add, rename, link, unlink, and delete this index's
groups.</p>""".format(QKeySequence(Qt.CTRL + Qt.Key_F5).toString()))

        self.addXRefAction = Lib.createAction(
            window, ":/xref-add.svg", "&Add Cross-reference...",
            self.addXRef, QKeySequence(Qt.CTRL + Qt.Key_K),
            tooltip="""\
<p><b>Entry→Add Cross-reference</b> ({})</p>
<p>Add a See or See Also cross reference.</p>""".format(
                QKeySequence(Qt.CTRL + Qt.Key_K).toString()))
        self.changeXRefAction = Lib.createAction(
            window, ":/xref-change.svg", "C&hange Cross-reference",
            self.changeXRef, tooltip="""\
<p><b>Entry→Change Cross-reference</b></p>
<p>Change the selected See cross reference to See Also or
vice-versa.</p>""")
        self.deleteXRefAction = Lib.createAction(
            window, ":/xref-delete.svg", "Delete Cr&oss-reference...",
            self.deleteXRef, tooltip="""\
<p><b>Entry→Delete Cross-reference</b></p>
<p>Delete the selected cross reference.</p>""")


    def forMenu(self):
        return (self.addTopAction, self.addChildAction,
                self.addSiblingAction, self.cancelAddAction,
                self.copyAction, self.moveAction, self.recreateAction,
                self.deleteAction, None, self.addXRefAction,
                self.changeXRefAction, self.deleteXRefAction, None,
                self.circleAction, None, self.addToNormalGroupAction,
                self.addToLinkedGroupAction, self.removeFromGroupAction,
                self.setGroupAction, self.editGroupsAction)


    def forToolbar1(self):
        return (self.addTopAction, self.addChildAction,
                self.addSiblingAction, self.cancelAddAction,
                self.copyAction, self.moveAction, self.deleteAction)


    def forToolbar2(self):
        return (self.addXRefAction, self.changeXRefAction,
                self.deleteXRefAction)


    def forToolbar3(self):
        return (self.circleAction, None, self.addToNormalGroupAction,
                self.addToLinkedGroupAction, self.removeFromGroupAction,
                self.setGroupAction, self.editGroupsAction)


    def updateUi(self):
        enable = bool(self.state.model and
                      self.state.model.count(CountKind.TOP_LEVEL_ENTRIES))
        for action in (self.deleteAction, self.addXRefAction,
                       self.copyAction, self.moveAction,
                       self.addChildAction, self.circleAction,):
            action.setEnabled(enable)
        if not enable:
            for action in (self.addToNormalGroupAction,
                           self.addToLinkedGroupAction,
                           self.removeFromGroupAction, self.setGroupAction):
                action.setEnabled(False)
        else:
            self.addToNormalGroupAction.setEnabled(
                self.state.model.normalGroupCount())
            eid = self.state.viewAllPanel.view.selectedEid
            enable = (self.state.model.linkedGroup(eid) is None and
                      self.state.model.linkedGroupCount())
            self.addToLinkedGroupAction.setEnabled(enable)
            enable = (self.state.groupsPanel.groupsList.currentItem()
                      is not None)
            self.removeFromGroupAction.setEnabled(enable)
            self.setGroupAction.setEnabled(enable)
        self.recreateAction.setEnabled(
            bool(self.state.model and
                 self.state.model.count(CountKind.DELETED_ENTRIES)))
        self.cancelAddAction.setEnabled(self.state.mode is ModeKind.ADD)


    def addSiblingEntry(self):
        if self.state.mode is ModeKind.ADD:
            self.save()
        peid = (self.state.entryPanel.entry.peid if
                self.state.entryPanel.entry is not None else ROOT)
        self.state.window.modeLabel.setText(
            "<font color=green>Adding {}</font>".format(
                "Main" if peid is ROOT else "Sibling"))
        self._add(peid)


    def addSubEntry(self):
        if self.state.mode is ModeKind.ADD:
            self.save()
        self.state.window.modeLabel.setText(
            "<font color=green>Adding Subentry</font>")
        self._add(self.state.entryPanel.entry.eid)


    def addToplevelEntry(self):
        if self.state.mode is ModeKind.ADD:
            self.save()
        self.state.window.modeLabel.setText(
            "<font color=green>Adding Main Entry</font>")
        self._add(ROOT)


    def _add(self, peid):
        if self.state.mode in {ModeKind.NO_INDEX, ModeKind.CHANGE}:
            return # Can't add if there's no index or big changes
        self.save() # Save any outstanding add or edit changes
        self.state.entryPanel.peid = ROOT if peid is None else peid
        self.state.entryPanel.entry = None
        self.state.entryPanel.clearForm()
        self.state.setMode(ModeKind.ADD)
        self.state.entryPanel.termEdit.setFocus()


    def cancelAdd(self):
        prefix = self.state.entryPanel.termEdit.toPlainText()
        with Lib.BlockSignals(self.state.entryPanel):
            self.state.entryPanel.clearForm()
        self.state.setMode(ModeKind.VIEW)
        if not self.state.window.gotoActions.gotoPrefix(prefix):
            eid = self.state.viewAllPanel.view.selectedEid
            if eid is not None:
                self.state.window.gotoActions.gotoEid(eid)
        if bool(self.state.model):
            editor = self.state.entryPanel.pagesEdit
            editor.setFocus()
            cursor = editor.textCursor()
            cursor.movePosition(QTextCursor.End)
            editor.setTextCursor(cursor)


    def copy(self):
        widget = QApplication.focusWidget()
        with Lib.Qt.DisableUI(*self.window.widgets(), forModalDialog=True):
            form = Forms.CopyEntry.Form(self.state, self.state.window)
            if form.exec_():
                widget = None
                self.state.entryPanel.termEdit.setFocus()
                self.state.entryPanel.termEdit.selectAll()
        Lib.restoreFocus(widget)


    def move(self):
        widget = QApplication.focusWidget()
        with Lib.Qt.DisableUI(*self.window.widgets(), forModalDialog=True):
            form = Forms.MoveEntry.Form(self.state, self.state.window)
            form.exec_()
        Lib.restoreFocus(widget)


    def recreate(self):
        widget = QApplication.focusWidget()
        with Lib.Qt.DisableUI(*self.window.widgets(), forModalDialog=True):
            form = Forms.Recreate.Form(self.state, self.state.window)
            form.exec_()
        Lib.restoreFocus(widget)


    def delete(self):
        widget = QApplication.focusWidget()
        if self.state.mode in {ModeKind.NO_INDEX, ModeKind.CHANGE}:
            return # Can't delete if there's no index or big changes
        if self.state.mode in {ModeKind.ADD, ModeKind.EDIT}:
            self.save() # Save outstanding changes & set to view mode first
        if self.state.entryPanel.entry is None:
            return # Should never happen
        eid = self.state.entryPanel.entry.eid
        if eid is None:
            return # Should never happen
        eids = list(self.state.model.deletableEntries(eid))
        if not eids:
            return # Should never happen
        message = "Delete entry “{}”".format(self.state.model.term(eid))
        if len(eids) == 2:
            message += ", and its subentry"
        elif len(eids) > 2:
            count = Lib.spellNumber(len(eids) - 1, limit=20)
            message += ", and its {} subentries".format(count)
        message += (", and any related cross-references, and also "
                    "remove from any groups")
        with Lib.Qt.DisableUI(*self.window.widgets(), forModalDialog=True):
            reply = QMessageBox.question(
                self.window, "Delete Entry — {}".format(
                    QApplication.applicationName()),
                "<p>{}?".format(message), QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes)
        if reply == QMessageBox.Yes:
            self.state.model.deleteEntry(eid, message[0].lower() +
                                         message[1:])
            with Lib.BlockSignals(self.state.entryPanel):
                self.state.entryPanel.clearForm()
            self.state.window.refreshBookmarks()
            self.state.viewFilteredPanel.setMatch()
            selectedEid = self.state.viewAllPanel.view.selectedEid
            if len(self.state.model):
                if selectedEid == eid:
                    self.state.viewAllPanel.view.goUp()
                elif selectedEid is None:
                    self.state.viewAllPanel.view.goEnd()
                else:
                    self.state.viewEntry(selectedEid)
        Lib.restoreFocus(widget)


    def addXRef(self):
        widget = QApplication.focusWidget()
        self.state.maybeSave()
        with Lib.Qt.DisableUI(*self.window.widgets(), forModalDialog=True):
            form = Forms.AddXRef.Form(self.state, self.state.window)
            form.exec_()
        Lib.restoreFocus(widget)


    def changeXRef(self):
        self.state.maybeSave()
        item = self.state.entryPanel.xrefList.currentItem()
        if item is not None:
            xref = Xix.Util.xref_for_data(item.data(Qt.UserRole))
            if xref.kind in {XrefKind.SEE, XrefKind.SEE_ALSO}:
                kind = (XrefKind.SEE_ALSO if xref.kind is XrefKind.SEE
                        else XrefKind.SEE)
                self.state.model.changeXRef(xref.from_eid, xref.to_eid,
                                            kind)
            elif xref.kind in {XrefKind.SEE_GENERIC,
                               XrefKind.SEE_ALSO_GENERIC}:
                kind = (XrefKind.SEE_ALSO_GENERIC if xref.kind is
                        XrefKind.SEE_GENERIC else
                        XrefKind.SEE_GENERIC)
                self.state.model.changeGenericXRef(xref.from_eid, xref.term,
                                                   kind)
            self.state.viewAllPanel.view.gotoEid(xref.from_eid)
            self.state.updateNavigationStatus()


    def deleteXRef(self):
        widget = QApplication.focusWidget()
        self.state.maybeSave()
        item = self.state.entryPanel.xrefList.currentItem()
        if item is not None:
            xref = Xix.Util.xref_for_data(item.data(Qt.UserRole))
            from_term = self.state.model.term(xref.from_eid)
            kind = "see" if xref.kind is XrefKind.SEE else "see also"
            if xref.kind in {XrefKind.SEE, XrefKind.SEE_ALSO}:
                term = self.state.model.term(xref.to_eid)
            elif xref.kind in {XrefKind.SEE_GENERIC,
                               XrefKind.SEE_ALSO_GENERIC}:
                term = xref.term
                kind += " (generic)"
            with Lib.Qt.DisableUI(*self.window.widgets(),
                                  forModalDialog=True):
                reply = QMessageBox.question(
                    self.window,
                    "Delete Cross-reference — {}".format(
                        QApplication.applicationName()),
                    "<p>Delete cross-reference from<br>“{}” to {} “{}”?"
                    .format(from_term, kind, term),
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if reply == QMessageBox.Yes:
                if xref.kind in {XrefKind.SEE, XrefKind.SEE_ALSO}:
                    self.state.model.deleteXRef(xref.from_eid, xref.to_eid,
                                                xref.kind)
                elif xref.kind in {XrefKind.SEE_GENERIC,
                                   XrefKind.SEE_ALSO_GENERIC}:
                    self.state.model.deleteGenericXRef(xref.from_eid,
                                                       xref.term, xref.kind)
        Lib.restoreFocus(widget)


    def save(self):
        self.state.maybeSave()


    def circle(self):
        self.state.maybeSave()
        widget = QApplication.focusWidget()
        self.state.viewAllPanel.view.circle()
        if widget is not None:
            widget.setFocus()



    def addToNormalGroup(self):
        self.state.maybeSave()
        eid = self.state.viewAllPanel.view.selectedEid
        groups = set(self.state.model.normalGroups())
        inGroups = set(self.state.model.groupsForEid(eid))
        groups = sorted(groups - inGroups, key=lambda g: g[1].casefold())
        names = [g[1] for g in groups]
        if not names: # Could happen if already in all the groups
            message = ("There are no other groups for this entry "
                       "to be added to.")
            QMessageBox.information(
                self.window, "Can't Link — {}".format(
                    QApplication.applicationName()), message)
            return
        name, ok = QInputDialog.getItem(
            self.window, "Add to Normal Group — {}".format(
                QApplication.applicationName()),
            "Normal Group", names, 0, False)
        if ok:
            for gid, gname in groups:
                if gname == name:
                    self.state.model.addToGroup(eid, gid)
                    self.state.viewAllPanel.view.gotoEid(eid)
                    break


    def addToLinkedGroup(self):
        self.state.maybeSave()
        eid = self.state.viewAllPanel.view.selectedEid
        groups = set(self.state.model.linkedGroups())
        inGroups = set(self.state.model.groupsForEid(eid))
        groups = sorted(groups - inGroups, key=lambda g: g[1].casefold())
        names = [g[1] for g in groups
                 if self.state.model.safeToAddToGroup(eid, g[0])]
        if not names:
            if self.state.model.linkedGroup(eid) is not None:
                message = "This entry is already in a linked group."
            else:
                message = ("There are no linked groups for this entry "
                           "to be added to.")
            QMessageBox.information(
                self.window, "Can't Link — {}".format(
                    QApplication.applicationName()), message)
        else:
            name, ok = QInputDialog.getItem(
                self.window, "Add to Linked Group — {}".format(
                    QApplication.applicationName()),
                "Linked Group", names, 0, False)
            if ok:
                for gid, gname in groups:
                    if gname == name:
                        self.state.model.addToGroup(eid, gid)
                        self.state.viewAllPanel.view.gotoEid(eid)
                        break


    def removeFromGroup(self):
        self.state.maybeSave()
        item = self.state.groupsPanel.groupsList.currentItem()
        if item is not None:
            eid = self.state.viewAllPanel.view.selectedEid
            gid = item.data(Qt.UserRole)
            self.state.model.removeFromGroup(eid, gid)
            self.state.viewFilteredPanel.groupChanged()


    def editGroups(self):
        widget = QApplication.focusWidget()
        eid = self.state.viewAllPanel.view.selectedEid
        term = (Lib.htmlToPlainText(self.state.model.term(eid))
                if eid is not None else "NEW")
        with Lib.Qt.DisableUI(*self.window.widgets(), forModalDialog=True):
            form = Forms.Groups.Form(term, self.state, self.window)
            form.exec_()
            self.state.viewFilteredPanel.requery()
        Lib.restoreFocus(widget)
