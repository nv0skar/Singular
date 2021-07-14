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
from . import network
from . import helper
import ast
import base64
import cfonts
from rich.prompt import Prompt, Confirm
from rich.console import Console, Style
import superPrinter

class Frontend:
    @staticmethod
    def initial(passedArguments=None):
        """
        Shows some info and update the miner address If requested
        """
        # Clear the screen
        os.system('cls' if os.name == 'nt' else 'clear')
        # Show name
        print(cfonts.render('Singular', colors=["#8b00a6", '#4328a6'], align='center'))
        # Show info
        print("{} - {}\nCtrl-C to exit\n".format(declarations.info.get("version"), declarations.info.get("url")))
        if passedArguments is not None:
            # Show path If the show argument was passed
            if passedArguments.show: print("Chain path: {}\nNodes path: {}\nNetwork name: {}\n".format(declarations.staticConfig.dataPath["chain"], declarations.staticConfig.dataPath["nodes"], declarations.chainConfig.name))
            # Show the network info, If the showNetwork argument was passed
            if passedArguments.showNetwork: print("Network settings: {}\nEncoded version: {}\n".format(network.Network.config.getConf(),(base64.b64encode(str(network.Network.config.getConf()).encode())).decode()))
        pass

    class setup:
        @staticmethod
        def network():
            """
            Setup a new network interface
            """
            # Clear the screen
            os.system('cls' if os.name == 'nt' else 'clear')
            # Show title
            Console().print("Network setup agent", style=Style(color="purple", bold=True, underline=True), justify="center")
            # Ask if directly get the RAW network info or configure manually
            if not Confirm.ask("Do you want to enter the RAW network configuration?"):
                # Ask for network name
                netName = Prompt.ask("Network name", default=str(declarations.chainConfig.name))
                # Ask for bootstrap IP
                netBootstrapIP = Prompt.ask("Bootstrap IP", default=str(declarations.chainConfig.bootstrapIP))
                # Ask for network's magic number
                netMagicNumber = Prompt.ask("Network's magic number (Leave empty to use the default one, put {generate} to generate a new one)", default=str(declarations.chainConfig.magicNumber))
                # Ask for maxSupply
                netMaxSupply = Prompt.ask("Network's max supply", default=str(declarations.chainConfig.maxSupply))
                # Ask for blockMaxReward
                netBlockMaxReward = Prompt.ask("Network's block max reward", default=str(declarations.chainConfig.blockMaxReward))
                # Ask for rewardName
                netRewardName = Prompt.ask("Network's reward name", default=str(declarations.chainConfig.rewardName))
                # Ask for maxAmount
                netMaxAmount = Prompt.ask("Network's max amount (The maximum amount that 1 transaction could send per time)", default=str(declarations.chainConfig.maxAmount))
                # Ask for minDiff
                netMinDiff = Prompt.ask("Network's minimum difficulty", default=str(declarations.miningConfig.minDiff))
                # Ask for maxDiff
                netMaxDiff = Prompt.ask("Network's maximum difficulty", default=str(declarations.miningConfig.maxDiff))
                # Ask for testNet
                netTestNet = Confirm.ask("Is a testnet?", default=bool(declarations.chainConfig.testNet))
            else:
                # Ask for the RAW network config
                rawNetConfInput = Prompt.ask("Network RAW configuration")
                # Get the values from the dict entered in rawNetConf
                try: rawNetConf = dict(ast.literal_eval(rawNetConfInput))
                except (ValueError, SyntaxError):
                    try: rawNetConf = dict(ast.literal_eval(str(base64.b64decode(rawNetConfInput.encode()).decode())))
                    except (ValueError, SyntaxError): Console().print("Network setup agent failed: {}".format("The entered configuration was invalid"), style=Style(color="red", bold=True)); return
                # Get the network name
                if bool(rawNetConf.get("name")): netName = str(rawNetConf.get("name"))
                else: netName = declarations.chainConfig.name
                # Get the bootstrap IP
                if bool(rawNetConf.get("bootstrapIP")): netBootstrapIP = str(rawNetConf.get("bootstrapIP"))
                else: netBootstrapIP = declarations.chainConfig.bootstrapIP
                # Get the network's magic number
                if bool(rawNetConf.get("magicNumber")): netMagicNumber = str(rawNetConf.get("magicNumber"))
                else: netMagicNumber = declarations.chainConfig.magicNumber
                # Get the maxSupply
                if bool(rawNetConf.get("maxSupply")): netMaxSupply = str(rawNetConf.get("maxSupply"))
                else: netMaxSupply = declarations.chainConfig.maxSupply
                # Get the blockMaxReward
                if bool(rawNetConf.get("blockMaxReward")): netBlockMaxReward = str(rawNetConf.get("blockMaxReward"))
                else: netBlockMaxReward = declarations.chainConfig.blockMaxReward
                # Get the rewardName
                if bool(rawNetConf.get("rewardName")): netRewardName = str(rawNetConf.get("rewardName"))
                else: netRewardName = declarations.chainConfig.rewardName
                # Get the maxAmount
                if bool(rawNetConf.get("maxAmount")): netMaxAmount = str(rawNetConf.get("maxAmount"))
                else: netMaxAmount = declarations.chainConfig.maxAmount
                # Get the minDiff
                if bool(rawNetConf.get("minDiff")): netMinDiff = str(rawNetConf.get("minDiff"))
                else: netMinDiff = declarations.miningConfig.minDiff
                # Get the maxDiff
                if bool(rawNetConf.get("maxDiff")): netMaxDiff = str(rawNetConf.get("maxDiff"))
                else: netMaxDiff = declarations.miningConfig.maxDiff
                # Get if network is testnet
                if bool(rawNetConf.get("minDiff")): netTestNet = bool(rawNetConf.get("testNet"))
                else: netTestNet = declarations.chainConfig.testNet
            # Execute setup
            setupSuccess = network.Network.config.setup(netName, netBootstrapIP, netMagicNumber, netMaxSupply, netBlockMaxReward, netRewardName, netMaxAmount, netMinDiff, netMaxDiff, netTestNet)
            if not type(setupSuccess) is str: Console().print("Network setup agent completed successfully", style=Style(color="green"))
            else: Console().print("Network setup agent failed: {}".format(setupSuccess), style=Style(color="red", bold=True))

    class dialogs:
        @staticmethod
        def startChain() -> bool:
            """
            Ask if a new chain should start
            """
            return bool(Confirm.ask("There isn't a chain started. Do you want to start a new one?"))

        @staticmethod
        def blockMined(block):
            """
            Print that the block Is mined
            """
            helper.report("main", "Block mined! Block number: {}; Mining time: {}".format(block.get("blockNumber"), block.get("minerTime")))
