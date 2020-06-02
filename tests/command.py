#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

# flake8: noqa

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import unittest

import Lib


DEBUG = 0


class LetterCommand(Lib.Command.Command):

    def __init__(self, letter):
        super().__init__()
        self.letter = letter
        self.description = letter.upper()

    def do(self):
        return self.letter


class TestCommand(unittest.TestCase):

    def setUp(self):
        self.stack = Lib.Command.Stack()


    def debug(self, message="    "):
        if not DEBUG:
            return
        if message:
            print(message, end=" ")
        if self.stack.index is not None:
            left = self.stack.commands[:self.stack.index]
            middle = ["<{}>".format(
                      self.stack.commands[self.stack.index])]
            right = self.stack.commands[self.stack.index + 1:]
            print(left + middle + right, self.stack.index)
        else:
            print(self.stack.commands, self.stack.index)


    def test_01(self):
        if DEBUG: print()
        self.stack.clear()
        self.assertEqual(0, len(self.stack))
        letters = "abcdef"
        for letter in letters:
            self.stack.push(LetterCommand(letter))
        self.assertEqual(len(letters), len(self.stack))
        self.assertFalse(self.stack.canRedo)
        self.debug()
        count = len(letters) - 1
        while self.stack.canUndo:
            command = self.stack.getUndo()
            self.debug("undo")
            self.assertEqual(command.letter, letters[count])
            count -= 1
        self.assertTrue(self.stack.canRedo)
        self.debug()
        count = 0
        while self.stack.canRedo:
            command = self.stack.getRedo()
            self.assertEqual(command.letter, letters[count])
            count += 1
            self.debug("redo")
        letters += "gh"
        self.stack.push(LetterCommand("g"))
        self.stack.push(LetterCommand("h"))
        count = len(letters) - 1
        while self.stack.canUndo:
            command = self.stack.getUndo()
            self.debug("undo")
            self.assertEqual(command.letter, letters[count])
            count -= 1
        self.assertTrue(self.stack.canRedo)
        self.debug()
        count = 0
        while self.stack.canRedo:
            command = self.stack.getRedo()
            self.assertEqual(command.letter, letters[count])
            count += 1
            self.debug("redo")
        command = self.stack.getUndo()
        self.assertEqual(command.letter, "h")
        command = self.stack.getUndo()
        self.assertEqual(command.letter, "g")
        command = self.stack.getUndo()
        self.assertEqual(command.letter, "f")
        self.assertTrue(self.stack.canRedo)
        self.assertTrue(self.stack.canUndo)
        self.debug("undo")
        self.stack.push(LetterCommand("X"))
        self.assertFalse(self.stack.canRedo)
        self.assertTrue(self.stack.canUndo)
        self.debug("redo")
        self.stack.push(LetterCommand("Y"))
        self.debug("redo")
        letters = "abcdeXY"
        count = len(letters) - 1
        while self.stack.canUndo:
            command = self.stack.getUndo()
            self.debug("undo")
            self.assertEqual(command.letter, letters[count])
            count -= 1
        self.assertTrue(self.stack.canRedo)
        self.debug()
        count = 0
        while self.stack.canRedo:
            command = self.stack.getRedo()
            self.assertEqual(command.letter, letters[count])
            count += 1
            self.debug("redo")
        self.assertFalse(self.stack.canRedo)
        self.assertTrue(self.stack.canUndo)


    def test_02(self):
        if DEBUG: print()
        self.stack.clear()
        self.assertEqual(0, len(self.stack))
        letters = "abcdef"
        for letter in letters:
            self.stack.push(LetterCommand(letter))
        self.debug()
        for i in range(len(letters) - 1, -1, -1):
            self.debug("preU")
            self.assertEqual(self.stack._command().letter, letters[i])
            command = self.stack.getUndo()
            self.debug("aftU")
            if DEBUG: print(command)
        self.debug()
        self.assertTrue(self.stack.canRedo)
        self.assertFalse(self.stack.canUndo)
        for i in range(len(letters)):
            self.debug("preR")
            command = self.stack.getRedo()
            self.debug("aftR")
            if DEBUG: print(command)
            self.assertEqual(self.stack._command().letter, letters[i])
        self.debug()


if __name__ == "__main__":
    unittest.main()
