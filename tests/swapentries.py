#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

import contextlib
import io
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import unittest

import apsw

import Saf
import SortAs
import Xix
from Const import EntryDataKind, LanguageKind, UNLIMITED, XrefKind


class TestSwapEntries(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None
        self.args = (LanguageKind.AMERICAN, "wordByWordCMS16",
                     "pageRangeCMS16")
        self.username = "Tester"
        self.data = ( # Term, peid, eid, pages
            ("X-Ray three", 0, 1, ""),
            ("Delta five", 0, 2, ""),
            ("Alpha four", 0, 3, ""),
            ("Kilo two", 0, 4, ""),
            ("Echo", 0, 5, ""),
            ("Juliet five", 0, 6, "19, 31, 108"),
            ("Uniform six", 0, 7, ""),
            ("Oscar four", 0, 8, ""),
            ("Tango six", 6, 9, "21, 86"),
            ("Foxtrot five", 3, 10, ""),
            ("Hotel three", 6, 11, "vii, 6, 18, 79"),
            ("Golf six", 4, 12, ""),
            ("Victor six", 5, 13, "xiv, 23, 98"),
            ("Romeo four", 3, 14, ""),
            ("Papa five", 1, 15, ""),
            ("Lima", 3, 16, ""),
            ("India five", 11, 17, "11, 19"),
            ("Mike", 9, 18, "17, 22"),
            ("November", 11, 19, "21, 91"),
            ("Sierra", 10, 20, ""),
            ("Whisky three", 14, 21, ""),
            ("Bravo four", 13, 22, "xi, xiv, 23"),
            ("Charlie six", 14, 23, ""),
            ("Zulu six", 11, 24, "17, 86"),
            ("Quebec one", 13, 25, "xii, 98, 111"),
            ("Yankee two", 13, 26, "17, 29"),
            )


    def test_01_swap_entries(self):
        model = None
        try:
            model = Xix.Model.Model(self.username)
            model.open(":memory:", *self.args)
            self.assertEqual(0, len(model))
            for term, peid, eid, pages in self.data:
                model.addEntry(Saf.AUTO, SortAs.wordByWordCMS16(term),
                               term, pages=pages, peid=peid)
            self.assertEqual(len(self.data), len(model))
            model.addXRef(6, 11, XrefKind.SEE_ALSO) # Juliet -> Hotel
            model.addXRef(26, 5, XrefKind.SEE) # Yankee -> Echo
            model.addGenericXRef(26, "under #1", XrefKind.SEE_GENERIC)

            # Swap parent <-> child
            self.compare_model(model, ALL)
            model.swapEntries(11, 6) # Hotel <-> Juliet
            self.compare_model(model, AFTER_01)
            model.swapEntries(11, 6) # Hotel <-> Juliet
            self.compare_model(model, ALL)

            # Swap grandparent <-> grandchild
            model.swapEntries(6, 24) # Juliet <-> Zulu
            self.compare_model(model, AFTER_02)
            model.swapEntries(6, 24) # Juliet <-> Zulu
            self.compare_model(model, ALL)

            # Swap two unrelated top-levels
            model.swapEntries(3, 5) # Alpha <-> Echo
            self.compare_model(model, AFTER_03)
            model.swapEntries(3, 5) # Alpha <-> Echo
            self.compare_model(model, ALL)

            # Swap two unrelated main and subsub
            model.swapEntries(6, 25) # Juliet <-> Quebec
            self.compare_model(model, AFTER_04)
            model.swapEntries(6, 25) # Juliet <-> Quebec
            self.compare_model(model, ALL)

            # Swap two unrelated main and sub
            model.swapEntries(5, 9) # Echo <-> Tango
            self.compare_model(model, AFTER_05)
            model.swapEntries(9, 5) # Tango <-> Echo
            self.compare_model(model, ALL)

            # Swap two unrelated main and sub
            model.swapEntries(11, 26) # Hotel <-> Yankee
            self.compare_model(model, AFTER_06)
            model.swapEntries(26, 11) # Yankee <-> Hotel
            self.compare_model(model, ALL)

        finally:
            if model is not None:
                model.close()


    def test_02_swap_entries(self):
        model = None
        try:
            model = Xix.Model.Model(self.username)
            model.open(":memory:", *self.args)
            self.assertEqual(0, len(model))
            for term, peid, eid, pages in self.data:
                model.addEntry(Saf.AUTO, SortAs.wordByWordCMS16(term),
                               term, pages=pages, peid=peid)
            self.assertEqual(len(self.data), len(model))
            model.addXRef(6, 11, XrefKind.SEE_ALSO) # Juliet -> Hotel
            model.addXRef(26, 5, XrefKind.SEE) # Yankee -> Echo
            model.addGenericXRef(26, "under #1", XrefKind.SEE_GENERIC)

            # Swap parent <-> child
            self.compare_model(model, ALL)
            model.swapEntries(11, 6) # Hotel <-> Juliet
            self.compare_model(model, AFTER_01)
            model.undo()
            self.compare_model(model, ALL)
            model.redo()
            self.compare_model(model, AFTER_01)
            model.undo()

            # Swap grandparent <-> grandchild
            model.swapEntries(6, 24) # Juliet <-> Zulu
            self.compare_model(model, AFTER_02)
            model.undo()
            self.compare_model(model, ALL)
            model.redo()
            self.compare_model(model, AFTER_02)
            model.undo()

            # Swap two unrelated top-levels
            model.swapEntries(3, 5) # Alpha <-> Echo
            self.compare_model(model, AFTER_03)
            model.undo()
            self.compare_model(model, ALL)
            model.redo()
            self.compare_model(model, AFTER_03)
            model.undo()

            # Swap two unrelated main and subsub
            model.swapEntries(6, 25) # Juliet <-> Quebec
            self.compare_model(model, AFTER_04)
            model.undo()
            self.compare_model(model, ALL)
            model.redo()
            self.compare_model(model, AFTER_04)
            model.undo()

            # Swap two unrelated main and sub
            model.swapEntries(5, 9) # Echo <-> Tango
            self.compare_model(model, AFTER_05)
            model.undo()
            self.compare_model(model, ALL)
            model.redo()
            self.compare_model(model, AFTER_05)
            model.undo()

            # Swap two unrelated main and sub
            model.swapEntries(11, 26) # Hotel <-> Yankee
            self.compare_model(model, AFTER_06)
            model.undo()
            self.compare_model(model, ALL)
            model.redo()
            self.compare_model(model, AFTER_06)
            model.undo()

        finally:
            if model is not None:
                model.close()


    def compare_model(self, model, output):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            self.print_entries(model)
        self.assertMultiLineEqual(stdout.getvalue().strip(), output)


    def print_entries(self, model):
        for entry in model.entries(offset=0, limit=UNLIMITED,
                                   entryData=EntryDataKind.ALL_DATA):
            xrefs = []
            for xref in list(model.xrefs(entry.eid, transaction=False)):
                xrefs.append("{} {}".format(
                    "see" if xref.kind is XrefKind.SEE else "see also",
                    model.term(xref.to_eid)))
            for xref in list(model.generic_xrefs(entry.eid,
                             transaction=False)):
                xrefs.append("{} (generic) {}".format(
                    "see" if xref.kind is XrefKind.SEE else "see also",
                    xref.term))
            xrefs = (" -> " + "; ".join(xrefs)) if xrefs else ""
            pages = "" if not entry.pages else ", {}".format(entry.pages)
            print("{}{}{}{}".format((4 * entry.indent) * " ", entry.term,
                  xrefs, pages))



    def dump(self, db):
        print("dump")
        shell = apsw.Shell(stdout=sys.stdout, db=db)
        shell.process_command(".dump entries xrefs generic_xrefs")


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
    Victor six, xiv, 23, 98
        Bravo four, xi, xiv, 23
        Quebec one, xii, 98, 111
        Yankee two -> see Echo; see also (generic) under #1, 17, 29
Juliet five -> see also Hotel three, 19, 31, 108
    Hotel three, vii, 6, 18, 79
        India five, 11, 19
        November, 21, 91
        Zulu six, 17, 86
    Tango six, 21, 86
        Mike, 17, 22
Kilo two
    Golf six
Oscar four
Uniform six
X-Ray three
    Papa five
""".strip()

AFTER_01 = """
Alpha four
    Foxtrot five
        Sierra
    Lima
    Romeo four
        Charlie six
        Whisky three
Delta five
Echo
    Victor six, xiv, 23, 98
        Bravo four, xi, xiv, 23
        Quebec one, xii, 98, 111
        Yankee two -> see Echo; see also (generic) under #1, 17, 29
Hotel three, vii, 6, 18, 79
    Juliet five -> see also Hotel three, 19, 31, 108
        India five, 11, 19
        November, 21, 91
        Zulu six, 17, 86
    Tango six, 21, 86
        Mike, 17, 22
Kilo two
    Golf six
Oscar four
Uniform six
X-Ray three
    Papa five
""".strip()

AFTER_02 = """
Alpha four
    Foxtrot five
        Sierra
    Lima
    Romeo four
        Charlie six
        Whisky three
Delta five
Echo
    Victor six, xiv, 23, 98
        Bravo four, xi, xiv, 23
        Quebec one, xii, 98, 111
        Yankee two -> see Echo; see also (generic) under #1, 17, 29
Kilo two
    Golf six
Oscar four
Uniform six
X-Ray three
    Papa five
Zulu six, 17, 86
    Hotel three, vii, 6, 18, 79
        India five, 11, 19
        Juliet five -> see also Hotel three, 19, 31, 108
        November, 21, 91
    Tango six, 21, 86
        Mike, 17, 22
""".strip()

AFTER_03 = """
Alpha four
    Victor six, xiv, 23, 98
        Bravo four, xi, xiv, 23
        Quebec one, xii, 98, 111
        Yankee two -> see Echo; see also (generic) under #1, 17, 29
Delta five
Echo
    Foxtrot five
        Sierra
    Lima
    Romeo four
        Charlie six
        Whisky three
Juliet five -> see also Hotel three, 19, 31, 108
    Hotel three, vii, 6, 18, 79
        India five, 11, 19
        November, 21, 91
        Zulu six, 17, 86
    Tango six, 21, 86
        Mike, 17, 22
Kilo two
    Golf six
Oscar four
Uniform six
X-Ray three
    Papa five
""".strip()

AFTER_04 = """
Alpha four
    Foxtrot five
        Sierra
    Lima
    Romeo four
        Charlie six
        Whisky three
Delta five
Echo
    Victor six, xiv, 23, 98
        Bravo four, xi, xiv, 23
        Juliet five -> see also Hotel three, 19, 31, 108
        Yankee two -> see Echo; see also (generic) under #1, 17, 29
Kilo two
    Golf six
Oscar four
Quebec one, xii, 98, 111
    Hotel three, vii, 6, 18, 79
        India five, 11, 19
        November, 21, 91
        Zulu six, 17, 86
    Tango six, 21, 86
        Mike, 17, 22
Uniform six
X-Ray three
    Papa five
""".strip()


AFTER_05 = """
Alpha four
    Foxtrot five
        Sierra
    Lima
    Romeo four
        Charlie six
        Whisky three
Delta five
Juliet five -> see also Hotel three, 19, 31, 108
    Echo
        Mike, 17, 22
    Hotel three, vii, 6, 18, 79
        India five, 11, 19
        November, 21, 91
        Zulu six, 17, 86
Kilo two
    Golf six
Oscar four
Tango six, 21, 86
    Victor six, xiv, 23, 98
        Bravo four, xi, xiv, 23
        Quebec one, xii, 98, 111
        Yankee two -> see Echo; see also (generic) under #1, 17, 29
Uniform six
X-Ray three
    Papa five
""".strip()

AFTER_06 = """
Alpha four
    Foxtrot five
        Sierra
    Lima
    Romeo four
        Charlie six
        Whisky three
Delta five
Echo
    Victor six, xiv, 23, 98
        Bravo four, xi, xiv, 23
        Hotel three, vii, 6, 18, 79
        Quebec one, xii, 98, 111
Juliet five -> see also Hotel three, 19, 31, 108
    Tango six, 21, 86
        Mike, 17, 22
    Yankee two -> see Echo; see also (generic) under #1, 17, 29
        India five, 11, 19
        November, 21, 91
        Zulu six, 17, 86
Kilo two
    Golf six
Oscar four
Uniform six
X-Ray three
    Papa five
""".strip()


if __name__ == "__main__":
    unittest.main()
