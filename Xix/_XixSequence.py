#!/usr/bin/env python3
# Copyright © 2016-20 Qtrac Ltd. All rights reserved.

import roman

import Sql
from Const import PagesOrderKind


MAX_PAGE_NUMBER = 2000


class Mixin:

    def unindexedPages(self, highestPage):
        cursor = self.db.cursor()
        numbers = []
        for record in cursor.execute(Sql.UNINDEXED_PAGES,
                                     dict(highestpage=highestPage)):
            numbers.append(int(record[0]))
        return sorted(numbers)


    def _create_page_number_sequences(self, cursor):
        for kind in PagesOrderKind:
            name = kind.name.lower()
            cursor.execute(Sql.CREATE_PAGE_NUMBER_SEQUENCE.format(name))
            start, end = kind.start_end
            if name.startswith("r"):
                cursor.executemany(
                    Sql.INSERT_PAGE_NUMBER_SEQUENCE.format(name),
                    tuple((roman.toRoman(n),) for n in range(start, end)))
            else:
                cursor.executemany(
                    Sql.INSERT_PAGE_NUMBER_SEQUENCE.format(name),
                    tuple((n,) for n in range(start, end)))
        cursor.execute(Sql.CREATE_PAGE_NUMBERS_SEQUENCE)
        cursor.executemany(Sql.INSERT_PAGE_NUMBERS_SEQUENCE,
                           tuple((n,) for n in range(1, MAX_PAGE_NUMBER)))
