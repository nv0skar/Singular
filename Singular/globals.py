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

from . import mapping

__name__ = "SingularNode"
__version__ = "0.0.1"
__protocolVersion__ = 1
__url__ = "https://github.com/ItsTheGuy/Singular"

# Default network constants
defaultNetwork = {
    mapping.Network.name: "mainSpace",
    mapping.Network.bootstrapIP: "",
    mapping.Network.magicID: "tLnAENVf5oN59ZcfCCPWShmzhLdgNvHZ1eib",
    mapping.Network.maxSupply: 10000000000,
    mapping.Network.blockMaxReward: 20,
    mapping.Network.rewardName: "bigBang",
    mapping.Network.maxAmount: 1000,
    mapping.Network.minDiff: 4,
    mapping.Network.maxDiff: 32,
    mapping.Network.testNet: True
}

# Default networking constants
defaultNetworking = {
    mapping.Networking.port: 1004
}
