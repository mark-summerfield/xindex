#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import unittest

from PySide.QtGui import QApplication

import Saf
import SortAs
import Xix
import Xix.Searcher
from Const import EntryDataKind, LanguageKind, RenumberOptions


def reportProgress(percent):
    pass # print("{}%".format(percent))


class TestXixRenumber(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None
        self.args = (LanguageKind.AMERICAN, "wordByWordNISO3",
                     "pageRangeCMS16")
        self.username = "Tester"


    def test_01(self):
        model = None
        try:
            model = Xix.Model.Model(self.username)
            pagesForEid = self.prepare(model, DATA_ADD)
            self.check(pagesForEid, model, 0)
            options = RenumberOptions(1, 3999, 5, 1, 99999, 5)
            model.renumber(options, reportProgress)
            self.check(pagesForEid, model, 1)
            model.undo() # Undo macro, i.e., all renumbering
            self.check(pagesForEid, model, 0)
            model.redo() # Redo macro, i.e., all renumbering
            self.check(pagesForEid, model, 1)
            model.undo() # Undo macro, i.e., all renumbering
            self.check(pagesForEid, model, 0)
            model.redo() # Redo macro, i.e., all renumbering
            self.check(pagesForEid, model, 1)
        finally:
            if model is not None:
                model.close()


    def test_02(self):
        model = None
        try:
            model = Xix.Model.Model(self.username)
            pagesForEid = self.prepare(model, DATA_SUB)
            self.check(pagesForEid, model, 0)
            options = RenumberOptions(1, 3999, -3, 1, 99999, -3)
            model.renumber(options, reportProgress)
            self.check(pagesForEid, model, 1)
            model.undo() # Undo macro, i.e., all renumbering
            self.check(pagesForEid, model, 0)
            model.redo() # Redo macro, i.e., all renumbering
            self.check(pagesForEid, model, 1)
            model.undo() # Undo macro, i.e., all renumbering
            self.check(pagesForEid, model, 0)
            model.redo() # Redo macro, i.e., all renumbering
            self.check(pagesForEid, model, 1)
        finally:
            if model is not None:
                model.close()


    def check(self, pagesForEid, model, which):
        for i, entry in enumerate(model.entries(
                entryData=EntryDataKind.ALL_DATA)):
            with self.subTest(i=i):
                if pagesForEid[entry.eid][which] != entry.pages:
                    print()
                    print(entry.term)
                    print("A", entry.pages)
                    print("X", pagesForEid[entry.eid][which])
                self.assertEqual(pagesForEid[entry.eid][which], entry.pages)


    def prepare(self, model, data):
        model.open(":memory:", *self.args)
        self.assertEqual(0, len(model))
        pagesForEid = {}
        for pages, expected, term in data:
            entry = model.addEntry(Saf.AUTO, SortAs.wordByWordNISO3(term),
                                   term, pages=pages)
            pagesForEid[entry.eid] = (pages, expected)
        self.assertEqual(len(data), len(model))
        return pagesForEid


DATA_ADD = (
    ("360–365, 461<i>fig</i>, 462tbl, 564–566",
     "365–70, 466<i>fig</i>, 467tbl, 569–71", "alpha"),
    ("xv, xix–xxii, 360–365, 461<i>fig</i>, 462tbl, 564–566",
     "xx, xxiv–xxvii, 365–70, 466<i>fig</i>, 467tbl, 569–71", "bravo"),
    ("2, 11–17, 19, 31", "7, 16–22, 24, 36", "foxtrot"),
    ("402, 411–17, 419, 431", "407, 416–22, 424, 436", "juliet"),
    ("""402, <span style="font-size: \
11pt; font-family: 'courier';">411–17</span>, <span \
style="font-size: 11pt; font-family: 'courier';">419</span>, 431""",
     """407, \
<span style="font-size: 11pt; font-family: 'courier';">416</span>–\
<span style="font-size: 11pt; font-family: 'courier';">22</span>, <span \
style="font-size: 11pt; font-family: 'courier';">424</span>, 436""",
     "lima"),
    ("", "", "mike"),
    ("1–6, 10tbl, 15–19, 26fig, 27–28", "6–11, 15tbl, 20–24, 31fig, 32–33",
     "quebec"),
    ("""vi, xii, xiv, 4, 12, 18(nn 12, 15), 32, 49, 89, 492""",
     """xi, xvii, xix, 9, 17, 23(nn 12, 15), 37, 54, 94, 497""", "romeo"),
    ("""<i>iv</i>, ix, 4, <b>11t</b>, <i>13f</i>, \
<b>34</b>, 39, 42, <i>88</i>, <b>719</b>""",
     """<i>ix</i>, xiv, 9, <b>16t</b>, <i>18f</i>, \
<b>39</b>, 44, 47, <i>93</i>, <b>724</b>""", "sierra"),
    ("""<b>35</b>(nn. 11, 19), 49, 75<sub>2</sub>, \
<i>81</i><sup><i>a</i></sup>, 85""",
     """<b>40</b>(nn. 11, 19), 54, 80<sub>2</sub>, \
<i>86</i><sup><i>a</i></sup>, 90""", "tango"),
    ("101–108, <b>808</b>–833, <i>1103</i>–1104, 1206(nn. <b>83</b>, 91)",
     "106–13, <b>813</b>–38, <i>1108</i>–9, 1211(nn. <b>83</b>, 91)",
     "uniform"),
    ("""xv, 24, <b>32t</b>, 116\u2013118, \
<i><span style="font-size: 11pt; font-family: 'times new roman';">240\
</span></i><i>\u2013</i>\
<i><span style="font-size: 11pt; font-family: 'times new roman';">248\
</span></i>, <i>281f</i>""",
     """xx, 29, <b>37t</b>, 121\u201323, \
<i><span style="font-size: 11pt; font-family: 'times new roman';">245\
</span></i><i>\u2013</i>\
<i><span style="font-size: 11pt; font-family: 'times new roman';">53\
</span></i>, <i>286f</i>""", "victor"),
    ("102–109, <b>908</b>–933, 2103–<i>2104</i>",
     "107–14, <b>913</b>–38, 2108–<i>9</i>", "whiskey"),
    ("321–328, 498–532, 1087–1089, 1496–1500, 11564–11615, 12991–13001",
     "326–33, 503–37, 1092–94, 1501–5, 11569–620, 12996–3006", "x-ray"),
    ("""vi, xii, <b>xiv</b>\u2013xvii, 4, 12, 32, 49, 89, 492""",
     """xi, xvii, <b>xix</b>\u2013xxii, 9, 17, 37, 54, 94, 497""",
     "alpha alpha"),
    )

DATA_SUB = (
    ("""vi, xii, <b>xiv</b>\u2013xvii, 4, 12, 32, 49, 89, 492""",
     """iii, ix, <b>xi</b>\u2013xiv, 1, 9, 29, 46, 86, 489""",
     "alpha bravo"),
    ("""<i>iv</i>, ix, 4, <b>11t</b>, <i>13f</i>, \
<b>34</b>, 39, 42, <i>88</i>, <b>719</b>""",
     """<i>i</i>, vi, 1, <b>8t</b>, <i>10f</i>, \
<b>31</b>, 36, 39, <i>85</i>, <b>716</b>""", "alpha charlie"),
    ("""<b>35</b>, 49, 75<sub>2</sub>, <i>81</i><sup><i>a</i></sup>, 85""",
     """<b>32</b>, 46, 72<sub>2</sub>, <i>78</i><sup><i>a</i></sup>, 82""",
     "alpha delta"),
    ("""xv, 24, <b>32t</b>, 116\u2013118, \
<i><span style="font-size: 11pt; font-family: 'times new roman';">240\
</span></i><i>\u2013</i>\
<i><span style="font-size: 11pt; font-family: 'times new roman';">248\
</span></i>, <i>281f</i>""",
     """xii, 21, <b>29t</b>, 113\u201315, \
<i><span style="font-size: 11pt; font-family: 'times new roman';">237\
</span></i><i>\u2013</i>\
<i><span style="font-size: 11pt; font-family: 'times new roman';">45\
</span></i>, <i>278f</i>""", "alpha echo"),
    ("""63, <span style="font-size: 11pt; font-family: \
'arial';">100</span>, <i><span style="font-size: 11pt; font-family: \
'arial';">105</span></i>, 110, 154, <i>177</i><i>\u2013</i><i>182</i>, \
<i>203</i>, <i><b>239</b></i>, 290\u2013293, \
<i>343</i><i>\u2013</i><i>350</i>, <b>482</b>""",
     """60, <span style="font-size: 11pt; font-family: \
'arial';">97</span>, <i><span style="font-size: 11pt; font-family: \
'arial';">102</span></i>, 107, 151, <i>174</i><i>\u2013</i><i>79</i>, \
<i>200</i>, <i><b>236</b></i>, 287\u201390, \
<i>340</i><i>\u2013</i><i>47</i>, <b>479</b>""", "alpha foxtrot"),
    ("""47\u2013<i>52</i>, 51<b>t</b>, \
<b>82</b><b>\u2013</b><i><b>84</b></i>, <i>91</i><i><b>f</b></i>, 98, \
420""",
     """44\u2013<i>49</i>, 48<b>t</b>, \
<b>79</b><b>\u2013</b><i><b>81</b></i>, <i>88</i><i><b>f</b></i>, 95, \
417""", "alpha golf"),
    ("""<i>2</i>, 47\u2013<i>52</i>, 51<b>t</b>, \
<b>62</b><b>\u2013</b><i><b>64</b></i>, <i>91</i><i><b>f</b></i>, 98, \
<b>117</b>, 420""",
     """<i>1</i>, 44\u2013<i>49</i>, 48<b>t</b>, \
<b>59</b><b>\u2013</b><i><b>61</b></i>, <i>88</i><i><b>f</b></i>, 95, \
<b>114</b>, 417""", "alpha hotel"),
    ("""iv, xviii, 7, 12, <b>75c</b>, 78, 81<i>f</i>, 92\u201396, \
203<b>t</b>, 206, 255, 290, 300t, 381, 482, 491""",
     """i, xv, 4, 9, <b>72c</b>, 75, 78<i>f</i>, 89\u201393, \
200<b>t</b>, 203, 252, 287, 297t, 378, 479, 488""", "alpha india"),
    ("Frontispiece@0.1, 21\u201325 <i>passim</i>, 31, 56\u201374, 83, 91",
     "Frontispiece@0.1, 18\u201322 <i>passim</i>, 28, 53\u201371, 80, 88",
     "alpha juliet"),
    ("1.2, 1.3 <i>illus.</i>, 1.8, 1.13, 1.49, 1.98, 2",
     "1, 1.2, 1.3 <i>illus.</i>, 1.8, 1.13, 1.49, 1.98", "alpha kilo"),
    ("""3\u201310, <i>71</i>\u201372, 82\u201385, 87\u2013<i>88</i>, \
96\u2013<b>117</b>, 97\u201399""",
     """1\u20137, <i>68</i>\u201369, 79\u201382, 84\u2013<i>85</i>, \
93\u2013<b>114</b>, 94\u201396""", "alpha mike"),
    ("1200\u20131213, 1300\u20131324, 1400\u20131481, 1500\u20131509",
     "1197\u2013210, 1297\u2013321, 1397\u2013478, 1497\u2013506",
     "alpha november"),
    )


if __name__ == "__main__":
    app = QApplication([])
    unittest.main()
