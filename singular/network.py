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
from . import manager
from . import integrity
from . import mapping
import nanoid

class network:
    class check:
        @staticmethod
        def am_I_in_the_chain() -> bool:
            """
            Check if the node's endpoint address is in the chain
            """
            for blockNumber in range(0, manager.manager.chainMan.getHeight()):
                blockData = manager.manager.chainMan.getChain(blockNumber)
                if str(declarations.config.minerEndpoint) == str(blockData.get(mapping.block.minerEndpoint)): return True
                return False

    class config:
        @staticmethod
        def setup(netName, netInitEndpoint, netID, netMaxSupply, netMaxAmount, netMaxReward, netRewardName, netMinDiff, netMaxDiff, testNet):
            """
            Setup a new network
            """
            # Check If the values are valid
            try:
                if not (((type(netName) is str) and (type(netInitEndpoint) is str) and (type(float(netMaxSupply)) is float) and (type(float(netMaxAmount)) is float) and (type(float(netMaxReward)) is float) and (type(int(netMinDiff)) is int) and (type(int(netMaxDiff)) is int) and (type(bool(testNet)) is bool) and (int(netMinDiff) > 0 and int(netMaxDiff) < 33))):
                    return str("The types of some value weren't valid")
                if float(netMaxAmount) > float(netMaxSupply):
                    return str("The max amount cannot be higher than the max supply")
                if float(netMaxSupply) == float(netMaxReward):
                    return str("The max supply and the max reward cannot be the same")
            except GeneratorExit: return str("The types of some value weren't valid")
            if float(netMaxAmount) < float(netMaxReward): return str("maxReward is higher than the maxAmount")
            # Set the values
            # Set networkName
            if str(declarations.chainConfig.name) != str(netName) and netName is not None: declarations.unsafeNetConfig.name.set(str(netName))
            # Set netInitEndpoint
            if str(declarations.chainConfig.initEndpoint) != str(netInitEndpoint): declarations.unsafeNetConfig.initEndpoint.set(str(netInitEndpoint))
            # Set netID
            if str(declarations.chainConfig.netID) != str(netID): declarations.unsafeNetConfig.netID.set(str(netID) if netID != "{generate}" else str(nanoid.generate(size=36)))
            # Set networkMaxSupply
            if str(declarations.chainConfig.maxSupply) != str(netMaxSupply): declarations.unsafeNetConfig.maxSupply.set(float(netMaxSupply))
            # Set networkMaxAmount
            if str(declarations.chainConfig.maxAmount) != str(netMaxAmount): declarations.unsafeNetConfig.maxAmount.set(float(netMaxAmount))
            # Set networkMaxReward
            if str(declarations.chainConfig.maxReward) != str(netMaxReward): declarations.unsafeNetConfig.maxReward.set(float(netMaxReward))
            # Set networkRewardName
            if str(declarations.chainConfig.rewardName) != str(netRewardName): declarations.unsafeNetConfig.rewardName.set(str(netRewardName))
           # Set networkMinDiff
            if str(declarations.miningConfig.minDiff) != str(netMinDiff): declarations.unsafeNetConfig.minDiff.set(int(netMinDiff))
            # Set networkMaxDiff
            if str(declarations.miningConfig.maxDiff) != str(netMaxDiff): declarations.unsafeNetConfig.maxDiff.set(int(netMaxDiff))
            # Set testNet
            if bool(declarations.chainConfig.testNet) != bool(testNet): declarations.unsafeNetConfig.testNet.set(bool(testNet))
            # Network setup completed at this point
            return True

        @staticmethod
        def getConf(bypassIntegrity=False) -> dict:
            """
            Get the network configuration
            """
            # Run integrity check
            if not bypassIntegrity: integrity.integrity.check()
            # Return data
            return {mapping.network.name:declarations.chainConfig.name, mapping.network.initEndpoint:declarations.chainConfig.initEndpoint, mapping.network.netID:declarations.chainConfig.netID, mapping.network.maxSupply:declarations.chainConfig.maxSupply, mapping.network.maxAmount:declarations.chainConfig.maxAmount, mapping.network.maxReward:declarations.chainConfig.maxReward, mapping.network.rewardName:declarations.chainConfig.rewardName, mapping.network.minDiff:declarations.miningConfig.minDiff, mapping.network.maxDiff:declarations.miningConfig.maxDiff, mapping.network.testNet:declarations.chainConfig.testNet}
