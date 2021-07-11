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

from time import time as getTime
from . import declarations
from . import manager
from . import transaction
from . import formulae
from . import helper
import hashlib

class Block:
    def __init__(self, transactions):
        self.blockNumber = 0
        self.lastBlockHash = str("0" * 64)
        self.transactions = transactions
        self.difficulty = declarations.miningConfig.minDiff
        self.nonce = 0
        self.miner = None
        self.time = getTime()
        self.minerTime = None
        self.protocolVersion = declarations.protocolVersion
        self.networkMagicNumber = declarations.chainConfig.magicNumber

    def hashBlock(self):
        """
        Hashes the current block
        """
        hashComposer = str("({}-{}-{}-{}-{}-{}-{})@{}-{}-{}".format(self.blockNumber,self.lastBlockHash,self.transactions,self.difficulty,self.nonce,self.time,self.minerTime,self.miner,self.protocolVersion,self.networkMagicNumber))
        blockHash = hashlib.sha256()
        blockHash.update(str(hashComposer).encode("utf-8"))
        return blockHash.hexdigest()


    def get(self):
        """
        Returns the blocks list
        """
        return {
            "blockNumber": self.blockNumber,
            "lastBlockHash": self.lastBlockHash,
            "transactions": self.transactions,
            "difficulty": self.difficulty,
            "nonce": self.nonce,
            "miner": self.miner,
            "time": self.time,
            "minerTime": self.minerTime,
            "hash": self.hashBlock(),
            "protocolVersion": self.protocolVersion,
            "networkMagicNumber": self.networkMagicNumber
        }

class utils:
    @staticmethod
    def verify(blockNumber, transactions, time, nonce, miner, minerTime, expectedHash, protocolVersion):
        """
        Verifies the integrity of a block
        """
        # Verify the transactions
        for trans in transactions:
            # Define transaction object
            transactionObject = transaction.Transaction(trans.get("sender"), trans.get("receiver"), trans.get("realAmount"), trans.get("signature"), trans.get("time"))
            # Check transaction
            if not transactionObject.check(True):
                # The block integrity was compromised!
                return False
        # Makes a new block with the data of the fetched one
        reconstructor = Block(transactions)
        # Set the blockNumber
        reconstructor.blockNumber = int(blockNumber)
        # Set the time of the block
        reconstructor.time = time
        # Stage 1 - Set the miner address as the miner who mined the block
        reconstructor.miner = miner
        # Stage 2 - Prepare transactions transactions to be added to the block
        reconstructor.transactions = transaction.utils.prepare(reconstructor.transactions, True)
        try:
            # Stage 3 - Get the previous block hash, and set protocol
            reconstructor.protocolVersion = protocolVersion
            reconstructor.lastBlockHash = str("0" * 64)
            for blockNumberSaved in range(manager.Manager.chainMan.getHeight()):
                block = manager.Manager.chainMan.getChain(blockNumberSaved)
                if block.get("blockNumber") == (blockNumber-1): reconstructor.lastBlockHash = block.get("hash")
            # Stage 4 - Set difficulty
            lastBlockAmount = 0
            # Add the amount of the block to lastBlockAmount
            for trans in reconstructor.transactions:
                lastBlockAmount += trans.get("realAmount")
            # Calculate difficulty
            try: reconstructor.difficulty = formulae.Formulae.calculateDifficulty(reconstructor.lastBlockHash, (lastBlockAmount if lastBlockAmount != 0 else declarations.miningConfig.minDiff), formulae.Formulae.calculateReward(reconstructor.transactions, reconstructor.blockNumber))
            except (AttributeError, ZeroDivisionError, TypeError): reconstructor.difficulty = declarations.miningConfig.minDiff
            # Checks If the blocks difficulty Is None type
            if type(reconstructor.difficulty) is None: reconstructor.difficulty = declarations.miningConfig.minDiff
        except (AttributeError, TypeError):
            # If there Is a AttributeError or a TypeError Is because this may be the first block In the chain
            reconstructor.lastBlockHash = str("0" * 64)
            reconstructor.blockNumber = 0
            reconstructor.difficulty = declarations.miningConfig.minDiff
        # Stage 5 - Set the miner time
        reconstructor.minerTime = minerTime
        # Stage 6 - Set the nonce
        reconstructor.nonce = nonce
        # Compare the block hash of the reconstructor with the expected hash
        if reconstructor.hashBlock() == expectedHash: return True # The block integrity Is correct
        else: return False # The block integrity was compromised!

    @staticmethod
    def prepare(blockData):
        """
        Prepare the block to be mined
        """
        # Stage 1 - Set the miner address as the miner who mined the block
        blockData.miner = declarations.staticConfig.minerAddress
        # Stage 2 - Prepare transactions transactions to be added to the block
        blockData.transactions = transaction.utils.prepare(blockData.transactions)
        if type(manager.Manager.chainMan.getChain()) is dict and type(manager.Manager.chainMan.getHeight()) is int:
            # Stage 3 - Get the previous block hash and block number
            blockData.lastBlockHash = manager.Manager.chainMan.getChain().get("hash")
            blockData.blockNumber = int(manager.Manager.chainMan.getHeight())
            # Stage 4 - Set difficulty
            lastBlockAmount = 0
            # Add the amount of the block to lastBlockAmount
            for trans in blockData.transactions:
                lastBlockAmount += trans.get("realAmount")
            # Calculate difficulty
            try: blockData.difficulty = formulae.Formulae.calculateDifficulty(manager.Manager.chainMan.getChain().get("hash"), (lastBlockAmount if lastBlockAmount != 0 else declarations.miningConfig.minDiff), formulae.Formulae.calculateReward())
            except (AttributeError, ZeroDivisionError, TypeError): blockData.difficulty = declarations.miningConfig.minDiff
            # Checks If the blocks difficulty Is None type
            if type(blockData.difficulty) is None: blockData.difficulty = declarations.miningConfig.minDiff
        else:
            # Announce that the first block In the chain Is about to be mined If debug is activated
            if declarations.debugConfig.debug: helper.report("main", "First block in the chain is about to be mined!")
            blockData.lastBlockHash = str("0" * 64)
            blockData.blockNumber = 0
            blockData.difficulty = declarations.miningConfig.minDiff
        # Return the prepared block
        return blockData
