# Singular
# Copyright (C) 2021 ItsTheGuy
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import ast
from distutils.util import strtobool
from . import declarations
from . import mapping
from . import helper
import numpy as np
import rocksdb

class database:
    class commons:
        @staticmethod
        def debugChecker(db, debugValueKey, calledFrom):
            """
            Check the debug status of the database passed
            Also if the debug status of the database passed and the global debug status doesn't match, this will raise an integrity exception.
            """
            try:
                debugStatus = bool(strtobool(bytes(db.get(str(debugValueKey).encode())).decode()))
                if debugStatus is not None:
                    if debugStatus is not bool(helper.debugging.status()): helper.reporter.compromised("Global debug status and {} database debug status doesn't match, however, you could try changing the path of the chain and nodes databases or maybe deleting the contents of the databases by passing the 'data --clear' argument".format(calledFrom), True)
                else: db.put(str(debugValueKey).encode(), str(bool(helper.debugging.status())).encode())
            except (AttributeError, TypeError):
                db.put(str(debugValueKey).encode(), str(bool(helper.debugging.status())).encode())

    class chain:
        def __init__(self):
            self.__staticKeys = dict(chainLengthValueKey="chainLength", debugValueKey="debug")
            try:
                self.db = rocksdb.DB(str(helper.path.preparePath(str(declarations.config.dbPath))), rocksdb.Options(create_if_missing=True))
            except (rocksdb.errors.RocksIOError): helper.reporter.compromised("For some reason the chain's lock file is temporarily unavailable. Maybe another Singular instance is using the same database.", True)
            self.chainLength = self.__lengthManager(init=True); self.__lastBlock = None

        def __lengthManager(self, operation=None, init=False):
            """
            Increment the length of the chain
            """
            if operation is not None and self.chainLength is not None:
                self.db.put(str(self.__staticKeys.get("chainLengthValueKey")).encode(), str(int(self.chainLength+(1))).encode())
                if not init: self.chainLength = int(self.chainLength+(1))
            else:
                try:
                    length = int(bytes(self.db.get(str(self.__staticKeys.get("chainLengthValueKey")).encode())).decode())
                    if not init: self.chainLength = int(length)
                    return int(length)
                except (TypeError, ValueError): return int(0)

        def add(self, block):
            """
            Add a new block
            """
            database.commons.debugChecker(self.db, self.__staticKeys.get("debugValueKey"), "chain")
            self.db.put(str(block.get(mapping.block.blockNumber)).encode(), str(block).encode())
            if int(block.get(mapping.block.blockNumber)) == int(self.chainLength): self.__lastBlock = block
            self.__lengthManager(1 if int(block.get(mapping.block.blockNumber)) == int(self.chainLength) else None)
            return True

        def remove(self, blockNumber):
            """
            Remove a block
            When a block is removed the chainLength doesn't decrement.
            """
            database.commons.debugChecker(self.db, self.__staticKeys.get("debugValueKey"), "chain")
            self.db.delete(str(int(blockNumber)).encode())
            self.__lengthManager()
            return True

        def get(self, blockNumber=None):
            """
            Get blocks
            """
            database.commons.debugChecker(self.db, self.__staticKeys.get("debugValueKey"), "chain")
            try:
                if blockNumber == (self.chainLength-1) and self.__lastBlock is not None: return self.__lastBlock
                else: return ast.literal_eval(bytes(self.db.get(str(int(blockNumber)).encode())).decode())
            except (AttributeError, TypeError): return None

        def clear(self):
            """
            Clear the chain
            """
            self.db.delete(str(self.__staticKeys.get("chainLengthValueKey")).encode())
            self.db.delete(str(self.__staticKeys.get("debugValueKey")).encode())
            for block in range(self.__lengthManager()):
                self.db.delete(str(int(block)).encode())
