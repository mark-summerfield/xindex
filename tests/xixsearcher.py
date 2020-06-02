#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import unittest

from PySide.QtGui import QApplication, QTextDocument

import Saf
import SortAs
import Window.ReplacePanel
import Xix
import Xix.Searcher
from Const import FilterKind, LanguageKind, SearchFieldKind


def reportProgress(percent):
    pass # print("{}%".format(percent))


"""
Alpha four #3
    Foxtrot five #10
        Sierra #20
    Lima #16
    Romeo four #14
        Charlie six #23
        Whisky three #21
Delta five #2
Echo #5
    Victor six #13
        Bravo four #22
        Quebec one #25
        Yankee two #26
Juliet five #6
    Hotel three #11
        India five #17
        November #19
        Zulu six #24
    Tango six #9
        Mike #18
Kilo two #4
    Golf six #12
Oscar four #8
Uniform six #7
web 1 #27
web 2 #28
web 3 webbing #29
webbed 4 #30
X-Ray three #1
    Papa five #15
"""


class TestXixSearcher(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None
        self.args = (LanguageKind.AMERICAN, "wordByWordNISO3",
                     "pageRangeCMS16")
        self.username = "Tester"
        self.data = ( # Term, pages, notes, peid, eid
            ("X-Ray three", "1-5", "", 0, 1),
            ("Delta five", "7, 11, 15pin", "", 0, 2),
            ("Alpha four pin", "", "things like this", 0, 3),
            ("Kilo two", "", "", 0, 4),
            ("Echo", "", "", 0, 5),
            ("Juliet five", "", "", 0, 6),
            ("Uniform pin six", "", "pinpoint accuracy", 0, 7),
            ("Oscar four", "", "", 0, 8),
            ("Tango six", "", "", 6, 9),
            ("Foxtrot five", "", "", 3, 10),
            ("Hotel three", "", "pin this pin on me", 6, 11),
            ("Golf six", "", "", 4, 12),
            ("Victor six", "3, 14, <i>25-27</i>", "", 5, 13),
            ("Romeo four", "", "", 3, 14),
            ("Papa five", "", "", 1, 15),
            ("Lima", "", "", 3, 16),
            ("India pin five pin", "", "metaphors", 11, 17),
            ("Mike", "", "", 9, 18),
            ("November", "", "", 11, 19),
            ("Sierra", "", "", 10, 20),
            ("Whisky three", "<i>11<b>pin</b></i>", "", 14, 21),
            ("Bravo four", "", "", 13, 22),
            ("Charlie six", "", "variability scenes", 14, 23),
            ("pin Zulu six", "", "", 11, 24),
            ("Quebec pin one", "", "Pins and needles", 13, 25),
            ("Yankee two", "", "", 13, 26),
            ("web 1", "", "", 0, 27),
            ("web 2", "", "", 0, 28),
            ("web 3 webbing", "", "", 0, 29),
            ("webbed 4", "", "", 0, 30),
            )
        self.dataForEid = {}
        for data in self.data:
            self.dataForEid[data[-1]] = data


    def editEntry(self, model, match):
        entry = model.entry(match.eid)
        term = entry.term
        pages = entry.pages
        notes = entry.notes
        if match.field is SearchFieldKind.TERM:
            term = match.text
        elif match.field is SearchFieldKind.PAGES:
            pages = match.text
        elif match.field is SearchFieldKind.NOTES:
            notes = match.text
        return model.editEntry(entry, entry.saf, entry.sortas, term, pages,
                               notes)


    def test_01(self):
        model = None
        searcher = Xix.Searcher.Searcher(reportProgress)
        try:
            model = Xix.Model.Model(self.username)
            self.prepare(model)
            options = Window.ReplacePanel.Options(
                pattern=None, literal="pin", replacement="%",
                ignorecase=True, wholewords=False, filter=None,
                match="", terms=True, pages=True, notes=True)
            Match = Xix.Searcher.Match
            expected = {
                Match(2, SearchFieldKind.PAGES, "7, 11, 15%", 9, 12),
                Match(3, SearchFieldKind.TERM, "Alpha four %", 11, 14),
                Match(7, SearchFieldKind.NOTES, "%point accuracy", 0, 3),
                Match(7, SearchFieldKind.TERM, "Uniform % six", 8, 11),
                Match(11, SearchFieldKind.NOTES, "% this pin on me", 0, 3),
                Match(11, SearchFieldKind.NOTES, "pin this % on me", 9, 12),
                Match(17, SearchFieldKind.TERM, "India % five pin", 6, 9),
                Match(17, SearchFieldKind.TERM, "India pin five %", 15, 18),
                Match(21, SearchFieldKind.PAGES, "<i>11<b>%</b></i>", 2, 5),
                Match(24, SearchFieldKind.TERM, "% Zulu six", 0, 3),
                Match(25, SearchFieldKind.TERM, "Quebec % one", 7, 10),
                Match(25, SearchFieldKind.NOTES, "%s and needles", 0, 3),
                }
            actual = set()
            searcher.prepare(model, options)
            while True:
                match = searcher.search()
                if match is None:
                    break
                actual.add(match)
            # self.debug(actual)
            self.assertSetEqual(actual, expected)
        finally:
            searcher.stop()
            if model is not None:
                model.close()


    def test_01a(self):
        model = None
        searcher = Xix.Searcher.Searcher(reportProgress)
        try:
            model = Xix.Model.Model(self.username)
            model.open(":memory:", *self.args)
            self.assertEqual(0, len(model))
            term = "India pin five pin"
            model.addEntry(Saf.AUTO, SortAs.wordByWordNISO3(term), term)
            self.assertEqual(1, len(model))
            options = Window.ReplacePanel.Options(
                pattern=None, literal="pin", replacement="%",
                ignorecase=True, wholewords=False, filter=None,
                match="", terms=True, pages=True, notes=True)
            Match = Xix.Searcher.Match
            expected = {
                Match(1, SearchFieldKind.TERM, "India % five pin", 6, 9),
                Match(1, SearchFieldKind.TERM, "India % five %", 13, 16),
                }
            actual = set()
            searcher.prepare(model, options)
            while True:
                match = searcher.search()
                if match is None:
                    break
                actual.add(match)
                self.editEntry(model, match)
            self.assertSetEqual(actual, expected)
        finally:
            searcher.stop()
            if model is not None:
                model.close()


    def test_01b(self):
        model = None
        searcher = Xix.Searcher.Searcher(reportProgress)
        try:
            model = Xix.Model.Model(self.username)
            self.prepare(model)
            options = Window.ReplacePanel.Options(
                pattern=None, literal="pin", replacement="%",
                ignorecase=True, wholewords=False, filter=None,
                match="", terms=True, pages=True, notes=True)
            Match = Xix.Searcher.Match
            expected = {
                Match(2, SearchFieldKind.PAGES, "7, 11, 15%", 9, 12),
                Match(3, SearchFieldKind.TERM, "Alpha four %", 11, 14),
                Match(7, SearchFieldKind.NOTES, "%point accuracy", 0, 3),
                Match(7, SearchFieldKind.TERM, "Uniform % six", 8, 11),
                Match(11, SearchFieldKind.NOTES, "% this pin on me", 0, 3),
                Match(11, SearchFieldKind.NOTES, "% this % on me", 7, 10),
                Match(17, SearchFieldKind.TERM, "India % five pin", 6, 9),
                Match(17, SearchFieldKind.TERM, "India % five %", 13, 16),
                Match(21, SearchFieldKind.PAGES, "<i>11<b>%</b></i>", 2, 5),
                Match(24, SearchFieldKind.TERM, "% Zulu six", 0, 3),
                Match(25, SearchFieldKind.TERM, "Quebec % one", 7, 10),
                Match(25, SearchFieldKind.NOTES, "%s and needles", 0, 3),
                }
            actual = set()
            searcher.prepare(model, options)
            while True:
                match = searcher.search()
                if match is None:
                    break
                actual.add(match)
                self.editEntry(model, match)
            # self.debug(actual)
            self.assertSetEqual(actual, expected)
        finally:
            searcher.stop()
            if model is not None:
                model.close()


    def test_02(self):
        model = None
        searcher = Xix.Searcher.Searcher(reportProgress)
        try:
            model = Xix.Model.Model(self.username)
            self.prepare(model)
            options = Window.ReplacePanel.Options(
                pattern=None, literal="pin", replacement="X1",
                ignorecase=False, wholewords=False, filter=None,
                match="", terms=True, pages=True, notes=True)
            Match = Xix.Searcher.Match
            expected = {
                Match(2, SearchFieldKind.PAGES, "7, 11, 15X1", 9, 12),
                Match(3, SearchFieldKind.TERM, "Alpha four X1", 11, 14),
                Match(7, SearchFieldKind.NOTES, "X1point accuracy", 0, 3),
                Match(7, SearchFieldKind.TERM, "Uniform X1 six", 8, 11),
                Match(11, SearchFieldKind.NOTES, "X1 this pin on me", 0, 3),
                Match(11, SearchFieldKind.NOTES, "X1 this X1 on me", 8, 11),
                Match(17, SearchFieldKind.TERM, "India X1 five pin", 6, 9),
                Match(17, SearchFieldKind.TERM, "India X1 five X1", 14, 17),
                Match(21, SearchFieldKind.PAGES, "<i>11<b>X1</b></i>", 2,
                      5),
                Match(24, SearchFieldKind.TERM, "X1 Zulu six", 0, 3),
                Match(25, SearchFieldKind.TERM, "Quebec X1 one", 7, 10),
                }
            actual = set()
            searcher.prepare(model, options)
            while True:
                match = searcher.search()
                if match is None:
                    break
                actual.add(match)
                self.editEntry(model, match)
            # self.debug(actual)
            self.assertSetEqual(actual, expected)
        finally:
            searcher.stop()
            if model is not None:
                model.close()

    def test_03(self):
        model = None
        searcher = Xix.Searcher.Searcher(reportProgress)
        try:
            model = Xix.Model.Model(self.username)
            self.prepare(model)
            options = Window.ReplacePanel.Options(
                pattern=None, literal="pin", replacement="(xOx)",
                ignorecase=False, wholewords=True, filter=None,
                match="", terms=True, pages=True, notes=True)
            Match = Xix.Searcher.Match
            expected = {
                Match(3, SearchFieldKind.TERM, "Alpha four (xOx)", 11, 14),
                Match(7, SearchFieldKind.TERM, "Uniform (xOx) six", 8, 11),
                Match(11, SearchFieldKind.NOTES, "(xOx) this pin on me", 0,
                      3),
                Match(11, SearchFieldKind.NOTES, "(xOx) this (xOx) on me",
                      11, 14),
                Match(17, SearchFieldKind.TERM, "India (xOx) five pin", 6,
                      9),
                Match(17, SearchFieldKind.TERM, "India (xOx) five (xOx)",
                      17, 20),
                Match(24, SearchFieldKind.TERM, "(xOx) Zulu six", 0, 3),
                Match(25, SearchFieldKind.TERM, "Quebec (xOx) one", 7, 10),
                }
            actual = set()
            searcher.prepare(model, options)
            while True:
                match = searcher.search()
                if match is None:
                    break
                actual.add(match)
                self.editEntry(model, match)
            # self.debug(actual)
            self.assertSetEqual(actual, expected)
        finally:
            searcher.stop()
            if model is not None:
                model.close()

    def test_04(self): # Matches none
        model = None
        searcher = Xix.Searcher.Searcher(reportProgress)
        try:
            model = Xix.Model.Model(self.username)
            self.prepare(model)
            options = Window.ReplacePanel.Options(
                pattern=None, literal="NOMATCH", replacement="",
                ignorecase=True, wholewords=False, filter=None,
                match="", terms=True, pages=True, notes=True)
            searcher.prepare(model, options)
            self.assertIsNone(searcher.search())
        finally:
            searcher.stop()
            if model is not None:
                model.close()

    def test_05(self): # terms only
        model = None
        searcher = Xix.Searcher.Searcher(reportProgress)
        try:
            model = Xix.Model.Model(self.username)
            self.prepare(model)
            options = Window.ReplacePanel.Options(
                pattern=None, literal="pin", replacement="%",
                ignorecase=True, wholewords=False, filter=None,
                match="", terms=True, pages=False, notes=False)
            Match = Xix.Searcher.Match
            expected = {
                Match(3, SearchFieldKind.TERM, "Alpha four %", 11, 14),
                Match(7, SearchFieldKind.TERM, "Uniform % six", 8, 11),
                Match(17, SearchFieldKind.TERM, "India % five pin", 6, 9),
                Match(17, SearchFieldKind.TERM, "India % five %", 13, 16),
                Match(24, SearchFieldKind.TERM, "% Zulu six", 0, 3),
                Match(25, SearchFieldKind.TERM, "Quebec % one", 7, 10),
                }
            actual = set()
            searcher.prepare(model, options)
            while True:
                match = searcher.search()
                if match is None:
                    break
                actual.add(match)
                self.editEntry(model, match)
            # self.debug(actual)
            self.assertSetEqual(actual, expected)
        finally:
            searcher.stop()
            if model is not None:
                model.close()


    def test_06(self): # pages only
        model = None
        searcher = Xix.Searcher.Searcher(reportProgress)
        try:
            model = Xix.Model.Model(self.username)
            self.prepare(model)
            options = Window.ReplacePanel.Options(
                pattern=None, literal="pin", replacement="%",
                ignorecase=True, wholewords=False, filter=None,
                match="", terms=False, pages=True, notes=False)
            Match = Xix.Searcher.Match
            expected = {
                Match(2, SearchFieldKind.PAGES, "7, 11, 15%", 9, 12),
                Match(21, SearchFieldKind.PAGES, "<i>11<b>%</b></i>", 2, 5),
                }
            actual = set()
            searcher.prepare(model, options)
            while True:
                match = searcher.search()
                if match is None:
                    break
                actual.add(match)
                self.editEntry(model, match)
            # self.debug(actual)
            self.assertSetEqual(actual, expected)
        finally:
            searcher.stop()
            if model is not None:
                model.close()


    def test_07(self): # notes only
        model = None
        searcher = Xix.Searcher.Searcher(reportProgress)
        try:
            model = Xix.Model.Model(self.username)
            self.prepare(model)
            options = Window.ReplacePanel.Options(
                pattern=None, literal="pin", replacement="Wong",
                ignorecase=True, wholewords=False, filter=None,
                match="", terms=False, pages=False, notes=True)
            Match = Xix.Searcher.Match
            expected = {
                Match(7, SearchFieldKind.NOTES, "Wongpoint accuracy", 0, 3),
                Match(11, SearchFieldKind.NOTES, "Wong this pin on me",
                      0, 3),
                Match(11, SearchFieldKind.NOTES, "Wong this Wong on me",
                      10, 13),
                Match(25, SearchFieldKind.NOTES, "Wongs and needles", 0, 3),
                }
            actual = set()
            searcher.prepare(model, options)
            while True:
                match = searcher.search()
                if match is None:
                    break
                actual.add(match)
                self.editEntry(model, match)
            # self.debug(actual)
            self.assertSetEqual(actual, expected)
        finally:
            searcher.stop()
            if model is not None:
                model.close()


    def test_08(self): # terms & notes
        model = None
        searcher = Xix.Searcher.Searcher(reportProgress)
        try:
            model = Xix.Model.Model(self.username)
            self.prepare(model)
            options = Window.ReplacePanel.Options(
                pattern=None, literal="pin", replacement="%",
                ignorecase=True, wholewords=False, filter=None,
                match="", terms=True, pages=False, notes=True)
            Match = Xix.Searcher.Match
            expected = {
                Match(3, SearchFieldKind.TERM, "Alpha four %", 11, 14),
                Match(7, SearchFieldKind.NOTES, "%point accuracy", 0, 3),
                Match(7, SearchFieldKind.TERM, "Uniform % six", 8, 11),
                Match(11, SearchFieldKind.NOTES, "% this pin on me", 0, 3),
                Match(11, SearchFieldKind.NOTES, "% this % on me", 7, 10),
                Match(17, SearchFieldKind.TERM, "India % five pin", 6, 9),
                Match(17, SearchFieldKind.TERM, "India % five %", 13, 16),
                Match(24, SearchFieldKind.TERM, "% Zulu six", 0, 3),
                Match(25, SearchFieldKind.TERM, "Quebec % one", 7, 10),
                Match(25, SearchFieldKind.NOTES, "%s and needles", 0, 3),
                }
            actual = set()
            searcher.prepare(model, options)
            while True:
                match = searcher.search()
                if match is None:
                    break
                actual.add(match)
                self.editEntry(model, match)
            # self.debug(actual)
            self.assertSetEqual(actual, expected)
        finally:
            searcher.stop()
            if model is not None:
                model.close()


    def test_09(self): # terms and pages
        model = None
        searcher = Xix.Searcher.Searcher(reportProgress)
        try:
            model = Xix.Model.Model(self.username)
            self.prepare(model)
            options = Window.ReplacePanel.Options(
                pattern=None, literal="pin", replacement="*",
                ignorecase=True, wholewords=False, filter=None,
                match="", terms=True, pages=True, notes=False)
            Match = Xix.Searcher.Match
            expected = {
                Match(2, SearchFieldKind.PAGES, "7, 11, 15*", 9, 12),
                Match(3, SearchFieldKind.TERM, "Alpha four *", 11, 14),
                Match(7, SearchFieldKind.TERM, "Uniform * six", 8, 11),
                Match(17, SearchFieldKind.TERM, "India * five pin", 6, 9),
                Match(17, SearchFieldKind.TERM, "India * five *", 13, 16),
                Match(21, SearchFieldKind.PAGES, "<i>11<b>*</b></i>", 2, 5),
                Match(24, SearchFieldKind.TERM, "* Zulu six", 0, 3),
                Match(25, SearchFieldKind.TERM, "Quebec * one", 7, 10),
                }
            actual = set()
            searcher.prepare(model, options)
            while True:
                match = searcher.search()
                if match is None:
                    break
                actual.add(match)
                self.editEntry(model, match)
            # self.debug(actual)
            self.assertSetEqual(actual, expected)
        finally:
            searcher.stop()
            if model is not None:
                model.close()


    def test_10(self): # pages and notes
        model = None
        searcher = Xix.Searcher.Searcher(reportProgress)
        try:
            model = Xix.Model.Model(self.username)
            self.prepare(model)
            options = Window.ReplacePanel.Options(
                pattern=None, literal="pin", replacement="X-Ray",
                ignorecase=True, wholewords=False, filter=None,
                match="", terms=False, pages=True, notes=True)
            Match = Xix.Searcher.Match
            expected = {
                Match(2, SearchFieldKind.PAGES, "7, 11, 15X-Ray", 9, 12),
                Match(7, SearchFieldKind.NOTES, "X-Raypoint accuracy", 0,
                      3),
                Match(11, SearchFieldKind.NOTES, "X-Ray this pin on me", 0,
                      3),
                Match(11, SearchFieldKind.NOTES, "X-Ray this X-Ray on me",
                      11, 14),
                Match(21, SearchFieldKind.PAGES, "<i>11<b>X-Ray</b></i>",
                      2, 5),
                Match(25, SearchFieldKind.NOTES, "X-Rays and needles", 0,
                      3),
                }
            actual = set()
            searcher.prepare(model, options)
            while True:
                match = searcher.search()
                if match is None:
                    break
                actual.add(match)
                self.editEntry(model, match)
            # self.debug(actual)
            self.assertSetEqual(actual, expected)
        finally:
            searcher.stop()
            if model is not None:
                model.close()


    def test_11(self): # first subentry notes
        model = None
        searcher = Xix.Searcher.Searcher(reportProgress)
        try:
            model = Xix.Model.Model(self.username)
            self.prepare(model)
            options = Window.ReplacePanel.Options(
                pattern=None, literal="pin", replacement="Able",
                ignorecase=True, wholewords=False,
                filter=FilterKind.FIRST_SUBENTRIES, match="", terms=True,
                pages=True, notes=True)
            Match = Xix.Searcher.Match
            expected = {
                Match(11, SearchFieldKind.NOTES, "Able this pin on me", 0,
                      3),
                Match(11, SearchFieldKind.NOTES, "Able this Able on me",
                      10, 13),
                }
            actual = set()
            searcher.prepare(model, options)
            while True:
                match = searcher.search()
                if match is None:
                    break
                actual.add(match)
                self.editEntry(model, match)
            # self.debug(actual)
            self.assertSetEqual(actual, expected)
        finally:
            searcher.stop()
            if model is not None:
                model.close()


    def test_12(self): # second subentries
        model = None
        searcher = Xix.Searcher.Searcher(reportProgress)
        try:
            model = Xix.Model.Model(self.username)
            self.prepare(model)
            options = Window.ReplacePanel.Options(
                pattern=None, literal="pin", replacement="%",
                ignorecase=True, wholewords=False,
                filter=FilterKind.SECOND_SUBENTRIES, match="", terms=True,
                pages=True, notes=True)
            Match = Xix.Searcher.Match
            expected = {
                Match(17, SearchFieldKind.TERM, "India % five pin", 6, 9),
                Match(17, SearchFieldKind.TERM, "India % five %", 13, 16),
                Match(21, SearchFieldKind.PAGES, "<i>11<b>%</b></i>", 2, 5),
                Match(24, SearchFieldKind.TERM, "% Zulu six", 0, 3),
                Match(25, SearchFieldKind.TERM, "Quebec % one", 7, 10),
                Match(25, SearchFieldKind.NOTES, "%s and needles", 0, 3),
                }
            actual = set()
            searcher.prepare(model, options)
            while True:
                match = searcher.search()
                if match is None:
                    break
                actual.add(match)
                self.editEntry(model, match)
            # self.debug(actual)
            self.assertSetEqual(actual, expected)
        finally:
            searcher.stop()
            if model is not None:
                model.close()


    def test_13(self):
        model = None
        searcher = Xix.Searcher.Searcher(reportProgress)
        try:
            model = Xix.Model.Model(self.username)
            self.prepare(model)
            options = Window.ReplacePanel.Options(
                pattern=None, literal="pin", replacement="%",
                ignorecase=True, wholewords=False,
                filter=FilterKind.TERMS_MATCHING, match="f*", terms=True,
                pages=True, notes=True)
            Match = Xix.Searcher.Match
            expected = {
                Match(2, SearchFieldKind.PAGES, "7, 11, 15%", 9, 12),
                Match(3, SearchFieldKind.TERM, "Alpha four %", 11, 14),
                Match(17, SearchFieldKind.TERM, "India % five pin", 6, 9),
                Match(17, SearchFieldKind.TERM, "India % five %", 13, 16),
                }
            actual = set()
            searcher.prepare(model, options)
            while True:
                match = searcher.search()
                if match is None:
                    break
                actual.add(match)
                self.editEntry(model, match)
            # self.debug(actual)
            self.assertSetEqual(actual, expected)
        finally:
            searcher.stop()
            if model is not None:
                model.close()


    def test_14(self):
        model = None
        searcher = Xix.Searcher.Searcher(reportProgress)
        try:
            model = Xix.Model.Model(self.username)
            self.prepare(model)
            options = Window.ReplacePanel.Options(
                pattern=None, literal="pin", replacement="Star born",
                ignorecase=True, wholewords=False,
                filter=FilterKind.TERMS_MATCHING, match="six", terms=True,
                pages=True, notes=True)
            Match = Xix.Searcher.Match
            expected = {
                Match(7, SearchFieldKind.NOTES, "Star bornpoint accuracy",
                      0, 3),
                Match(7, SearchFieldKind.TERM, "Uniform Star born six",
                      8, 11),
                Match(24, SearchFieldKind.TERM, "Star born Zulu six", 0, 3),
                }
            actual = set()
            searcher.prepare(model, options)
            while True:
                match = searcher.search()
                if match is None:
                    break
                actual.add(match)
                self.editEntry(model, match)
            # self.debug(actual)
            self.assertSetEqual(actual, expected)
        finally:
            searcher.stop()
            if model is not None:
                model.close()


    def test_15(self):
        model = None
        searcher = Xix.Searcher.Searcher(reportProgress)
        try:
            model = Xix.Model.Model(self.username)
            self.prepare(model)
            options = Window.ReplacePanel.Options(
                pattern=r"\bsix\b", literal=None, replacement="6",
                ignorecase=True, wholewords=False, filter=None,
                match="", terms=True, pages=True, notes=True)
            Match = Xix.Searcher.Match
            expected = {
                Match(7, SearchFieldKind.TERM, "Uniform pin 6", 12, 15),
                Match(9, SearchFieldKind.TERM, "Tango 6", 6, 9),
                Match(12, SearchFieldKind.TERM, "Golf 6", 5, 8),
                Match(13, SearchFieldKind.TERM, "Victor 6", 7, 10),
                Match(23, SearchFieldKind.TERM, "Charlie 6", 8, 11),
                Match(24, SearchFieldKind.TERM, "pin Zulu 6", 9, 12),
                }
            actual = set()
            searcher.prepare(model, options)
            while True:
                match = searcher.search()
                if match is None:
                    break
                actual.add(match)
                self.editEntry(model, match)
            # self.debug(actual)
            self.assertSetEqual(actual, expected)
        finally:
            searcher.stop()
            if model is not None:
                model.close()


    def test_16(self):
        model = None
        searcher = Xix.Searcher.Searcher(reportProgress)
        try:
            model = Xix.Model.Model(self.username)
            self.prepare(model)
            options = Window.ReplacePanel.Options(
                pattern=r"\b(?:six|one)\b", literal=None,
                replacement="61", ignorecase=True, wholewords=False,
                filter=None, match="", terms=True, pages=True,
                notes=True)
            Match = Xix.Searcher.Match
            expected = {
                Match(7, SearchFieldKind.TERM, "Uniform pin 61", 12, 15),
                Match(9, SearchFieldKind.TERM, "Tango 61", 6, 9),
                Match(12, SearchFieldKind.TERM, "Golf 61", 5, 8),
                Match(13, SearchFieldKind.TERM, "Victor 61", 7, 10),
                Match(23, SearchFieldKind.TERM, "Charlie 61", 8, 11),
                Match(24, SearchFieldKind.TERM, "pin Zulu 61", 9, 12),
                Match(25, SearchFieldKind.TERM, "Quebec pin 61", 11, 14),
                }
            actual = set()
            searcher.prepare(model, options)
            while True:
                match = searcher.search()
                if match is None:
                    break
                actual.add(match)
                self.editEntry(model, match)
            # self.debug(actual)
            self.assertSetEqual(actual, expected)
        finally:
            searcher.stop()
            if model is not None:
                model.close()


    def test_17(self):
        model = None
        searcher = Xix.Searcher.Searcher(reportProgress)
        try:
            model = Xix.Model.Model(self.username)
            self.prepare(model)
            options = Window.ReplacePanel.Options(
                pattern=None, literal="web", replacement="WWW",
                ignorecase=True, wholewords=False, filter=None,
                match="", terms=True, pages=True, notes=True)
            Match = Xix.Searcher.Match
            expected = {
                Match(27, SearchFieldKind.TERM, "WWW 1", 0, 3),
                Match(28, SearchFieldKind.TERM, "WWW 2", 0, 3),
                Match(29, SearchFieldKind.TERM, "WWW 3 webbing", 0, 3),
                Match(29, SearchFieldKind.TERM, "WWW 3 WWWbing", 6, 9),
                Match(30, SearchFieldKind.TERM, "WWWbed 4", 0, 3),
                }
            actual = set()
            searcher.prepare(model, options)
            while True:
                match = searcher.search()
                if match is None:
                    break
                actual.add(match)
                self.editEntry(model, match)
            # self.debug(actual)
            self.assertSetEqual(actual, expected)
        finally:
            searcher.stop()
            if model is not None:
                model.close()


    def prepare(self, model):
        model.open(":memory:", *self.args)
        self.assertEqual(0, len(model))
        for term, pages, notes, peid, eid in self.data:
            model.addEntry(Saf.AUTO, SortAs.wordByWordNISO3(term),
                           term, pages=pages, notes=notes, peid=peid)
        self.assertEqual(len(self.data), len(model))


    def debug(self, matches):
        print()
        for match in sorted(matches, key=lambda m: m.eid):
            term, pages, notes = self.dataForEid[match.eid][:3]
            self.printEntry(match, term, pages, notes)


    def printEntry(self, match, term, pages, notes):
        if match.field is SearchFieldKind.TERM:
            text = term
        elif match.field is SearchFieldKind.PAGES:
            text = pages
        elif match.field is SearchFieldKind.NOTES:
            text = notes
        doc = QTextDocument()
        doc.setHtml(text)
        print("{: 3d}: [{}]".format(match.eid, doc.toPlainText()))


if __name__ == "__main__":
    app = QApplication([])
    unittest.main()
