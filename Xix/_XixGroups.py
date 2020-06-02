#!/usr/bin/env python3
# Copyright © 2016-20 Qtrac Ltd. All rights reserved.

import re

import Lib
import Sql


INC_RX = re.compile(r"\s*\(\d+\)\s*")


class Mixin:

    def allGroups(self):
        with Lib.Transaction.Transaction(self) as cursor:
            for record in cursor.execute(Sql.GET_ALL_GROUPS):
                yield record[0], record[1], bool(record[2])
                # gid, name, linked


    def normalGroups(self):
        with Lib.Transaction.Transaction(self) as cursor:
            for record in cursor.execute(Sql.GET_NORMAL_GROUPS):
                yield record[0], record[1] # gid, name


    def linkedGroups(self):
        with Lib.Transaction.Transaction(self) as cursor:
            for record in cursor.execute(Sql.GET_LINKED_GROUPS):
                yield record[0], record[1] # gid, name


    def nameForGid(self, gid):
        with Lib.Transaction.Transaction(self) as cursor:
            return Sql.first(cursor, Sql.GET_GROUP_NAME, dict(gid=gid),
                             Class=str)


    def gidForName(self, name):
        with Lib.Transaction.Transaction(self) as cursor:
            return Sql.first(cursor, Sql.GET_GID_FOR_NAME, dict(name=name))


    def groupsForEid(self, eid, *, withLinks=False):
        with Lib.Transaction.Transaction(self) as cursor:
            if withLinks:
                for record in cursor.execute(
                        Sql.GET_ENTRY_GROUPS_WITH_LINKS, dict(eid=eid)):
                    yield record[0], record[1], bool(record[2])
                    # gid, name, linked
            else:
                for record in cursor.execute(Sql.GET_ENTRY_GROUPS,
                                             dict(eid=eid)):
                    yield record[0], record[1] # gid, name


    def eidsForGid(self, gid):
        with Lib.Transaction.Transaction(self) as cursor:
            for record in cursor.execute(Sql.EIDS_FOR_GROUPS,
                                         dict(gid=gid)):
                yield record[0] # eid


    def inGroup(self, eid):
        with Lib.Transaction.Transaction(self) as cursor:
            return Sql.first(cursor, Sql.IN_GROUP, dict(eid=eid),
                             Class=bool)


    def normalGroupCount(self):
        with Lib.Transaction.Transaction(self) as cursor:
            return Sql.first(cursor, Sql.NORMAL_GROUP_COUNT, default=0)


    def linkedGroupCount(self):
        with Lib.Transaction.Transaction(self) as cursor:
            return Sql.first(cursor, Sql.LINKED_GROUP_COUNT, default=0)


    def groupMemberCount(self, gid):
        with Lib.Transaction.Transaction(self) as cursor:
            return Sql.first(cursor.execute(Sql.GROUP_MEMBER_COUNT,
                                            dict(gid=gid), default=0))


    def deletedGidsForEid(self, eid):
        with Lib.Transaction.Transaction(self) as cursor:
            for record in cursor.execute(Sql.DELETED_GIDS, dict(eid=eid)):
                yield record[0] # gid


    def linkedGroup(self, eid):
        with Lib.Transaction.Transaction(self) as cursor:
            return Sql.first(cursor, Sql.LINKED_GROUP, dict(eid=eid))


    def isLinkedGroup(self, gid, *, cursor=None):
        if cursor is None:
            with Lib.Transaction.Transaction(self) as cursor:
                return Sql.first(cursor, Sql.IS_LINKED_GROUP, dict(gid=gid),
                                 default=False, Class=bool)
        else:
            return Sql.first(cursor, Sql.IS_LINKED_GROUP, dict(gid=gid),
                             default=False, Class=bool)


    def safeToLinkGroup(self, gid):
        with Lib.Transaction.Transaction(self) as cursor:
            if self.isLinkedGroup(gid, cursor=cursor):
                return False # Already linked
            eids = []
            for record in cursor.execute(Sql.EIDS_FOR_GROUPS,
                                         dict(gid=gid)):
                eids.append(record[0]) # eid
            for eid in eids:
                if cursor.execute(Sql.LINKED_GROUP,
                                  dict(eid=eid)).fetchone() is not None:
                    return False
                    # At least one member of the group is linked
        return True


    def safeToAddToGroup(self, eid, gid):
        with Lib.Transaction.Transaction(self) as cursor:
            if not self.isLinkedGroup(gid, cursor=cursor):
                return True # Always safe to add to an unlinked group
            if cursor.execute(Sql.LINKED_GROUP,
                              dict(eid=eid)).fetchone() is not None:
                return False # This entry is already in a linked group
        return True


    def uniqueGroupName(self, name):
        name = Lib.htmlToPlainText(name)
        names = set({group[1] for group in self.allGroups()})
        n = 1
        while name in names:
            name = "{} ({})".format(INC_RX.sub("", name), n)
            n += 1
        return name
