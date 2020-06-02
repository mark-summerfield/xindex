#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

from PySide.QtCore import QObject, Signal


class Error(Exception):
    pass


class Stack(QObject):

    can_undo = Signal(bool, str)
    can_redo = Signal(bool, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.commands = []
        self.index = None


    def push(self, command):
        if self.canRedo: # Get rid of all redoables
            if self.index is None:
                self.commands.clear()
            else:
                del self.commands[self.index + 1:]
        self.commands.append(command)
        self.index = len(self.commands) - 1
        self._notify()


    def _command(self): # Only for testing
        return self.commands[self.index]


    def _notify(self):
        description = "(Nothing to undo)"
        if self.canUndo:
            description = self.commands[self.index].description
        self.can_undo.emit(self.canUndo, description)
        description = "(Nothing to redo)"
        if self.canRedo:
            index = (self.index + 1) if self.index is not None else 0
            description = self.commands[index].description
        self.can_redo.emit(self.canRedo, description)


    def clear(self):
        self.commands.clear()
        self.index = None
        self._notify()


    @property
    def isRedoMacro(self):
        if not self.canRedo:
            return False
        index = (self.index + 1) if self.index is not None else 0
        return isinstance(self.commands[index], Macro)


    @property
    def canRedo(self):
        return bool(self.commands and (self.index is None or
                                       self.index < len(self.commands) - 1))


    def getRedo(self):
        if not self.canRedo:
            raise Error("no command to redo")
        self.index = (self.index + 1) if self.index is not None else 0
        command = self.commands[self.index]
        self._notify()
        return command


    @property
    def isUndoMacro(self):
        if not self.canUndo:
            return False
        return isinstance(self.commands[self.index], Macro)


    @property
    def canUndo(self):
        return self.index is not None


    def getUndo(self):
        if not self.canUndo:
            raise Error("no command to undo")
        command = self.commands[self.index]
        self.index -= 1
        if self.index < 0:
            self.index = None
        self._notify()
        return command


    def __len__(self):
        return len(self.commands)


class Command:

    def __init__(self):
        self.description = None


    def do(self):
        raise NotImplementedError

    undo = do


    def __str__(self):
        return "{} {}".format(self.__class__.__name__, self.description)


class Macro:

    def __init__(self, description=None):
        self._commands = []
        self.description = description


    def append(self, command):
        if not isinstance(command, Command):
            raise TypeError("Expected object of type Command, got {}".
                            format(type(command).__name__))
        self._commands.append(command)


    def do_sequence(self): # Caller must provide transaction control
        for command in self._commands:
            yield command


    def undo_sequence(self): # Caller must provide transaction control
        for command in reversed(self._commands):
            yield command


    def __str__(self):
        return "Macro\n\t" + "\n\t".join(str(cmd) for cmd in self._commands)
