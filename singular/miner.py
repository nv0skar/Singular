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

import random
import time
from . import declarations
from . import manager
# from . import startpoint
from . import helper
import multiprocessing

class miner:
    @staticmethod
    def start(block, difficulty, prefix, initializingTime):
        """
        Starts the miner
        """
        declarations.status.miner.newBlock = False
        if (declarations.miningConfig.multiprocessingMining) and (multiprocessing.cpu_count() > 1):
            # Define a process shared object to retrieve the block mined
            blockToMine = multiprocessing.Queue()
            # Make event to stop processes when one finishes or the block is synced from other node
            stopMining = multiprocessing.Event()
            # Define processes pool
            pool = []
            # Append processes
            for cpuNumber in range(multiprocessing.cpu_count()):
                if int(multiprocessing.cpu_count()-cpuNumber) != 0: pool.append(multiprocessing.Process(target=miner.mine, args=(block, difficulty, prefix, initializingTime, blockToMine, stopMining)))
                else: pool.append(multiprocessing.Process(target=miner.utils.multiprocessSpecific.sync2Check, args=(int(block.blockNumber), stopMining)))
            # Start processes
            for process in pool:
                # Set daemon as True to avoid the KeyboardInterrupt exception not being catched
                process.daemon = True
                # Start process
                process.start()
            # Wait until one process finishes
            while not stopMining.is_set(): pass
            # Wait for them to finish
            for process in pool: process.join()
            # Kill processes
            for process in pool: process.kill()
            # Get block
            blockMined = blockToMine.get()
        else:
            # Display a message if multiprocessing is enabled but there's only 1 core
            if (declarations.miningConfig.multiprocessingMining) and (multiprocessing.cpu_count() == 1): helper.reporter.report("miner", "Couldn't mine multiprocess because there's only 1 core", level=declarations.helpers.messageLevelTypes.warning)
            blockMined = miner.mine(block, difficulty, prefix, initializingTime, None, None)
        # Return block mined
        if type(blockMined) is bool: return False
        else: return dict(blockMined)

    @staticmethod
    def mine(blockToMine, difficulty, prefix, initializingTime, passBlock, stopMining):
        if stopMining is None and not declarations.miningConfig.multiprocessingMining: lastCheckTime = float(time.time())
        while miner.utils.check2Continue(stopMining):
            # Check if a block was received and sync with other nodes
            if stopMining is None and not declarations.miningConfig.multiprocessingMining: 
                if float(lastCheckTime+declarations.miningConfig.timeBetweenCheck) <= float(time.time()):
                    miner.utils.sync2Check(int(blockToMine.blockNumber), stopMining)
                    lastCheckTime = float(time.time())
            # Stage 5 - Set the miner time
            '''
            The miner time randomizes the hash, requiring more or less nonces.
            This makes the network less dependant of powerful computers.
            '''
            blockToMine.minerTime = (float(time.time()) - initializingTime)
            # Stage 6 - Set the nonce
            '''
            The following line calculate a random nonce to use each time
            '''
            blockToMine.nonce = random.randint(0, pow(2,64))
            # Check If the block Is mined
            if blockToMine.hashBlock()[:difficulty] == prefix:
                # The nonce was found
                if declarations.miningConfig.multiprocessingMining:
                    # Pass the block
                    passBlock.put(blockToMine.get())
                    # Set that one block was mined
                    stopMining.set()
                return blockToMine.get()
        # If no more tries, return
        return

    class utils:
        class multiprocessSpecific:
            @staticmethod
            def sync2Check(blockNumber, stopMining):
                """
                Loop the miner.utils.sync2Check function with the setted delay
                """
                while miner.utils.check2Continue(stopMining): 
                    miner.utils.sync2Check(blockNumber, stopMining)
                    # Wait until continue
                    sleep(float(declarations.miningConfig.timeBetweenCheck))
                return

        @staticmethod
        def sync2Check(blockNumber, stopMining):
            """
            Sync the chain and check if the block that is being mined is in the chain
            """
            print("Miner called")
            # Check if a block was received
            if bool(declarations.status.miner.newBlock): stopMining.set(); return
            # Sync the chain
            # if not bool(helper.debugging.status()): startpoint.startpoint.sync()
            # Get the last block number and check if is the same as the block number that is being mined
            if (int(manager.manager.chainMan.getHeight()-1) == blockNumber): stopMining.set(); return
            else: return
            
        @staticmethod
        def check2Continue(stopMining):
            """
            Check if multiprocessing is enabled and give different responses
            """
            if stopMining is None and not declarations.miningConfig.multiprocessingMining: 
                return True
            if stopMining is not None and declarations.miningConfig.multiprocessingMining: 
                return (not stopMining.is_set())
