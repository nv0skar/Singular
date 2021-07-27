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

import os
import base64
from . import declarations
from . import manager
from . import block
from . import chain
from . import transaction
from . import database
from . import helper
import nacl.signing, nacl.exceptions
from rich.prompt import Prompt

class Test:
    @staticmethod
    def blockGenerator(passMemPool):
        """
        This will create a new block, mine the block, and finally add the block to the temporal chain
        """
        # Create a new block
        declarations.helpers.printer.sprint("test", "Creating a new empty block")
        bruteBlock = block.Block(manager.Manager.memPool.getFromPool() if passMemPool else [])
        # Mine the block
        declarations.helpers.printer.sprint("test", "Mining the block")
        minedBlock, rewardMiner = chain.Chain.mine(bruteBlock)
        # Add block to the temporal chain
        declarations.helpers.printer.sprint("test", "Adding block to the temporal chain")
        manager.Manager.chainMan.addToChain(minedBlock, addReward=True, reward=rewardMiner, clean=True)
        return rewardMiner

    @staticmethod
    def performTests():
        """
        This will perform the tests to check the correct functionality
        """
        # Activate debug mode
        helper.enableDebug()
        # Activate test mode
        declarations.status.testMode = True
        # Declarations
        addresses = []
        # Ask for temporal databases path
        chainPathTmp = Prompt.ask("Temporal database chain path", default=str("{}/{}".format(os.path.dirname(__file__), str("tests/chain/"))))
        nodesPathTmp = Prompt.ask("Temporal database nodes path", default=str("{}/{}".format(os.path.dirname(__file__), str("tests/nodes/"))))
        # Set the temporal databases path
        declarations.helpers.printer.sprint("test", "Setting the chain and node temporal path")
        declarations.staticConfig.dataPath["chain"] = str(chainPathTmp)
        declarations.staticConfig.dataPath["nodes"] = str(nodesPathTmp)
        # Delete the networkMagicNumber
        declarations.chainConfig.magicNumber = "testMode"
        # Set the rewardName
        declarations.chainConfig.rewardName = "test"
        # Redeclare the databases objects to make the new path take effect
        declarations.helpers.printer.sprint("test", "Reinitializing databases managers")
        declarations.databases.chainDB = database.Database.chain()
        declarations.databases.nodesDB = database.Database.nodes()
        # Generate 2 addresses
        declarations.helpers.printer.sprint("test", "Generating 2 addresses")
        for _ in range(2):
            privateKey = nacl.signing.SigningKey.generate()
            publicKey = privateKey.verify_key
            addresses.append(dict(pubKey=str(publicKey), encodedPubKey=base64.b16encode(eval(str(publicKey))), privKey=str(privateKey), object=privateKey))
        # Set the miner address
        declarations.helpers.printer.sprint("test", "Setting '{}' as the new miner address".format(str(addresses[0].get("encodedPubKey").decode())))
        declarations.staticConfig.minerAddress = str(addresses[0].get("encodedPubKey").decode())
        # Generate a new block
        rewardMiner = Test.blockGenerator(False)
        # Generate a new block
        Test.blockGenerator(True)
        # Compose transaction
        declarations.helpers.printer.sprint("test", "Composing new transaction from '{}' to '{}'".format(str(addresses[0].get("encodedPubKey").decode()), str(addresses[1].get("encodedPubKey").decode())))
        transaction1 = transaction.Transaction(str(addresses[0].get("encodedPubKey").decode()), str(addresses[1].get("encodedPubKey").decode()), float(rewardMiner/2))
        # Sign transaction
        declarations.helpers.printer.sprint("test", "Sign transaction")
        verificationKey = base64.b16encode(bytes(addresses[0].get("object").sign(str(transaction1.compose()).encode()).signature))
        # Issue transaction to the another address
        declarations.helpers.printer.sprint("test", "Issuing transaction")
        manager.Manager.wallet.transaction(addresses[0].get("encodedPubKey").decode(), addresses[1].get("encodedPubKey").decode(), float(rewardMiner/2), verificationKey, transaction1.time)
        # Generate a new block
        Test.blockGenerator(True)
        # Check if the transaction was added
        declarations.helpers.printer.sprint("test", "Checking if the transaction was added")
        lastBlockAdded = manager.Manager.chainMan.getChain()
        madeTransactionLastBlockAdded = lastBlockAdded.get("transactions")[1]
        if madeTransactionLastBlockAdded.get("sender") == str(addresses[0].get("encodedPubKey").decode()) and madeTransactionLastBlockAdded.get("receiver") == str(addresses[1].get("encodedPubKey").decode()):
                    declarations.helpers.printer.sprint("test", "Transaction in the chain")
        else: declarations.helpers.printer.sprint("test", "Tests weren't passed! Reason: Transaction weren't in the chain"); return
        # Check if the reward transactions were duplicated
        if (lastBlockAdded.get("transactions")[0].get("sender") == str(declarations.chainConfig.rewardName)) and (lastBlockAdded.get("transactions")[1].get("sender") != str(declarations.chainConfig.rewardName)):
            declarations.helpers.printer.sprint("test", "Reward transaction not duplicated")
        else: declarations.helpers.printer.sprint("test", "Tests weren't passed! Reason: Reward transaction duplicated"); return
        declarations.helpers.printer.sprint("test", "Tests successfully passed!")
