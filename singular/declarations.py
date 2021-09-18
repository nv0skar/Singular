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
import mars
import requests
import superPrinter

# Core info
class core:
    name = str(globals.__name__)
    version = str(globals.__version__)
    protocolVersion = int(globals.__protocolVersion__)
    url = str(globals.__url__)
    agent = "{}@v{}".format(str(name), str(protocolVersion))

# Config files
configFiles = dict(config="config.json", networkConfig="network.json", chain="data/chain")
globalConfigFile = mars.generate(str("{}/{}".format(os.path.dirname(__file__), configFiles["config"])), mars.types.json)
netConfigFile = mars.generate(str("{}/{}".format(os.path.dirname(__file__), configFiles["networkConfig"])), mars.types.json)

# Configs
## Unsafe configs
class unsafeConfig:
    dataPath = mars.element(mapping.commons.dataPath, dict(chain=str("{}/{}".format(os.path.dirname(__file__), configFiles["chain"][1:] if configFiles["chain"][0] == "/" else configFiles["chain"]))), globalConfigFile)
    inform = mars.element(mapping.commons.inform, False, globalConfigFile)
    minerAddress = mars.element(mapping.commons.minerAddress, "", globalConfigFile)
    minerEndpoint = mars.element(mapping.commons.minerEndpoint, "", globalConfigFile)
    mining = mars.element(mapping.commons.mining, True, globalConfigFile)
    multiprocessingMining = mars.element(mapping.commons.multiprocessingMining, False, globalConfigFile)
    timeToCheck = mars.element(mapping.commons.timeToCheck, 4, globalConfigFile)

### Network config
class unsafeNetConfig:
    name = mars.element(mapping.network.name, globals.defaultNetwork.get(mapping.network.name), netConfigFile)
    initAddress = mars.element(mapping.network.initAddress, globals.defaultNetwork.get(mapping.network.initAddress), netConfigFile)
    initEndpoint = mars.element(mapping.network.initEndpoint, globals.defaultNetwork.get(mapping.network.initEndpoint), netConfigFile)
    netID = mars.element(mapping.network.netID, globals.defaultNetwork.get(mapping.network.netID), netConfigFile)
    maxSupply = mars.element(mapping.network.maxSupply, globals.defaultNetwork.get(mapping.network.maxSupply), netConfigFile)
    maxAmount = mars.element(mapping.network.maxAmount, globals.defaultNetwork.get(mapping.network.maxAmount), netConfigFile)
    maxReward = mars.element(mapping.network.maxReward, globals.defaultNetwork.get(mapping.network.maxReward), netConfigFile)
    rewardName = mars.element(mapping.network.rewardName, globals.defaultNetwork.get(mapping.network.rewardName), netConfigFile)
    minDiff = mars.element(mapping.network.minDiff, globals.defaultNetwork.get(mapping.network.minDiff), netConfigFile)
    maxDiff = mars.element(mapping.network.maxDiff, globals.defaultNetwork.get(mapping.network.maxDiff), netConfigFile)
    testNet = mars.element(mapping.network.testNet, globals.defaultNetwork.get(mapping.network.testNet), netConfigFile)

## Safe configs
class config:
    dataPath = dict(unsafeConfig.dataPath.get())
    minerAddress = str(unsafeConfig.minerAddress.get())
    minerEndpoint = str(unsafeConfig.minerEndpoint.get())

### Chain config
class chainConfig:
    name = str(unsafeNetConfig.name.get())
    initEndpoint = str(unsafeNetConfig.initEndpoint.get())
    netID = str(unsafeNetConfig.netID.get())
    maxSupply = float(unsafeNetConfig.maxSupply.get())
    maxAmount = float(unsafeNetConfig.maxAmount.get())
    maxReward = float(unsafeNetConfig.maxReward.get())
    rewardName = str(unsafeNetConfig.rewardName.get())
    testNet = bool(unsafeNetConfig.testNet.get())

### Mining config
class miningConfig:
    mining = bool(unsafeConfig.mining.get())
    multiprocessingMining = bool(unsafeConfig.multiprocessingMining.get())
    timeBetweenCheck = float(unsafeConfig.timeToCheck.get())
    minDiff = int(unsafeNetConfig.minDiff.get())
    maxDiff = int(unsafeNetConfig.maxDiff.get())

# Helpers
class helpers:
    printer, messageLevelTypes = superPrinter.printer(), superPrinter.levels
    baseExceptions = (AttributeError, TypeError, ValueError, ZeroDivisionError)
    networkingExceptions = (AttributeError, TypeError, ValueError, ZeroDivisionError, requests.exceptions.HTTPError, requests.exceptions.ConnectTimeout, requests.exceptions.SSLError, requests.exceptions.Timeout, requests.exceptions.TooManyRedirects, requests.exceptions.ConnectionError)
    updateExceptions = (AttributeError, TypeError, ValueError, ZeroDivisionError, PermissionError, FileNotFoundError)

# Status
class status:
    debug = False
    inform = bool(unsafeConfig.inform.get())
    class miner: newBlockMined = False
    class extras: bypassIntegrityCheck = False

# Databases
class databases:
    # The databases manager won't load if the process is not the main
    if str(multiprocessing.current_process().name) == "MainProcess":
        from . import storage
        chainDB = storage.storage.chain()
        nodesDB = storage.storage.nodes()
        memPool = storage.storage.memPool()
