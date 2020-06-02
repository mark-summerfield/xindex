#!/usr/bin/env python3
# Copyright © 2016-20 Qtrac Ltd. All rights reserved.

import atexit
import multiprocessing

import Xix


def filteredEntries(*, filename, filter, match):
    if filteredEntries.pool is None:
        filteredEntries.pool = multiprocessing.Pool()
    kwargs = dict(filename=filename, filter=filter, match=match)
    return filteredEntries.pool.apply_async(_filterEntries, (), kwargs)


filteredEntries.pool = None


def _filterEntries(*, filename, filter, match):
    xix = None
    try:
        xix = Xix.XixRO.XixRO()
        if not xix.open(filename):
            return None
        return list(xix.filteredEntries(filter=filter, match=match))
    finally:
        if xix is not None:
            xix.close()


def finish():
    if filteredEntries.pool is not None:
        filteredEntries.pool.close()
        filteredEntries.pool.join()
        del filteredEntries.pool
        filteredEntries.pool = None


atexit.register(finish)
