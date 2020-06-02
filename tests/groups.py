#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

import os
import random
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import unittest

import Saf
import SortAs
import Xix
from Const import LanguageKind, XrefKind


class TestXixGroups(unittest.TestCase):

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
            )


    def test_01(self):
        model = None
        try:
            model = Xix.Model.Model(self.username)
            model.open(":memory:", *self.args)
            self.assertEqual(0, len(model))
            for term, peid, eid in self.data:
                model.addEntry(Saf.AUTO, SortAs.wordByWordCMS16(term),
                               term, peid=peid)
            self.assertEqual(len(self.data), len(model))
            for _, _, eid in self.data:
                self.assertListEqual([], list(model.groupsForEid(eid)))
            self.assertListEqual([], list(model.normalGroups()))

            groups = [(1, "Group #1"), (2, "Second Group"), (3, "3rd grp")]
            for _, name in groups:
                model.addGroup(name)
            groups.sort(key=lambda t: t[1].lower())
            self.assertListEqual(groups, list(model.normalGroups()))
            model.undo()
            self.assertListEqual([(1, "Group #1"), (2, "Second Group")],
                                 list(model.normalGroups()))
            model.undo()
            self.assertListEqual([(1, "Group #1")],
                                 list(model.normalGroups()))
            model.undo()
            self.assertListEqual([], list(model.normalGroups()))

            model.redo()
            self.assertListEqual([(1, "Group #1")],
                                 list(model.normalGroups()))
            model.redo()
            self.assertListEqual([(1, "Group #1"), (2, "Second Group")],
                                 list(model.normalGroups()))
            model.redo()
            self.assertListEqual(groups, list(model.normalGroups()))

        finally:
            if model is not None:
                model.close()


    def test_02(self):
        model = None
        try:
            model = Xix.Model.Model(self.username)
            model.open(":memory:", *self.args)
            self.assertEqual(0, len(model))
            for term, peid, eid in self.data:
                model.addEntry(Saf.AUTO, SortAs.wordByWordCMS16(term),
                               term, peid=peid)
            self.assertEqual(len(self.data), len(model))
            for _, _, eid in self.data:
                self.assertListEqual([], list(model.groupsForEid(eid)))
            self.assertListEqual([], list(model.normalGroups()))

            groups = [(1, "Group #1"), (2, "Second Group"), (3, "3rd grp")]
            for _, name in groups:
                model.addGroup(name)
            groups.sort(key=lambda t: t[1].lower())
            self.assertListEqual(groups, list(model.normalGroups()))

            model.renameGroup(3, "Third Group")
            model.renameGroup(1, "First Group")
            self.assertListEqual(
                [(1, "First Group"), (2, "Second Group"),
                 (3, "Third Group")], list(model.normalGroups()))

            model.undo()
            self.assertListEqual(
                [(1, "Group #1"), (2, "Second Group"),
                 (3, "Third Group")], list(model.normalGroups()))
            model.undo()
            self.assertListEqual(groups, list(model.normalGroups()))
            model.undo()
            self.assertListEqual([(1, "Group #1"), (2, "Second Group")],
                                 list(model.normalGroups()))
            model.redo()
            model.redo()
            model.redo()
            self.assertListEqual(
                [(1, "First Group"), (2, "Second Group"),
                 (3, "Third Group")], list(model.normalGroups()))

            model.deleteGroup(2)
            model.deleteGroup(3)
            self.assertListEqual([(1, "First Group")],
                                 list(model.normalGroups()))
            model.undo()
            model.undo()
            self.assertListEqual(
                [(1, "First Group"), (2, "Second Group"),
                 (3, "Third Group")], list(model.normalGroups()))
            model.redo()
            self.assertListEqual(
                [(1, "First Group"), (3, "Third Group")],
                list(model.normalGroups()))
            model.redo()
            self.assertListEqual([(1, "First Group")],
                                 list(model.normalGroups()))
            model.undo()
            model.undo()
            self.assertListEqual(
                [(1, "First Group"), (2, "Second Group"),
                 (3, "Third Group")], list(model.normalGroups()))

        finally:
            if model is not None:
                model.close()


    def test_03(self):
        model = None
        try:
            model = Xix.Model.Model(self.username)
            model.open(":memory:", *self.args)
            self.assertEqual(0, len(model))
            for term, peid, eid in self.data:
                model.addEntry(Saf.AUTO, SortAs.wordByWordCMS16(term),
                               term, peid=peid)
            self.assertEqual(len(self.data), len(model))
            for _, _, eid in self.data:
                self.assertListEqual([], list(model.groupsForEid(eid)))
            self.assertListEqual([], list(model.normalGroups()))

            groups = [(1, "Group #1"), (2, "Second Group"), (3, "3rd grp")]
            for _, name in groups:
                model.addGroup(name)
            groups.sort(key=lambda t: t[1].lower())
            self.assertListEqual(groups, list(model.normalGroups()))

            self.assertEqual(len(list(model.normalGroups())), len(groups))
            gid1 = model.addGroup("4D")
            self.assertEqual(len(list(model.normalGroups())),
                             len(groups) + 1)
            self.assertEqual(gid1, model.gidForName("4D"))
            self.assertEqual("4D", model.nameForGid(gid1))
            gid2 = model.addGroup("4D")
            self.assertEqual(len(list(model.normalGroups())),
                             len(groups) + 1)
            self.assertEqual(gid1, gid2)
            self.assertEqual("4D", model.nameForGid(gid2))

        finally:
            if model is not None:
                model.close()


    def test_04(self):
        model = None
        try:
            model = Xix.Model.Model(self.username)
            model.open(":memory:", *self.args)
            self.assertEqual(0, len(model))
            threes = []
            fives = []
            for term, peid, eid in self.data:
                model.addEntry(Saf.AUTO, SortAs.wordByWordCMS16(term),
                               term, peid=peid)
                if "three" in term:
                    threes.append(eid)
                if "five" in term:
                    fives.append(eid)
            self.assertEqual(len(self.data), len(model))
            for _, _, eid in self.data:
                self.assertListEqual([], list(model.groupsForEid(eid)))
            self.assertListEqual([], list(model.normalGroups()))

            groups = [(1, "Empty"), (2, "Threes"), (3, "Fives"),
                      (4, "3 + 5")]
            for _, name in groups:
                model.addGroup(name)
            groups.sort(key=lambda t: t[1].lower())
            self.assertListEqual(groups, list(model.normalGroups()))

            for eid in threes:
                model.addToGroup(eid, 2)
                model.addToGroup(eid, 4)
            for eid in fives:
                model.addToGroup(eid, 3)
                model.addToGroup(eid, 4)
            for eid, groups in (
                    (1, [(4, "3 + 5"), (2, "Threes")]),
                    (11, [(4, "3 + 5"), (2, "Threes")]),
                    (21, [(4, "3 + 5"), (2, "Threes")]),
                    (2, [(4, "3 + 5"), (3, "Fives")]),
                    (10, [(4, "3 + 5"), (3, "Fives")]),
                    (15, [(4, "3 + 5"), (3, "Fives")]),
                    (17, [(4, "3 + 5"), (3, "Fives")]),
                    ):
                self.assertEqual(list(model.groupsForEid(eid)), groups)

            model.removeFromGroup(21, 4)
            model.removeFromGroup(21, 2)
            model.removeFromGroup(17, 4)
            for eid, groups in (
                    (1, [(4, "3 + 5"), (2, "Threes")]),
                    (11, [(4, "3 + 5"), (2, "Threes")]),
                    (21, []),
                    (2, [(4, "3 + 5"), (3, "Fives")]),
                    (10, [(4, "3 + 5"), (3, "Fives")]),
                    (15, [(4, "3 + 5"), (3, "Fives")]),
                    (17, [(3, "Fives")]),
                    ):
                self.assertEqual(list(model.groupsForEid(eid)), groups)

            model.undo()
            model.undo()
            for eid, groups in (
                    (1, [(4, "3 + 5"), (2, "Threes")]),
                    (11, [(4, "3 + 5"), (2, "Threes")]),
                    (21, [(2, "Threes")]),
                    (2, [(4, "3 + 5"), (3, "Fives")]),
                    (10, [(4, "3 + 5"), (3, "Fives")]),
                    (15, [(4, "3 + 5"), (3, "Fives")]),
                    (17, [(4, "3 + 5"), (3, "Fives")]),
                    ):
                self.assertEqual(list(model.groupsForEid(eid)), groups)

            model.redo()
            for eid, groups in (
                    (1, [(4, "3 + 5"), (2, "Threes")]),
                    (11, [(4, "3 + 5"), (2, "Threes")]),
                    (21, []),
                    (2, [(4, "3 + 5"), (3, "Fives")]),
                    (10, [(4, "3 + 5"), (3, "Fives")]),
                    (15, [(4, "3 + 5"), (3, "Fives")]),
                    (17, [(4, "3 + 5"), (3, "Fives")]),
                    ):
                self.assertEqual(list(model.groupsForEid(eid)), groups)

            model.deleteGroup(2)
            for eid, groups in (
                    (1, [(4, "3 + 5")]),
                    (11, [(4, "3 + 5")]),
                    (21, []),
                    (2, [(4, "3 + 5"), (3, "Fives")]),
                    (10, [(4, "3 + 5"), (3, "Fives")]),
                    (15, [(4, "3 + 5"), (3, "Fives")]),
                    (17, [(4, "3 + 5"), (3, "Fives")]),
                    ):
                self.assertEqual(list(model.groupsForEid(eid)), groups)

            model.deleteGroup(4)
            for eid, groups in (
                    (1, []),
                    (11, []),
                    (21, []),
                    (2, [(3, "Fives")]),
                    (10, [(3, "Fives")]),
                    (15, [(3, "Fives")]),
                    (17, [(3, "Fives")]),
                    ):
                self.assertEqual(list(model.groupsForEid(eid)), groups)

            model.deleteGroup(3)
            for eid in (1, 11, 21, 2, 10, 15, 17,):
                self.assertEqual(list(model.groupsForEid(eid)), [])

            model.undo() # GID 3
            for eid, groups in (
                    (1, []),
                    (11, []),
                    (21, []),
                    (2, [(3, "Fives")]),
                    (10, [(3, "Fives")]),
                    (15, [(3, "Fives")]),
                    (17, [(3, "Fives")]),
                    ):
                self.assertEqual(list(model.groupsForEid(eid)), groups)

            model.undo() # GID 4
            for eid, groups in (
                    (1, [(4, "3 + 5")]),
                    (11, [(4, "3 + 5")]),
                    (21, []),
                    (2, [(4, "3 + 5"), (3, "Fives")]),
                    (10, [(4, "3 + 5"), (3, "Fives")]),
                    (15, [(4, "3 + 5"), (3, "Fives")]),
                    (17, [(4, "3 + 5"), (3, "Fives")]),
                    ):
                self.assertEqual(list(model.groupsForEid(eid)), groups)

            model.undo() # GID 2
            for eid, groups in (
                    (1, [(4, "3 + 5"), (2, "Threes")]),
                    (11, [(4, "3 + 5"), (2, "Threes")]),
                    (21, []),
                    (2, [(4, "3 + 5"), (3, "Fives")]),
                    (10, [(4, "3 + 5"), (3, "Fives")]),
                    (15, [(4, "3 + 5"), (3, "Fives")]),
                    (17, [(4, "3 + 5"), (3, "Fives")]),
                    ):
                self.assertEqual(list(model.groupsForEid(eid)), groups)

            model.redo()
            for eid, groups in (
                    (1, [(4, "3 + 5")]),
                    (11, [(4, "3 + 5")]),
                    (21, []),
                    (2, [(4, "3 + 5"), (3, "Fives")]),
                    (10, [(4, "3 + 5"), (3, "Fives")]),
                    (15, [(4, "3 + 5"), (3, "Fives")]),
                    (17, [(4, "3 + 5"), (3, "Fives")]),
                    ):
                self.assertEqual(list(model.groupsForEid(eid)), groups)

        finally:
            if model is not None:
                model.close()


    def test_05(self):
        model = None
        try:
            model = Xix.Model.Model(self.username)
            model.open(":memory:", *self.args)
            self.assertEqual(0, len(model))
            threes = []
            fives = []
            for term, peid, eid in self.data:
                model.addEntry(Saf.AUTO, SortAs.wordByWordCMS16(term),
                               term, peid=peid)
                if "three" in term:
                    threes.append(eid)
                if "five" in term:
                    fives.append(eid)
            self.assertEqual(len(self.data), len(model))
            for _, _, eid in self.data:
                self.assertListEqual([], list(model.groupsForEid(eid)))
            self.assertListEqual([], list(model.normalGroups()))

            groups = [(1, "Empty"), (2, "Threes"), (3, "Fives"),
                      (4, "3 + 5")]
            for _, name in groups:
                model.addGroup(name)
            groups.sort(key=lambda t: t[1].lower())
            self.assertListEqual(groups, list(model.normalGroups()))

            for eid in threes:
                model.addToGroup(eid, 2)
                model.addToGroup(eid, 4)
            for eid, groups in (
                    (1, [(4, "3 + 5"), (2, "Threes")]),
                    (11, [(4, "3 + 5"), (2, "Threes")]),
                    (21, [(4, "3 + 5"), (2, "Threes")]),
                    ):
                self.assertEqual(list(model.groupsForEid(eid)), groups)

            model.deleteEntry(21)
            for eid, groups in (
                    (1, [(4, "3 + 5"), (2, "Threes")]),
                    (11, [(4, "3 + 5"), (2, "Threes")]),
                    ):
                self.assertEqual(list(model.groupsForEid(eid)), groups)
            model.undo()
            for eid, groups in (
                    (1, [(4, "3 + 5"), (2, "Threes")]),
                    (11, [(4, "3 + 5"), (2, "Threes")]),
                    (21, [(4, "3 + 5"), (2, "Threes")]),
                    ):
                self.assertEqual(list(model.groupsForEid(eid)), groups)
            model.redo()
            for eid, groups in (
                    (1, [(4, "3 + 5"), (2, "Threes")]),
                    (11, [(4, "3 + 5"), (2, "Threes")]),
                    ):
                self.assertEqual(list(model.groupsForEid(eid)), groups)

            model.deleteEntry(8) # No effect on groups
            for eid, groups in (
                    (1, [(4, "3 + 5"), (2, "Threes")]),
                    (11, [(4, "3 + 5"), (2, "Threes")]),
                    ):
                self.assertEqual(list(model.groupsForEid(eid)), groups)
            model.undo()
            for eid, groups in (
                    (1, [(4, "3 + 5"), (2, "Threes")]),
                    (11, [(4, "3 + 5"), (2, "Threes")]),
                    ):
                self.assertEqual(list(model.groupsForEid(eid)), groups)
            model.redo()
            for eid, groups in (
                    (1, [(4, "3 + 5"), (2, "Threes")]),
                    (11, [(4, "3 + 5"), (2, "Threes")]),
                    ):
                self.assertEqual(list(model.groupsForEid(eid)), groups)

            self.assertTrue(model.inGroup(1))
            self.assertTrue(model.inGroup(11))
            self.assertFalse(model.inGroup(4))

        finally:
            if model is not None:
                model.close()


    def test_06(self):
        model = None
        try:
            model = Xix.Model.Model(self.username)
            model.open(":memory:", *self.args)
            self.assertEqual(0, len(model))
            for term, peid, eid in self.data:
                model.addEntry(Saf.AUTO, SortAs.wordByWordCMS16(term),
                               term, peid=peid)
            self.assertEqual(len(self.data), len(model))
            for _, _, eid in self.data:
                self.assertListEqual([], list(model.groupsForEid(eid)))
            self.assertListEqual([], list(model.normalGroups()))

            groups = [(1, "Group (1)"), (2, "Second Group"), (3, "3rd grp")]
            for _, name in groups:
                model.addGroup(name)
            names = sorted(group[1] for group in model.allGroups())
            self.assertListEqual(["3rd grp", "Group (1)", "Second Group"],
                                 names)
            name = model.uniqueGroupName("New Group")
            self.assertEqual(name, "New Group")
            name = model.uniqueGroupName("Group (1)")
            self.assertEqual(name, "Group (2)")
            model.addGroup(name)
            name = model.uniqueGroupName("Group (2)")
            self.assertEqual(name, "Group (3)")
        finally:
            if model is not None:
                model.close()


    def test_07(self):
        model = None
        try:
            model = Xix.Model.Model(self.username)
            model.open(":memory:", *self.args)
            self.assertEqual(0, len(model))
            for term, peid, eid in self.data:
                model.addEntry(Saf.AUTO, SortAs.wordByWordCMS16(term),
                               term, peid=peid)
            self.assertEqual(len(self.data), len(model))
            for _, _, eid in self.data:
                self.assertListEqual([], list(model.groupsForEid(eid)))
            self.assertListEqual([], list(model.normalGroups()))

            group = "Linked Group"
            gid = model.addGroup(group)
            model.linkGroup(gid)
            self.assertListEqual([(gid, group, True)],
                                 list(model.allGroups()))
            self.assertListEqual([(gid, group)],
                                 list(model.linkedGroups()))
            self.assertListEqual([], list(model.normalGroups()))
            self.assertListEqual([], list(model.eidsForGid(gid)))
            eids = (2, 6, 10, 15, 17)
            for eid in eids:
                entry = model.entry(eid)
                model.editEntry(entry, entry.saf, entry.sortas,
                                entry.term, str(eid))
                self.assertEqual(str(eid), model.entry(eid).pages)
            for eid in eids:
                model.addToGroup(eid, 1)
            self.assertListEqual(list(eids), sorted(model.eidsForGid(gid)))
            pages = ", ".join(str(eid) for eid in eids)
            for eid in eids:
                self.assertEqual(pages, model.entry(eid).pages)
            eid = random.choice(eids)
            pages += ", 85-7, 91"
            model.editEntry(entry, entry.saf, entry.sortas, entry.term,
                            pages)
            for eid in eids:
                self.assertEqual(pages, model.entry(eid).pages)

            # Delete Group (preserve pages)
            model.deleteGroup(gid)
            self.assertListEqual([], list(model.eidsForGid(gid)))
            self.assertListEqual([], list(model.normalGroups()))
            self.assertListEqual([], list(model.linkedGroups()))
            self.assertListEqual([], list(model.allGroups()))
            for eid in eids:
                self.assertEqual(pages, model.entry(eid).pages)

            model.undo()
            for eid in eids:
                self.assertEqual(pages, model.entry(eid).pages)
                self.assertEqual([], list(model.all_xrefs(eid)))
            self.assertListEqual(list(eids), list(model.eidsForGid(gid)))
            self.assertListEqual([], list(model.normalGroups()))
            self.assertListEqual([(gid, group)], list(model.linkedGroups()))
            self.assertListEqual([(gid, group, True)],
                                 list(model.allGroups()))

            # Delete Group (use cross-references)
            targetEid = random.choice(eids)
            model.deleteGroup(gid, targetEid=targetEid)
            self.assertListEqual([], list(model.eidsForGid(gid)))
            self.assertListEqual([], list(model.normalGroups()))
            self.assertListEqual([], list(model.linkedGroups()))
            self.assertListEqual([], list(model.allGroups()))
            xrefs = []
            for eid in eids:
                if eid == targetEid:
                    self.assertEqual(pages, model.entry(eid).pages)
                else:
                    self.assertEqual("", model.entry(eid).pages)
                    xrefs.append(Xix.Util.Xref(eid, targetEid, "",
                                               XrefKind.SEE))
            self.assertEqual(xrefs, list(model.all_xrefs(targetEid)))

            model.undo()
            for eid in eids:
                self.assertEqual(pages, model.entry(eid).pages)
                self.assertEqual([], list(model.all_xrefs(eid)))
            self.assertListEqual(list(eids), list(model.eidsForGid(gid)))
            self.assertListEqual([], list(model.normalGroups()))
            self.assertListEqual([(gid, group)], list(model.linkedGroups()))
            self.assertListEqual([(gid, group, True)],
                                 list(model.allGroups()))

            # Unlink Group (preserve pages)
            model.unlinkGroup(gid)
            self.assertListEqual(list(eids), list(model.eidsForGid(gid)))
            self.assertListEqual([(gid, group)], list(model.normalGroups()))
            self.assertListEqual([], list(model.linkedGroups()))
            self.assertListEqual([(gid, group, False)],
                                 list(model.allGroups()))
            for eid in eids:
                self.assertEqual(pages, model.entry(eid).pages)

            model.undo()
            for eid in eids:
                self.assertEqual(pages, model.entry(eid).pages)
                self.assertEqual([], list(model.all_xrefs(eid)))
            self.assertListEqual(list(eids), list(model.eidsForGid(gid)))
            self.assertListEqual([], list(model.normalGroups()))
            self.assertListEqual([(gid, group)], list(model.linkedGroups()))
            self.assertListEqual([(gid, group, True)],
                                 list(model.allGroups()))

            # Unlink Group (use cross-references)
            targetEid = random.choice(eids)
            model.unlinkGroup(gid, targetEid=targetEid)
            self.assertListEqual(list(eids), list(model.eidsForGid(gid)))
            self.assertListEqual([(gid, group)], list(model.normalGroups()))
            self.assertListEqual([], list(model.linkedGroups()))
            self.assertListEqual([(gid, group, False)],
                                 list(model.allGroups()))
            xrefs = []
            for eid in eids:
                if eid == targetEid:
                    self.assertEqual(pages, model.entry(eid).pages)
                else:
                    self.assertEqual("", model.entry(eid).pages)
                    xrefs.append(Xix.Util.Xref(eid, targetEid, "",
                                               XrefKind.SEE))
            self.assertEqual(xrefs, list(model.all_xrefs(targetEid)))

            model.undo()
            for eid in eids:
                self.assertEqual(pages, model.entry(eid).pages)
                self.assertEqual([], list(model.all_xrefs(eid)))
            self.assertListEqual(list(eids), list(model.eidsForGid(gid)))
            self.assertListEqual([], list(model.normalGroups()))
            self.assertListEqual([(gid, group)], list(model.linkedGroups()))
            self.assertListEqual([(gid, group, True)],
                                 list(model.allGroups()))

        finally:
            if model is not None:
                model.close()


if __name__ == "__main__":
    unittest.main()
