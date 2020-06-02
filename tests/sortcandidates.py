#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import unittest

import Saf
import SortAs



class TestCandidatesForByWordCMS16(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None
        self.data = (
            ("C language", {
                ("one hundred L language", Saf.AUTO),
                ("c L language", Saf.AUTO_NUMBER_SPELL),
                ("0100 L language", Saf.AUTO_NUMBER_ROMAN),
                }
             ),
            ("X Best", {
                ("ten L best", Saf.AUTO),
                ("x L best", Saf.AUTO_NUMBER_SPELL),
                ("0010 L best", Saf.AUTO_NUMBER_ROMAN),
                }
             ),
            ("100000 limit", {
                ("one hundred thousand L limit", Saf.AUTO),
                ("100000 L limit", Saf.AUTO_NUMBER_ROMAN),
                }
             ),
            ("Henry VIII", {
                ("henry P 0008", Saf.AUTO),
                ("henry L viii", Saf.AUTO_NUMBER_SPELL),
                }
             ),
            )


    def test_01(self):
        for term, expected in self.data:
            expected = {SortAs.Candidate(*item) for item in expected}
            candidates = SortAs.candidatesFor(term, "wordByWordCMS16", None)
            self.assertSetEqual(expected, set(candidates))



if __name__ == "__main__":
    unittest.main()
