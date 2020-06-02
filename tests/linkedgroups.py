#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import unittest

import Lib
import Saf
import SortAs
import Xix
from Const import LanguageKind


class TestXixLinkedGroups(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None
        self.args = (LanguageKind.AMERICAN, "wordByWordCMS16",
                     "pageRangeCMS16")
        self.username = "Tester"
        self.data = { # key = eid, value = [term, pages]
            1: ["Alpha", "3, 5, 7"],
            2: ["Bravo", "4, 6, 8"],
            3: ["Charlie", "1, 2, 3, 4"],
            4: ["Delta", "7, 8, 9, 10"],
            5: ["Echo", "5, 8, 10, 11"],
            }


    def test_01(self):
        model = None
        try:
            model = Xix.Model.Model(self.username)
            model.open(":memory:", *self.args)
            self.assertEqual(0, len(model))
            for eid, (term, pages) in self.data.items():
                model.addEntry(Saf.AUTO, SortAs.wordByWordCMS16(term),
                               term, pages=pages)
            self.assertEqual(len(self.data), len(model))
            self.check(model)

            for eid in self.data:
                self.assertListEqual([], list(model.groupsForEid(eid)))
            self.assertListEqual([], list(model.allGroups()))

            groups = [(1, "Group #1", False), (2, "Group #2", False)]
            for _, name, _ in groups:
                model.addGroup(name)
            self.assertListEqual(groups, list(model.allGroups()))

            # make group 1 linked (with no members)
            self.assertTrue(model.safeToLinkGroup(1))
            model.linkGroup(1)
            self.assertFalse(model.safeToLinkGroup(1))
            # add members to group 1 & check their pages are synced
            model.addToGroup(1, 1)
            self.assertEqual(model.entry(1).pages, self.data[1][1])
            model.addToGroup(3, 1)
            self.assertEqual(model.entry(1).pages, "1, 2, 3, 4, 5, 7")
            self.assertEqual(model.entry(3).pages, "1, 2, 3, 4, 5, 7")
            model.addToGroup(5, 1)
            for eid in (1, 3, 5):
                self.assertEqual(model.entry(eid).pages,
                                 "1, 2, 3, 4, 5, 7, 8, 10, 11")
            model.undo() # addToNormalGroup 5
            self.assertEqual(model.entry(1).pages, "1, 2, 3, 4, 5, 7")
            self.assertEqual(model.entry(3).pages, "1, 2, 3, 4, 5, 7")
            self.assertEqual(model.entry(5).pages, "5, 8, 10, 11")
            model.undo() # addToNormalGroup 3
            self.assertEqual(model.entry(1).pages, "3, 5, 7")
            self.assertEqual(model.entry(3).pages, "1, 2, 3, 4")
            model.undo() # addToNormalGroup 1
            self.assertEqual(model.entry(1).pages, "3, 5, 7")
            model.undo() # link group 1

            model.redo() # link group 1
            model.redo() # addToNormalGroup 1
            model.redo() # addToNormalGroup 3
            model.redo() # addToNormalGroup 5
            for eid in (1, 3, 5):
                self.assertEqual(model.entry(eid).pages,
                                 "1, 2, 3, 4, 5, 7, 8, 10, 11")
            model.undo() # addToNormalGroup 1
            model.undo() # addToNormalGroup 3
            model.undo() # addToNormalGroup 5
            self.check(model)

            model.addToGroup(3, 1)
            self.assertFalse(model.safeToLinkGroup(1))
            self.assertTrue(model.safeToAddToGroup(3, 2))
            self.assertTrue(model.safeToLinkGroup(2))
            self.assertFalse(model.isLinkedGroup(2))
            model.linkGroup(2)
            self.assertTrue(model.isLinkedGroup(2))
            self.assertFalse(model.safeToAddToGroup(3, 2))
            model.removeFromGroup(3, 1)

            for eid in (2, 3, 4):
                self.assertTrue(model.safeToAddToGroup(eid, 2))
            model.unlinkGroup(2)
            self.assertFalse(model.isLinkedGroup(2))
            for eid in (2, 3, 4):
                self.assertTrue(model.safeToAddToGroup(eid, 2))
            model.undo() # undo unlink
            self.assertTrue(model.isLinkedGroup(2))
            model.redo() # redo unlink
            self.assertFalse(model.isLinkedGroup(2))

            # add members to (unlinked) group 2
            model.addToGroup(2, 2)
            self.check(model)
            model.addToGroup(3, 2)
            self.check(model)
            model.addToGroup(4, 2)
            self.check(model)
            for eid in (2, 3, 4):
                self.assertEqual(model.entry(eid).pages,
                                 self.data[eid][1])
            # make group 2 linked & check their pages are synced
            model.linkGroup(2)
            for eid in (2, 3, 4):
                self.assertEqual(model.entry(eid).pages,
                                 "1, 2, 3, 4, 6, 7, 8, 9, 10")
            model.undo() # undo link
            for eid in (2, 3, 4):
                self.assertEqual(model.entry(eid).pages,
                                 self.data[eid][1])
            model.redo() # redo link
            for eid in (2, 3, 4):
                self.assertEqual(model.entry(eid).pages,
                                 "1, 2, 3, 4, 6, 7, 8, 9, 10")
            model.unlinkGroup(2)
            for eid in (2, 3, 4):
                self.assertEqual(model.entry(eid).pages,
                                 "1, 2, 3, 4, 6, 7, 8, 9, 10")
            model.undo() # undo unlink
            for eid in (2, 3, 4):
                self.assertEqual(model.entry(eid).pages,
                                 "1, 2, 3, 4, 6, 7, 8, 9, 10")
            model.undo() # redo link
            model.undo() # undo link
            model.undo() # do link
            for eid in (2, 3, 4):
                self.assertEqual(model.entry(eid).pages,
                                 self.data[eid][1])

            model.linkGroup(2)
            for eid in (2, 3, 4):
                model.addToGroup(eid, 2)
            for eid in (2, 3, 4):
                self.assertEqual(model.entry(eid).pages,
                                 "1, 2, 3, 4, 6, 7, 8, 9, 10")

            self.assertEqual(model.entry(5).pages, "5, 8, 10, 11")

            entry = model.entry(5)
            model.editEntry(entry, entry.saf, entry.sortas, entry.term,
                            pages="5, 55")
            self.assertEqual(model.entry(5).pages, "5, 55")

            entry = model.entry(3)
            model.editEntry(entry, entry.saf, entry.sortas, entry.term,
                            pages="9, 99, 999")
            for eid in (2, 3, 4):
                self.assertEqual(model.entry(eid).pages, "9, 99, 999")

            model.unlinkGroup(2)
            for eid in (2, 3, 4):
                self.assertEqual(model.entry(eid).pages, "9, 99, 999")
            entry = model.entry(2)
            model.editEntry(entry, entry.saf, entry.sortas, entry.term,
                            pages="1, 11, 111")
            self.assertEqual(model.entry(2).pages, "1, 11, 111")
            for eid in (3, 4):
                self.assertEqual(model.entry(eid).pages, "9, 99, 999")

            model.undo()
            model.undo()
            model.undo()
            model.undo()
            for eid in (2, 3, 4):
                self.assertEqual(model.entry(eid).pages,
                                 "1, 2, 3, 4, 6, 7, 8, 9, 10")
            self.assertTrue(model.isLinkedGroup(2))

            model.redo()
            model.redo()
            model.redo()
            model.redo()
            self.assertFalse(model.isLinkedGroup(2))
            self.assertEqual(model.entry(2).pages, "1, 11, 111")
            for eid in (3, 4):
                self.assertEqual(model.entry(eid).pages, "9, 99, 999")

            self.assertTrue(model.isLinkedGroup(1))
            model.unlinkGroup(1)
            self.assertFalse(model.isLinkedGroup(1))

        finally:
            if model is not None:
                model.close()


    def test_02(self):
        model = None
        try:
            model = Xix.Model.Model(self.username)
            model.open(":memory:", *self.args)
            self.assertEqual(0, len(model))
            for eid, (term, pages) in self.data.items():
                model.addEntry(Saf.AUTO, SortAs.wordByWordCMS16(term),
                               term, pages=pages)
            self.assertEqual(len(self.data), len(model))
            self.check(model)

            for eid in self.data:
                self.assertListEqual([], list(model.groupsForEid(eid)))
            self.assertListEqual([], list(model.allGroups()))

            groups = [(1, "Group #1", False), (2, "Group #2", False)]
            for _, name, _ in groups:
                model.addGroup(name)
            self.assertListEqual(groups, list(model.allGroups()))

            self.check(model)
            model.linkGroup(2)
            self.check(model)
            model.addToGroup(5, 2)
            self.assertEqual(model.entry(5).pages, "5, 8, 10, 11")
            model.addToGroup(4, 2)
            self.assertEqual(model.entry(5).pages, "5, 7, 8, 9, 10, 11")
            self.assertEqual(model.entry(4).pages, "5, 7, 8, 9, 10, 11")
            model.deleteEntry(4)
            self.assertEqual(model.entry(5).pages, "5, 7, 8, 9, 10, 11")
            model.undo() # delete entry 4
            self.assertEqual(model.entry(5).pages, "5, 7, 8, 9, 10, 11")
            self.assertEqual(model.entry(4).pages, "5, 7, 8, 9, 10, 11")
            entry = model.entry(4)
            model.editEntry(entry, entry.saf, entry.sortas, entry.term,
                            pages="6, 16, 61")
            self.assertEqual(model.entry(5).pages, "6, 16, 61")
            self.assertEqual(model.entry(4).pages, "6, 16, 61")

        finally:
            if model is not None:
                model.close()


    def test_03(self):
        model = None
        try:
            model = Xix.Model.Model(self.username)
            model.open(":memory:", *self.args)
            self.assertEqual(0, len(model))
            for eid, (term, pages) in self.data.items():
                model.addEntry(Saf.AUTO, SortAs.wordByWordCMS16(term),
                               term, pages=pages)
            self.assertEqual(len(self.data), len(model))
            self.check(model)

            for eid in self.data:
                self.assertListEqual([], list(model.groupsForEid(eid)))
            self.assertListEqual([], list(model.allGroups()))

            groups = [(1, "Linked Group", False),
                      (2, "Normal Group", False)]
            for _, name, _ in groups:
                model.addGroup(name)
            self.assertListEqual(groups, list(model.allGroups()))

            self.check(model)
            model.linkGroup(1)
            self.check(model)
            model.addToGroup(5, 1)
            self.assertEqual(model.entry(5).pages, "5, 8, 10, 11")
            model.addToGroup(4, 1)
            self.assertEqual(model.entry(5).pages, "5, 7, 8, 9, 10, 11")
            self.assertEqual(model.entry(4).pages, "5, 7, 8, 9, 10, 11")
            model.deleteEntry(4)
            self.assertEqual(model.entry(5).pages, "5, 7, 8, 9, 10, 11")
            model.undo() # delete entry 4
            self.assertEqual(model.entry(5).pages, "5, 7, 8, 9, 10, 11")
            self.assertEqual(model.entry(4).pages, "5, 7, 8, 9, 10, 11")
            entry = model.entry(4)
            model.editEntry(entry, entry.saf, entry.sortas, entry.term,
                            pages="6, 16, 61")
            self.assertEqual(model.entry(5).pages, "6, 16, 61")
            self.assertEqual(model.entry(4).pages, "6, 16, 61")

            self.assertTrue(model.isLinkedGroup(1))
            self.assertFalse(model.isLinkedGroup(2))
            groups = [(1, "Linked Group", True),
                      (2, "Normal Group", False)]
            self.assertListEqual(groups, list(model.allGroups()))
            model.addToGroup(1, 2)
            model.addToGroup(5, 2)

            term = "Foxtrot" # eid==6
            model.addEntry(Saf.AUTO, SortAs.wordByWordCMS16(term), term,
                           pages="2, 3, 5", peid=1)
            term = "Golf" # eid==7
            model.addEntry(Saf.AUTO, SortAs.wordByWordCMS16(term), term,
                           pages="7, 11, 13", peid=5)
            term = "Hotel" # eid==8
            model.addEntry(Saf.AUTO, SortAs.wordByWordCMS16(term), term,
                           pages="17, 19", peid=7)
            term = "India" # eid==9
            model.addEntry(Saf.AUTO, SortAs.wordByWordCMS16(term), term,
                           pages="17, 19, 23", peid=8)
            term = "Juliet" # eid==10
            model.addEntry(Saf.AUTO, SortAs.wordByWordCMS16(term), term,
                           pages="1, 2, 3, 4", peid=8)
            term = "Kilo" # eid==11
            model.addEntry(Saf.AUTO, SortAs.wordByWordCMS16(term), term,
                           pages="5, 6, 7", peid=7)
            term = "Lima" # eid==12
            model.addEntry(Saf.AUTO, SortAs.wordByWordCMS16(term), term,
                           pages="8, 9", peid=5)
            model.addToGroup(8, 1)
            model.addToGroup(8, 2)
            model.addToGroup(10, 2)
            self.assertEqual(model.entry(4).pages, model.entry(8).pages)
            self.assertEqual(model.entry(5).pages, model.entry(8).pages)

            peid = model.entry(1).peid
            eid = model.copyEntry(Lib.CopyInfo(1, peid)) # eid==13
            self.assertEqual(eid, 13)
            self.assertEqual(model.entry(1).term, model.entry(eid).term)
            self.assertEqual(model.entry(1).pages, model.entry(eid).pages)
            self.assertListEqual([], list(model.groupsForEid(eid)))

            model.undo()

            peid = model.entry(1).peid
            eid = model.copyEntry(Lib.CopyInfo(1, peid,
                                               copygroups=True)) # eid==14
            self.assertEqual(eid, 14)
            self.assertEqual(model.entry(1).term, model.entry(eid).term)
            self.assertEqual(model.entry(1).pages, model.entry(eid).pages)
            self.assertListEqual([(2, "Normal Group")],
                                 list(model.groupsForEid(eid)))

            peid = model.entry(8).peid
            eid = model.copyEntry(Lib.CopyInfo(8, peid)) # eid==15
            self.assertEqual(eid, 15)
            self.assertEqual(model.entry(8).term, model.entry(eid).term)
            self.assertEqual(model.entry(8).pages, model.entry(eid).pages)
            self.assertListEqual([], list(model.groupsForEid(eid)))

            model.undo()

            peid = model.entry(8).peid
            eid = model.copyEntry(Lib.CopyInfo(8, peid,
                                               copygroups=True)) # eid==16
            self.assertEqual(eid, 16)
            self.assertEqual(model.entry(8).term, model.entry(eid).term)
            self.assertEqual(model.entry(8).pages, model.entry(eid).pages)
            self.assertListEqual([(1, "Linked Group"), (2, "Normal Group")],
                                 list(model.groupsForEid(eid)))

            model.undo()
            model.undo()

            peid = model.entry(5).peid
            eid = model.copyEntry(Lib.CopyInfo(5, peid)) # eid==17
            self.assertEqual(eid, 17)
            self.assertEqual(model.entry(5).term, model.entry(eid).term)
            self.assertEqual(model.entry(5).pages, model.entry(eid).pages)
            self.assertListEqual([], list(model.groupsForEid(eid)))

            model.undo()

            peid = model.entry(5).peid
            eid = model.copyEntry(Lib.CopyInfo(5, peid,
                                               copygroups=True)) # eid==18
            self.assertEqual(eid, 18)
            self.assertEqual(model.entry(5).term, model.entry(eid).term)
            self.assertEqual(model.entry(5).pages, model.entry(eid).pages)
            self.assertListEqual([(1, "Linked Group"), (2, "Normal Group")],
                                 list(model.groupsForEid(eid)))
            self.assertListEqual([(-1, eid)], list(model.entries(peid=eid)))

            model.undo()
            model.undo()

            peid = model.entry(5).peid
            eid = model.copyEntry(Lib.CopyInfo(5, peid,
                                  copysubentries=True)) # eid==19
            self.assertEqual(eid, 19)
            self.assertEqual(model.entry(5).term, model.entry(eid).term)
            self.assertEqual(model.entry(5).pages, model.entry(eid).pages)
            self.assertListEqual([], list(model.groupsForEid(eid)))
            self.assertListEqual([(-1, 19), (0, 20), (1, 21), (2, 22),
                                  (2, 23), (1, 24), (0, 25)],
                                 list(model.entries(peid=eid)))

            for _ in range(7):
                model.undo()

            peid = model.entry(5).peid
            eid = model.copyEntry(Lib.CopyInfo(5, peid, copygroups=True,
                                               copysubentries=True))
            self.assertEqual(eid, 26) # eid==26
            self.assertEqual(model.entry(5).term, model.entry(eid).term)
            self.assertEqual(model.entry(5).pages, model.entry(eid).pages)
            self.assertListEqual([(-1, 26), (0, 27), (1, 28), (2, 29),
                                  (2, 30), (1, 31), (0, 32)],
                                 list(model.entries(peid=eid)))
            for eid in (27, 29, 31, 32):
                self.assertListEqual([], list(model.groupsForEid(eid)))
            for eid in (26, 28):
                self.assertListEqual([(1, "Linked Group"),
                                      (2, "Normal Group")],
                                     list(model.groupsForEid(eid)))
            self.assertListEqual([(2, "Normal Group")],
                                 list(model.groupsForEid(30)))

        finally:
            if model is not None:
                model.close()


    def test_04(self):
        model = None
        try:
            model = Xix.Model.Model(self.username)
            model.open(":memory:", *self.args)
            self.assertEqual(0, len(model))
            for eid, (term, pages) in self.data.items():
                model.addEntry(Saf.AUTO, SortAs.wordByWordCMS16(term),
                               term, pages=pages)
            self.assertEqual(len(self.data), len(model))
            self.check(model)

            for eid in self.data:
                self.assertListEqual([], list(model.groupsForEid(eid)))
            self.assertListEqual([], list(model.allGroups()))

            groups = [(1, "Linked Group", False),
                      (2, "Normal Group", False)]
            for _, name, _ in groups:
                model.addGroup(name)
            self.assertListEqual(groups, list(model.allGroups()))

            self.check(model)
            model.linkGroup(1)
            self.check(model)
            for eid in (4, 5):
                self.assertListEqual([], list(model.groupsForEid(eid)))
            model.addToGroup(5, 1)
            self.assertEqual(model.entry(5).pages, "5, 8, 10, 11")
            model.addToGroup(4, 1)
            self.assertEqual(model.entry(5).pages, "5, 7, 8, 9, 10, 11")
            self.assertEqual(model.entry(4).pages, "5, 7, 8, 9, 10, 11")
            for eid in (4, 5):
                self.assertListEqual([(1, "Linked Group")],
                                     list(model.groupsForEid(eid)))
            model.undo()
            self.assertListEqual([], list(model.groupsForEid(4)))
            self.assertListEqual([(1, "Linked Group")],
                                 list(model.groupsForEid(5)))
            model.undo()
            for eid in (4, 5):
                self.assertListEqual([], list(model.groupsForEid(eid)))

        finally:
            if model is not None:
                model.close()


    def check(self, model):
        for eid, (term, pages) in self.data.items():
            entry = model.entry(eid)
            self.assertEqual(entry.term, term)
            self.assertEqual(entry.pages, pages)


    def debug2(self, model):
        print()
        for indent, eid in model.entries():
            print("    " * indent, (eid, model.entry(eid).term,
                  model.entry(eid).pages, list(model.groupsForEid(eid))))


    def debug(self, model):
        print("#" * 30)
        cursor = model.db.cursor()
        for record in cursor.execute("""SELECT gid, name, linked FROM
                                        groups ORDER BY gid;"""):
            print(record)
        for record in cursor.execute("""SELECT gid, eid FROM
                                        grouped ORDER BY gid, eid;"""):
            print(record)
        print("#" * 30)


if __name__ == "__main__":
    unittest.main()
