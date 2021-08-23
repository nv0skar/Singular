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
import time
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
        parser = argparse.ArgumentParser(prog="{}{}".format(("\r"*len("usage: ")), "Singular"))
        subParser = parser.add_subparsers(help="pass '-h' or '--help' to a positional argument to display its usage")
        networkParser = subParser.add_parser("network", prog="{}{}".format(("\r"*len("usage: ")), "Singular -> Network"))
        dataParser = subParser.add_parser("data", prog="{}{}".format(("\r"*len("usage: ")), "Singular -> Data"))
        configParser = subParser.add_parser("config", prog="{}{}".format(("\r"*len("usage: ")), "Singular -> Settings"))
        extraParser = subParser.add_parser("extra", prog="{}{}".format(("\r"*len("usage: ")), "Singular -> Extras"))
        networkParser.add_argument("-sN", "--showNetwork", help="get network raw info", dest="showNetwork", action="store_true")
        networkParser.add_argument("-nS", "--networkSetup", help="prompt the Network Setup Agent", action="store_true")
        dataParser.add_argument("-s", "--show", help="display the path of the databases and the network name before start", dest="show", action="store_true")
        dataParser.add_argument("--pathChain", help="change the default path to save the chain (Add {path} to get the Singular path)", type=str, dest="chainPath")
        dataParser.add_argument("--pathNodes", help="change the default path to save the nodes (Add {path} to get the Singular path)", type=str, dest="nodesPath")
        dataParser.add_argument("--clear", help="delete the databases contents", action="store_true")
        configParser.add_argument("-m", "--minerAddress", help="set miner address", type=str, dest="address")
        configParser.add_argument("-tm", "--toggleMining", help=("enable mining" if declarations.miningConfig.mining is False else "disable mining"), action="store_true")
        configParser.add_argument("-tmP", "--toggleMultiprocessingMining", help=("enable multiprocessing mining" if declarations.miningConfig.multiprocessingMining is False else "disable multiprocessing mining"), action="store_true")
        extraParser.add_argument("-t", "--test", help="perform the tests", action="store_true")
        extraParser.add_argument("-d", "--debug", help="enables debug mode", action="store_true")
        parser.add_argument("-v", "--version", help="show version", action="store_true")
        parser.add_argument("-q", "--quit", help="exit", action="store_true")
        # Parse the arguments
        parsedArgs = parser.parse_args()
        # Perform the function the arguments passed
        Arguments.update(parsedArgs)
        # Check if has to exit
        hasToExit = Arguments.utils.argsToExitCheck(parsedArgs)
        # If the show argument was passed, show the paths
        try:
            if parsedArgs.show:
                print("\nChain path: {}\nNodes path: {}\nNetwork name: {}\n".format(declarations.staticConfig.dataPath["chain"], declarations.staticConfig.dataPath["nodes"], declarations.chainConfig.name))
                if not hasToExit: print("Waiting 5 seconds before resuming initialization process"); time.sleep(5)
        except (AttributeError): pass
        # If the showNetwork argument was passed, show the network info
        try:
            if parsedArgs.showNetwork:
                print("\nRaw network settings: {}{}Encoded network settings: {}\n".format(str(network.Network.config.getConf(True)), ("\n\n{}\n\n".format("-"*32)), (base64.b64encode(str(network.Network.config.getConf(True)).encode())).decode()))
                if not hasToExit: print("Waiting 5 seconds before resuming initialization process"); time.sleep(5)
        except (AttributeError): pass
        # If the version argument was passed, show the version info
        try:
            if parsedArgs.version:
                print("Version: v{}\nImplementation version: v{}\n".format(declarations.core.version, declarations.core.protocolVersion))
                if not hasToExit: print("Waiting 5 seconds before resuming initialization process"); time.sleep(5)
        except (AttributeError): pass
        # Check if has to exit after the arguments passed
        if hasToExit: exit()
        return

    @staticmethod
    def update(args):
        """
        Check the arguments passed
        """
        # Check if debug was passed
        try:
            if args.debug:
                # Activate debug mode
                helper.enableDebug()
        except (AttributeError): pass
        # Check if network setup was passed
        try:
            if args.networkSetup:
                # Initialize network setup agent
                try: frontend.Frontend.setup.network()
                except declarations.helpers.updateExceptions as error: print("Unable to update network settings. Error: {}".format(error))
        except (AttributeError): pass
        # Check if the minerAddress argument was passed
        try:
            if args.address:
                # Set the minerAddress
                try: declarations.dynamicConfig.minerAddress.set(str(args.address))
                except declarations.helpers.updateExceptions as error: print("Unable to update miner address. Error {}".format(error))
        except (AttributeError): pass
        # Check if chainPath was passed
        try:
            if args.chainPath:
                # Declare the newDataPath
                newDataPath = declarations.staticConfig.dataPath
                # Update newDataPath with the new chainPath
                newDataPath["chain"] = str("{}/{}".format(os.path.dirname(__file__), str(args.chainPath)[6:])) if str(args.chainPath)[:6] == "{path}" else str(args.chainPath) # If {path} was added append the Singular path
                # Save newDataPath
                try: declarations.dynamicConfig.dataPath.set(dict(newDataPath))
                except declarations.helpers.updateExceptions as error: print("Unable to set chain path. Error: {}".format(error))
        except (AttributeError): pass
        # Check if nodesPath was passed
        try:
            if args.nodesPath:
                # Declare the newDataPath
                newDataPath = declarations.staticConfig.dataPath
                # Update newDataPath with the new nodesPath
                newDataPath["nodes"] = str("{}/{}".format(os.path.dirname(__file__), str(args.nodesPath)[6:])) if str(args.nodesPath)[:6] == "{path}" else str(args.nodesPath) # If {path} was added append the Singular path
                # Save newDataPath
                try: declarations.dynamicConfig.dataPath.set(dict(newDataPath))
                except declarations.helpers.updateExceptions as error: print("Unable to set nodes path. Error: {}".format(error))
        except (AttributeError): pass
        # Check if toggleMining was passed
        try:
            if args.toggleMining:
                try: declarations.dynamicConfig.mining.set(True if declarations.miningConfig.mining is False else False)
                except declarations.helpers.updateExceptions as error: print("Unable to toggle mining. Error: {}".format(error))
        except (AttributeError): pass
        # Check if toggleMultiprocessingMining was passed
        try:
            if args.toggleMultiprocessingMining:
                try: declarations.dynamicConfig.multiprocessingMining.set(True if declarations.miningConfig.multiprocessingMining is False else False)
                except declarations.helpers.updateExceptions as error: print("Unable to toggle multiprocessing mining. Error: {}".format(error))
        except (AttributeError): pass
        # Check if clear was passed
        try:
            if args.clear:
                # Remove chain
                if manager.Manager.chainMan.clearChain(): print("Chain deleted from the database successfully!")
                else: print("There was some error while trying to delete the chain from the database")
                if manager.Manager.nodesMan.clearNodes(): print("Nodes deleted from the database successfully!")
                else: print("There was some error while trying to delete the nodes from the database")
        except (AttributeError): pass
        # Check if test was passes
        try:
            if args.test: test.Test.performTests() # Execute tests
        except (AttributeError): pass
        return

    class utils:
        @staticmethod
        def argsToExitCheck(args):
            try:
                if args.networkSetup: return True
            except (AttributeError): pass
            try:
                if args.address: return True
            except (AttributeError): pass
            try:
                if args.chainPath: return True
            except (AttributeError): pass
            try:
                if args.nodesPath: return True
            except (AttributeError): pass
            try:
                if args.toggleMining: return True
            except (AttributeError): pass
            try:
                if args.toggleMultiprocessingMining: return True
            except (AttributeError): pass
            try:
                if args.clear: return True
            except (AttributeError): pass
            try:
                if args.test: return True
            except (AttributeError): pass
            try:
                if args.version: return True
            except (AttributeError): pass
            try:
                if args.quit: return True
            except (AttributeError): pass
            return False
