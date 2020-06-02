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


class TestMerge(unittest.TestCase):

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
            ("Tango six", 6, 9, ""),
            ("Foxtrot five", 3, 10, ""),
            ("Hotel three", 6, 11, "vii, 6, 18, 79"),
            ("Golf six", 4, 12, ""),
            ("Victor six", 5, 13, "xiv, 23, 98"),
            ("Romeo four", 3, 14, ""),
            ("Papa five", 1, 15, ""),
            ("Lima", 3, 16, ""),
            ("India five", 11, 17, ""),
            ("Mike", 9, 18, ""),
            ("November", 11, 19, ""),
            ("Sierra", 10, 20, ""),
            ("Whisky three", 14, 21, ""),
            ("Bravo four", 13, 22, ""),
            ("Charlie six", 14, 23, ""),
            ("Zulu six", 11, 24, ""),
            ("Quebec one", 13, 25, ""),
            ("Yankee two", 13, 26, "17, 29"),
            )
        self.extra = {"India five": "11, 19",
                      "November": "21, 91",
                      "Zulu six": "17, 86",
                      "Tango six": "21, 86",
                      "Mike": "17, 22",
                      "Bravo four": "xi, xiv, 23",
                      "Quebec one": "xii, 98, 111"}


    def test_01_merge_into_parent(self):
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

            self.compare_model(model, ALL)

            # Merge Yankee into Victor
            model.mergeIntoParent(26, 13)

            self.compare_model(model, AFTER_01)

        finally:
            if model is not None:
                model.close()


    def test_02_merge_into_parent(self):
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

            self.compare_model(model, ALL)

            # Merge Hotel into Juliet
            model.mergeIntoParent(11, 6)

            self.compare_model(model, AFTER_02)

        finally:
            if model is not None:
                model.close()


    def test_03_merge_into_parent(self):
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

            self.compare_model(model, ALL)

            # Merge Hotel into Juliet
            model.mergeIntoParent(11, 6)
            # Merge Yankee into Victor
            model.mergeIntoParent(26, 13)

            self.compare_model(model, AFTER_03)

            model.undo()

            self.compare_model(model, AFTER_02)

            model.undo()

            self.compare_model(model, ALL)

            model.redo()

            self.compare_model(model, AFTER_02)

            model.redo()

            self.compare_model(model, AFTER_03)

        finally:
            if model is not None:
                model.close()


    def test_04_merge_subentries(self):
        model = None
        try:
            model = Xix.Model.Model(self.username)
            model.open(":memory:", *self.args)
            self.assertEqual(0, len(model))
            for term, peid, eid, pages in self.data:
                pages = self.extra.get(term, pages)
                model.addEntry(Saf.AUTO, SortAs.wordByWordCMS16(term),
                               term, pages=pages, peid=peid)
            self.assertEqual(len(self.data), len(model))
            model.addXRef(6, 11, XrefKind.SEE_ALSO) # Juliet -> Hotel
            model.addXRef(26, 5, XrefKind.SEE) # Yankee -> Echo
            model.addGenericXRef(26, "under #1", XrefKind.SEE_GENERIC)

            self.compare_model(model, ALL_04)

            model.mergeSubentries(13)

            self.compare_model(model, AFTER_04)

            model.undo()

            self.compare_model(model, ALL_04)

            model.redo()

            self.compare_model(model, AFTER_04)

        finally:
            if model is not None:
                model.close()



    def test_05_merge_subentries(self):
        model = None
        try:
            model = Xix.Model.Model(self.username)
            model.open(":memory:", *self.args)
            self.assertEqual(0, len(model))
            for term, peid, eid, pages in self.data:
                pages = self.extra.get(term, pages)
                model.addEntry(Saf.AUTO, SortAs.wordByWordCMS16(term),
                               term, pages=pages, peid=peid)
            self.assertEqual(len(self.data), len(model))
            model.addXRef(6, 11, XrefKind.SEE_ALSO) # Juliet -> Hotel
            model.addXRef(26, 5, XrefKind.SEE) # Yankee -> Echo
            model.addGenericXRef(26, "under #1", XrefKind.SEE_GENERIC)

            self.compare_model(model, ALL_04)

            model.mergeSubentries(6)

            self.compare_model(model, AFTER_05A)

            model.undo()

            self.compare_model(model, ALL_04)

            model.redo()

            self.compare_model(model, AFTER_05A)

            model.mergeSubentries(6)

            self.compare_model(model, AFTER_05B)

            model.undo()

            self.compare_model(model, AFTER_05A)

            model.redo()

            self.compare_model(model, AFTER_05B)

            model.undo()
            model.undo()
            self.compare_model(model, ALL_04)

            model.redo()

            self.compare_model(model, AFTER_05A)

            model.redo()

            self.compare_model(model, AFTER_05B)

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
        Bravo four
        Quebec one
        Yankee two -> see Echo; see also (generic) under #1, 17, 29
Juliet five -> see also Hotel three, 19, 31, 108
    Hotel three, vii, 6, 18, 79
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
    Victor six -> see Echo; \
see also (generic) under #1, xiv, 17, 23, 29, 98
        Bravo four
        Quebec one
Juliet five -> see also Hotel three, 19, 31, 108
    Hotel three, vii, 6, 18, 79
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
        Bravo four
        Quebec one
        Yankee two -> see Echo; see also (generic) under #1, 17, 29
Juliet five, vii, 6, 18, 19, 31, 79, 108
    India five
    November
    Tango six
        Mike
    Zulu six
Kilo two
    Golf six
Oscar four
Uniform six
X-Ray three
    Papa five
""".strip()


AFTER_03 = """
Alpha four
    Foxtrot five
        Sierra
    Lima
    Romeo four
        Charlie six
        Whisky three
Delta five
Echo
    Victor six -> see Echo; \
see also (generic) under #1, xiv, 17, 23, 29, 98
        Bravo four
        Quebec one
Juliet five, vii, 6, 18, 19, 31, 79, 108
    India five
    November
    Tango six
        Mike
    Zulu six
Kilo two
    Golf six
Oscar four
Uniform six
X-Ray three
    Papa five
""".strip()


ALL_04 = """
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
    Victor six -> see Echo; see also (generic) under #1, xi, xii, xiv, \
17, 23, 29, 98, 111
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


AFTER_05A = """
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
Juliet five, vii, 6, 18, 19, 21, 31, 79, 86, 108
    India five, 11, 19
    Mike, 17, 22
    November, 21, 91
    Zulu six, 17, 86
Kilo two
    Golf six
Oscar four
Uniform six
X-Ray three
    Papa five
""".strip()

AFTER_05B = """
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
Juliet five, vii, 6, 11, 17, 18, 19, 21, 22, 31, 79, 86, 91, 108
Kilo two
    Golf six
Oscar four
Uniform six
X-Ray three
    Papa five
""".strip()


ALL_06 = """
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
    Tango, dance, 21, 86
        Mike, 17, 22
Kilo two
    Golf six
Oscar four
Uniform six
X-Ray three
    Papa five
""".strip()


AFTER_06A = """
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
            November, 21, 91
        Zulu six, 17, 86
    Tango, dance, 21, 86
        Mike, 17, 22
Kilo two
    Golf six
Oscar four
Uniform six
X-Ray three
    Papa five
""".strip()


AFTER_06B = """
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
            November, 21, 91
        Zulu six, 17, 86
    Tango, 21, 86
        dance, 21, 86
        Mike, 17, 22
Kilo two
    Golf six
Oscar four
Uniform six
X-Ray three
    Papa five
""".strip()


if __name__ == "__main__":
    unittest.main()
