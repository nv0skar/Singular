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
from . import path
from . import exceptions
import numpy as np
import rocksdb

class Database:
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
                    if debugStatus is not bool(declarations.debugConfig.debug): exceptions.Exceptions.Compromised("Global debug status and {} database debug status doesn't match, however, you could try changing the path of the chain and nodes databases or maybe deleting the contents of the databases by passing the --clear argument".format(calledFrom), True)
                else: db.put(str(debugValueKey).encode(), str(bool(declarations.debugConfig.debug)).encode())
            except (AttributeError, TypeError):
                db.put(str(debugValueKey).encode(), str(bool(declarations.debugConfig.debug)).encode())

    class chain:
        def __init__(self):
            self.__staticKeys = dict(chainLengthValueKey="chainLength", debugValueKey="debug")
            try:
                path.Path.preparePath(str(declarations.staticConfig.dataPath["chain"]))
                self.db = rocksdb.DB(str(declarations.staticConfig.dataPath["chain"]), rocksdb.Options(create_if_missing=True))
            except (rocksdb.errors.RocksIOError): exceptions.Exceptions.Compromised("For some reason the chain's lock file is temporarily unavailable", True)
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
            Database.commons.debugChecker(self.db, self.__staticKeys.get("debugValueKey"), "chain")
            self.db.put(str(block.get(mapping.Block.blockNumber)).encode(), str(block).encode())
            if int(block.get(mapping.Block.blockNumber)) == int(self.chainLength): self.__lastBlock = block
            self.__lengthManager(1 if int(block.get(mapping.Block.blockNumber)) == int(self.chainLength) else None)
            return True

        def remove(self, blockNumber):
            """
            Remove a block
            When a block is removed the chainLength doesn't decrement.
            """
            Database.commons.debugChecker(self.db, self.__staticKeys.get("debugValueKey"), "chain")
            self.db.delete(str(int(blockNumber)).encode())
            self.__lengthManager()
            return True

        def get(self, blockNumber=None):
            """
            Get blocks
            """
            Database.commons.debugChecker(self.db, self.__staticKeys.get("debugValueKey"), "chain")
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

    class nodes:
        def __init__(self):
            self.__staticKeys = dict(nodesNumberValueKey="nodesNumber", debugValueKey="debug")
            try:
                path.Path.preparePath(str(declarations.staticConfig.dataPath["nodes"]))
                self.db = rocksdb.DB(str(declarations.staticConfig.dataPath["nodes"]), rocksdb.Options(create_if_missing=True))
            except (rocksdb.errors.RocksIOError): exceptions.Exceptions.Compromised("For some reason the node's lock file is temporarily unavailable", True)
            self.nodesNumber = self.__numberManager(init=True)

        def __numberManager(self, operation=None, init=False):
            """
            Increment the number of nodes
            """
            if operation is not None and self.nodesNumber is not None:
                self.db.put(str(self.__staticKeys.get("nodesNumberValueKey")).encode(), str(int(self.nodesNumber + (1))).encode())
                if not init: self.nodesNumber = int(self.nodesNumber + (1))
            else:
                try:
                    length = int(bytes(self.db.get(str(self.__staticKeys.get("nodesNumberValueKey")).encode())).decode())
                    if not init: self.nodesNumber = int(length)
                    return int(length)
                except (TypeError, ValueError):
                    return int(0)

        def add(self, node):
            """
            Add a new node
            """
            Database.commons.debugChecker(self.db, self.__staticKeys.get("debugValueKey"), str("nodes"))
            self.db.put(str(self.nodesNumber).encode(), str(node).encode())
            self.__numberManager(1)
            return True

        def remove(self, nodeNumber):
            """
            Remove a node
            When a node is removed the nodesNumber doesn't decrement.
            """
            Database.commons.debugChecker(self.db, self.__staticKeys.get("debugValueKey"), str("nodes"))
            self.db.delete(str(nodeNumber).encode())
            self.__numberManager()
            return True

        def get(self):
            """
            Get nodes
            """
            Database.commons.debugChecker(self.db, self.__staticKeys.get("debugValueKey"), str("nodes"))
            nodes = np.array([ast.literal_eval(bytes(self.db.get(str(int(nodeNumber)).encode())).decode()) for nodeNumber in range(self.nodesNumber)], dict)
            return nodes

        def clear(self):
            """
            Clear the nodes
            """
            self.db.delete(str(self.__staticKeys.get("nodesNumberValueKey")).encode())
            self.db.delete(str(self.__staticKeys.get("debugValueKey")).encode())
            for node in range(self.__numberManager()):
                self.db.delete(str(int(node)).encode())
