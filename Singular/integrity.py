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
from . import exceptions

class Integrity:
    @staticmethod
    def check():
        """
        Check the integrity of the system
        """
        # Bypass the integrity check if test mode is enabled
        if declarations.status.testMode: return
        # Check that the dynamic data are the same that the ones in memory
        ## Check configs
        dataPathStatus = declarations.dynamicConfig.dataPath.get() != declarations.staticConfig.dataPath
        minerAddressStatus = declarations.dynamicConfig.minerAddress.get() != declarations.staticConfig.minerAddress
        multiprocessingMiningStatus = declarations.dynamicConfig.multiprocessingMining.get() != declarations.miningConfig.multiprocessingMining
        ## Check network configs
        networkNameStatus = declarations.networkConfig.name.get() != declarations.chainConfig.name
        networkBootstrapIPStatus = declarations.networkConfig.bootstrapIP.get() != declarations.chainConfig.bootstrapIP
        networkMagicIDStatus = declarations.networkConfig.magicID.get() != declarations.chainConfig.magicID
        networkMaxSupplyStatus = declarations.networkConfig.maxSupply.get() != declarations.chainConfig.maxSupply
        networkBlockMaxRewardStatus = declarations.networkConfig.blockMaxReward.get() != declarations.chainConfig.blockMaxReward
        networkRewardNameStatus = declarations.networkConfig.rewardName.get() != declarations.chainConfig.rewardName
        networkMaxAmountStatus = declarations.networkConfig.maxAmount.get() != declarations.chainConfig.maxAmount
        networkMinDiffStatus = declarations.networkConfig.minDiff.get() != declarations.miningConfig.minDiff
        networkMaxDiffStatus = declarations.networkConfig.maxDiff.get() != declarations.miningConfig.maxDiff
        networkTestNetStatus = declarations.networkConfig.testNet.get() != declarations.chainConfig.testNet
        # Check all the status
        if dataPathStatus or minerAddressStatus or multiprocessingMiningStatus or networkNameStatus or networkBootstrapIPStatus or networkMagicIDStatus or networkMaxSupplyStatus or networkBlockMaxRewardStatus or networkRewardNameStatus or networkMaxAmountStatus or networkMinDiffStatus or networkMaxDiffStatus or networkTestNetStatus:
            if not (networkMinDiffStatus or networkMaxDiffStatus and declarations.debugConfig.debug):
                    exceptions.Exceptions.Compromised("Inconsistent constant status", True)
        # Check the integrity of the settings
        if declarations.staticConfig.minerAddress == "": exceptions.Exceptions.Compromised("Miner address Is unset, you can set one with the -m argument", True)
        if declarations.miningConfig.minDiff < 1 or declarations.miningConfig.minDiff > 32: exceptions.Exceptions.Compromised("Network's minDiff Is too low or too high", True)
        if declarations.miningConfig.maxDiff < 1 or declarations.miningConfig.maxDiff > 32: exceptions.Exceptions.Compromised("Network's maxDiff Is too low or too high", True)
        if declarations.chainConfig.maxAmount < declarations.chainConfig.blockMaxReward: exceptions.Exceptions.Compromised("Network's blockMaxReward Is higher than the maxAmount", True)
        if declarations.chainConfig.maxSupply == declarations.chainConfig.blockMaxReward: exceptions.Exceptions.Compromised("Network's max supply and max reward are the same", True)
        # Get the last block for further checks
        lastBlock = manager.Manager.chainMan.getChain()
        # Check If the last blockMagicID Is the same as networkMagicID
        if lastBlock is not None and lastBlock.get(mapping.Block.networkMagicID) != declarations.chainConfig.magicID: exceptions.Exceptions.Compromised("The last block saved hasn't got the same networkMagicID as the set", True)
        # Check that the rewardName in the database is the same as the established in the network config
        try:
            if lastBlock.get(mapping.Block.transactions)[0].get(mapping.Transactions.sender) != declarations.chainConfig.rewardName: exceptions.Exceptions.Compromised("Network's rewardName It's different than the rewardName In the first transaction of the last block", True)
        except (AttributeError, IndexError): pass
        return
