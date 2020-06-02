#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

import contextlib
import copy
import io
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import unittest

import Saf
import SortAs
import Xix
from Const import (
    CountKind, EntryDataKind, LanguageKind, UNLIMITED, XrefKind)


def copyAndReplace(entry, **kwargs):
    newEntry = copy.deepcopy(entry)
    for key, value in kwargs.items():
        setattr(newEntry, key, value)
    return newEntry


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
            ("and Reasons", 13, 27),
            )


    def test_01(self):
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

            self.compare_model(model, ALL)

            count = len(model)
            while model.canUndo:
                model.undo()
                term = added.pop()
                for entry in model.entries(
                    offset=0, limit=UNLIMITED,
                        entryData=EntryDataKind.ALL_DATA):
                    self.assertNotEqual(entry.term, term)
                count -= 1
                self.assertEqual(count, len(model))
            self.assertEqual(0, len(model))

            while model.canRedo:
                model.redo()
            self.compare_model(model, ALL)
            self.assertEqual(len(self.data), len(model))

        finally:
            if model is not None:
                model.close()


    def print_entries(self, model):
        for entry in model.entries(offset=0, limit=UNLIMITED,
                                   entryData=EntryDataKind.ALL_DATA):
            xrefs = []
            for xref in list(model.xrefs(entry.eid, transaction=False)):
                xrefs.append("{} {}".format(
                    "see" if xref.kind is XrefKind.SEE else "see also",
                    model.term(xref.to_eid)))
            xrefs = (" -> " + "; ".join(xrefs)) if xrefs else ""
            print("{}{}{}".format((4 * entry.indent) * " ", entry.term,
                  xrefs))


    def test_02(self):
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

            for match, result in (
                ("one", ONE), ("two", TWO), ("three", THREE),
                    ("four", FOUR), ("five", FIVE), ("six", SIX)):
                stdout = io.StringIO()
                with contextlib.redirect_stdout(stdout):
                    self.print_found_entries(model, match)
                self.assertMultiLineEqual(stdout.getvalue().strip(),
                                          result)

        finally:
            if model is not None:
                model.close()


    def print_found_entries(self, model, match):
        for entry in model.filteredEntries(
                match=match, offset=0, limit=UNLIMITED,
                entryData=EntryDataKind.ALL_DATA):
            print(entry.term)



    def test_03_delete(self):
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

            self.compare_model(model, ALL)

            model.addXRef(14, 24, XrefKind.SEE) # Romeo see Zulu
            model.addXRef(26, 16, XrefKind.SEE) # Yankee see Lima
            model.addXRef(19, 14, XrefKind.SEE) # November see Romeo

            self.compare_model(model, ALL_WITH_XREFS)

            model.deleteEntry(14) # Delete Romeo etc.
            self.compare_model(model, ALL_WITH_XREFS_NO_ROMEO)

            model.undo()
            self.compare_model(model, ALL_WITH_XREFS)

            model.deleteEntry(3) # Alpha etc.
            self.compare_model(model, ALL_WITH_XREFS_NO_ALPHA)

            model.undo()
            self.compare_model(model, ALL_WITH_XREFS)

            model.deleteEntry(13) # Victor
            model.deleteEntry(8) # Oscar
            model.deleteEntry(1) # X-Ray
            model.deleteEntry(6) # Juliet
            self.compare_model(model, MANY_DELETED)

            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                for entry in model.deletedEntries():
                    print(entry)
            self.assertMultiLineEqual(stdout.getvalue().strip(),
                                      DELETED_ENTRIES)

            model.undo() # Juliet
            model.undo() # X-Ray
            model.undo() # Oscar
            model.undo() # Victor
            self.compare_model(model, ALL_WITH_XREFS)

            self.assertListEqual([], list(model.deletedEntries()))

        finally:
            if model is not None:
                model.close()


    def test_04_reparent(self):
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

            self.compare_model(model, ALL)

            model.moveToTop(23)
            model.moveToTop(11)
            model.moveUnder(25, 5)
            model.moveUnder(6, 21, "pinned")
            model.moveUnder(7, 25, "found")
            self.compare_model(model, PROMOTE1)

            for _ in range(5): # 5 moves
                model.undo()
            self.compare_model(model, ALL)

        finally:
            if model is not None:
                model.close()


    def test_05_indent(self):
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
            for eid in (1, 2, 3, 4, 5, 6, 7, 8):
                entry = model.entry(eid, withIndent=True)
                self.assertEqual(0, entry.indent)
            for eid in (10, 16, 14, 13, 11, 9, 12, 15):
                entry = model.entry(eid, withIndent=True)
                self.assertEqual(1, entry.indent)
            for eid in (20, 23, 21, 22, 25, 26, 17, 19, 24, 18):
                entry = model.entry(eid, withIndent=True)
                self.assertEqual(2, entry.indent)
        finally:
            if model is not None:
                model.close()


    def test_06_xrefs(self):
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

            self._check_xrefs(model)

            while model.canUndo: # get rid of everything
                model.undo()
            for _ in range(27): # recreate the entries sans xrefs
                model.redo()
            self.assertEqual(len(self.data), len(model))
            self.assertEqual(model.count(CountKind.XREFS), 0)
            for x in range(1, 27):
                self.assertEqual(model.count(CountKind.XREFS, x), 0)

            self._check_xrefs(model)

        finally:
            if model is not None:
                model.close()


    def test_07_swap_terms(self):
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

            self.compare_model(model, ALL)

            entry3 = model.entry(3)
            entry23 = model.entry(23)
            self.check_entry(model, 3, entry3)
            self.check_entry(model, 23, entry23)
            model.swapTerms(3, 23) # Alpha <-> Charlie
            entry3m = copyAndReplace(entry3, term=entry23.term,
                                     sortas=entry23.sortas, saf=entry23.saf)
            entry23m = copyAndReplace(entry23, term=entry3.term,
                                      sortas=entry3.sortas, saf=entry3.saf)
            self.check_entry(model, 3, entry3m)
            self.check_entry(model, 23, entry23m)
            model.undo() # Undo Swap 3, 23
            self.check_entry(model, 3, entry3)
            self.check_entry(model, 23, entry23)
            model.redo() # Redo Swap 3, 23
            self.check_entry(model, 3, entry3m)
            self.check_entry(model, 23, entry23m)
            model.swapTerms(23, 3) # should be the same as undo
            self.check_entry(model, 3, entry3)
            self.check_entry(model, 23, entry23)
            model.undo() # Swap 3, 23
            self.check_entry(model, 3, entry3m)
            self.check_entry(model, 23, entry23m)

        finally:
            if model is not None:
                model.close()


    def test_08_swap_terms(self):
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

            self.compare_model(model, ALL)

            entry12 = model.entry(12)
            entry11 = model.entry(11)
            self.check_entry(model, 12, entry12)
            self.check_entry(model, 11, entry11)
            model.swapTerms(12, 11) # Golf <-> Hotel
            entry12m = copyAndReplace(entry12, term=entry11.term,
                                      sortas=entry11.sortas,
                                      saf=entry11.saf)
            entry11m = copyAndReplace(entry11, term=entry12.term,
                                      sortas=entry12.sortas,
                                      saf=entry12.saf)
            self.check_entry(model, 12, entry12m)
            self.check_entry(model, 11, entry11m)
            model.undo() # Undo Swap 12, 11
            self.check_entry(model, 12, entry12)
            self.check_entry(model, 11, entry11)
            model.redo() # Redo Swap 12, 11
            self.check_entry(model, 12, entry12m)
            self.check_entry(model, 11, entry11m)
            model.swapTerms(11, 12) # should be the same as undo
            self.check_entry(model, 12, entry12)
            self.check_entry(model, 11, entry11)
            model.undo() # Swap 12, 11
            self.check_entry(model, 12, entry12m)
            self.check_entry(model, 11, entry11m)
            model.undo() # Undo Swap 12, 11
            self.check_entry(model, 12, entry12)
            self.check_entry(model, 11, entry11)
            model.swapTerms(11, 12) # should be the same as redo
            self.check_entry(model, 12, entry12m)
            self.check_entry(model, 11, entry11m)

        finally:
            if model is not None:
                model.close()


    def test_09_edit(self):
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

            self.compare_model(model, ALL)

            entry = model.entry(8)
            self.check_entry(model, 8, entry)
            entry8a = model.editEntry(
                entry, entry.saf, entry.sortas, entry.term,
                "1, 5, 7", "Notes #8")
            self.check_entry(model, 8, entry8a)
            model.undo()
            self.check_entry(model, 8, entry)
            model.redo()
            self.check_entry(model, 8, entry8a)

        finally:
            if model is not None:
                model.close()


    def test_10_move_to_top(self):
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

            self.compare_model(model, ALL)

            model.moveToTop(27)
            self.compare_model(model, MOVE_TO_TOP)
            model.undo()
            self.compare_model(model, ALL)

        finally:
            if model is not None:
                model.close()


    def compare_model(self, model, output):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            self.print_entries(model)
        self.assertMultiLineEqual(stdout.getvalue().strip(), output)


    def check_entry(self, model, eid, entry):
        mentry = model.entry(eid)
        self.assertEqual(mentry.term, entry.term)
        self.assertEqual(mentry.saf, entry.saf)
        self.assertEqual(mentry.sortas, entry.sortas)
        self.assertEqual(mentry.pages, entry.pages)
        self.assertEqual(mentry.notes, entry.notes)


    def _check_xrefs(self, model):
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



