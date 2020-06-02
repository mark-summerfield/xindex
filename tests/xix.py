#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import unittest

import Lib
import MakeTestXix
import Saf
import SortAs
import Xix
from Const import LanguageKind, ROOT, XrefKind


DEBUG = 1


class TestXix(unittest.TestCase):

    def setUp(self):
        self.username = "Tester"
        self.stack = Lib.Command.Stack()


    def debug(self, message="    "):
        if not DEBUG:
            return

        def fixup(lst):
            return [str(x) for x in lst]

        if message:
            print(message, end=" ")
        if self.stack.index is not None:
            left = self.stack.commands[:self.stack.index]
            middle = ["<{}>".format(
                self.stack.commands[self.stack.index])]
            right = self.stack.commands[self.stack.index + 1:]
            print(fixup(left + middle + right), self.stack.index)
        else:
            print(fixup(self.stack.commands), self.stack.index)


    def test_01(self):
        xix = None
        count = 20
        try:
            xix, _ = MakeTestXix.create_xix(
                count, self.username, ":memory:")
            self.assertEqual(0, len(xix))
            MakeTestXix.populate_xix(count, xix)
            self.assertEqual(count, len(xix))
        finally:
            if xix is not None:
                xix.close()


    def test_02(self):
        count = 20
        with Xix.Xix.Xix(":memory:", self.username,
                         LanguageKind.AMERICAN) as xix:
            self.assertEqual(0, len(xix))
            MakeTestXix.populate_xix(count, xix)
            self.assertEqual(count, len(xix))


    def test_03_add(self):
        self.stack.clear()
        with Xix.Xix.Xix(":memory:", self.username,
                         LanguageKind.AMERICAN) as xix:
            self.assertEqual(0, len(xix))
            self.assertFalse(self.stack.canUndo)
            self.assertFalse(self.stack.canRedo)
            expected = {}
            for i, term in enumerate(
                ("Zipper", "Apple Pie", "Middle", "Three Quarters",
                    "Early On", "Quirky"), 1):
                expected[i] = term
                self.addEntryX(xix, term, i=i)
            order = (2, 5, 3, 6, 4, 1)
            for i, entry in enumerate(xix):
                self.assertEqual(order[i], entry.eid)
                self.assertEqual(expected[entry.eid], entry.term)
                self.assertEqual(entry.peid, ROOT)
                self.assertIsNone(entry.pages)

            self.assertTrue(self.stack.canUndo)
            self.assertFalse(self.stack.canRedo)

            command = self.stack._command()
            self.assertIsInstance(command, Xix.Command.AddEntry)
            self.assertEqual(command.term, "Quirky")
            command = self.stack.getUndo()
            self.assertEqual(command.term, "Quirky")
            command = self.stack._command()
            self.assertEqual(command.term, "Early On")
            command = self.stack.getUndo()
            self.assertEqual(command.term, "Early On")
            command = self.stack._command()
            self.assertEqual(command.term, "Three Quarters")
            command = self.stack.getUndo()
            self.assertEqual(command.term, "Three Quarters")
            command = self.stack._command()
            self.assertEqual(command.term, "Middle")

            command = self.stack.getRedo()
            self.assertEqual(command.term, "Three Quarters")
            command = self.stack._command()
            self.assertEqual(command.term, "Three Quarters")
            command = self.stack.getRedo()
            self.assertEqual(command.term, "Early On")
            command = self.stack._command()
            self.assertEqual(command.term, "Early On")
            command = self.stack.getRedo()
            self.assertEqual(command.term, "Quirky")
            command = self.stack._command()
            self.assertEqual(command.term, "Quirky")

            self.assertTrue(self.stack.canUndo)
            self.assertFalse(self.stack.canRedo)
            self.assertEqual(len(self.stack), len(order))

            while self.stack.canUndo:
                self.stack.getUndo()
            self.assertFalse(self.stack.canUndo)
            with self.assertRaises(Lib.Command.Error):
                self.stack.getUndo()
            self.assertTrue(self.stack.canRedo)
            self.assertEqual(len(self.stack), len(order))

            while self.stack.canRedo:
                self.stack.getRedo()
            with self.assertRaises(Lib.Command.Error):
                self.stack.getRedo()
            self.assertTrue(self.stack.canUndo)
            self.assertFalse(self.stack.canRedo)
            command = self.stack._command()
            self.assertEqual(command.term, "Quirky")


    def test_04_add(self):
        self.stack.clear()
        with Xix.Xix.Xix(":memory:", self.username,
                         LanguageKind.AMERICAN) as xix:
            self.assertEqual(0, len(xix))
            self.assertFalse(self.stack.canUndo)
            self.assertFalse(self.stack.canRedo)
            expected = {}
            for i, term in enumerate(
                ("Zipper", "Apple Pie", "Middle",
                    "Three Quarters", "Early On", "Quirky"), 1):
                expected[i] = term
                self.addEntryX(xix, term, i=i)
            order = (2, 5, 3, 6, 4, 1)
            for i, entry in enumerate(xix):
                self.assertEqual(order[i], entry.eid)
                self.assertEqual(expected[entry.eid], entry.term)
                self.assertEqual(entry.peid, ROOT)
                self.assertIsNone(entry.pages)
            self.assertEqual(len(xix), len(order))

            command = self.stack._command()
            self.assertEqual(command.term, "Quirky")
            command = self.stack.getUndo()
            self.assertEqual(command.term, "Quirky")
            xix.undoCommand(command)
            command = self.stack._command()
            self.assertEqual(command.term, "Early On")
            self.assertEqual(len(xix), len(order) - 1)
            command = self.stack.getUndo()
            self.assertEqual(command.term, "Early On")
            xix.undoCommand(command)
            command = self.stack._command()
            self.assertEqual(command.term, "Three Quarters")
            self.assertEqual(len(xix), len(order) - 2)
            command = self.stack.getUndo()
            self.assertEqual(command.term, "Three Quarters")
            xix.undoCommand(command)
            command = self.stack._command()
            self.assertEqual(command.term, "Middle")
            self.assertEqual(len(xix), len(order) - 3)
            temporder = (2, 3, 1)
            for i, entry in enumerate(xix):
                self.assertEqual(temporder[i], entry.eid)
                self.assertEqual(expected[entry.eid], entry.term)
                self.assertEqual(entry.peid, ROOT)
                self.assertIsNone(entry.pages)
            command = self.stack.getRedo()
            self.assertEqual(command.term, "Three Quarters")
            xix.doCommand(command)
            command = self.stack._command()
            self.assertEqual(command.term, "Three Quarters")
            self.assertEqual(len(xix), len(order) - 2)
            command = self.stack.getRedo()
            self.assertEqual(command.term, "Early On")
            xix.doCommand(command)
            command = self.stack._command()
            self.assertEqual(command.term, "Early On")
            self.assertEqual(len(xix), len(order) - 1)
            command = self.stack.getRedo()
            self.assertEqual(command.term, "Quirky")
            xix.doCommand(command)
            command = self.stack._command()
            self.assertEqual(command.term, "Quirky")
            self.assertEqual(len(xix), len(order))
            for i, entry in enumerate(xix):
                self.assertEqual(order[i], entry.eid)
                self.assertEqual(expected[entry.eid], entry.term)
                self.assertEqual(entry.peid, ROOT)
                self.assertIsNone(entry.pages)


    def test_05(self):
        self.stack.clear()
        with Xix.Xix.Xix(":memory:", self.username,
                         LanguageKind.AMERICAN) as xix:
            self.assertEqual(0, len(xix))
            self.assertFalse(self.stack.canUndo)
            self.assertFalse(self.stack.canRedo)
            expected = {}
            for i, term in enumerate(
                ("Zipper", "Apple Pie", "Middle",
                    "Three Quarters", "Early On", "Quirky"), 1):
                expected[i] = term
                self.addEntryX(xix, term, i=i)
            order = (2, 5, 3, 6, 4, 1)
            for i, entry in enumerate(xix):
                self.assertEqual(order[i], entry.eid)
                self.assertEqual(expected[entry.eid], entry.term)
                self.assertEqual(entry.peid, ROOT)
                self.assertIsNone(entry.pages)
            self.assertEqual(len(xix), len(order))


    def test_06(self):
        self.stack.clear()
        with Xix.Xix.Xix(":memory:", self.username,
                         LanguageKind.AMERICAN) as xix:
            self.assertEqual(0, len(xix))
            self.assertFalse(self.stack.canUndo)
            self.assertFalse(self.stack.canRedo)
            expected = {}
            for i, term in enumerate(
                ("Zipper", "Apple Pie", "Middle",
                    "Three Quarters", "Early On", "Quirky"), 1):
                expected[i] = term
                self.addEntryX(xix, term, i=i)
            order = (2, 5, 3, 6, 4, 1)
            for i, entry in enumerate(xix):
                self.assertEqual(order[i], entry.eid)
                self.assertEqual(expected[entry.eid], entry.term)
                self.assertEqual(entry.peid, ROOT)
                self.assertIsNone(entry.pages)
            self.assertEqual(len(xix), len(order))
            expected = {}
            for eid in range(len(xix)):
                entry = xix.entry(eid)
                parts = entry.term.split()
                if len(parts) > 1:
                    term = " ".join(reversed(parts))
                    expected[eid] = term
                    self.editEntryX(xix, entry, term=term)
            for eid, term in expected.items():
                self.assertEqual(xix.entry(eid).term, term)


    def test_07(self): # noqa
        self.stack.clear()
        with Xix.Xix.Xix(":memory:", self.username,
                         LanguageKind.AMERICAN) as xix:
            self.assertEqual(0, len(xix))
            self.assertFalse(self.stack.canUndo)
            self.assertFalse(self.stack.canRedo)
            terms = ("Zipper", "Apple Pie", "Middle", "Three Quarters",
                     "Early On", "Quirky")
            for i, term in enumerate(terms, 1):
                self.addEntryX(xix, term, i=i)
            self.addXRef(xix, "Zipper", 1, "Quirky", 6, XrefKind.SEE)
            self.addXRef(xix, "Zipper", 1, "Apple Pie", 2,
                         XrefKind.SEE_ALSO)
            self.addXRef(xix, "Middle", 3, "Early On", 5, XrefKind.SEE)
            self.addXRef(xix, "Three Quarters", 4, "Zipper", 1,
                         XrefKind.SEE_ALSO)
            self.assertTrue(self.stack.canUndo)
            self.assertFalse(self.stack.canRedo)
            for i in range(1, len(terms) + 1):
                xrefs = list(xix.xrefs(i, transaction=False))
                if i in {2, 5, 6}:
                    self.assertListEqual([], xrefs)
                elif i == 1:
                    self.assertEqual(len(xrefs), 2)
                    self.assertEqual(xrefs[0].to_eid, 6)
                    self.assertEqual(xrefs[0].kind, XrefKind.SEE)
                    self.assertEqual(xrefs[1].to_eid, 2)
                    self.assertEqual(xrefs[1].kind, XrefKind.SEE_ALSO)
                elif i == 3:
                    self.assertEqual(xrefs[0].to_eid, 5)
                    self.assertEqual(xrefs[0].kind, XrefKind.SEE)
                elif i == 4:
                    self.assertEqual(xrefs[0].to_eid, 1)
                    self.assertEqual(xrefs[0].kind, XrefKind.SEE_ALSO)
            command = self.stack.getUndo()
            self.assertEqual(command.from_term, "Three Quarters")
            xix.undoCommand(command)
            for i in range(1, len(terms) + 1):
                xrefs = list(xix.xrefs(i, transaction=False))
                if i in {2, 4, 5, 6}:
                    self.assertListEqual([], xrefs)
            self.assertTrue(self.stack.canUndo)
            self.assertTrue(self.stack.canRedo)
            command = self.stack.getUndo()
            self.assertEqual(command.from_term, "Middle")
            xix.undoCommand(command)
            for i in range(1, len(terms) + 1):
                xrefs = list(xix.xrefs(i, transaction=False))
                if i in {2, 3, 4, 5, 6}:
                    self.assertListEqual([], xrefs)
                elif i == 1:
                    self.assertEqual(len(xrefs), 2)
                    self.assertEqual(xrefs[0].to_eid, 6)
                    self.assertEqual(xrefs[0].kind, XrefKind.SEE)
                    self.assertEqual(xrefs[1].to_eid, 2)
                    self.assertEqual(xrefs[1].kind, XrefKind.SEE_ALSO)
            self.assertTrue(self.stack.canUndo)
            self.assertTrue(self.stack.canRedo)
            command = self.stack.getUndo()
            self.assertEqual(command.from_term, "Zipper")
            xix.undoCommand(command)
            for i in range(1, len(terms) + 1):
                xrefs = list(xix.xrefs(i, transaction=False))
                if i in {2, 3, 4, 5, 6}:
                    self.assertListEqual([], xrefs)
                elif i == 1:
                    self.assertEqual(len(xrefs), 1)
                    self.assertEqual(xrefs[0].to_eid, 6)
                    self.assertEqual(xrefs[0].kind, XrefKind.SEE)
            self.assertTrue(self.stack.canUndo)
            self.assertTrue(self.stack.canRedo)
            command = self.stack.getUndo()
            self.assertEqual(command.from_term, "Zipper")
            xix.undoCommand(command)
            for i in range(1, len(terms) + 1):
                xrefs = list(xix.xrefs(i, transaction=False))
                self.assertListEqual([], xrefs)
            self.assertTrue(self.stack.canUndo)
            self.assertTrue(self.stack.canRedo)
            command = self.stack.getRedo()
            self.assertEqual(command.from_term, "Zipper")
            xix.doCommand(command)
            command = self.stack.getRedo()
            self.assertEqual(command.from_term, "Zipper")
            xix.doCommand(command)
            command = self.stack.getRedo()
            self.assertEqual(command.from_term, "Middle")
            xix.doCommand(command)
            for i in range(1, len(terms) + 1):
                xrefs = list(xix.xrefs(i, transaction=False))
                if i in {2, 4, 5, 6}:
                    self.assertListEqual([], xrefs)
                elif i == 1:
                    self.assertEqual(len(xrefs), 2)
                    self.assertEqual(xrefs[0].to_eid, 6)
                    self.assertEqual(xrefs[0].kind, XrefKind.SEE)
                    self.assertEqual(xrefs[1].to_eid, 2)
                    self.assertEqual(xrefs[1].kind, XrefKind.SEE_ALSO)
                elif i == 3:
                    self.assertEqual(xrefs[0].to_eid, 5)
                    self.assertEqual(xrefs[0].kind, XrefKind.SEE)


    def test_08(self):
        def orig(xix, terms):
            for i in range(1, len(terms) + 1):
                xrefs = list(xix.xrefs(i, transaction=False))
                if i in {2, 5, 6}:
                    self.assertListEqual([], xrefs)
                elif i == 1:
                    self.assertEqual(len(xrefs), 2)
                    self.assertEqual(xrefs[0].to_eid, 6)
                    self.assertEqual(xrefs[0].kind, XrefKind.SEE)
                    self.assertEqual(xrefs[1].to_eid, 2)
                    self.assertEqual(xrefs[1].kind, XrefKind.SEE_ALSO)
                elif i == 3:
                    self.assertEqual(xrefs[0].to_eid, 5)
                    self.assertEqual(xrefs[0].kind, XrefKind.SEE)
                elif i == 4:
                    self.assertEqual(xrefs[0].to_eid, 1)
                    self.assertEqual(xrefs[0].kind, XrefKind.SEE_ALSO)

        def modif(xix, terms):
            for i in range(1, len(terms) + 1):
                xrefs = list(xix.xrefs(i, transaction=False))
                if i in {2, 5, 6}:
                    self.assertListEqual([], xrefs)
                elif i == 1:
                    self.assertEqual(len(xrefs), 2)
                    self.assertEqual(xrefs[0].to_eid, 2)
                    self.assertEqual(xrefs[0].kind, XrefKind.SEE)
                    self.assertEqual(xrefs[1].to_eid, 6)
                    self.assertEqual(xrefs[1].kind, XrefKind.SEE)
                elif i == 3:
                    self.assertEqual(xrefs[0].to_eid, 5)
                    self.assertEqual(xrefs[0].kind, XrefKind.SEE_ALSO)
                elif i == 4:
                    self.assertEqual(xrefs[0].to_eid, 1)
                    self.assertEqual(xrefs[0].kind, XrefKind.SEE_ALSO)

        self.stack.clear()
        with Xix.Xix.Xix(":memory:", self.username,
                         LanguageKind.AMERICAN) as xix:
            self.assertEqual(0, len(xix))
            self.assertFalse(self.stack.canUndo)
            self.assertFalse(self.stack.canRedo)
            terms = ("Zipper", "Apple Pie", "Middle", "Three Quarters",
                     "Early On", "Quirky")
            for i, term in enumerate(terms, 1):
                self.addEntryX(xix, term, i=i)
            self.addXRef(xix, "Zipper", 1, "Quirky", 6, XrefKind.SEE)
            self.addXRef(xix, "Zipper", 1, "Apple Pie", 2,
                         XrefKind.SEE_ALSO)
            self.addXRef(xix, "Middle", 3, "Early On", 5, XrefKind.SEE)
            self.addXRef(xix, "Three Quarters", 4, "Zipper", 1,
                         XrefKind.SEE_ALSO)
            orig(xix, terms)
            self.changeXRef(xix, "Zipper", 1, "Apple Pie", 2, XrefKind.SEE)
            self.changeXRef(xix, "Middle", 3, "Early On", 5,
                            XrefKind.SEE_ALSO)
            modif(xix, terms)
            command = self.stack.getUndo()
            self.assertEqual(command.from_term, "Middle")
            xix.undoCommand(command)
            command = self.stack.getUndo()
            self.assertEqual(command.from_term, "Zipper")
            xix.undoCommand(command)
            orig(xix, terms)
            command = self.stack.getRedo()
            self.assertEqual(command.from_term, "Zipper")
            xix.doCommand(command)
            command = self.stack.getRedo()
            self.assertEqual(command.from_term, "Middle")
            xix.doCommand(command)
            modif(xix, terms)

    def test_09(self):
        def orig(xix, terms):
            for i in range(1, len(terms) + 1):
                xrefs = list(xix.xrefs(i, transaction=False))
                if i in {2, 5, 6}:
                    self.assertListEqual([], xrefs)
                elif i == 1:
                    self.assertEqual(len(xrefs), 2)
                    self.assertEqual(xrefs[0].to_eid, 6)
                    self.assertEqual(xrefs[0].kind, XrefKind.SEE)
                    self.assertEqual(xrefs[1].to_eid, 2)
                    self.assertEqual(xrefs[1].kind, XrefKind.SEE_ALSO)
                elif i == 3:
                    self.assertEqual(xrefs[0].to_eid, 5)
                    self.assertEqual(xrefs[0].kind, XrefKind.SEE)
                elif i == 4:
                    self.assertEqual(xrefs[0].to_eid, 1)
                    self.assertEqual(xrefs[0].kind, XrefKind.SEE_ALSO)

        def modif(xix, terms):
            for i in range(1, len(terms) + 1):
                xrefs = list(xix.xrefs(i, transaction=False))
                if i in {2, 3, 5, 6}:
                    self.assertListEqual([], xrefs)
                elif i == 1:
                    self.assertEqual(len(xrefs), 1)
                    self.assertEqual(xrefs[0].to_eid, 6)
                    self.assertEqual(xrefs[0].kind, XrefKind.SEE)
                elif i == 4:
                    self.assertEqual(xrefs[0].to_eid, 1)
                    self.assertEqual(xrefs[0].kind, XrefKind.SEE_ALSO)

        self.stack.clear()
        with Xix.Xix.Xix(":memory:", self.username,
                         LanguageKind.AMERICAN) as xix:
            self.assertEqual(0, len(xix))
            self.assertFalse(self.stack.canUndo)
            self.assertFalse(self.stack.canRedo)
            terms = ("Zipper", "Apple Pie", "Middle", "Three Quarters",
                     "Early On", "Quirky")
            for i, term in enumerate(terms, 1):
                self.addEntryX(xix, term, i=i)
            self.addXRef(xix, "Zipper", 1, "Quirky", 6, XrefKind.SEE)
            self.addXRef(xix, "Zipper", 1, "Apple Pie", 2,
                         XrefKind.SEE_ALSO)
            self.addXRef(xix, "Middle", 3, "Early On", 5, XrefKind.SEE)
            self.addXRef(xix, "Three Quarters", 4, "Zipper", 1,
                         XrefKind.SEE_ALSO)
            orig(xix, terms)
            self.deleteXRef(xix, "Zipper", 1, "Apple Pie", 2,
                            XrefKind.SEE_ALSO)
            self.deleteXRef(xix, "Middle", 3, "Early On", 5, XrefKind.SEE)
            command = self.stack.getUndo()
            self.assertEqual(command.from_term, "Middle")
            xix.undoCommand(command)
            command = self.stack.getUndo()
            self.assertEqual(command.from_term, "Zipper")
            xix.undoCommand(command)
            orig(xix, terms)
            command = self.stack.getRedo()
            self.assertEqual(command.from_term, "Zipper")
            xix.doCommand(command)
            command = self.stack.getRedo()
            self.assertEqual(command.from_term, "Middle")
            xix.doCommand(command)
            modif(xix, terms)


    def deleteXRef(self, xix, from_term, from_eid, to_term, to_eid, kind):
        command = Xix.Command.DeleteXRef(from_term, from_eid, to_term,
                                         to_eid, kind)
        self.stack.push(command) # Store, then do
        xix.doCommand(command) # should be self.xix.doCommand(command)


    def changeXRef(self, xix, from_term, from_eid, to_term, to_eid, kind):
        command = Xix.Command.ChangeXRef(from_term, from_eid, to_term,
                                         to_eid, kind)
        self.stack.push(command) # Store, then do
        xix.doCommand(command) # should be self.xix.doCommand(command)


    def addXRef(self, xix, from_term, from_eid, to_term, to_eid, kind):
        command = Xix.Command.AddXRef(from_term, from_eid, to_term, to_eid,
                                      kind)
        self.stack.push(command) # Store, then do
        xix.doCommand(command) # should be self.xix.doCommand(command)


    def addEntryX(self, xix, term, saf=Saf.AUTO, sortas=None, pages=None,
                  notes=None, peid=ROOT, i=None):
        if sortas is None:
            sortas = SortAs.wordByWordCMS16(term)
        self.addEntry(xix, saf, sortas, term, pages, notes, peid)
        command = self.stack._command()
        self.assertEqual(command.eid, i)
        self.assertEqual(i, len(xix))
        self.assertEqual(xix.entry(i).term, term)


    # How to add a new entry (in Xix don't need to pass xix)
    def addEntry(self, xix, saf, sortas, term, pages, notes, peid):
        self.assertIsNotNone(peid)
        command = Xix.Command.AddEntry(saf, sortas, term, pages, notes,
                                       peid)
        self.stack.push(command) # Store, then do
        xix.doCommand(command) # should be self.xix.doCommand(command)


    def editEntryX(self, xix, entry, saf=Saf.AUTO, sortas=None, term=None,
                   pages=None, notes=None):
        if sortas is None:
            sortas = SortAs.wordByWordCMS16(term)
        self.editEntry(xix, entry, saf, sortas, term, pages, notes)
        command = self.stack._command()
        self.assertEqual(command.entry.eid, entry.eid)
        self.assertEqual(command.entry.peid, entry.peid)
        updatedEntry = xix.entry(entry.eid)
        self.assertEqual(updatedEntry.saf, saf or entry.saf)
        self.assertEqual(updatedEntry.sortas, sortas or entry.sortas)
        self.assertEqual(updatedEntry.term, term or entry.term)
        self.assertEqual(updatedEntry.pages, pages or entry.pages)


    def editEntry(self, xix, entry, saf, sortas, term, pages, notes):
        self.assertIsNotNone(entry)
        self.assertIsNotNone(entry.eid)
        self.assertIsNotNone(entry.peid)
        command = Xix.Command.EditEntry(entry, saf, sortas, term, pages,
                                        notes)
        self.stack.push(command) # Store, then do
        xix.doCommand(command) # should be self.xix.doCommand(command)


if __name__ == "__main__":
    unittest.main()
