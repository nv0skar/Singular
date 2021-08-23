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
from . import integrity
import nanoid

class Network:
    class config:
        @staticmethod
        def setup(netName, netBootstrapIP, netMagicID, netMaxSupply, netMaxAmount, netBlockMaxReward, netRewardName, netMinDiff, netMaxDiff, testNet):
            """
            Setup a new network
            """
            # Check If the values are valid
            try:
                if not (((type(netName) is str) and ((type(netBootstrapIP) is str) or (type(netBootstrapIP) is None)) and (type(float(netMaxSupply)) is float) and (type(float(netMaxAmount)) is float) and (type(float(netBlockMaxReward)) is float) and (type(int(netMinDiff)) is int) and (type(int(netMaxDiff)) is int) and (type(bool(testNet)) is bool) and (int(netMinDiff) > 0 and int(netMaxDiff) < 33))):
                    return str("The types of some value weren't valid")
                if float(netMaxAmount) > float(netMaxSupply):
                    return str("The max amount cannot be higher than the max supply")
                if float(netMaxSupply) == float(netBlockMaxReward):
                    return str("The max supply and the max reward cannot be the same")
            except GeneratorExit: return str("The types of some value weren't valid")
            if float(netMaxAmount) < float(netBlockMaxReward): return str("blockMaxReward Is higher than the maxAmount")
            # Set the values
            # Set networkName
            if str(declarations.chainConfig.name) != str(netName) and netName is not None: declarations.networkConfig.name.set(str(netName))
            # Set networkBootstrapIP
            if str(declarations.chainConfig.bootstrapIP) != str(netBootstrapIP): declarations.networkConfig.bootstrapIP.set(str(netBootstrapIP))
            # Set networkMagicID
            if str(declarations.chainConfig.magicID) != str(netMagicID): declarations.networkConfig.magicID.set(str(netMagicID) if netMagicID != "{generate}" else str(nanoid.generate(size=36)))
            # Set networkMaxSupply
            if str(declarations.chainConfig.maxSupply) != str(netMaxSupply): declarations.networkConfig.maxSupply.set(float(netMaxSupply))
            # Set networkMaxAmount
            if str(declarations.chainConfig.maxAmount) != str(netMaxAmount): declarations.networkConfig.maxAmount.set(float(netMaxAmount))
            # Set networkBlockMaxReward
            if str(declarations.chainConfig.blockMaxReward) != str(netBlockMaxReward): declarations.networkConfig.blockMaxReward.set(float(netBlockMaxReward))
            # Set networkRewardName
            if str(declarations.chainConfig.rewardName) != str(netRewardName): declarations.networkConfig.rewardName.set(str(netRewardName))
           # Set networkMinDiff
            if str(declarations.miningConfig.minDiff) != str(netMinDiff): declarations.networkConfig.minDiff.set(int(netMinDiff))
            # Set networkMaxDiff
            if str(declarations.miningConfig.maxDiff) != str(netMaxDiff): declarations.networkConfig.maxDiff.set(int(netMaxDiff))
            # Set testNet
            if bool(declarations.chainConfig.testNet) != bool(testNet): declarations.networkConfig.testNet.set(bool(testNet))
            # Network setup completed at this point
            return True

        @staticmethod
        def getConf(bypassIntegrity=False) -> dict:
            """
            Get the network configuration
            """
            # Run integrity check
            if not bypassIntegrity: integrity.Integrity.check()
            # Return data
            return dict(name=declarations.chainConfig.name, bootstrapIP=declarations.chainConfig.bootstrapIP, magicID=declarations.chainConfig.magicID, maxSupply=declarations.chainConfig.maxSupply, maxAmount=declarations.chainConfig.maxAmount, blockMaxReward=declarations.chainConfig.blockMaxReward, rewardName=declarations.chainConfig.rewardName, minDiff=declarations.miningConfig.minDiff, maxDiff=declarations.miningConfig.maxDiff, testNet=declarations.chainConfig.testNet)