ALL = """
Alpha four
    Foxtrot five
        Sierra
    Lima
    Romeo four
        Charlie six
        Whisky three
Delta five
Echo
    Victor six
        and Reasons
        Bravo four
        Quebec one
        Yankee two
Juliet five
    Hotel three
        India five
        November
        Zulu six
    Tango six
        Mike
Kilo two
    Golf six
Oscar four
Uniform six
X-Ray three
    Papa five
""".strip()

ONE = """
Quebec one
""".strip()

TWO = """
Kilo two
Yankee two
""".strip()

THREE = """
Hotel three
Whisky three
X-Ray three
""".strip()

FOUR = """
Alpha four
Bravo four
Oscar four
Romeo four
""".strip()

FIVE = """
Delta five
Foxtrot five
India five
Juliet five
Papa five
""".strip()

SIX = """
Charlie six
Golf six
Tango six
Uniform six
Victor six
Zulu six
""".strip()

ALL_WITH_XREFS = """
Alpha four
    Foxtrot five
        Sierra
    Lima
    Romeo four -> see Zulu six
        Charlie six
        Whisky three
Delta five
Echo
    Victor six
        and Reasons
        Bravo four
        Quebec one
        Yankee two -> see Lima
Juliet five
    Hotel three
        India five
        November -> see Romeo four
        Zulu six
    Tango six
        Mike
Kilo two
    Golf six
Oscar four
Uniform six
X-Ray three
    Papa five
""".strip()

