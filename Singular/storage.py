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

from . import declarations
import numpy as np

class Storage:
    class chainMan:
        @staticmethod
        def saveBlock(block):
            """
            Saves block to chain
            """
            declarations.databases.chainDB.add(block)

        @staticmethod
        def getBlock(blockNumber=None):
            """
            Return last block. If all Is True, will return all the chain.
            """
            try:
                if blockNumber is not None: return dict(declarations.databases.chainDB.get(blockNumber))
                else: return dict(declarations.databases.chainDB.get(declarations.databases.chainDB.chainLength-1))
            except (AttributeError, TypeError): return None

        @staticmethod
        def clearChain():
            """
            Delete the chain from the database
            """
            declarations.databases.chainDB.clear()
            return True

        @staticmethod
        def getLength():
            """
            Get the length of the chain
            """
            return (declarations.databases.chainDB.chainLength)

    class nodesMan:
        @staticmethod
        def addNode(node):
            """
            Add a new node to the nodes list
            """
            declarations.databases.nodesDB.add(node)

        @staticmethod
        def removeNode(nodeNumber):
            """
            Remove node from the list
            """
            declarations.databases.nodesDB.remove(nodeNumber)

        @staticmethod
        def getNodes():
            """
            Get nodes in the list
            """
            return (declarations.databases.nodesDB.get())

        @staticmethod
        def clearNodes():
            """
            Delete the nodes in the database
            """
            declarations.databases.nodesDB.clear()
            return True

    class memPool:
        def __init__(self):
            self.unconfirmedTransact = np.array([])

        def addToPool(self, transaction):
            """
            Add transaction to the memPool
            """
            self.unconfirmedTransact = np.concatenate([self.unconfirmedTransact, np.array([transaction])])

        def removeFromPool(self, transaction):
            """
            Remove transaction from the memPool
            """
            remainingTransactions = np.array([])
            for trans in self.unconfirmedTransact:
                if dict(trans) != dict(transaction): remainingTransactions = np.concatenate([remainingTransactions, trans])
            self.unconfirmedTransact = remainingTransactions

        def getFromPool(self):
            """
            Get all the unconfirmed transactions from memPool
            """
            return self.unconfirmedTransact

        def clearPool(self):
            """
            Delete all transactions from memPool
            """
            self.unconfirmedTransact = np.array([])
            return True
