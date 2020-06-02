#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

import collections
import functools
import os

import Lib


RulesForName = collections.OrderedDict()
registerRules = functools.partial(Lib.registerRules, RulesForName)


@registerRules
def pageRangeCMS16(from_value, to_value):
    """Compact (Chicago Manual of Style) «CMS Compact»

    Ensures the to-page number is compact according to the rules.
    """
    # Returns the appropriate str for to_value
    from_str = str(from_value)
    to_str = str(to_value)
    if to_value < from_value: # Scale up to_value if necessary
        to_str = from_str[:-len(to_str)] + to_str
        if int(to_str) < from_value:
            to_str = str(round(from_value, -1) + to_value)
    prefix = ""
    if (from_value < 100) or (from_value % 100 == 0):
        pass
    elif from_str.endswith(("01", "02", "03", "04", "05", "06", "07",
                            "08", "09")):
        prefix = os.path.commonprefix([from_str, to_str])
    else:
        prefix = os.path.commonprefix([from_str, to_str[:-2]])
    return to_str[len(prefix):]


@registerRules
def pageRangeISO999(from_value, to_value):
    """Compact (ISO 999) «ISO Compact»

    Ensures the to-page number is compact according to the rules.
    (These rules are the same as the Oxford Guide to Style rules.)
    """
    # Returns the appropriate str for to_value
    from_str = str(from_value)
    to_str = str(to_value)
    if to_value < from_value: # Scale up to_value if necessary
        to_str = from_str[:-len(to_str)] + to_str
        if int(to_str) < from_value:
            to_str = str(round(from_value, -1) + to_value)
    if to_str.endswith(("10", "11", "12", "13", "14", "15", "16", "17",
                        "18", "19")):
        prefix = os.path.commonprefix([from_str, to_str[:-2]])
    else:
        prefix = os.path.commonprefix([from_str, to_str])
    return to_str[len(prefix):]


@registerRules
def pageRangeFull(from_value, to_value):
    """Full Form (“to” pages are shown in full) «Full»

    Ensures the to-page number is shown in full.
    """
    # Returns the appropriate str for to_value
    from_str = str(from_value)
    to_str = str(to_value)
    if to_value < from_value: # Scale up to_value if necessary
        to_str = from_str[:-len(to_str)] + to_str
        if int(to_str) < from_value:
            to_str = str(round(from_value, -1) + to_value)
    return to_str
