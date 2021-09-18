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
from . import mapping
from . import helper
import requests
import json

class startpoint:
    @staticmethod
    def spread(block: dict) -> bool:
        """
        Send the mined block to all the peers in the database
        """
        # Get the nodes from the database
        nodes = manager.manager.nodesMan.getNodes()
        # Count the nodes in the database
        nodesCounter = int(len(nodes))
        # Count the nodes that accepted the block
        accepted = 0
        # For each node send the block
        for node in nodes:
            status = startpoint.api.utils.send.block(node.get(mapping.nodes.endpoint), dict(block))
            if status: accepted += 1
            elif status is None: nodesCounter -= 1 # If a node was asked and an error happened remove subtract a node from the nodes counter
        # Count the success rate
        if (accepted != 0) and (nodesCounter != 0): 
            success = float(accepted/nodesCounter)
            consensus = ((True) if (success >= float(0.5)) else (False))
        else: 
            success = float(0)
            if (str(declarations.config.minerEndpoint) != str(declarations.chainConfig.initEndpoint)): consensus = False
            else: consensus = True
        # Report the success rate
        helper.reporter.report("networking", "Block sent to the registered peers with a rate of success of {}%".format(str(float(success*100))))
        return bool(consensus)

    @staticmethod
    def sync(block=None):
        """
        Sync the chain
        """
        # If a block is not passed, get the latest block from the bootstrap node
        if block is None:
             # Check if there is any node to ask
            if str(startpoint.api.utils.retrieve.whoToAsk()) == "": helper.reporter.report("networking", "There is no available node to sync from", level=declarations.helpers.messageLevelTypes.warning); return False
            # Retrieve block
            nodeToRetrieveFrom = str(startpoint.api.utils.retrieve.whoToAsk())
            block = startpoint.api.utils.retrieve.block(str(nodeToRetrieveFrom), True)
            if not block: helper.reporter.report("networking", "Couldn't sync chain from: {}".format(nodeToRetrieveFrom), level=declarations.helpers.messageLevelTypes.warning); return False
            # Check if the retrieved block is the next block in the local chain
            if not startpoint.api.syncMissingBlocks(block): return False
            # Add the block to the chain
            if not manager.manager.chainMan.addToChain(block, True, True): helper.reporter.report("networking", "Couldn't add the block retrieved from: {}".format(nodeToRetrieveFrom), level=declarations.helpers.messageLevelTypes.warning); return False
            else: return True
        else:
            # Check if the passed block is the next block in the local chain
            if not startpoint.api.syncMissingBlocks(block): return False
            # Add the block to the chain
            if not manager.manager.chainMan.addToChain(block, True, True): helper.reporter.report("networking", "Couldn't add the block received", level=declarations.helpers.messageLevelTypes.warning); return False
            else: return True

    class api:
        @staticmethod
        def syncMissingBlocks(passedBlock=None):
            """
            Sync missing blocks of the local chain
            The blocks will be retrieved from the node that mined the last block in the local chain, if there aren't any blocks in the local chain retrieve the blocks from the bootstrap node.
            """
            # Check if there is any node to ask
            if str(startpoint.api.utils.retrieve.whoToAsk()) == "": helper.reporter.report("networking", "There is no available node to sync from", level=declarations.helpers.messageLevelTypes.warning); return True
            latestBlockNumber = int((startpoint.api.utils.retrieve.block(str(startpoint.api.utils.retrieve.whoToAsk()), True).get(mapping.block.blockNumber)) if passedBlock is None else (passedBlock.get(mapping.block.blockNumber)))
            if (int(latestBlockNumber) >= int(manager.manager.chainMan.getHeight()-1)):
                # Retrieve blocks
                for blockNumber in range(int(manager.manager.chainMan.getHeight()), int(latestBlockNumber+1)):
                    nodeToRetrieveFrom = str(startpoint.api.utils.retrieve.whoToAsk())
                    retrievedBlock = startpoint.api.utils.retrieve.block(str(nodeToRetrieveFrom), False, blockNumber)
                    print(retrievedBlock)
                    # Check the retrieved block
                    if not retrievedBlock: helper.reporter.report("networking", "Couldn't sync missing chain blocks from: {}".format(str(nodeToRetrieveFrom)), level=declarations.helpers.messageLevelTypes.warning); return False
                    # Add the block to the chain
                    alreadyInChain = False
                    for blockNumberCheck in range(0, int(manager.manager.chainMan.getHeight()-1)):
                        blockCheck = manager.manager.chainMan.getChain(blockNumberCheck)
                        if int(blockCheck.get(mapping.block.blockNumber)) == int(blockNumber): alreadyInChain = True
                    if not alreadyInChain:
                        if not manager.manager.chainMan.addToChain(retrievedBlock, True, True): helper.reporter.report("networking", "Couldn't add the block retrieved from: {}".format(nodeToRetrieveFrom), level=declarations.helpers.messageLevelTypes.warning); return False
            else: helper.reporter.report("networking", "Chain already up-to date")

        class utils:
            class retrieve:
                @staticmethod
                def whoToAsk() -> str:
                    """
                    Get if the blocks should be synced from the last block's node miner or from the bootstrap node
                    """
                    selectedNode:str = ""
                    if int(manager.manager.chainMan.getHeight()) != 0:
                        if int(manager.manager.chainMan.getHeight()) != 1:
                            for blockNumber in reversed(range(0, int(manager.manager.chainMan.getHeight()-1))):
                                block = manager.manager.chainMan.getChain(blockNumber)
                                if not (str(block.get(mapping.block.minerEndpoint)) == str(declarations.config.minerEndpoint)): 
                                    selectedNode = str(manager.manager.chainMan.getChain().get(mapping.block.minerEndpoint))
                                    break
                        else:
                            block = manager.manager.chainMan.getChain(0)
                            if not (str(block.get(mapping.block.minerEndpoint)) == str(declarations.config.minerEndpoint)): 
                                selectedNode = str(manager.manager.chainMan.getChain().get(mapping.block.minerEndpoint))
                    else: selectedNode = str((declarations.chainConfig.initEndpoint) if str(declarations.chainConfig.initEndpoint) != str(declarations.config.minerEndpoint) else str(""))
                    return str(selectedNode)

                @staticmethod
                def block(endpoint:str, latest:bool, blockNumber=0):
                    """
                    Retrieve block from a given endpoint
                    """
                    try:
                        response = requests.get("{}{}{}".format(str(mapping.networking.api.protocol), str(endpoint), "{}{}".format(mapping.networking.api.node.get.block, "/{}".format("latest" if latest else str(blockNumber)))), headers=({"content-type":"application/json"}))
                        if (type(int(response.json().get("blockNumber"))) is int) and (response.status_code == 200): return dict(response.json())
                    except (declarations.helpers.networkingExceptions):
                        helper.reporter.report("networking", "Couldn't retrieve block from: {}".format(str(endpoint)), level=declarations.helpers.messageLevelTypes.warning); return False

            class send:
                @staticmethod
                def block(endpoint:str, data:dict):
                    """
                    Send block to a given endpoint
                    """
                    try:
                        response = requests.post("{}{}{}".format(str(mapping.networking.api.protocol), str(endpoint), mapping.networking.api.node.add.block), data=json.dumps(dict(data)), headers=({"content-type":"application/json"}))
                        if (dict(response.json()).get("status") == "success") and (response.status_code == 200): return True
                        elif (dict(response.json()).get("status") == "failed") and (response.status_code == 400): return False
                        else:
                            helper.reporter.report("networking", "An unexpected response was obtained while sending a block to: {}".format(str(endpoint)), level=declarations.helpers.messageLevelTypes.warning)
                            return None
                    except (declarations.helpers.networkingExceptions):
                        helper.reporter.report("networking", "An error occured while trying to send a block to: {}".format(str(endpoint)), level=declarations.helpers.messageLevelTypes.warning)
                        return None
