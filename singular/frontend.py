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
import base64
from . import declarations
from . import mapping
from . import network
from . import helper
import ast
import cfonts
from rich.prompt import Prompt, Confirm
from rich.console import Console, Style

class frontend:
    @staticmethod
    def initial():
        """
        Shows some info and update the miner address If requested
        """
        # Clear the screen
        os.system('cls' if os.name == 'nt' else 'clear')
        # Show name
        print(cfonts.render('Singular', colors=["#8b00a6", '#4328a6'], align='center'))
        # Show info
        print("{} - {}\nCtrl-C to exit\n".format(str(declarations.core.version), str(declarations.core.url)))

    class setup:
        @staticmethod
        def address():
            """
            Setup a new address for the node
            """
            # Clear the screen
            os.system('cls' if os.name == 'nt' else 'clear')
            # Show title
            Console().print("Node's address setup agent", style=Style(color="purple", bold=True, underline=True), justify="center")
            # Ask if want to directly provide a public key or generate a new one
            if not Confirm.ask("Do you want to enter an existent public key?"):
                # Generate new address
                publicKey, privateKey = helper.address.generate()
                # Print the info
                print("Public key (base16 Encoded): {}".format(base64.b16encode(eval(str(publicKey))).decode()))
                print("Private key (base16 Encoded): {}".format(base64.b16encode(eval(str(privateKey))).decode()))
                # Set the address
                declarations.unsafeConfig.minerAddress.set(base64.b16encode(eval(str(publicKey))).decode())
            else:
                # Ask for public key
                publicKey = Prompt.ask("Public key", default=str(declarations.config.minerAddress))
                # Set the address
                declarations.unsafeConfig.minerAddress.set(publicKey)

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
                # Ask for network's init endpoint's address
                netInitEndpoint = Prompt.ask("Initial endpoint's address", default=str(declarations.chainConfig.initEndpoint))
                # Ask for network's ID
                netID = Prompt.ask("Network's ID (Leave empty to use the default one, put {generate} to generate a new one)", default=str(declarations.chainConfig.netID))
                # Ask for maxSupply
                netMaxSupply = Prompt.ask("Network's max supply", default=str(declarations.chainConfig.maxSupply))
                 # Ask for maxAmount
                netMaxAmount = Prompt.ask("Network's max amount (The maximum amount that 1 transaction could send per time)", default=str(declarations.chainConfig.maxAmount))
                # Ask for maxReward
                netMaxReward = Prompt.ask("Network's max reward", default=str(declarations.chainConfig.maxReward))
                # Ask for rewardName
                netRewardName = Prompt.ask("Network's reward name", default=str(declarations.chainConfig.rewardName))
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
                if bool(rawNetConf.get(mapping.network.name)): netName = str(rawNetConf.get(mapping.network.name))
                else: netName = declarations.chainConfig.name
                # Get the network's init endpoint's address
                if bool(rawNetConf.get(mapping.network.initEndpoint)): netInitEndpoint = str(rawNetConf.get(mapping.network.initEndpoint))
                else: netInitEndpoint = declarations.chainConfig.initEndpoint
                # Get the network's magic number
                if bool(rawNetConf.get(mapping.network.netID)): netID = str(rawNetConf.get(mapping.network.netID))
                else: netID = declarations.chainConfig.netID
                # Get the maxSupply
                if bool(rawNetConf.get(mapping.network.maxSupply)): netMaxSupply = float(rawNetConf.get(mapping.network.maxSupply))
                else: netMaxSupply = declarations.chainConfig.maxSupply
                # Get the maxAmount
                if bool(rawNetConf.get(mapping.network.maxAmount)): netMaxAmount = float(rawNetConf.get(mapping.network.maxAmount))
                else: netMaxAmount = declarations.chainConfig.maxAmount
                # Get the maxReward
                if bool(rawNetConf.get(mapping.network.maxReward)): netMaxReward = float(rawNetConf.get(mapping.network.maxReward))
                else: netMaxReward = declarations.chainConfig.maxReward
                # Get the rewardName
                if bool(rawNetConf.get(mapping.network.rewardName)): netRewardName = str(rawNetConf.get(mapping.network.rewardName))
                else: netRewardName = declarations.chainConfig.rewardName
                # Get the minDiff
                if bool(rawNetConf.get(mapping.network.minDiff)): netMinDiff = str(rawNetConf.get(mapping.network.minDiff))
                else: netMinDiff = declarations.miningConfig.minDiff
                # Get the maxDiff
                if bool(rawNetConf.get(mapping.network.maxDiff)): netMaxDiff = str(rawNetConf.get(mapping.network.maxDiff))
                else: netMaxDiff = declarations.miningConfig.maxDiff
                # Get if network is testnet
                if bool(rawNetConf.get(mapping.network.minDiff)): netTestNet = bool(rawNetConf.get(mapping.network.testNet))
                else: netTestNet = declarations.chainConfig.testNet
            # Execute setup
            setupSuccess = network.network.config.setup(netName, netInitEndpoint, netID, netMaxSupply, netMaxAmount, netMaxReward, netRewardName, netMinDiff, netMaxDiff, netTestNet)
            if not type(setupSuccess) is str: Console().print("Network setup agent completed successfully", style=Style(color="green"))
            else: Console().print("Network setup agent failed: {}".format(setupSuccess), style=Style(color="red", bold=True))

    class dialogs:
        @staticmethod
        def startChain() -> bool:
            """
            Ask if a new chain should start
            """
            return bool(Confirm.ask("There isn't a chain started. Do you want to start a new one? (Syncing with other nodes will occur after starting the local chain)"))

        @staticmethod
        def blockMined(block):
            """
            Print that the block Is mined
            """
            helper.reporter.report("main", "Block mined! Block number: {}; Mining time: {}".format(block.get(mapping.block.blockNumber), block.get(mapping.block.minerTime)), force=True)
