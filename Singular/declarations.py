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
from . import database
from . import storage
from . import miner
import mars
import superPrinter

# Network constants
defaultNetwork = dict(globals.defaultNetwork)

# Info
info = dict(version=str(globals.__version__), url=str(globals.__url__))
nodeAgent = "SingularNode@V{}".format(str(globals.__version__))
protocolVersion = int(globals.__protocolVersion__)

# Declarations
files = dict(config="config.plist", networkConfig="network.json", chain="data/chain", nodes="data/nodes")

# Configs helpers
configHelper = mars.generate(str("{}/{}".format(os.path.dirname(__file__), files["config"])), mars.types.plist)
networkConfigHelper = mars.generate(str("{}/{}".format(os.path.dirname(__file__), files["networkConfig"])), mars.types.json)

# Config
class dynamicConfig:
    dataPath = mars.element("dataPath", dict(chain=str("{}/{}".format(os.path.dirname(__file__), files["chain"][1:] if files["chain"][0] == "/" else files["chain"])), nodes=str("{}/{}".format(os.path.dirname(__file__), files["nodes"][1:] if files["nodes"][0] == "/" else files["nodes"]))), configHelper)
    minerAddress = mars.element("minerAddress", "", configHelper)
    multiprocessingMining = mars.element("multiProcessingMining", True, configHelper)

class debugConfig:
    debug = False
    minDiff_debug = 1
    maxDiff_debug = 1

class staticConfig:
    dataPath = dict(dynamicConfig.dataPath.get())
    minerAddress = str(dynamicConfig.minerAddress.get())

# Network config
class networkConfig:
    name = mars.element("name", defaultNetwork.get("name"), networkConfigHelper)
    bootstrapIP = mars.element("bootstrapIP", defaultNetwork.get("bootstrapIP"), networkConfigHelper)
    magicNumber = mars.element("magicNumber", defaultNetwork.get("magicNumber"), networkConfigHelper)
    maxSupply = mars.element("maxSupply", defaultNetwork.get("maxSupply"), networkConfigHelper)
    blockMaxReward = mars.element("blockMaxReward", defaultNetwork.get("blockMaxReward"), networkConfigHelper)
    rewardName = mars.element("rewardName", defaultNetwork.get("rewardName"), networkConfigHelper)
    maxAmount = mars.element("maxAmount", defaultNetwork.get("maxAmount"), networkConfigHelper)
    minDiff = mars.element("minDiff", defaultNetwork.get("minDiff"), networkConfigHelper)
    maxDiff = mars.element("maxDiff", defaultNetwork.get("maxDiff"), networkConfigHelper)
    testNet = mars.element("testNet", defaultNetwork.get("testNet"),  networkConfigHelper)

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
    magicNumber = str(networkConfig.magicNumber.get())
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

# Status
class status:
    mine = miner.Miner.status()
    testMode = False
