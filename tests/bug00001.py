#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import unittest

import Saf
import SortAs
import Xix
from Const import CountKind, LanguageKind, XrefKind


class TestXixModel(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None
        self.args = (LanguageKind.AMERICAN, "wordByWordCMS16",
                     "pageRangeCMS16")
        self.username = "Tester"
        self.data = ( # Term, peid, eid
            ("X-Ray three", 0, 1),
            ("Delta five", 0, 2),
            ("Alpha four", 0, 3),
            ("Kilo two", 0, 4),
            ("Echo", 0, 5),
            ("Juliet five", 0, 6),
            ("Uniform six", 0, 7),
            ("Oscar four", 0, 8),
            ("Tango six", 6, 9),
            ("Foxtrot five", 3, 10),
            ("Hotel three", 6, 11),
            ("Golf six", 4, 12),
            ("Victor six", 5, 13),
            ("Romeo four", 3, 14),
            ("Papa five", 1, 15),
            ("Lima", 3, 16),
            ("India five", 11, 17),
            ("Mike", 9, 18),
            ("November", 11, 19),
            ("Sierra", 10, 20),
            ("Whisky three", 14, 21),
            ("Bravo four", 13, 22),
            ("Charlie six", 14, 23),
            ("Zulu six", 11, 24),
            ("Quebec one", 13, 25),
            ("Yankee two", 13, 26),
            )


    def test_01_xrefs(self):
        model = None
        try:
            model = Xix.Model.Model(self.username)
            model.open(":memory:", *self.args)
            self.assertEqual(0, len(model))
            added = []
            for term, peid, eid in self.data:
                model.addEntry(Saf.AUTO, SortAs.wordByWordCMS16(term),
                               term, peid=peid)
                added.append(term)
            self.assertEqual(len(self.data), len(model))
            self.assertEqual(model.count(CountKind.XREFS), 0)
            self.assertFalse(model.canRedo)

            self.check_xrefs(model)

            model.deleteEntry(3) # Alpha
            model.undo() # restore
            self.check_xrefs(model)

            while model.canUndo: # get rid of everything
                model.undo()
            for _ in range(26): # recreate the entries sans xrefs
                model.redo()
            self.assertEqual(len(self.data), len(model))
            self.assertEqual(model.count(CountKind.XREFS), 0)
            for x in range(1, 27):
                self.assertEqual(model.count(CountKind.XREFS, x), 0)

            self.check_xrefs(model)

        finally:
            if model is not None:
                model.close()


    def check_xrefs(self, model):
        model.addXRef(10, 5, XrefKind.SEE) # Foxtrot -> Echo
        model.addXRef(10, 11, XrefKind.SEE_ALSO) # Foxtrot -> Hotel
        model.addXRef(16, 18, XrefKind.SEE_ALSO) # Lima -> Mike
        model.addGenericXRef(16, "under #1", XrefKind.SEE_GENERIC) # Lima ->
        # Lima ->
        model.addGenericXRef(16, "under #2", XrefKind.SEE_ALSO_GENERIC)
        model.addGenericXRef(12, "under #3", XrefKind.SEE_GENERIC) # Golf ->

        self.assertEqual(model.count(CountKind.XREFS, 10), 2)
        self.assertEqual(model.count(CountKind.XREFS, 16), 3)
        self.assertEqual(model.count(CountKind.XREFS, 12), 1)
        self.assertEqual(model.count(CountKind.XREFS, 18), 1)
        for x in range(1, 27):
            if x not in (5, 10, 11, 12, 16, 18):
                self.assertEqual(model.count(CountKind.XREFS, x), 0)
        self.assertFalse(model.canRedo)

        xrefs = list(model.xrefs(16, transaction=False))
        self.assertEqual(len(xrefs), 1)
        xref = xrefs[0]
        self.assertEqual(xref.from_eid, 16)
        self.assertEqual(xref.to_eid, 18)
        self.assertEqual(xref.kind, XrefKind.SEE_ALSO)
        generic_xrefs = sorted(model.generic_xrefs(16, transaction=False))
        self.assertEqual(len(generic_xrefs), 2)
        generic_xref = generic_xrefs[0]
        self.assertEqual(generic_xref.from_eid, 16)
        self.assertEqual(generic_xref.term, "under #1")
        generic_xref = generic_xrefs[1]
        self.assertEqual(generic_xref.from_eid, 16)
        self.assertEqual(generic_xref.term, "under #2")

        model.deleteGenericXRef(16, "under #2", XrefKind.SEE_ALSO_GENERIC)
        model.addGenericXRef(16, "under #A", XrefKind.SEE_ALSO_GENERIC)
        generic_xrefs = sorted(model.generic_xrefs(16, transaction=False))
        self.assertEqual(len(generic_xrefs), 2)
        generic_xref = generic_xrefs[1]
        self.assertEqual(generic_xref.from_eid, 16)
        self.assertEqual(generic_xref.term, "under #A")

        self.assertFalse(model.canRedo)
        model.undo() # Undo the add
        model.undo() # Undo the delete - leaving the original
        self.assertTrue(model.canRedo)
        generic_xrefs = sorted(model.generic_xrefs(16, transaction=False))
        generic_xref = generic_xrefs[1]
        self.assertEqual(generic_xref.from_eid, 16)
        self.assertEqual(generic_xref.term, "under #2")


if __name__ == "__main__":
    unittest.main()
