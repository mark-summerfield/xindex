#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

import Lib
import Sql
from Const import Query


# NOTE: It is the caller's responsibility to ensure that gname isn't in use
# See Xix.uniqueGroupName()
class AddGroup(Lib.Command.Command):

    def __init__(self, gname, *, link=False, name="add new"):
        super().__init__()
        self.gid = None
        self.gname = gname
        self.link = link
        self.description = "{} {} group “{}”".format(
            name, "linked" if link else "normal", gname)


    def do(self):
        params = dict(linked=self.link, name=self.gname)
        if self.gid is None:
            sql = Sql.ADD_GROUP
        else:
            params["gid"] = self.gid # redo
            sql = Sql.RE_ADD_GROUP
        return Query(sql, params)


    def undo(self):
        return Query(Sql.DELETE_GROUP, dict(gid=self.gid))


# NOTE: It is the caller's responsibility to ensure that gname isn't in use
class RenameGroup(AddGroup):

    def __init__(self, gid, gname, oldname):
        super().__init__(gname, name="edit")
        self.oldname = oldname
        self.gid = gid


    def do(self):
        return Query(Sql.RENAME_GROUP, dict(gid=self.gid, name=self.gname))


    def undo(self):
        return Query(Sql.RENAME_GROUP, dict(gid=self.gid,
                                            name=self.oldname))


# Must only be created in the context of a macro and only done if there
# are no entries in this group
class DeleteGroup(AddGroup):

    def __init__(self, gid, gname):
        super().__init__(gname, name="delete")
        self.gid = gid


    def do(self):
        return Query(Sql.DELETE_GROUP, dict(gid=self.gid))


    def undo(self):
        return Query(Sql.RE_ADD_GROUP, dict(gid=self.gid, name=self.gname))


# Must only be created in the context of a macro that syncs pages on do
class LinkGroup(AddGroup):

    def __init__(self, gid, gname):
        super().__init__(gname, name="link")
        self.gid = gid


    def do(self):
        return Query(Sql.UPDATE_GROUP, dict(linked=1, gid=self.gid))


    def undo(self):
        return Query(Sql.UPDATE_GROUP, dict(linked=0, gid=self.gid))


class UnlinkGroup(AddGroup):

    def __init__(self, gid, gname):
        super().__init__(gname, name="unlink")
        self.gid = gid


    def do(self):
        return Query(Sql.UPDATE_GROUP, dict(linked=0, gid=self.gid))


    def undo(self):
        return Query(Sql.UPDATE_GROUP, dict(linked=1, gid=self.gid))


class AddToGroup(Lib.Command.Command):

    def __init__(self, eid, term, gid, gname, *, name="add"):
        super().__init__()
        self.eid = eid
        self.term = term
        self.gid = gid
        self.gname = gname
        self.description = "{} entry “{}” to group “{}”".format(
            name, Lib.elide(term), gname)


    def do(self):
        return Query(Sql.ADD_TO_GROUP, dict(gid=self.gid, eid=self.eid))


    def undo(self):
        return Query(Sql.REMOVE_FROM_GROUP, dict(gid=self.gid,
                                                 eid=self.eid))


class RecreateGrouped(AddToGroup):

    def __init__(self, eid, term, gid, gname, *, name="recreate"):
        super().__init__(eid, term, gid, gname)


class RemoveFromGroup(AddToGroup):

    def __init__(self, eid, term, gid, gname, *, name="remove"):
        super().__init__(eid, term, gid, gname)
        self.description = self.description.replace("to group",
                                                    "from group")


    def do(self):
        return Query(Sql.REMOVE_FROM_GROUP, dict(gid=self.gid,
                                                 eid=self.eid))


    def undo(self):
        return Query(Sql.ADD_TO_GROUP, dict(gid=self.gid, eid=self.eid))
