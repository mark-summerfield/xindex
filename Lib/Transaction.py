#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.


class Transaction:

    def __init__(self, xix):
        self.xix = xix
        self.xix.error = None
        self.cursor = None


    def __enter__(self):
        self.cursor = self.xix.db.cursor()
        self.cursor.execute("BEGIN;")
        return self.cursor


    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.cursor.execute("COMMIT;")
        else:
            self.cursor.execute("ROLLBACK;") # Exception will be raised
