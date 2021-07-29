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
import multiprocessing
from . import globals
from . import mapping
from . import database
from . import storage
from . import miner
import mars
import superPrinter

# Core info
class core:
    name = str(globals.__name__)
    version = str(globals.__version__)
    protocolVersion = str(globals.__protocolVersion__)
    url = str(globals.__url__)
    agent = "{}@v{}".format(str(name), str(protocolVersion))
    class networking: defaultPort = globals.defaultNetworking.get("port")

# Declarations
files = dict(config="config.plist", networkConfig="network.json", chain="data/chain", nodes="data/nodes")

# Configs helpers
configHelper = mars.generate(str("{}/{}".format(os.path.dirname(__file__), files["config"])), mars.types.plist)
networkConfigHelper = mars.generate(str("{}/{}".format(os.path.dirname(__file__), files["networkConfig"])), mars.types.json)

# Config
class dynamicConfig:
    dataPath = mars.element(mapping.Commons.dataPath, dict(chain=str("{}/{}".format(os.path.dirname(__file__), files["chain"][1:] if files["chain"][0] == "/" else files["chain"])), nodes=str("{}/{}".format(os.path.dirname(__file__), files["nodes"][1:] if files["nodes"][0] == "/" else files["nodes"]))), configHelper)
    minerAddress = mars.element(mapping.Commons.minerAddress, "", configHelper)
    multiprocessingMining = mars.element(mapping.Commons.multiprocessingMining, True, configHelper)

class debugConfig:
    debug = False
    minDiff_debug = 1
    maxDiff_debug = 1

class staticConfig:
    dataPath = dict(dynamicConfig.dataPath.get())
    minerAddress = str(dynamicConfig.minerAddress.get())

# Network config
class networkConfig:
    name = mars.element(mapping.Network.name, globals.defaultNetwork.get(mapping.Network.name), networkConfigHelper)
    bootstrapIP = mars.element(mapping.Network.bootstrapIP, globals.defaultNetwork.get(mapping.Network.bootstrapIP), networkConfigHelper)
    magicID = mars.element(mapping.Network.magicID, globals.defaultNetwork.get(mapping.Network.magicID), networkConfigHelper)
    maxSupply = mars.element(mapping.Network.maxSupply, globals.defaultNetwork.get(mapping.Network.maxSupply), networkConfigHelper)
    blockMaxReward = mars.element(mapping.Network.blockMaxReward, globals.defaultNetwork.get(mapping.Network.blockMaxReward), networkConfigHelper)
    rewardName = mars.element(mapping.Network.rewardName, globals.defaultNetwork.get(mapping.Network.rewardName), networkConfigHelper)
    maxAmount = mars.element(mapping.Network.maxAmount, globals.defaultNetwork.get(mapping.Network.maxAmount), networkConfigHelper)
    minDiff = mars.element(mapping.Network.minDiff, globals.defaultNetwork.get(mapping.Network.minDiff), networkConfigHelper)
    maxDiff = mars.element(mapping.Network.maxDiff, globals.defaultNetwork.get(mapping.Network.maxDiff), networkConfigHelper)
    testNet = mars.element(mapping.Network.testNet, globals.defaultNetwork.get(mapping.Network.testNet),  networkConfigHelper)

# Databases
class databases:
    # The databases manager won't load if the process is not the main
    if str(multiprocessing.current_process().name) == "MainProcess":
        chainDB = database.Database.chain()
        nodesDB = database.Database.nodes()
        memPool = storage.Storage.memPool()

# Chain constants
class chainConfig:
    name = str(networkConfig.name.get())
    bootstrapIP = str(networkConfig.bootstrapIP.get())
    magicID = str(networkConfig.magicID.get())
    maxSupply = int(networkConfig.maxSupply.get())
    blockMaxReward = int(networkConfig.blockMaxReward.get())
    rewardName = str(networkConfig.rewardName.get())
    maxAmount = int(networkConfig.maxAmount.get())
    testNet = bool(networkConfig.testNet.get())

# Mining config
class miningConfig:
    multiprocessingMining = bool(dynamicConfig.multiprocessingMining.get())
    minDiff = int(networkConfig.minDiff.get())
    maxDiff = int(networkConfig.maxDiff.get())

# Helpers
class helpers:
    printer, messageLevelTypes = superPrinter.printer(), superPrinter.levels
    baseExceptions = (AttributeError, TypeError, ValueError)

# Status
class status:
    mine = miner.Miner.status()
    walletServer = None
    testMode = False
