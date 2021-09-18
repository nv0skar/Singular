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
from . import manager
from . import database
from . import mapping
import hashlib
import numpy as np

class storage:
    class chain:
        def __init__(self):
            self.chain = database.database.chain()

        def saveBlock(self, block):
            """
            Saves block to chain
            """
            self.chain.add(block)

        def getBlock(self, blockNumber=None):
            """
            Return last block. If all Is True, will return all the chain.
            """
            try:
                if blockNumber is not None: return dict(self.chain.get(blockNumber))
                else: return dict(self.chain.get(self.chain.chainLength-1))
            except (AttributeError, TypeError): return None

        def clearChain(self):
            """
            Delete the chain from the database
            """
            self.chain.clear()
            return True

        def getLength(self):
            """
            Get the length of the chain
            """
            return (self.chain.chainLength)

    class nodes:
        def __init__(self):
            self.nodes = np.array([])

        def getNodes(self):
            """
            Get the nodes
            """
            initEndpointListed = False
            for blockNumber in range(0, manager.manager.chainMan.getHeight()):
                addToList = True
                blockData = manager.manager.chainMan.getChain(blockNumber)
                for nodeInList in self.nodes:
                    # Check if the actual node endpoint's address is the initial endpoint's address
                    if str(nodeInList.get(mapping.nodes.endpoint)) == str(declarations.chainConfig.initEndpoint): initEndpointListed = True
                    # Hash the node data in the list
                    nodeInListHash = hashlib.sha256()
                    nodeInListHash.update(str({mapping.nodes.address: nodeInList.get(mapping.block.minerAddress), mapping.nodes.endpoint: nodeInList.get(mapping.block.minerEndpoint)}).encode("utf-8"))
                    # Hash the node data in the block
                    nodeInBlockHash = hashlib.sha256()
                    nodeInBlockHash.update(str({mapping.nodes.address: blockData.get(mapping.block.minerAddress), mapping.nodes.endpoint: blockData.get(mapping.block.minerEndpoint)}).encode("utf-8"))
                    # Compare them
                    if str(nodeInListHash.hexdigest()) == str(nodeInBlockHash.hexdigest()): addToList = False
                # If the node in the block is not in the list, add it
                if addToList:
                    try: np.concatenate([self.nodes, np.array(dict({mapping.nodes.address: blockData.get(mapping.block.minerAddress), mapping.nodes.endpoint: blockData.get(mapping.block.minerEndpoint)}))])
                    except (declarations.helpers.baseExceptions): pass
            # Check if the initialEndpoint is already in the list
            if not initEndpointListed and str(declarations.config.minerEndpoint) != str(declarations.chainConfig.initEndpoint): 
                if self.nodes != []: np.concatenate([self.nodes, np.array(dict({mapping.nodes.address: "", mapping.nodes.endpoint: str(declarations.chainConfig.initEndpoint)}))])
                else: self.nodes = np.array([dict({mapping.nodes.address: "", mapping.nodes.endpoint: str(declarations.chainConfig.initEndpoint)})])
            return self.nodes

    class memPool:
        def __init__(self):
            self.pool = np.array([])

        def addToPool(self, transaction):
            """
            Add transaction to the memPool
            """
            self.pool = np.concatenate([self.pool, np.array([transaction])])

        def removeFromPool(self, transaction):
            """
            Remove transaction from the memPool
            """
            remainingTransactions = np.array([])
            for trans in self.pool:
                if dict(trans) != dict(transaction): remainingTransactions = np.concatenate([remainingTransactions, trans])
            self.pool = remainingTransactions

        def getFromPool(self):
            """
            Get all the unconfirmed transactions from memPool
            """
            return self.pool

        def clearPool(self):
            """
            Delete all transactions from memPool
            """
            self.pool = np.array([])
            return True
