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

class integrity:
    @staticmethod
    def check():
        """
        Check the integrity of the system
        """
        # Bypass the integrity check if test mode is enabled
        if declarations.status.extras.bypassIntegrityCheck: return
        # Check that the dynamic data are the same that the ones in memory
        ## Check configs
        dataPathStatus = declarations.unsafeConfig.dbPath.get() != declarations.config.dbPath
        minerAddressStatus = declarations.unsafeConfig.minerAddress.get() != declarations.config.minerAddress
        minerEndpointStatus = declarations.unsafeConfig.minerEndpoint.get() != declarations.config.minerEndpoint
        multiprocessingMiningStatus = declarations.unsafeConfig.multiprocessingMining.get() != declarations.miningConfig.multiprocessingMining
        ## Check network configs
        networkNameStatus = declarations.unsafeNetConfig.name.get() != declarations.chainConfig.name
        networkInitEndpointStatus = declarations.unsafeNetConfig.initEndpoint.get() != declarations.chainConfig.initEndpoint
        networkID_Status = declarations.unsafeNetConfig.netID.get() != declarations.chainConfig.netID
        networkMaxSupplyStatus = declarations.unsafeNetConfig.maxSupply.get() != declarations.chainConfig.maxSupply
        networkMaxAmountStatus = declarations.unsafeNetConfig.maxAmount.get() != declarations.chainConfig.maxAmount
        networkMaxRewardStatus = declarations.unsafeNetConfig.maxReward.get() != declarations.chainConfig.maxReward
        networkRewardNameStatus = declarations.unsafeNetConfig.rewardName.get() != declarations.chainConfig.rewardName
        networkMinDiffStatus = declarations.unsafeNetConfig.minDiff.get() != declarations.miningConfig.minDiff
        networkMaxDiffStatus = declarations.unsafeNetConfig.maxDiff.get() != declarations.miningConfig.maxDiff
        networkTestNetStatus = declarations.unsafeNetConfig.testNet.get() != declarations.chainConfig.testNet
        # Check all the status
        if dataPathStatus or minerAddressStatus or minerEndpointStatus or multiprocessingMiningStatus or networkNameStatus or networkInitEndpointStatus or networkID_Status or networkMaxSupplyStatus or networkMaxAmountStatus or networkMaxRewardStatus or networkRewardNameStatus or networkMinDiffStatus or networkMaxDiffStatus or networkTestNetStatus:
            if not (networkMinDiffStatus or networkMaxDiffStatus and helper.debugging.status()): helper.reporter.compromised("Inconsistent constant status", True)
        # Check the integrity of the settings
        if str(declarations.config.minerAddress) == "": helper.reporter.compromised("Node's address is unset, you can set one with the 'config -mA'/'config --minerAddress' argument", True)
        if str(declarations.config.minerEndpoint) == "": helper.reporter.compromised("Node's endpoint address is unset, you can set one with the 'config -mE'/'config --minerEndpoint' argument", True)
        if declarations.miningConfig.minDiff < 1 or declarations.miningConfig.minDiff > 32: helper.reporter.compromised("Network's minDiff Is too low or too high", True)
        if declarations.miningConfig.maxDiff < 1 or declarations.miningConfig.maxDiff > 32: helper.reporter.compromised("Network's maxDiff Is too low or too high", True)
        if declarations.chainConfig.maxAmount < declarations.chainConfig.maxReward: helper.reporter.compromised("Network's maxReward Is higher than the maxAmount", True)
        if declarations.chainConfig.maxSupply == declarations.chainConfig.maxReward: helper.reporter.compromised("Network's max supply and max reward are the same", True)
        if str(declarations.chainConfig.initEndpoint) == "" or str(declarations.chainConfig.initEndpoint) == "": helper.reporter.compromised("The initial node's address or endpoint's address is missing", True)
        # Check the endpoint's address integrity
        try: _, _ = helper.networking.segmentEndpointAddress(str(declarations.config.minerEndpoint))
        except (declarations.helpers.baseExceptions): helper.reporter.compromised("The endpoint's address is not valid. Check that follows the following format: IP:PORT", True)
        # Get the last block for further checks
        lastBlock = manager.manager.chainMan.getChain()
        # Check if the last block's network's ID is the same as the node's network ID
        if lastBlock is not None and str(lastBlock.get(mapping.block.netID)) != str(declarations.chainConfig.netID): helper.reporter.compromised("The last block saved hasn't got the same netID as the set", True)
        # Check if the last block's difficulty is within the config's min diff and max diff
        if lastBlock is not None:
            if int(lastBlock.get(mapping.block.difficulty)) > int(declarations.miningConfig.maxDiff) or int(lastBlock.get(mapping.block.difficulty)) < int(declarations.miningConfig.minDiff):
                helper.reporter.compromised("The last block's difficulty higher than the configured max difficulty or lower than the configured minimum difficulty", True)
        # Check that the rewardName in the database is the same as the established in the network config
        try:
            if str(lastBlock.get(mapping.block.transactions)[0].get(mapping.transactions.sender)) != str(declarations.chainConfig.rewardName): helper.reporter.compromised("Network's rewardName It's different than the rewardName In the first transaction of the last block", True)
        except (AttributeError, IndexError): pass
        return
