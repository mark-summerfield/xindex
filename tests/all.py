#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

import sys
import unittest

WIN = sys.platform.startswith("win")


import command
import output_i
import output_r
import output_x
import pages
import pages_at_output
import combinepages
import renumberpages
import xixrenumber
import sortbycms
import sortbyniso
import sortbyiso
import xix
import xixmodel
import xixmodelro
import mergeentries
import swapentries
import import_xml
import markup
import sortcandidates
import normalize
import xixsearcher
import htmlreplacer
import elidehtml
import groups
import linkedgroups
import copyentry
import bug00001

load = unittest.defaultTestLoader.loadTestsFromModule
verbosity = 1 if len(sys.argv) == 1 else 2

modules = (
    command,
    output_i,
    output_r,
    output_x,
    pages,
    pages_at_output,
    combinepages,
    renumberpages,
    xixrenumber,
    sortbycms,
    sortbyniso,
    sortbyiso,
    xix,
    xixmodel,
    xixmodelro,
    mergeentries,
    swapentries,
    import_xml,
    markup,
    sortcandidates,
    normalize,
    xixsearcher,
    htmlreplacer,
    elidehtml,
    groups,
    linkedgroups,
    copyentry,
    bug00001,
    )

if not WIN:
    suite = unittest.TestSuite()
    for module in modules:
        suite.addTest(load(module))
    unittest.TextTestRunner(verbosity=verbosity).run(suite)
else: # Windows spawn is v. slow
    for module in modules:
        print(module.__name__)
        suite = unittest.TestSuite()
        unittest.TextTestRunner(verbosity=verbosity).run(suite)
