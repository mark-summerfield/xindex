#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

import collections
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import unittest

import SortAs


DEBUG = 0


class TestSortAs(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None


    # Letter by Letter (Chicago 16th edn.)
    def test_letterByLetterCMS16(self):
        for key in SORTASSEQS:
            pairs = []
            byletter = SORTASSEQS[key].byletter
            for term in byletter:
                pairs.append((SortAs.letterByLetterCMS16(
                              term, pad_digits=4), term))
            pairs.sort(key=lambda pair: pair[0])
            terms = [pair[1] for pair in pairs]
            if DEBUG or byletter != terms:
                print()
                print(key, SortAs.letterByLetterCMS16.__name__)
                for i, pair in enumerate(pairs):
                    print("{:40} {}".format(byletter[i], pair))
            self.assertListEqual(byletter, terms)


    # Word by Word (Chicago 16th edn.)
    def test_wordByWordCMS16(self):
        for key in SORTASSEQS:
            pairs = []
            byword = SORTASSEQS[key].byword
            for term in byword:
                pairs.append((SortAs.wordByWordCMS16(term, pad_digits=4),
                              term))
            pairs.sort(key=lambda pair: pair[0])
            terms = [pair[1] for pair in pairs]
            if DEBUG or byword != terms:
                print()
                print(key, SortAs.wordByWordCMS16.__name__)
                for i, pair in enumerate(pairs):
                    print("{:40} {}".format(byword[i], pair))
            self.assertListEqual(byword, terms)


    def test_ApostropheS(self):
        original = "Mr O'Brien's car it's green"
        expected = "mr L obriens car its green"
        actual = SortAs.wordByWordCMS16(original)
        self.assertEqual(actual, expected)


    def test_ApostropheAsPunctuation(self):
        original = "‘this’ and “that”, that's it, that\u2019s really it!"
        expected = "this L and that thats it thats really it"
        actual = SortAs.wordByWordCMS16(original)
        self.assertEqual(actual, expected)


SortData = collections.namedtuple("SortData", "byletter byword")
SORTASSEQS = {
    "Chicago 16th (16.61)": SortData("""
NEW (Neighbors Ever Watchful)
NEW (Now End War)
New, Arthur
New, Zoë
new-12 compound
newborn
newcomer
New Deal
new economics
newel
New England
“new-fangled notions”
Newfoundland
newlyweds
new math
new/old continuum
news, lamentable
News, Networks, and the Arts
newsboy
news conference
newsletter
News of the World (Queen)
news release
newt
NEWT (Northern Estuary Wind Tunnel)
New Thorndale
new town
New Year's Day
""".strip().split("\n"), """
NEW (Neighbors Ever Watchful)
NEW (Now End War)
New, Arthur
New, Zoë
New Deal
new economics
New England
new math
New Thorndale
new town
New Year's Day
new-12 compound
newborn
newcomer
newel
“new-fangled notions”
Newfoundland
newlyweds
new/old continuum
news, lamentable
News, Networks, and the Arts
news conference
News of the World (Queen)
news release
newsboy
newsletter
newt
NEWT (Northern Estuary Wind Tunnel)
""".strip().split("\n")),
    "Chicago 16th (16.66)": SortData("""
5 Stars
Henry III
Henry IV
Henry V
Henry IX
1983, Annual festival
section 9
section 44
section 77
10 Downing St.
""".strip().split("\n"), """
5 Stars
Henry III
Henry IV
Henry V
Henry IX
1983, Annual festival
section 9
section 44
section 77
10 Downing St.
""".strip().split("\n")),
    # Chicago etc.
    # Mulvaney etc.
    # Z39.43 etc.
    }


if __name__ == "__main__":
    unittest.main()
