#!/usr/bin/env python3
# Copyright © 2014-20 Qtrac Ltd. All rights reserved.

import apsw
import sys


if len(sys.argv) == 1 or sys.argv[1] in {"-h", "--help"}:
    raise SystemExit("usage: xix_dump.py file.xix")

db = None
try:
    db = apsw.Connection(sys.argv[1])
    shell = apsw.Shell(stdout=sys.stdout, db=db)
    shell.process_command(".dump entries xrefs generic_xrefs config")
finally:
    if db is not None:
        db.close()
