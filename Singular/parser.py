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
from . import declarations
from . import manager
from . import frontend
from . import network
from . import helper
from . import test
import argparse
import base64

class Arguments:
    @staticmethod
    def parse():
        """
        Parse arguments
        """
        arguments = argparse.ArgumentParser(prog="Singular")
        arguments.add_argument("-m", "--minerAddress", help="Pass miner address", type=str, dest="address")
        arguments.add_argument("-s", "--show", help="Display the path of the databases and the network name before start", dest="show", action="store_true")
        arguments.add_argument("-sN", "--showNetwork", help="Get network raw info", dest="showNetwork", action="store_true")
        arguments.add_argument("-tm", "--toggleMining", help=("Enable mining" if declarations.miningConfig.mining is False else "Disable mining"), action="store_true")
        arguments.add_argument("-tmP", "--toggleMultiprocessingMining", help=("Enable multiprocessing mining" if declarations.miningConfig.multiprocessingMining is False else "Disable multiprocessing mining"), action="store_true")
        arguments.add_argument("--pathChain", help="Change the default path to save the chain (Add {path} to get the Singular path)", type=str, dest="chainPath")
        arguments.add_argument("--pathNodes", help="Change the default path to save the nodes (Add {path} to get the Singular path)", type=str, dest="nodesPath")
        arguments.add_argument("--clear", help="Delete the databases contents", action="store_true")
        arguments.add_argument("-nS", "--networkSetup", help="Prompt the Network Setup Agent", action="store_true")
        arguments.add_argument("-t", "--test", help="Perform the tests", action="store_true")
        arguments.add_argument("-d", "--debug", help="Enables debug mode", action="store_true")
        arguments.add_argument("-q", "--quit", help="Exit", action="store_true")
        argsReturns = arguments.parse_args()
        # Perform the tasks of the arguments
        Arguments.update(argsReturns)
        # Check if has to exit after the arguments passed
        argsToExit = argsReturns.networkSetup or argsReturns.address or argsReturns.chainPath or argsReturns.nodesPath or argsReturns.toggleMining or argsReturns.toggleMultiprocessingMining or argsReturns.clear or argsReturns.test or argsReturns.quit
        if argsToExit:
            # If the show argument was passed, show the paths before exiting
            if argsReturns.show: print("\nChain path: {}\nNodes path: {}\nNetwork name: {}\n".format(declarations.staticConfig.dataPath["chain"], declarations.staticConfig.dataPath["nodes"], declarations.chainConfig.name))
            # If the showNetwork argument was passed, show the network info before exiting
            if argsReturns.showNetwork: print("Network settings: {}\nEncoded version: {}\n".format(network.Network.config.getConf(),(base64.b64encode(str(network.Network.config.getConf()).encode())).decode()))
            exit()
        return argsReturns

    @staticmethod
    def update(argsReturns):
        """
        Check the arguments passed
        """
        # Check if debug was passed
        if argsReturns.debug:
            # Activate debug mode
            helper.enableDebug()
        # Check if network setup was passed
        if argsReturns.networkSetup:
            # Initialize network setup agent
            try: frontend.Frontend.setup.network()
            except declarations.helpers.updateExceptions as error: print("Unable to update network settings because of the file's permissions. Error: {}".format(error))
        # Check if the minerAddress argument was passed
        if argsReturns.address:
            # Set the minerAddress
            try: declarations.dynamicConfig.minerAddress.set(str(argsReturns.address))
            except declarations.helpers.updateExceptions as error: print("Unable to update miner address because of the file's permissions".format(error))
        # Check if chainPath was passed
        if argsReturns.chainPath:
            # Declare the newDataPath
            newDataPath = declarations.staticConfig.dataPath
            # Update newDataPath with the new chainPath
            newDataPath["chain"] = str("{}/{}".format(os.path.dirname(__file__), str(argsReturns.chainPath)[6:])) if str(argsReturns.chainPath)[:6] == "{path}" else str(argsReturns.chainPath) # If {path} was added append the Singular path
            # Save newDataPath
            try: declarations.dynamicConfig.dataPath.set(dict(newDataPath))
            except declarations.helpers.updateExceptions as error: print("Unable to set chain path because of the file's permissions. Error: {}".format(error))
        # Check if nodesPath was passed
        if argsReturns.nodesPath:
            # Declare the newDataPath
            newDataPath = declarations.staticConfig.dataPath
            # Update newDataPath with the new nodesPath
            newDataPath["nodes"] = str("{}/{}".format(os.path.dirname(__file__), str(argsReturns.nodesPath)[6:])) if str(argsReturns.nodesPath)[:6] == "{path}" else str(argsReturns.nodesPath) # If {path} was added append the Singular path
            # Save newDataPath
            try: declarations.dynamicConfig.dataPath.set(dict(newDataPath))
            except declarations.helpers.updateExceptions as error: print("Unable to set nodes path. Error: {}".format(error))
        # Check if toggleMining was passed
        if argsReturns.toggleMining:
            try: declarations.dynamicConfig.mining.set(True if declarations.miningConfig.mining is False else False)
            except declarations.helpers.updateExceptions as error: print("Unable to toggle mining. Error: {}".format(error))
        # Check if toggleMultiprocessingMining was passed
        if argsReturns.toggleMultiprocessingMining:
            try: declarations.dynamicConfig.multiprocessingMining.set(True if declarations.miningConfig.multiprocessingMining is False else False)
            except declarations.helpers.updateExceptions as error: print("Unable to toggle multiprocessing mining. Error: {}".format(error))
        # Check if clear was passed
        if argsReturns.clear:
            # Remove chain
            if manager.Manager.chainMan.clearChain(): print("Chain deleted from the database successfully!")
            else: print("There was some error while trying to delete the chain from the database")
            if manager.Manager.nodesMan.clearNodes(): print("Nodes deleted from the database successfully!")
            else: print("There was some error while trying to delete the nodes from the database")
        # Check if test was passes
        if argsReturns.test:
            # Execute tests
            test.Test.performTests()
        return
