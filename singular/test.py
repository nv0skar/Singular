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
from . import mapping
from . import block
from . import chain
from . import transaction
from . import storage
from . import helper
from rich.prompt import Prompt

class test:
    @staticmethod
    def blockGenerator(passMemPool):
        """
        This will create a new block, mine the block, and finally add the block to the temporal chain
        """
        # Create a new block
        declarations.helpers.printer.sprint("test", "Creating a new empty block")
        bruteBlock = block.block(manager.manager.memPool.getFromPool() if passMemPool else [])
        # Mine the block
        declarations.helpers.printer.sprint("test", "Mining the block")
        minedBlock, rewardMiner = chain.chain.mine(bruteBlock)
        # Add block to the temporal chain
        declarations.helpers.printer.sprint("test", "Adding block to the temporal chain")
        manager.manager.chainMan.addToChain(minedBlock, addReward=True, reward=rewardMiner, clean=True)
        return rewardMiner

    @staticmethod
    def performTests():
        """
        This will perform the tests to check the correct functionality
        """
        # Activate debug mode
        helper.debugging.enableDebug()
        # Bypass integrity check
        declarations.status.extras.bypassIntegrityCheck = True
        # Declarations
        addresses = []
        # Ask for temporal databases path
        chainPathTmp = Prompt.ask("Temporal database path", default=str("{}/{}".format(os.path.dirname(__file__), str("tests/"))))
        # Set the temporal database path
        declarations.helpers.printer.sprint("test", "Setting the temporal database path")
        declarations.config.dataPath["chain"] = str(chainPathTmp)
        # Change the miner's address and endpoint's address
        declarations.config.minerAddress = ""
        declarations.config.minerEndpoint = ""
        # Change the netID
        declarations.chainConfig.netID = "testMode"
        # Set the rewardName
        declarations.chainConfig.rewardName = "test"
        # Redeclare the databases objects to make the new path take effect
        declarations.helpers.printer.sprint("test", "Reinitializing chain's database manager")
        declarations.databases.chainDB = storage.storage.chain()
        # Generate 2 addresses
        declarations.helpers.printer.sprint("test", "Generating 2 addresses")
        for _ in range(2):
            publicKey, privateKey = helper.address.generate()
            addresses.append(dict(pubKey=str(publicKey), encodedPubKey=base64.b16encode(eval(str(publicKey))), privKey=str(privateKey), object=privateKey))
        # Set the miner address
        declarations.helpers.printer.sprint("test", "Setting '{}' as the new miner address".format(str(addresses[0].get("encodedPubKey").decode())))
        declarations.config.minerAddress = str(addresses[0].get("encodedPubKey").decode())
        # Generate a new block
        rewardMiner = test.blockGenerator(False)
        # Generate a new block
        test.blockGenerator(True)
        # Compose transaction
        declarations.helpers.printer.sprint("test", "Composing new transaction from '{}' to '{}'".format(str(addresses[0].get("encodedPubKey").decode()), str(addresses[1].get("encodedPubKey").decode())))
        transaction1 = transaction.transaction(str(addresses[0].get("encodedPubKey").decode()), str(addresses[1].get("encodedPubKey").decode()), float(rewardMiner / 2))
        # Sign transaction
        declarations.helpers.printer.sprint("test", "Signing transaction")
        verificationKey = base64.b16encode(bytes(addresses[0].get("object").sign(str(transaction1.compose()).encode()).signature))
        # Issue transaction to the another address
        declarations.helpers.printer.sprint("test", "Issuing transaction")
        manager.manager.wallet.transaction(addresses[0].get("encodedPubKey").decode(), addresses[1].get("encodedPubKey").decode(), float(rewardMiner / 2), verificationKey, transaction1.time)
        # Generate a new block
        test.blockGenerator(True)
        # Check if the transaction was added
        declarations.helpers.printer.sprint("test", "Checking if the transaction was added")
        lastBlockAdded = manager.manager.chainMan.getChain()
        try: madeTransactionLastBlockAdded = lastBlockAdded.get(mapping.block.transactions)[1]
        except (IndexError): declarations.helpers.printer.sprint("test", "Tests weren't passed! Reason: A block wasn't added to the chain"); return
        if not (madeTransactionLastBlockAdded.get(mapping.transactions.sender) == str(addresses[0].get("encodedPubKey").decode()) and madeTransactionLastBlockAdded.get(mapping.transactions.receiver) == str(addresses[1].get("encodedPubKey").decode())):
            declarations.helpers.printer.sprint("test", "Tests weren't passed! Reason: Transaction weren't in the chain"); return
        # Check if the reward transactions were duplicated
        declarations.helpers.printer.sprint("test", "Checking if the reward transaction is duplicated")
        if not ((lastBlockAdded.get(mapping.block.transactions)[0].get(mapping.transactions.sender) == str(declarations.chainConfig.rewardName)) and (lastBlockAdded.get(mapping.block.transactions)[1].get(mapping.transactions.sender) != str(declarations.chainConfig.rewardName))):
            declarations.helpers.printer.sprint("test", "Tests weren't passed! Reason: Reward transaction duplicated"); return
        declarations.helpers.printer.sprint("test", "Tests successfully passed!")
