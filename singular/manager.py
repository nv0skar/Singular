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

from . import declarations
from . import mapping
from . import chain
from . import block
from . import transaction
from . import formulae
from . import integrity
from . import endpoint
# from . import startpoint
from . import network
from . import helper
from . import frontend

class manager:
    class main:
        @staticmethod
        def loop(graphical=False):
            """
            Initialize routine.
            """
            # Check integrity
            integrity.integrity.check()
            # Check if the miner endpoint is in the chain
            if not network.network.check.am_I_in_the_chain() and not declarations.miningConfig.mining and not helper.debugging.status(): helper.reporter.compromised("Cannot initialize without mining mode if the node's endpoint address is not in the chain.", True)
            # Get the height of the chain, and check if there are any blocks. If doesn't, ask to start a new chain
            try:
                if (int(manager.chainMan.getHeight()) == 0) and declarations.miningConfig.mining:
                    if not bool(frontend.frontend.dialogs.startChain()): exit()
            except (declarations.helpers.baseExceptions): helper.reporter.report("main", "There was an error while checking the the chain height. Chain height check was performed to ask if should start a new chain.", level=declarations.helpers.messageLevelTypes.critical); exit()
            # Sync the chain
            # if not helper.debugging.status(): startpoint.startpoint.sync()
            # Start the server
            endpoint.endpoint.init()
            # Initialize mining
            while bool(declarations.miningConfig.mining):
                routine = manager.main.go()
                if routine is not False:
                    if graphical: frontend.frontend.dialogs.blockMined(routine)

        @staticmethod
        def go():
            """
            Request unconfirmed transactions from another blocks, fetches nodes.
            Get unconfirmed transactions, and make blocks to mine.
            When mining Is completed share the proof (Mined block).
            """
            # Check integrity
            integrity.integrity.check()
            # Manually sync chain if the address is not known to other nodes
            # if not helper.debugging.status():
            #    if not network.network.check.am_I_in_the_chain() and str(declarations.config.minerEndpoint) != str(declarations.chainConfig.initEndpoint): startpoint.startpoint.sync()
            # Get unconfirmed transactions
            unconfirmedTransacts = manager.memPool.getFromPool()
            # Generate block
            blockToMine = block.block(unconfirmedTransacts)
            # Mine block
            minedBlock, rewardMiner = chain.chain.mine(blockToMine, autoCleanMemPool=False)
            # Check If block was mined or not
            if minedBlock is False:
                return False
            # Check if debug mode or test mode is enabled before sending block to other nodes
            if not helper.debugging.status(): 
                # consensus = startpoint.startpoint.spread(minedBlock) # Send block other nodes and get the consensus
                # if not consensus: helper.reporter.report("networking", "Consensus wasn't reached so the mined block won't be added to the chain", level=declarations.helpers.messageLevelTypes.warning)
                consensus = True
            else: consensus = True
            # Remove confirmed transactions of memPool, reward the miner, and add block to the chain If the consensus Is reached
            if consensus:
                manager.chainMan.addToChain(minedBlock, addReward=True, reward=rewardMiner, clean=True) # Add block to the chain
                return minedBlock
            return False

    class chainMan:
        @staticmethod
        def getHeight() -> int:
            """
            Get the height of the chain
            This function Is on top of the getHeight function in Storage.
            """
            return int(declarations.databases.chainDB.getLength())

        @staticmethod
        def clearChain():
            """
            Delete the chain from the database
            This function Is on top of the clearChain function in Storage.
            """
            try:
                declarations.databases.chainDB.clearChain()
                return True
            except (declarations.helpers.baseExceptions): return False

        @staticmethod
        def getChain(blockNumber=None):
            """
            Get the chain or at least the last block.
            This function Is on top of the getBlock function in Storage.
            """
            return declarations.databases.chainDB.getBlock(blockNumber)

        @staticmethod
        def addToChain(blockToAdd:dict, verify=True, addReward=False, reward=0, clean=False):
            """
            Add the block to the chain.
            This function Is on top of the saveBlock function in Storage.
            """
            try:
                # Check if the blockNumber of the block to add Is already taken by a block in the chain
                for blockCheckNumber in range(manager.chainMan.getHeight()):
                    blockCheck = manager.chainMan.getChain(blockCheckNumber)
                    if blockCheck.get(mapping.block.blockNumber) == blockToAdd.get(mapping.block.blockNumber):
                        helper.reporter.report("chain manager", "Unable to add block: A block with the same height is already in the chain (Block number: {}; Hash: {})".format(blockToAdd.get(mapping.block.blockNumber), blockToAdd.get(mapping.block.hash)), level=declarations.helpers.messageLevelTypes.warning); return False
                # Verify the block
                if bool(verify):
                    if not block.utils.verify(blockToAdd.get(mapping.block.blockNumber), blockToAdd.get(mapping.block.transactions), blockToAdd.get(mapping.block.time), blockToAdd.get(mapping.block.nonce), blockToAdd.get(mapping.block.minerAddress), blockToAdd.get(mapping.block.minerEndpoint), blockToAdd.get(mapping.block.minerTime), blockToAdd.get(mapping.block.hash), blockToAdd.get(mapping.block.protocolVersion)):
                        helper.reporter.report("chain manager", "Block verification failed (Block number: {}; Hash: {})".format(blockToAdd.get(mapping.block.blockNumber), blockToAdd.get(mapping.block.hash)), level=declarations.helpers.messageLevelTypes.warning); return False
                # Remove confirmed transactions from memPool
                if clean: manager.memPool.removeFromPool(clean=True)
                # Add the reward to the memPool
                if addReward:
                    if reward <= 0: reward = formulae.formulae.calculateReward(blockToAdd.get(mapping.block.transactions), blockToAdd.get(mapping.block.blockNumber))
                    manager.memPool.addToPool(transaction.utils.rewardTransactionComposer(blockToAdd.get(mapping.block.minerAddress), reward), True)
                # Mark that a new block is going to be saved
                declarations.status.miner.newBlock = True
                # Save the block
                declarations.databases.chainDB.saveBlock(blockToAdd)
                helper.reporter.report("chain manager", "Block added! (Block number: {}; Hash: {})".format(blockToAdd.get(mapping.block.blockNumber), blockToAdd.get(mapping.block.hash)))
                return True
            except (AttributeError, TypeError) as e:
                helper.reporter.report("chain manager", e)
                return False

    class nodesMan:
        @staticmethod
        def getNodes():
            """
            Retrieve nodes from the chain
            This function is on top of the getNodes function in Storage.nodesMan
            """
            return declarations.databases.nodesDB.getNodes()

    class memPool:
        @staticmethod
        def getFromPool():
            """
            Get all the unconfirmed transactions.
            This function is on top of the getFromPool function in Storage.memPool
            """
            return declarations.databases.memPool.getFromPool()

        @staticmethod
        def addToPool(transactionToAdd, bigBangAdd=False):
            """
            Add unconfirmed transaction.
            This function is on top of the addToPool function in Storage.memPool
            """
            # Before adding, if the sender is the reward name check out if the amount is valid
            if transactionToAdd.get(mapping.transactions.sender) == str(declarations.chainConfig.rewardName) or transactionToAdd.get(mapping.transactions.receiver) == str(declarations.chainConfig.rewardName):
                if not bigBangAdd: return False
            try: declarations.databases.memPool.addToPool(transactionToAdd); return True
            except (declarations.helpers.baseExceptions): return False

        @staticmethod
        def removeFromPool(clean=False, transactionToRemove=None):
            """
            Remove unconfirmed transaction.
            This function is on top of the removeFromPool function in Storage.memPool
            """
            # Check If have to clean all the memPool
            if clean: declarations.databases.memPool.clearPool(); return True
            else: declarations.databases.memPool.removeFromPool(transactionToRemove)

    class wallet:
        @staticmethod
        def getBalance(wallet):
            """
            Get the balance of a wallet based on the transactions
            """
            # Define a var to save the balance
            balance = 0
            # Get all the transactions that the sender or the receiver is the wallet
            transactions = manager.wallet.getTransactions(str(wallet))
            # Now calculate the balance
            for walletTransaction in transactions:
                # If the wallet is the sender rest the amount of transaction and if it's the receiver sum the amount of transaction
                if walletTransaction.get(mapping.transactions.sender) == wallet:
                    balance -= walletTransaction.get(mapping.transactions.amount)
                elif walletTransaction.get(mapping.transactions.receiver) == wallet:
                    balance += walletTransaction.get(mapping.transactions.amount)
            # Return balance
            return balance

        @staticmethod
        def getTransactions(wallet):
            """
            Get all the transactions of a wallet
            """
            # Define a list to append the transactions that the requested wallet have done
            transactions = []
            # Get all the transactions that the sender or the receiver is the wallet
            for blockNumber in range(manager.chainMan.getHeight()):
                blockCheck = manager.chainMan.getChain(blockNumber)
                for trans in blockCheck.get(mapping.block.transactions):
                    if (trans.get(mapping.transactions.sender) == wallet) or (trans.get(mapping.transactions.receiver) == wallet):
                        transactions.append(trans)
            # Return all the transactions
            return transactions

        @staticmethod
        def transaction(sender, receiver, realAmount, signature, time):
            """
            Generate a transaction by appending it to the unconfirmed transactions list
            """
            # Check If the sender or the receiver Is the reward name
            if sender == declarations.chainConfig.rewardName or receiver == declarations.chainConfig.rewardName: return False
            # Make transaction object
            transactionObject = transaction.transaction(sender, receiver, realAmount, signature, time)
            # Check If the transaction could be added to the memPool
            if not transactionObject.check(): return False
            # Append object to the chain
            manager.memPool.addToPool(transactionObject.get())
            return True
