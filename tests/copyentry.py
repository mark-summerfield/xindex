#!/usr/bin/env python3
# Copyright © 2016-20 Qtrac Ltd. All rights reserved.

import contextlib
import io
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import tempfile
import unittest

import Lib
import Saf
import SortAs
import Xix
from Const import EntryDataKind, LanguageKind, UNLIMITED, XrefKind


class TestCopyEntry(unittest.TestCase):

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

            model.addXRef(21, 9, XrefKind.SEE_ALSO)
            gid = model.addGroup("Group four")
            eids = (3, 8, 14, 22)
            for eid in eids:
                model.addToGroup(eid, gid)
            model.copyEntry(Lib.CopyInfo(9, 0))
            model.copyEntry(Lib.CopyInfo(3, 12, copyxrefs=True,
                            copygroups=True, copysubentries=True))
            entry = model.entry(24)
            model.editEntry(entry, entry.saf, entry.sortas, entry.term,
                            "2, 3, 5, 7")
            self.assertEqual("2, 3, 5, 7", model.entry(24).pages)
            entry = model.entry(9)
            model.editEntry(entry, entry.saf, entry.sortas, entry.term,
                            "7, 11")
            self.assertEqual("7, 11", model.entry(9).pages)
            model.copyEntry(Lib.CopyInfo(24, 9, withsee=True))

            self.compare_model(model, UPDATED)

            while model.canUndo:
                model.undo()
            for _ in range(len(self.data)):
                model.redo()
            self.compare_model(model, ALL)
            while model.canRedo:
                model.redo()
            self.compare_model(model, UPDATED)

        finally:
            if model is not None:
                model.close()


    def test_02(self):
        model = None
        original = os.path.join(tempfile.gettempdir(), "copyentry02o.xix")
        new = os.path.join(tempfile.gettempdir(), "copyentry02n.xix")
        Lib.remove_file(original)
        Lib.remove_file(new)
        try:
            model = Xix.Model.Model(self.username)
            model.open(original, *self.args)
            self.assertEqual(0, len(model))
            added = []
            for term, peid, eid in self.data:
                model.addEntry(Saf.AUTO, SortAs.wordByWordCMS16(term),
                               term, peid=peid)
                added.append(term)
            self.assertEqual(len(self.data), len(model))

            self.compare_model(model, ALL)

            gid = model.addGroup("Copy Group")
            for eid in {3, 16, 5, 13, 22, 25, 12, 7, 1}:
                model.addToGroup(eid, gid)

            model.saveGrouped(new, {gid})
            model.close()
            model = Xix.Model.Model(self.username)
            model.open(new, *self.args)
            self.assertEqual(8, len(model))
            self.compare_model(model, GROUPED)

        finally:
            if model is not None:
                model.close()
            Lib.remove_file(original)
            Lib.remove_file(new)



    def print_entries(self, model):
        for entry in model.entries(offset=0, limit=UNLIMITED,
                                   entryData=EntryDataKind.ALL_DATA):
            pages = ", " + entry.pages if entry.pages else ""
            xrefs = []
            for xref in list(model.xrefs(entry.eid, transaction=False)):
                xrefs.append("{} {}".format(
                    "see" if xref.kind is XrefKind.SEE else "see also",
                    model.term(xref.to_eid)))
            xrefs = (" -> " + "; ".join(xrefs)) if xrefs else ""
            groups = []
            for group in list(model.groupsForEid(entry.eid)):
                groups.append(group[1])
            groups = " [{}]".format(", ".join(groups)) if groups else ""
            print("{}{}{}{}{}".format((4 * entry.indent) * " ", entry.term,
                  pages, xrefs, groups))


    def compare_model(self, model, output):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            self.print_entries(model)
        self.assertMultiLineEqual(stdout.getvalue().strip(), output)


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

UPDATED = """
Alpha four [Group four]
    Foxtrot five
        Sierra
    Lima
    Romeo four [Group four]
        Charlie six
        Whisky three -> see also Tango six
Delta five
Echo
    Victor six
        and Reasons
        Bravo four [Group four]
        Quebec one
        Yankee two
Juliet five
    Hotel three
        India five
        November
        Zulu six, 2, 3, 5, 7
    Tango six, 7, 11
        Mike
        Zulu six -> see Zulu six
Kilo two
    Golf six
        Alpha four [Group four]
            Foxtrot five
                Sierra
            Lima
            Romeo four [Group four]
                Charlie six
                Whisky three -> see also Tango six
Oscar four [Group four]
Tango six
Uniform six
X-Ray three
    Papa five
""".strip()

GROUPED = """
Alpha four [Copy Group]
    Lima [Copy Group]
Echo [Copy Group]
    Victor six [Copy Group]
        Bravo four [Copy Group]
        Quebec one [Copy Group]
Uniform six [Copy Group]
X-Ray three [Copy Group]
""".strip()


if __name__ == "__main__":
    unittest.main()
