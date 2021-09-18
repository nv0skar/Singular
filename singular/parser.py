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

class argParser:
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
        extraParser = subParser.add_parser("extra", prog="{}{}".format(("\r"*len("usage: ")), "Singular -> Extra"))
        networkParser.add_argument("-sN", "--showNetwork", help="get network raw info", dest="showNetwork", action="store_true")
        networkParser.add_argument("-nS", "--networkSetup", help="prompt the Network Setup Agent", dest="networkSetup", action="store_true")
        dataParser.add_argument("-s", "--show", help="display the path of the chain's database and the network name before start", dest="show", action="store_true")
        dataParser.add_argument("-p", "--pathDB", help="change the default path of the database (Add {path} to get the Singular path)", type=str, dest="pathDB")
        dataParser.add_argument("--clear", help="delete the databases contents", dest="clear", action="store_true")
        configParser.add_argument("-mA", "--minerAddress", help="set a miner address", dest="minerAddress", action="store_true")
        configParser.add_argument("-mE", "--minerEndpoint", help="set miner endpoint's address", type=str, dest="minerEndpoint")
        configParser.add_argument("-tM", "--toggleMining", help=("enable mining" if declarations.miningConfig.mining is False else "disable mining"), dest="toggleMining", action="store_true")
        configParser.add_argument("-tmP", "--toggleMultiprocessMining", help=("enable multiprocess mining" if declarations.miningConfig.multiprocessingMining is False else "disable multiprocess mining"), dest="toggleMultiprocessMining", action="store_true")
        configParser.add_argument("-tC", "--timeToCheck", help=("set the time (in seconds) to wait until syncing from other nodes and checking if a new block is in the chain"), type=float, dest="timeToCheck")
        extraParser.add_argument("-i", "--inform", help=("show all types of log messages" if declarations.status.inform is False else "not show all log messages"), dest="inform", action="store_true")
        extraParser.add_argument("-t", "--test", help="perform the tests", dest="test", action="store_true")
        parser.add_argument("-d", "--debug", help="enables debug mode", dest="debug", action="store_true")
        parser.add_argument("-v", "--version", help="show version", dest="version", action="store_true")
        # Parse the arguments
        parsedArgs = parser.parse_args()
        # Perform the function of the arguments passed
        argParser.update(parsedArgs)
        # Check if has to exit depending in the arguments passed
        if bool(argParser.utils.argsToExitCheck(parsedArgs)): exit()
        return

    @staticmethod
    def update(args):
        """
        Check the arguments passed
        """
        # Check if the show argument was passed
        try:
            if args.show:
                print("\nChain path: {}\nNetwork name: {}\n".format(str(declarations.config.dbPath), str(declarations.chainConfig.name)))
        except (AttributeError): pass
        # Check if the showNetwork argument was passed
        try:
            if args.showNetwork:
                print("\nRaw network settings: {}{}Encoded network settings: {}\n".format(str(network.network.config.getConf(True)), ("\n\n{}\n\n".format("-" * 32)), (base64.b64encode(str(network.network.config.getConf(True)).encode())).decode()))
        except (AttributeError): pass
        # Check if debug was passed
        try:
            if args.debug:
                # Activate debug mode
                helper.debugging.enableDebug()
        except (AttributeError): pass
        # Check if inform was passed
        try:
            if args.inform:
                try: declarations.unsafeConfig.inform.set(True if declarations.status.inform is False else False)
                except declarations.helpers.updateExceptions as error: helper.reporter.compromised("Unable to toggle inform. Error: {}".format(error))
        except (AttributeError): pass
        # Check if network setup was passed
        try:
            if args.networkSetup:
                # Initialize network setup agent
                try: frontend.frontend.setup.network()
                except declarations.helpers.updateExceptions as error: helper.reporter.compromised("Unable to set network settings. Error: {}".format(error))
        except (AttributeError): pass
        # Check if the minerAddress argument was passed
        try:
            if args.minerAddress:
                # Initialize node's address setup agent
                try: frontend.frontend.setup.address()
                except declarations.helpers.updateExceptions as error: helper.reporter.compromised("Unable to set miner's address. Error: {}".format(error))
        except (AttributeError): pass
        # Check if the minerEndpoint argument was passed
        try:
            if args.minerEndpoint:
                dataIntegrity = True
                # Check the endpoint's address integrity
                try: _, _ = helper.networking.segmentEndpointAddress(str(args.minerEndpoint))
                except (declarations.helpers.baseExceptions): dataIntegrity = False; helper.reporter.compromised("The passed endpoint's address is not valid. Check that follows the following format: IP:PORT")
                # Set the minerEndpoint
                if dataIntegrity:
                    try: declarations.unsafeConfig.minerEndpoint.set(str(args.minerEndpoint))
                    except declarations.helpers.updateExceptions as error: helper.reporter.compromised("Unable to set miner's endpoint address. Error {}".format(error))
        except (AttributeError): pass
        # Check if pathDB was passed
        try:
            if args.pathDB:
                # Compose the new database path
                newDBPath = str("{}/{}".format(os.path.dirname(__file__), str(args.pathDB)[6:])) if str(args.pathDB)[:6] == "{path}" else str(args.pathDB) # If {path} was added append the Singular path
                # Save the new database path
                try: declarations.unsafeConfig.dbPath.set(newDBPath)
                except declarations.helpers.updateExceptions as error: helper.reporter.compromised("Unable to set database path. Error: {}".format(error))
        except (AttributeError): pass
        # Check if toggleMining was passed
        try:
            if args.toggleMining:
                try: declarations.unsafeConfig.mining.set(True if declarations.miningConfig.mining is False else False)
                except declarations.helpers.updateExceptions as error: helper.reporter.compromised("Unable to toggle mining. Error: {}".format(error))
        except (AttributeError): pass
        # Check if toggleMultiprocessMining was passed
        try:
            if args.toggleMultiprocessMining:
                try: declarations.unsafeConfig.multiprocessingMining.set(True if declarations.miningConfig.multiprocessingMining is False else False)
                except declarations.helpers.updateExceptions as error: helper.reporter.compromised("Unable to toggle multiprocessing mining. Error: {}".format(error))
        except (AttributeError): pass
        # Check if the timeToCheck argument was passed
        try:
            if args.timeToCheck:
                dataIntegrity = True
                # Check the time to check integrity
                try: _ = float(args.timeToCheck)
                except (declarations.helpers.baseExceptions): dataIntegrity = False; helper.reporter.compromised("The passed number was not valid.")
                # Set the timeToCheck
                if dataIntegrity:
                    try: declarations.unsafeConfig.timeToCheck.set(str(args.timeToCheck))
                    except declarations.helpers.updateExceptions as error: helper.reporter.compromised("Unable to update the value. Error {}".format(error))
        except (AttributeError): pass
        # Check if clear was passed
        try:
            if args.clear:
                # Delete local chain
                if manager.manager.chainMan.clearChain(): print("Chain deleted from the database successfully!")
                else: helper.reporter.compromised("There was some error while trying to delete the chain from the database")
        except (AttributeError): pass
        # Check if test was passes
        try:
            if args.test: test.test.performTests() # Execute tests
        except (AttributeError): pass
        # Check if the version argument was passed
        try:
            if args.version: print("Version: v{}\nImplementation version: v{}\n".format(declarations.core.version, declarations.core.protocolVersion))
        except (AttributeError): pass
        return

    class utils:
        @staticmethod
        def argsToExitCheck(args):
            try:
                if args.show: return True
            except (AttributeError): pass
            try:
                if args.showNetwork: return True
            except (AttributeError): pass
            try:
                if args.networkSetup: return True
            except (AttributeError): pass
            try:
                if args.minerAddress: return True
            except (AttributeError): pass
            try:
                if args.minerEndpoint: return True
            except (AttributeError): pass
            try:
                if args.pathDB: return True
            except (AttributeError): pass
            try:
                if args.toggleMining: return True
            except (AttributeError): pass
            try:
                if args.toggleMultiprocessMining: return True
            except (AttributeError): pass
            try:
                if args.timeToCheck: return True
            except (AttributeError): pass
            try:
                if args.clear: return True
            except (AttributeError): pass
            try:
                if args.inform: return True
            except (AttributeError): pass
            try:
                if args.test: return True
            except (AttributeError): pass
            try:
                if args.version: return True
            except (AttributeError): pass
            return False
