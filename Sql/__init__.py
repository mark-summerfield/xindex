#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.
# flake8: noqa

# Sql/Create.py
# Sql/Cache.py
# Sql/Copy.py
# Sql/Modify.py
# Sql/Select.py
# Sql/SelectFilter.py
# Sql/Maintain.py
# Sql/PageOrder.py


from .Create import *
from .Cache import *
from .Copy import *
from .Modify import *
from .Select import *
from .SelectFilter import *
from .Maintain import *
from .PageOrder import *


def first(cursor, sql, params=None, *, default=None, Class=int):
    params = {} if params is None else params
    record = cursor.execute(sql, params).fetchone()
    if record is None:
        return default # Deliberately ignores Class
    first = record[0]
    return bool(int(first)) if isinstance(Class, bool) else Class(first)