ALL_WITH_XREFS_NO_ROMEO = """
Alpha four
    Foxtrot five
        Sierra
    Lima
Delta five
Echo
    Victor six
        and Reasons
        Bravo four
        Quebec one
        Yankee two -> see Lima
Juliet five
    Hotel three
        India five
        November
        Zulu six
    Tango six
        Mike
Kilo two
    Golf six
Oscar four
Uniform six
X-Ray three
    Papa five
""".strip()

ALL_WITH_XREFS_NO_ALPHA = """
Delta five
Echo
    Victor six
        and Reasons
        Bravo four
        Quebec one
        Yankee two
Juliet five
    Hotel three
        India five
        November
        Zulu six
    Tango six
        Mike
Kilo two
    Golf six
Oscar four
Uniform six
X-Ray three
    Papa five
""".strip()
MANY_DELETED = """
Alpha four
    Foxtrot five
        Sierra
    Lima
    Romeo four
        Charlie six
        Whisky three
Delta five
Echo
Kilo two
    Golf six
Uniform six
""".strip()
DELETED_ENTRIES = """
DeletedEntry(eid=6, term='Juliet five', pages=None, peid=0)
DeletedEntry(eid=8, term='Oscar four', pages=None, peid=0)
DeletedEntry(eid=1, term='X-Ray three', pages=None, peid=0)
DeletedEntry(eid=15, term='Papa five', pages=None, peid=1)
DeletedEntry(eid=13, term='Victor six', pages=None, peid=5)
DeletedEntry(eid=11, term='Hotel three', pages=None, peid=6)
DeletedEntry(eid=9, term='Tango six', pages=None, peid=6)
DeletedEntry(eid=18, term='Mike', pages=None, peid=9)
DeletedEntry(eid=17, term='India five', pages=None, peid=11)
DeletedEntry(eid=19, term='November', pages=None, peid=11)
DeletedEntry(eid=24, term='Zulu six', pages=None, peid=11)
DeletedEntry(eid=27, term='and Reasons', pages=None, peid=13)
DeletedEntry(eid=22, term='Bravo four', pages=None, peid=13)
DeletedEntry(eid=25, term='Quebec one', pages=None, peid=13)
DeletedEntry(eid=26, term='Yankee two', pages=None, peid=13)
""".strip()

PROMOTE1 = """
Alpha four
    Foxtrot five
        Sierra
    Lima
    Romeo four
        Whisky three
            Juliet five
                Tango six
                    Mike
Charlie six
Delta five
Echo
    Quebec one
        Uniform six
    Victor six
        and Reasons
        Bravo four
        Yankee two
Hotel three
    India five
    November
    Zulu six
Kilo two
    Golf six
Oscar four
X-Ray three
    Papa five
""".strip()

MOVE_TO_TOP = """
Alpha four
    Foxtrot five
        Sierra
    Lima
    Romeo four
        Charlie six
        Whisky three
Delta five
Echo
    Victor six
        Bravo four
        Quebec one
        Yankee two
Juliet five
    Hotel three
        India five
        November
        Zulu six
    Tango six
        Mike
Kilo two
    Golf six
Oscar four
Reasons
Uniform six
X-Ray three
    Papa five
""".strip()


if __name__ == "__main__":
    unittest.main()
