#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

import os
import random
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import unittest

import Saf
import SortAs


DEBUG = 0


class TestSortAs(unittest.TestCase):

    def setUp(self):
        pass # self.maxDiff = None


    # Word by Word (ISO 999)
    def test_wordByWordISO999en(self):
        items = EXPECTED_BY_WORD[:]
        random.shuffle(items)
        results = []
        for term, saf, sortas in items:
            if saf != Saf.CUSTOM:
                sortas = SortAs.wordByWordISO999en(term, saf, pad_digits=4)
            results.append((sortas, term, saf))
        results.sort()
        for i in range(len(EXPECTED_BY_WORD)):
            sortas, aterm, asaf = results[i]
            xterm, xsaf = EXPECTED_BY_WORD[i][:2]
            if DEBUG == 1:
                print("{:35} → {:35} : {}".format(aterm, sortas, xterm))
            self.assertEqual(aterm, xterm)
            self.assertEqual(asaf, xsaf)


    # Letter by Letter (ISO 999)
    def test_letterByLetterISO999en(self):
        items = EXPECTED_BY_LETTER[:]
        random.shuffle(items)
        results = []
        for term, saf, sortas in items:
            if saf != Saf.CUSTOM:
                sortas = SortAs.letterByLetterISO999en(term, saf,
                                                       pad_digits=4)
            results.append((sortas, term, saf))
        results.sort()
        for i in range(len(EXPECTED_BY_LETTER)):
            sortas, aterm, asaf = results[i]
            xterm, xsaf = EXPECTED_BY_LETTER[i][:2]
            if DEBUG == 2:
                print("{:35} → {:35} : {}".format(aterm, sortas, xterm))
            self.assertEqual(aterm, xterm)
            self.assertEqual(asaf, xsaf)


EXPECTED_BY_WORD = [
    ("<i>1:30 a.m.</i>", Saf.CUSTOM, "0001.0030 am"),
    ("<i>XX century cyclopedia and atlas</i>", Saf.AUTO_NUMBER_ROMAN, None),
    ("<i>1001 nights</i>", Saf.AUTO_NUMBER_ROMAN, None),
    ("<i>1066 and all that</i>", Saf.AUTO_NUMBER_ROMAN, None),
    ("<i>1984", Saf.AUTO_NUMBER_ROMAN, None),
    ("<i>Bag of bricks</i>", Saf.AUTO, None),
    ("Bagby, George", Saf.AUTO, None),
    ("Bagshaw, Malcolm A", Saf.AUTO, None),
    ("Bank of England", Saf.AUTO, None),
    ("Banking", Saf.AUTO, None),
    ("5-ethoxy-2-ethylyne", Saf.CUSTOM, "ethoxy-2-ethylyne"),
    ("3-ethyl-4-picoline", Saf.CUSTOM, "ethyl-3-4-picoline"),
    ("4-ethyl-α-picoline", Saf.CUSTOM, "ethyl-3-α-picoline"),
    ("milk", Saf.AUTO, None),
    ("<i>Milk</i> (report)", Saf.AUTO, None),
    ("milk allergies", Saf.AUTO, None),
    ("Milk Marketing Board", Saf.AUTO, None),
    ("<i>1984</i> (nineteen eighty-four)", Saf.CUSTOM,
        "nineteen eighty-four"),
    ("<i>1:30 a.m.</i>", Saf.CUSTOM, "one thirty am"),
    ("<i>1001 nights</i> (one thousand and one)", Saf.AUTO, None),
    ("<i>1066 and all that</i> (ten sixty-six)", Saf.CUSTOM,
        "ten sixty-six"),
    ("<i>XX century cyclopedia and atlas</i> (twenty)", Saf.AUTO, None),
    ]

EXPECTED_BY_LETTER = [
    ("<i>1:30 a.m.</i>", Saf.CUSTOM, "0001.0030 am"),
    ("<i>XX century cyclopedia and atlas</i>", Saf.AUTO_NUMBER_ROMAN, None),
    ("<i>1001 nights</i>", Saf.AUTO_NUMBER_ROMAN, None),
    ("<i>1066 and all that</i>", Saf.AUTO_NUMBER_ROMAN, None),
    ("<i>1984", Saf.AUTO_NUMBER_ROMAN, None),
    ("Bagby, George", Saf.AUTO, None),
    ("<i>Bag of bricks</i>", Saf.AUTO, None),
    ("Bagshaw, Malcolm A", Saf.AUTO, None),
    ("Banking", Saf.AUTO, None),
    ("Bank of England", Saf.AUTO, None),
    ("5-ethoxy-2-ethylyne", Saf.CUSTOM, "ethoxy-2-ethylyne"),
    ("3-ethyl-4-picoline", Saf.CUSTOM, "ethyl-3-4-picoline"),
    ("4-ethyl-α-picoline", Saf.CUSTOM, "ethyl-3-α-picoline"),
    ("milk", Saf.AUTO, None),
    ("<i>Milk</i> (report)", Saf.AUTO, None),
    ("milk allergies", Saf.AUTO, None),
    ("Milk Marketing Board", Saf.AUTO, None),
    ("<i>1984</i> (nineteen eighty-four)", Saf.CUSTOM,
        "nineteen eighty-four"),
    ("<i>1:30 a.m.</i>", Saf.CUSTOM, "one thirty am"),
    ("<i>1001 nights</i> (one thousand and one)", Saf.AUTO, None),
    ("<i>1066 and all that</i> (ten sixty-six", Saf.CUSTOM,
        "ten sixty-six"),
    ("<i>XX century cyclopedia and atlas</i> (twenty)", Saf.AUTO, None),
    ]

if __name__ == "__main__":
    unittest.main()
