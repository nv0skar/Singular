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

import multiprocessing
from . import declarations
from . import mapping
from . import chain
from . import block
from . import transaction
from . import p2p
from . import storage
from . import integrity
from . import helper
from . import endpoint
from . import frontend

class Manager:
    class chainMan:
        @staticmethod
        def getHeight() -> int:
            """
            Get the height of the chain
            This function Is on top of the getHeight function in Storage.
            """
            return int(storage.Storage.chainMan.getLength())

        @staticmethod
        def clearChain():
            """
            Delete the chain from the database
            This function Is on top of the clearChain function in Storage.
            """
            try:
                storage.Storage.chainMan.clearChain()
                return True
            except (declarations.helpers.baseExceptions): return False

        @staticmethod
        def getChain(blockNumber=None):
            """
            Get the chain or at least the last block.
            This function Is on top of the getBlock function in Storage.
            """
            return storage.Storage.chainMan.getBlock(blockNumber)

        @staticmethod
        def addToChain(blockToAdd, verify=True, addReward=False, reward=0, clean=False):
            """
            Add the block to the chain.
            This function Is on top of the saveBlock function in Storage.
            """
            try:
                # Check if the blockNumber of the block to add Is already taken by a block In the chain
                for blockCheckNumber in range(Manager.chainMan.getHeight()):
                    blockCheck = Manager.chainMan.getChain(blockCheckNumber)
                    if blockCheck.get(mapping.Block.blockNumber) == blockToAdd.get(mapping.Block.blockNumber): return False
                # Verify the block
                if verify:
                    if block.utils.verify(blockToAdd.get(mapping.Block.blockNumber), blockToAdd.get(mapping.Block.transactions), blockToAdd.get(mapping.Block.time), blockToAdd.get(mapping.Block.nonce), blockToAdd.get(mapping.Block.miner), blockToAdd.get(mapping.Block.minerTime), blockToAdd.get(mapping.Block.hash), blockToAdd.get(mapping.Block.protocolVersion)) is True:
                        # Remove confirmed transactions from memPool
                        if clean: Manager.memPool.removeFromPool(clean=True)
                        # Add the reward to the memPool
                        if addReward and not reward <= 0: Manager.memPool.addToPool(transaction.utils.rewardTransactionComposer(blockToAdd.get(mapping.Block.miner), reward), True)
                        # Mark a block as saved
                        declarations.status.mine.newBlockMined = True
                        # Save the block
                        storage.Storage.chainMan.saveBlock(blockToAdd)
                        return True
                    else: helper.report("Chain manager", "Block verification failed"); return False
                else:
                    # Remove confirmed transactions from memPool
                    if clean: Manager.memPool.removeFromPool(clean=True)
                    # Add the reward to the memPool
                    if addReward and not reward <= 0: Manager.memPool.addToPool(transaction.Transaction(declarations.chainConfig.rewardName, blockToAdd.get(mapping.Block.miner), reward, "Unnecessary!").get(), True)
                    # Mark a block as saved
                    declarations.status.mine.newBlockMined = True
                    # Save the block
                    storage.Storage.chainMan.saveBlock(block)
                    return True
            except (AttributeError, TypeError) as e:
                helper.report("Chain manager", e)
                return False

    class nodesMan:
        @staticmethod
        def addNode(node):
            """
            Add node to the nodes list.
            This function Is on top of the addNode function in Storage.savedNodes.
            """
            try:
                storage.Storage.nodesMan.addNode(node)
                return True
            except (declarations.helpers.baseExceptions): return False

        @staticmethod
        def removeNode(nodeNumber):
            """
            Remove node from the nodes list.
            This function Is on top of the removeNode function in Storage.savedNodes.
            """
            try:
                storage.Storage.nodesMan.removeNode(nodeNumber)
                return True
            except (declarations.helpers.baseExceptions): return False

        @staticmethod
        def getNodes():
            """
            Get nodes to the nodes list.
            This function Is on top of the getNodes function in Storage.savedNodes.
            """
            return storage.Storage.nodesMan.getNodes()

        @staticmethod
        def clearNodes():
            """
            Delete the nodes in the database
            This function Is on top of the clearNodes function in Storage.
            """
            try:
                storage.Storage.nodesMan.clearNodes()
                return True
            except (declarations.helpers.baseExceptions): return False

    class protocol:
        @staticmethod
        def loop(graphical=False):
            """
            Initialize routine.
            """
            # Check integrity
            integrity.Integrity.check()
            # Get the height of the chain, and check if there are any blocks. If doesn't, ask to start a new chain
            try:
                if (int(Manager.chainMan.getHeight()) == 0) and (not bool(frontend.Frontend.dialogs.startChain())): exit()
            except (declarations.helpers.baseExceptions): declarations.helpers.printer.sprint("main", "There was an error while checking the the chain height. Chain height check was performed to ask if should start a new chain.")
            # Start the server
            endpoint.Endpoint.init()
            # TODO - Sync the chain, and not continue until there is no error
            # Initialize
            while True:
                routine = Manager.protocol.go()
                if routine is not False:
                    if graphical: frontend.Frontend.dialogs.blockMined(routine)

        @staticmethod
        def p2p():
            """
            Run p2p process
            """
            # Define process
            p2pProcess = multiprocessing.Process(target=p2p.p2p.start)
            # Set daemon as True to avoid the KeyboardInterrupt exception to not be handled
            p2pProcess.daemon = True
            # Run process
            p2pProcess.start()

        @staticmethod
        def go():
            """
            Request unconfirmed transactions from another blocks, fetches nodes.
            Get unconfirmed transactions, and make blocks to mine.
            When mining Is completed share the proof (Mined block).
            """
            # Check integrity
            integrity.Integrity.check()
            # TODO - Fetch new blocks
            # Check
            # TODO - Fetch unconfirmed transactions
            # Get unconfirmed transactions
            unconfirmedTransacts = Manager.memPool.getFromPool()
            # Generate block
            blockToMine = block.Block(unconfirmedTransacts)
            # Mine block
            minedBlock, rewardMiner = chain.Chain.mine(blockToMine, autoCleanMemPool=False)
            # Check If block was mined or not
            if minedBlock is False:
                return False
            # Send proof other miners and get the consensus
            # TODO - Implement networking
            nodesConsensus = True
            # Remove confirmed transactions of memPool, reward the miner, and add block to the chain If the consensus Is reached
            if nodesConsensus:
                # Add to the chain
                Manager.chainMan.addToChain(minedBlock, addReward=True, reward=rewardMiner, clean=True)
                return minedBlock
            return False

    class memPool:
        @staticmethod
        def getFromPool():
            """
            Get all the unconfirmed transactions.
            This function Is on top of the getFromPool function in Storage.memPool
            """
            return declarations.databases.memPool.getFromPool()

        @staticmethod
        def addToPool(transactionToAdd, bigBangAdd=False):
            """
            Add unconfirmed transaction.
            This function Is on top of the addToPool function in Storage.memPool
            """
            # Before adding, if the sender is the reward name check out if the amount is valid
            if transactionToAdd.get(mapping.Transactions.sender) == str(declarations.chainConfig.rewardName) or transactionToAdd.get(mapping.Transactions.receiver) == str(declarations.chainConfig.rewardName):
                if not bigBangAdd: return False
            try: declarations.databases.memPool.addToPool(transactionToAdd); return True
            except (declarations.helpers.baseExceptions): return False

        @staticmethod
        def removeFromPool(clean=False, transactionToRemove=None):
            """
            Remove unconfirmed transaction.
            This function Is on top of the removeFromPool function in Storage.memPool
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
            transactions = Manager.wallet.getTransactions(str(wallet))
            # Now calculate the balance
            for walletTransaction in transactions:
                # If the wallet is the sender rest the amount of transaction and if it's the receiver sum the amount of transaction
                if walletTransaction.get(mapping.Transactions.sender) == wallet:
                    balance -= walletTransaction.get(mapping.Transactions.amount)
                elif walletTransaction.get(mapping.Transactions.receiver) == wallet:
                    balance += walletTransaction.get(mapping.Transactions.amount)
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
            for blockNumber in range(Manager.chainMan.getHeight()):
                blockCheck = Manager.chainMan.getChain(blockNumber)
                for trans in blockCheck.get(mapping.Block.transactions):
                    if (trans.get(mapping.Transactions.sender) == wallet) or (trans.get(mapping.Transactions.receiver) == wallet):
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
            transactionObject = transaction.Transaction(sender, receiver, realAmount, signature, time)
            # Check If the transaction could be added to the memPool
            if not transactionObject.check(): return False
            # Append object to the chain
            Manager.memPool.addToPool(transactionObject.get())
            return True
