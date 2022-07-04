# Singular
# Copyright (C) 2022 Oscar
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

from time import time as getTime
from . import declarations
from . import manager
from . import mapping
from . import transaction
from . import formulae
from . import helper
import hashlib

class block:
    def __init__(self, transactions):
        self.blockNumber = 0
        self.lastBlockHash = str("0" * 64)
        self.transactions = transactions
        self.difficulty = declarations.miningConfig.minDiff
        self.nonce = 0
        self.minerAddress = None
        self.minerEndpoint = None
        self.time = getTime()
        self.minerTime = None
        self.protocolVersion = declarations.core.protocolVersion
        self.netID = declarations.chainConfig.netID

    def hashBlock(self):
        """
        Hash the current block
        """
        hashComposer = str("({}-{}-{}-{}-{}-{}-{}-{})@{}-{}-{}".format(self.blockNumber, self.lastBlockHash, self.transactions, self.difficulty, self.nonce, self.time, self.minerTime, self.minerAddress, self.minerEndpoint, self.protocolVersion, self.netID))
        blockHash = hashlib.sha256()
        blockHash.update(str(hashComposer).encode("utf-8"))
        return blockHash.hexdigest()

    def get(self):
        """
        Return the block in a dict format
        """
        return {
            mapping.block.blockNumber: self.blockNumber,
            mapping.block.lastBlockHash: self.lastBlockHash,
            mapping.block.transactions: self.transactions,
            mapping.block.difficulty: self.difficulty,
            mapping.block.nonce: self.nonce,
            mapping.block.minerAddress: self.minerAddress,
            mapping.block.minerEndpoint: self.minerEndpoint,
            mapping.block.time: self.time,
            mapping.block.minerTime: self.minerTime,
            mapping.block.hash: self.hashBlock(),
            mapping.block.protocolVersion: self.protocolVersion,
            mapping.block.netID: self.netID
        }

class utils:
    @staticmethod
    def verify(blockNumber, transactions, time, nonce, minerAddress, minerEndpoint, minerTime, expectedHash, protocolVersion):
        """
        Verify the integrity of a block
        """
        # Verify the transactions
        for trans in transactions:
            # Define transaction object
            transactionObject = transaction.transaction(trans.get(mapping.transactions.sender), trans.get(mapping.transactions.receiver), trans.get(mapping.transactions.realAmount), trans.get(mapping.transactions.signature), trans.get(mapping.transactions.time))
            # Check transaction
            if not transactionObject.check(True): return False # The block integrity was compromised!
        # Makes a new block with the data of the fetched one
        reconstructor = block(transactions)
        # Set the blockNumber
        reconstructor.blockNumber = int(blockNumber)
        # Set the time of the block
        reconstructor.time = time
        # Stage 1 - Set the miner address and the miner endpoint's address
        reconstructor.minerAddress = minerAddress
        reconstructor.minerEndpoint = minerEndpoint
        # Stage 2 - Prepare transactions to be added to the block
        reconstructor.transactions = transaction.utils.prepare(reconstructor.transactions, False)
        try:
            # Stage 3 - Get the previous block hash, and set protocol
            reconstructor.protocolVersion = protocolVersion
            reconstructor.lastBlockHash = str("0" * 64)
            reconstructor.lastBlockHash = manager.manager.chainMan.getChain(blockNumber - 1).get(mapping.block.hash)
            # Stage 4 - Set difficulty
            # Get the real amount and the number of transactions in the last block
            lastBlockTransactions = 0
            lastBlockRealAmount = 0
            for trans in manager.manager.chainMan.getChain(blockNumber - 1).get(mapping.block.transactions):
                lastBlockTransactions += 1
                lastBlockRealAmount += trans.get(mapping.transactions.realAmount)
            # Calculate difficulty
            try: reconstructor.difficulty = formulae.formulae.calculateDifficulty(lastBlockTransactions, lastBlockRealAmount)
            except (AttributeError, ZeroDivisionError, TypeError): reconstructor.difficulty = declarations.miningConfig.minDiff
            # Checks If the blocks difficulty is None type
            if type(reconstructor.difficulty) is None: reconstructor.difficulty = declarations.miningConfig.minDiff
        except (AttributeError, TypeError):
            # If there Is a AttributeError or a TypeError is because this may be the first block In the chain
            reconstructor.lastBlockHash = str("0" * 64)
            reconstructor.blockNumber = 0
            reconstructor.difficulty = declarations.miningConfig.minDiff
        # Stage 5 - Set the miner time
        reconstructor.minerTime = minerTime
        # Stage 6 - Set the nonce
        reconstructor.nonce = nonce
        # Evaluate the block integrity
        if reconstructor.hashBlock() == expectedHash: return True # The block integrity is correct
        else: return False # The block integrity was compromised!

    @staticmethod
    def prepare(blockData: block):
        """
        Prepare the block to be mined
        """
        # Stage 1 - Set the miner address and the miner endpoint's address
        blockData.minerAddress = declarations.config.minerAddress
        blockData.minerEndpoint = declarations.config.minerEndpoint
        # Stage 2 - Prepare transactions transactions to be added to the block
        blockData.transactions = transaction.utils.prepare(blockData.transactions)
        if type(manager.manager.chainMan.getChain()) is dict and type(manager.manager.chainMan.getHeight()) is int:
            # Stage 3 - Get the previous block hash and block number
            blockData.lastBlockHash = manager.manager.chainMan.getChain().get(mapping.block.hash)
            blockData.blockNumber = int(manager.manager.chainMan.getHeight())
            # Stage 4 - Set difficulty
            # Get the real amount and the number of transactions in the last block
            lastBlockTransactions = 0
            lastBlockRealAmount = 0
            for trans in manager.manager.chainMan.getChain().get(mapping.block.transactions):
                lastBlockTransactions += 1
                lastBlockRealAmount += trans.get(mapping.transactions.realAmount)# Calculate difficulty
            try: blockData.difficulty = formulae.formulae.calculateDifficulty(lastBlockTransactions, lastBlockRealAmount)
            except (AttributeError, ZeroDivisionError, TypeError): blockData.difficulty = declarations.miningConfig.minDiff
            # Checks If the blocks difficulty Is None type
            if type(blockData.difficulty) is None: blockData.difficulty = declarations.miningConfig.minDiff
        else:
            # Announce that the first block In the chain Is about to be mined If debug is activated
            if helper.debugging.status(): helper.reporter.report("main", "First block in the chain is about to be mined!", force=True)
            blockData.lastBlockHash = str("0" * 64)
            blockData.blockNumber = 0
            blockData.difficulty = declarations.miningConfig.minDiff
        # Return the prepared block
        return blockData
