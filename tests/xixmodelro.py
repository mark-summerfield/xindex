#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

import contextlib
import io
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import tempfile
import unittest

import Check
import Saf
import SortAs
import Xix
from Const import (
    EntryDataKind, FilterKind, LanguageKind, UNLIMITED, XrefKind)


class TestXixModelRO(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None
        self.args = (LanguageKind.AMERICAN, "wordByWordCMS16",
                     "pageRangeCMS16")
        self.username = "Tester"
        data = ( # Term, peid, eid
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
            ("<b>Oscar Four</b>", 0, 28),
            ("Victor <i>Six</i>", 5, 29),
            )
        self.filename = os.path.join(tempfile.gettempdir(), "ro.xix")
        try:
            os.remove(self.filename)
        except OSError:
            pass
        model = None
        try:
            model = Xix.Model.Model(self.username)
            model.open(self.filename, *self.args)
            added = []
            for term, peid, eid in data:
                model.addEntry(Saf.AUTO, SortAs.wordByWordCMS16(term),
                               term, peid=peid)
                added.append(term)
        finally:
            if model is not None:
                model.close()


    def test_0_setup(self):
        model = None
        try:
            model = Xix.Model.Model(self.username)
            model.open(self.filename, *self.args)
            self.compare_model(model, ALL)
        finally:
            if model is not None:
                model.close()


    def test_1(self):
        xix = None
        try:
            xix = Xix.XixRO.XixRO()
            self.assertFalse(xix.open("no such file"))
            self.assertTrue(xix.open(self.filename))
            self.assertEqual(len(xix), 29)
            eids = sorted(xix.filteredEntries(
                          filter=FilterKind.SAME_TERM_TEXTS))
            self.assertListEqual([8, 13, 28, 29], eids)
        finally:
            if xix is not None:
                xix.close()


    def test_2(self):
        reply = Check.filteredEntries(
            filename="no such file", filter=FilterKind.SAME_TERM_TEXTS,
            match="")
        reply.wait()
        self.assertIsNone(reply.get())


    def test_3(self):
        reply = Check.filteredEntries(
            filename=self.filename, filter=FilterKind.SAME_TERM_TEXTS,
            match="")
        reply.wait()
        self.assertListEqual([8, 13, 28, 29], sorted(reply.get()))


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
            xrefs = (" -> " + "; ".join(xrefs)) if xrefs else ""
            print("{}{}{}".format((4 * entry.indent) * " ", entry.term,
                  xrefs))


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
    Victor <i>Six</i>
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
<b>Oscar Four</b>
Uniform six
X-Ray three
    Papa five
""".strip()


if __name__ == "__main__":
    unittest.main()
